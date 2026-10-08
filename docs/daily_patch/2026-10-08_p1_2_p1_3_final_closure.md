# 2026-10-08 - P1.2 and P1.3 Final Closure (production evidence)

Status: **P1.2 = CLOSED** (scheduled cross-day acceptance PASS). **P1.3 = FULL DOCKER FROZEN.**
Production runtime: image `trading-agent-20261007:f4fa335` (application SHA `f4fa33521c1aeed30813a2799824eed5e12a58d6`),
container `trading-agent-live`, memory limit 2 GiB (`--memory 2g --memory-swap 3g`).
This record is read-only evidence from the first full live session after the 2026-10-07 22:39 KST deployment.

## Historical truth (not rewritten)

| Day | Scheduled 16:45 Daily UEF | Notes |
|---|---|---|
| 2026-10-06 | FAIL | closeout-written daily sources stale (Docker closeout restart storm; Host fallback finished 17:09) |
| 2026-10-07 | FAIL | same cause; Host fallback closeout finished 16:48 |
| 2026-10-07 | manual recovery PASS | one canonical manual run (UEF9RUN_26b039605760f90b); proved the chain, not scheduled timing |
| 2026-10-08 | **PASS** | first scheduled run on a same-day Docker closeout |

## A. Runtime identity

- One canonical Docker runtime, Host intraday runtime count 0, Python PID 1, `unless-stopped`, health PASS.
- Image revision label = the full f4fa335 SHA; `HostConfig.Memory` 2147483648; container up since 2026-10-07 22:39 KST with
  `RestartCount` 0, `OOMKilled` false; cgroup `memory.events`: max 0, oom 0, oom_kill 0.
- Ownership: owner `34873019aabd:1`, instance `cb57014e5312`, generation 1 all day (no takeover, no restart), heartbeat 4 s old.

## B. Preopen / live session

- 08:45 Q12-Preopen, 08:50 Preopen, 08:55 Q12-BTC-0855, 09:00 Session and SessionWatchdog each fired at its scheduled time with last result 0 (77 watchdog runs recorded).
  Preopen manifest SUCCESS (strategist ok); Q10 CAPTURED 12/13; Q12 0855 CAPTURED (BTC/KRW + BTC/USD); opening-macro 21/25
  slots (the same four 08:50-08:59 slots that the collector structurally misses every day).
- R4: 77/77 watchdog runs and the 09:00 start recorded `HOST_LIVE_START_SKIPPED_CANONICAL_RUNTIME_DOCKER`; no Host live runtime.
- Readiness: fresh execution readiness at 09:00:09 KST and 15:29:53 KST - `ready` true, `recovery_required` false,
  portfolio and open-order reconciled, `orphan_claim_count` 0, generation 1, instance `cb57014e...`.

## C. Orders and R6.2 live acceptance (first real-order exercise)

Two legitimate orders, both from Docker:

| Time | Side | Symbol | Qty | Broker order | Fill |
|---|---|---|---|---|---|
| 09:02:06 | BUY | 002720 | 155 | 0009477 | 155 @ 4840 |
| 09:04:22 | SELL | 002720 | 155 | 0013018 | 155 @ 4668 |

- Chain per order: intent -> `execution_attempt_id` -> immutable R6 evidence record (hash-verified; verdict ALLOW, phase
  `pre_broker_submit`, readiness ready, instance `cb57014e...`, generation 1, `recorded_at` 09:02:05.737 / 09:04:21.975, i.e.
  before the Step5C `executing` CAS and the broker submit) -> Step5C CAS -> broker ACCEPTED -> filled. Distinct attempt ids,
  intent_sequence 1 each, no `readiness_evidence_stale/invalid/required` event all day.
- End state: positions 0, open orders 0, Step5C claim rows 0, Step5D orphans 0, no unresolved execution, no duplicate execution.
- This is a PASS of R6.2 under real (mock-account) orders; it says nothing about strategy quality.

## D. P1.3 - Docker closeout (primary gate)

- Started 15:30:08 KST (`kiwoom_market_status_4`, run `tick-2026-10-08-2026-10-08:regular_close`), completed 15:51:50 KST
  (21 min 42 s), all 17 steps ok, lock released by its exact owner. PID 1 survived; `RestartCount` 0 before and after; no OOM;
  no restart storm.
- Durable completion: exactly one `2026-10-08:daily_closeout_maintenance` SUCCESS (trigger `kiwoom_market_status_4`, owner pid 1,
  15:51:50). The 16:00:02 Host fallback recorded `stage_skip closeout_completion_authority` (already complete) and did no
  maintenance; the 16:00:06 final-refresh trigger was skipped the same way. No lock contention occurred, so the cross-namespace
  guard was not exercised live today (verified earlier by unit tests and the isolated Docker-vs-Host run). No Host lock steal.

## E. Production closeout memory (in-container stage logs)

- Baseline at closeout start: RSS 393 MiB, cgroup current 359 MiB (live loop after the session).
- RSS at stage starts: q8 393, visibility 393, q9 start 408 (the q9 stage did not raise the process peak above the earlier
  startup VmHWM of 816 MiB), opening_rank1 559, rank1 566, same-symbol 613, end 610 MiB; final after 16:00 about 645 MiB.
- Process peak (VmHWM) 1066 MiB reached in the opening_rank1/rank1 stages (1081 MiB by 16:00). The cgroup `memory.peak` of
  1691 MiB includes reclaimable file cache and was already reached before the closeout started; it did not change during it.
  `memory.events` max 0 / oom 0 / oom_kill 0 against the 2 GiB limit. Headroom about 0.9 GiB (the 1 GiB limit would not have fit).

## F. UEF source readiness (all `through_day` 2026-10-08, written before 16:45)

| Source | Written |
|---|---|
| opening_cumulative | 15:44:59 |
| latent_reactivation | 15:50:58 |
| prospective_candidates | 15:51:48 |
| fresh_change | 15:51:48 |

## G-J. P1.2 - scheduled 16:45 Daily UEF

- Task fired once at 16:45:01, `LastTaskResult` 0; one `process_start`/`process_end` pair, exit 0, canonical root `C:\Agentra`,
  source_sha `72fc4856e4d0c72ffb4dd997741499a8dd5a6468` (docs/config only above f4fa335), duration under 1 s, no stale-source failure.
- Canonical generation `UEF9RUN_559c27f2d0d1f62b`, exactly one COMPLETE, digests of board/UEF-7/UEF-8/UEF-9 match their files;
  `current.json`, `latest.json` and the cross-day registry entry for 2026-10-08 all point to it (registry holds 09-30, 10-01,
  10-02, 10-07 manual, 10-08).
- UEF-7: 14 candidates in, 14 out, ids identical, unique, uniform schema, no null sample_count/question_id.
- UEF-8: N=14, pairs expected 91, actual 91, 91 unique pair ids, no duplicate or self pairs; 0 COMPARABLE / 7 CONDITIONAL /
  84 NOT_COMPARABLE.
- UEF-9: VALID, binding PASS, authority prohibitions promotion/ranking/trading_execution all NONE.
- Read-only in-memory replay of UEF-7/8/9 from the published board reproduced all three run ids (determinism PASS).

## K-L. Freeze and scheduler

- UEF freeze manifest 11/11 MATCH; no UEF/board semantic file and no strategy, Scanner, Strategist, Step5C/5D, entry/exit file
  changed since a38bf4e (only closeout/evaluation/research loaders, the closeout-only lock guard, and docs/config).
- Exactly the seven canonical tasks are enabled (Q12-Preopen, Preopen, Q12-BTC-0855, Session, SessionWatchdog, Closeout,
  Daily UEF); legacy tasks remain Disabled.

## Non-blocking backlog

- Q9 forward-outcome rows are still recomputed per consumer (compute-once/share not implemented).
- The full 20-day rolling Q9 window was never compared against the old implementation (NOT_AVAILABLE).
- 12 `test_monitor_exit_guard` tests fail in `C:\Agentra` but pass in a clean export of the same code (environment contamination, unexplained).
- Production container still binds through the `C:/Trading_Agent_System` junction (cleanup out of scope).
- Yahoo 404 log noise for a few Korean tickers during the opening_rank1 step.
- Branch cleanup deferred until P1.5 prework finishes.
