# 2026-10-07 - P1.3 Closeout OOM Root Cause, Memory Fix, 2 GiB Limit and After-Hours Production Deployment

Status: **P1.3 = PRODUCTION_DEPLOYED_PENDING_LIVE_ACCEPTANCE**. **P1.2 = OBSERVING.**
Not claimed: FULL P1.3 FREEZE, P1.2 scheduled-validation PASS, R6 live acceptance PASS, next-day (15:30) Docker closeout PASS.

## 1. Incident

- 2026-10-06 15:34-17:13 and again 2026-10-07 15:30-16:48: the Docker live container restarted 23 and then 13+ times
  (`RestartCount` 23 -> 43, ownership generation 5 -> 28 -> 48). PID 1 died about 200-250 s after each in-process
  closeout started (`kiwoom_market_status_4` trigger). Because the durable completion marker is written only after
  a full successful closeout, every restart re-triggered the same closeout; the storm ended only when the Host
  fallback closeout wrote durable SUCCESS (10-06 17:09, 10-07 16:48).
- Daily UEF failed closed at 16:45 on both days (closeout-written daily sources still stale). UEF semantics were
  correct and unchanged; a manual recovery run on 10-07 afterwards passed (UEF9RUN_26b039605760f90b, 14 candidates,
  91 pairs: 0 COMPARABLE / 7 CONDITIONAL / 84 NOT_COMPARABLE) and does not replace the failed scheduled run.

## 2. Root cause

- **Proven: kernel memory-cgroup OOM kills.** The `docker-desktop` kernel log retained one `Killed process ... (python)`
  per restart (anon RSS 848-1019 MiB against the container's 1 GiB limit). `docker inspect` `OOMKilled=false` /
  `ExitCode=0` read earlier was NOT evidence: those fields reset on every restart.
- The memory was consumed inside the in-process closeout. Measured sources (Host and isolated-container profiling):
  whole-day shadow payload lists, repeated whole-file parses of the ~120 MB `q9_decision_windows.json`, the
  operator-visibility whole-day event list, a 20-day q9 window load in the Q9 evaluation, 59 overlapping cumulative
  q16 reviews, the rank1 feature mart loading every symbol and window at once, and the evaluation lens, which loads
  EVERY shadow payload from the freeze start (2026-06-29) to the day (tens of GB of JSON and growing daily).

## 3. Fix (application SHA `f4fa33521c1aeed30813a2799824eed5e12a58d6`; commits db775c2 ... f4fa335)

- Opt-in `keys=` / `drop_q9_row_keys=` projection of shadow payloads (consumers proven, by static checks and
  access-trapping tests, never to read the dropped keys); streaming `json_array_stream` reader for the q9 windows
  file; streamed visibility day rows; streamed/reduced q9 windows in Q9 evaluation, stage-2 authority, inventory,
  trade read model, no-trade attribution, candidate decisions; per-symbol rank1 loading; incremental q16 folding;
  evaluation lens folded day by day into streaming accumulators; results released after use in closeout.
- Outputs were compared with the previous implementation on real 10-01/10-02/10-06/10-07 data and were identical
  (rank1: 141 files byte-for-byte). The full 20-day rolling Q9 window was NOT compared against the old path
  (it needs several GB); the effectiveness builders were compared on 5 real days and the lens on a 9-day range.
- Per-stage cgroup/RSS logging added to the closeout stage events (`memory` block) so the next real closeout leaves
  first-hand in-container numbers.
- **Cross-namespace lock:** a Host process judged the Docker pid-1 closeout lock "dead owner" (and Docker did the
  same to a Host lock). `acquire_live_loop_lock(cross_namespace_guard=True)` (closeout only) now never reclaims a
  foreign-namespace (win vs posix identity) lock whose heartbeat is fresh (< 180 s); the closeout refreshes its own
  lock heartbeat every 30 s; a stale foreign heartbeat can be reclaimed so the Host fallback still works. The m13
  trading lock semantics are unchanged. Verified live: a Host attempt during the isolated Docker closeout returned
  `ALREADY_RUNNING_FOREIGN_NAMESPACE_OWNER` and ran nothing.
- Trading, Step5C/Step5D, UEF semantics unchanged; UEF freeze manifest 11/11 MATCH.

## 4. Limit decision

- Isolated container (same image build, mirror data incl. all shadow history since 06-29, 350 MiB ballast standing
  in for the live loop, network on, no broker credentials): **1 GiB -> OOM** (killed in the Q9 stage) -> rejected.
  **2 GiB -> PASS**: exit 0, 1381 s (23 min), durable SUCCESS exactly once, `oom_kill` 0, four UEF source files
  refreshed; max cgroup anon 1233 MiB (ballast included), process RSS peak ~984 MiB (rank1 stage), q9 stage ~795 MiB.
- Production limit adopted: **2 GiB** (`--memory 2g --memory-swap 3g`, i.e. unchanged 1 GiB of swap headroom).
  The remaining peak scales with one day's data, not the whole history. This is defense-in-depth on top of the code
  fixes, not the fix itself. `deploy/trading/compose.trading.real.yaml` `mem_limit` is now 2g (rendered
  `docker compose config` shows 2147483648).

## 5. After-hours production deployment (2026-10-07 22:39 KST)

- Pre-deploy: positions 0, open orders 0, no unresolved execution, Step5C claim rows 0, Step5D orphans 0; durable
  closeout SUCCESS present for 2026-10-02, 2026-10-06 and 2026-10-07; `.env` values identical to the old container's.
- Image `trading-agent-20261007:f4fa335` (id `sha256:4e462e62c94d...`, revision label = the full SHA above), built
  from a clean `git archive` of the SHA (no worktree). Python 3.12.15, yfinance 1.7.0, R6.2 modules, closeout
  memory fixes and `cross_namespace_guard` present.
- Controlled swap: old `trading-agent-live` (image 61586ae, RestartCount 43) stopped gracefully (exit 0, no OOM) and
  kept as the stopped rollback container `trading-agent-live-pre-20261007-deploy` (restart policy `no`); exactly one
  new `trading-agent-live`: user 10002, read-only rootfs, tmpfs /tmp, 1 CPU, `unless-stopped`, same healthcheck,
  same command, same bind mounts (`C:/Trading_Agent_System/{data,reports}`, junctions to `C:\Agentra\{data,reports}`,
  not changed here). Python is PID 1.
- Acceptance: healthy, `RestartCount` 0, `OOMKilled` false, `HostConfig.Memory` 2147483648 / `MemorySwap` 3221225472,
  idle memory ~235-258 MiB (startup transient: VmHWM 835 MiB), no memory events. Persistent state visible; today's
  2026-10-07 closeout SUCCESS visible and no second SUCCESS written. Broker read path PASS (positions 0, open orders
  0, the three known fills; the same five mock-unsupported APIs). Host live runtime count 0; the seven canonical
  scheduler tasks unchanged; `TRADING_RUNTIME_MODE=docker`; the Host watchdog keeps recording
  `HOST_LIVE_START_SKIPPED_CANONICAL_RUNTIME_DOCKER`.
- **Ownership generation did NOT advance:** the old container released its lease on graceful shutdown (the row is
  deleted by design), so the new container performed a fresh acquisition: owner `34873019aabd:1`, generation **1**
  (was 48). No stale takeover, no fencing conflict. Healthcheck `EXECUTION_READY_STATUS=EXECUTION_READY_UNKNOWN:
  snapshot_stale_...`: the readiness file is the 15:29 snapshot (after hours no readiness is produced);
  `recovery_required` false in that snapshot. Fresh GREEN readiness is a next-session item.
- R6 evidence directory `data/logs/execution_readiness_evidence/` does not exist yet (created lazily on the first
  legitimate order; none today; nothing fabricated). Its parent is writable inside the container.

## 6. Next live acceptance (not yet proven)

Preopen/scheduler; R4 Host suppression; ownership/readiness (fresh GREEN); R6.2 real-order evidence if a legitimate
order occurs; RestartCount/OOM; 15:30 Docker closeout; durable SUCCESS exactly once; closeout memory peak under
2 GiB (see the new stage `memory` events); 16:45 scheduled UEF; UEF7/8/9 + COMPLETE.

## 7. Rollback

Stop the new container, start `trading-agent-live-pre-20261007-deploy` with `docker update --restart unless-stopped`
and `docker start`, after confirming the new container is stopped (single canonical runtime). The old image
`trading-agent-20261002:61586ae` is retained.
