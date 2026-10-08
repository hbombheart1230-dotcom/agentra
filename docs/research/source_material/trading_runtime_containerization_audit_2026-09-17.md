# Trading Runtime Containerization / Restart Safety Audit — 2026-09-17

READ-ONLY AUDIT. No file was modified, no docker/compose command was run, no process was
restarted, no broker call was made, no `.env`/mode/threshold was changed to produce this
report. This document is analysis and design proposal only — nothing in it has been
implemented.

---

## TRADING RUNTIME CONTAINERIZATION AUDIT

```
CURRENT PROCESS MODEL:
Single OS process (scripts/run_session.py --mode live --phase intraday) running one
synchronous tick loop. Commander/Strategist/Scanner/Monitor/Supervisor/Executor/Reporter
are all plain in-process function calls sharing one in-memory `state` dict -- no threads,
no subprocesses, no LangGraph, no microservices for any of the seven agents. One
background daemon thread (Kiwoom market-status WebSocket listener). Five independent
shadow-loop OS subprocesses (Q10/Q11/Q12 research collectors, observation-only, no
trading). Orchestrated externally by Windows Task Scheduler + scripts/start_trading_day.py
(watchdog) + scripts/restart_live_session.py (hard taskkill /F stop, fresh subprocess.Popen
start).

CURRENT RESTART SAFETY:
CONDITIONALLY SAFE

IDEMPOTENCY AFTER RESTART:
CONDITIONALLY SAFE

PERSISTENT STATE:
GAPS FOUND

GRACEFUL SHUTDOWN:
MISSING

STARTUP RECONCILIATION:
PARTIAL

SPLIT-BRAIN RISK:
LOW

DOCKERIZATION:
GO AFTER FIXES

RECOMMENDED CONTAINER BOUNDARY:
Option A -- one `trading-runtime` container matching the CURRENT process boundary exactly
(the whole main loop, all seven agents in-process, unchanged). Shadow loops as a separate,
lower-priority container (or left outside Docker for now). Do NOT split the seven agents
into separate services (Option C) -- no such boundary exists in the code today; forcing one
would be a large rewrite unrelated to the actual problem being solved.

OBSERVABILITY COMPOSE:
KEEP SEPARATE

RECOMMENDED RESTART POLICY:
`restart: on-failure` with a capped retry count (e.g. `on-failure:5`), NOT `always`, NOT
bare `unless-stopped` -- combined with an internal EXECUTION_READY gate (reusing
build_portfolio_snapshot's existing reader_ok / positions_mismatch_detected /
reconciliation_applied signals) that must independently pass before the tick loop is
allowed to dispatch any order after a restart.

K8S NOW:
NOT JUSTIFIED

BLOCKERS BEFORE MOCK CONTAINER:
1. Fix the m13_live_loop.lock PID-reuse hazard (bare OS-PID liveness check is a false-
   positive risk under container PID-namespace reuse; low effort, Docker-specific).
2. Add log rotation for data/logs/events.jsonl (~953 MB, unbounded, no rotation found)
   before bind-mounting it into a container volume.
3. Clean the M24/M28 milestone-check fixture files out of data/state/ so the persistent-
   volume boundary is unambiguous.

BLOCKERS BEFORE REAL TRADING:
1. Add a hard pending/open-order reconciliation gate on the ENTRY path, mirroring the
   existing position-reconciliation gate -- closes the one concrete duplicate-entry-order
   restart gap this audit found.
2. Add a SIGTERM handler with a best-effort fast-drain (stop accepting new dispatch, let
   an in-flight execute_owned_order call finish) to reduce how often a crash-during-
   dispatch leaves a stuck EXECUTING row requiring manual reconciliation.
3. Implement (or at minimum runbook + alert) the "Step5D" automated reconciliation the
   code's own comments already anticipate but do not implement -- Docker-style frequent
   redeploys will exercise the crash-during-dispatch path far more often than today's rare
   Windows-native restarts.
4. Rehearse Scenarios A-F against the ACTUAL containerized runtime (not just source
   analysis) during shadow validation, before any real-money flag is flipped.
5. Explicitly resolve the mock-mode Supervisor-bypass (execute_from_packet.py:3592-3593)
   for the real-trading container configuration -- if EXECUTION_MODE were ever
   misconfigured to "mock" in a real-trading container, Supervisor's risk gating is
   silently disabled entirely.
```

---

## 1. The Problem We're Actually Solving

Today: which trading process is alive is hard to verify; knowing what to restart after a
patch is complex; stale processes can linger; restart ORDER can scramble runtime state;
confirming a patch reached the live process is hard; the operator manages several
scripts/processes by hand; mid-session restart's duplicate-order risk is not clearly
understood. This audit evaluates whether `docker compose ps / logs -f / up -d --build`
could replace this, and answers: **conditionally yes**, contingent on the fixes listed
above — the existing safety architecture (Step5C intent-ownership CAS store) is
considerably more mature than the pre-audit assumption, and is the main reason the
verdict is GO-AFTER-FIXES rather than NO-GO.

---

## 2. Process / Entrypoint Discovery

### Entrypoint chain (live intraday trading)

```
scripts/run_session.py --mode live --phase intraday
  -> libs/runtime/session_entry_dispatch.py::dispatch_entry_implementation()  [plain import+call, no subprocess]
  -> libs/runtime/entrypoints/m13_live_loop.py::main()
  -> libs/runtime/live_loop_runner.py::run_live_loop()
       - session_hard_gate: MarketHours().is_open() check (09:00-15:30 KST weekdays);
         aborts exit-code 5 if closed, BEFORE any lock/broker/state activity
       - acquire_live_loop_lock()  [data/state/m13_live_loop.lock, PID-based single-instance]
       - starts ONE background daemon thread: KiwoomMarketStatusListener (WebSocket)
       - while True:
           refresh_live_loop_lock()
           run_m13_once(state)    [graphs/pipelines/m13_live_loop.py:117]
             load_state()          -> StateStore.load() (data/state.json)
             clear _PER_RUN_TRANSIENT_KEYS (run_id, scan_results, monitor, decision_packet, ...)
             run_m13_tick(state)   [graphs/pipelines/m13_tick.py:29]
               if market closed: tick_skipped=True, return (no commander call at all)
               else: run_commander_runtime(state, mode="integrated_chain")
                 [graphs/commander_runtime.py -- _run_integrated_chain_impl, ALL PLAIN FUNCTION CALLS]
                 1. build_portfolio_snapshot()         <- BROKER READ, every tick incl. tick #1
                 2. _apply_portfolio_preflight_guard() <- HARD BLOCK on reader failure / unresolved mismatch
                 3. strategist_node()
                 4. scanner_node()
                 5. monitor_node()
                 6. decision_node() / decide_trade()
                 7. execute_from_packet()  -> real_executor.py -> Kiwoom HTTP API
                 8. reporter_node()
             save_state()           -> StateStore.save() (atomic tmp+fsync+os.replace)
           sleep(sleep_sec)   [default 60s, env SCAN_INTERVAL_SEC]
       - finally: stop listener thread; release lock
         [NEVER RUNS under taskkill /F -- see Section 6]
```

No `multiprocessing`, no `threading.Thread` (except the one WebSocket listener), no
LangGraph anywhere in the repo (`graphs/trading_graph.py:5-7` explicitly documents avoiding
it). No HTTP server / port binding inside the trading-loop process itself (the FastAPI/
uvicorn stack that exists in the repo is exclusively the separate observability dashboard).

### Watchdog / shadow loops (`scripts/start_trading_day.py`)

Five independent `subprocess.Popen` OS processes (`_start_shadow_loop`, lines 203-229;
`CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW` on Windows), all observation-only:

| Name | Script |
|---|---|
| `opening_macro_snapshots` | `scripts/run_opening_macro_snapshot_collector.py` |
| `q10_samsung_hynix` | `scripts/run_baseline_samsung_hynix.py --loop --interval-sec 300` |
| `q11_opening_opportunity` | `scripts/run_opportunity_engine_shadow.py --loop --interval-sec 300` |
| `q12_btc_woori` | `scripts/run_baseline_btc_woori_tech.py --loop --interval-sec 300` |
| `q10_index_observation` | `scripts/run_q10_index_observation_collector.py --loop --poll-sec 30` |

Liveness detection for these is PowerShell `Get-CimInstance Win32_Process` scraping — no
PID file, no lock mechanism.

### Windows Task Scheduler registration

`scripts/register_mock_exam_tasks_example.bat` and `deploy/m31_registration_helpers/
windows/*.ps1` register **mock-exam-scoped** tasks only (`run_mock_exam_session*.bat`).
**No committed registration script wiring `start_trading_day.py`/`restart_live_session.py`
to Task Scheduler for genuine live trading was found** — the live tasks confirmed running
on the actual host this session (`TradingAgent-MockExamDay-SessionWatchdog` etc., verified
via `schtasks /query` in an earlier turn of this conversation) were apparently registered
ad hoc/outside the committed automation, or via a template not fully traced in this pass.
`deploy/m28_launch_templates/windows/{worker,scheduler}_task.xml` are separate one-shot
(`run_commander_runtime_once.py`) templates whose actual registration status on the live
host is unverified from source alone.

---

## 3. Runtime State Audit

### 3.1 `intent_id` — corrected finding

`decide_trade.py:1463` still sets `intent_id = state["run_id"]` by default. On the LIVE
path this default is what actually reaches the SQLite store — `_build_order_from_intent`
does not copy `intent_id` into `order`, so `bind_intent(state, order, intent)` finds it
only on `intent` and reuses `state["run_id"]` as-is; the deterministic content-hash scheme
(`compute_self_minted_intent_id`) is a fallback that in practice doesn't fire on this path.
Since `run_id` is a `_PER_RUN_TRANSIENT_KEY`, cleared and regenerated (`uuid4().hex`) at the
start of every tick, **`intent_id` is effectively unique per order-attempt/per tick** —
this does not need to survive a restart for uniqueness; restart safety instead rests on the
SQLite row keyed by that id plus the independent physical-order fingerprint (3.2).

### 3.2 The real idempotency mechanism — `SQLiteIntentStateStore` (Step5C)

`data/state/intent_state.db`. State machine `pending_approval -> approved -> executing ->
{executed | failed}` (strict CAS transitions, `libs/supervisor/intent_state_store.py:62-160`).
**Confirmed wired into the live path**: `execute_from_packet.py:3626-3638` calls
`admit_order_intent()` then `execute_owned_order()` for every real BUY/SELL/CANCEL the live
loop sends — the same sequence used for the auto-cancel/child-order path too
(lines 841-843, 970-972). This directly corrects an earlier (stale, pre-Step5C) hypothesis
that this store was disconnected from the live path via a separate `IntentStore` JSONL file
(`data/logs/intents.jsonl`, confirmed stale, last written Feb 12 2026 — that file serves
only the separate manual-approval/agent-tool path, not `execute_from_packet.py`).

Two independent CAS layers, both required to pass before `executor.execute()` is ever
called:
1. **`claim_execution(intent_id, ...)`** — one owner per `intent_id`.
2. **`claim_physical_order(physical_order_key, ...)`** — one owner per real-world order
   SHAPE (`execution_scope + action + symbol + order_type + qty + price + orig_ord_no`,
   canonicalized so `qty=10` and `qty="10"` collide, `intent_identity.py:151-219`) —
   catches two *different* intent_id schemes describing the same real mutation.

**Deliberately no automatic release on crash/UNKNOWN** (explicit code comments,
`intent_state_store.py:574-591, 644-654`): a lease is released only on a genuine terminal
state (EXECUTED/FAILED). An orphaned lease from a crash **stays held, fail-closed**, until
an operator runs `scripts/reconcile_intent_state_store.py` — "Step5D owns automatic
reconciliation; it is not implemented here."

### 3.3 Live duplicate-prevention state summary table

| State | Storage | Class | Restart behavior |
|---|---|---|---|
| Intent/execution CAS (`intent_state`, `intent_journal`, `intent_execution_binding`, `intent_admission`, `physical_order_claim`) | `data/state/intent_state.db` (SQLite) | **D** | Kill mid-tx -> clean rollback (SQLite durability). Completed `executing` row is NOT auto-released; needs manual reconciliation |
| Recent-buy / settle-sell duplicate guard | `data/state/execution_recent_buy_guard.json` | C | Atomic tmp+replace; file is sole source of truth; safe across restart; 600s TTL |
| Recent-sell duplicate guard | `data/state/execution_recent_sell_guard.json` | C | Same pattern; 180s TTL |
| UNKNOWN-outcome quarantine lock | `data/state/execution_unknown_quarantine/<symbol>.lock` | **D** | O_CREAT\|O_EXCL, durable, never auto-expires; re-opens automated mutation on that symbol if lost |
| Positions / cash / daily P&L | `data/state.json` (~11.6 MB) | **D** | Atomic write (tmp+fsync+os.replace) is correct; full-file rewrite every tick is an I/O-cost concern on a bind-mounted volume, not a corruption risk |
| `m13_live_loop.lock` (single-instance + heartbeat) | `data/state/m13_live_loop.lock` | D (liveness) | **PID-existence check — container PID-reuse false-positive/negative risk on restart, needs fixing before Docker** |
| Cycle-scoped decision/scanner/monitor/strategist state | in-memory `state` dict | A | Explicitly cleared every tick (`_PER_RUN_TRANSIENT_KEYS`); rebuilt fresh |
| Event log | `data/logs/events.jsonl` (~953 MB, growing, **no rotation found**) | B | Append-only, safe against corruption; unbounded size is an operational/volume concern |
| Legacy manual-approval intent log | `data/logs/intents.jsonl` (3.3 KB, stale) | C (separate path only) | Not touched by the live automated flow at all |
| Broker/market status cache | `data/state/kiwoom_market_status*.json` (+ orphaned `.tmp.*` stragglers observed on disk) | B | Reconstructable from broker; stray uncommitted tmp files found, writer not fully traced |
| Token cache | `data/token_cache.json` | B | Fully reconstructable, cheap to keep |
| M24/M28 `.db`/dirs under `data/state/` | various | N/A | **Milestone-acceptance-check fixture output, not live runtime state — recommend removing from `data/state/` before finalizing the volume boundary** |

Full table with writer/reader/risk-if-lost/risk-if-stale for every row is in the raw
research notes; summarized here for the ones that matter for the GO/NO-GO decision.

### 3.4 "Broker truth wins" merge rule

`libs/storage/state_store.py` protects `open_positions`/`mock_positions`/closeout-related
keys with a timestamp-based anti-clobber rule (`_BROKER_TRUTH_PROTECTED_KEYS`,
`_preserve_newer_broker_truth`) — on save, if the on-disk copy's broker-truth timestamp is
newer than the in-process state's, the on-disk position data wins. This is timestamp-based,
**not lock-based** — it assumes single-writer-with-read-modify-write semantics on one
shared `data/state.json`. **This is a real constraint for any future multi-instance idea**
(and part of why K8s-style horizontal scaling of this component is actively wrong — see
Section 14).

---

## 4. Restart Safety Audit — Scenario Findings

### Scenario A — OrderIntent created -> restart

The `intent` dict lives only in the per-tick in-memory `state["decision_packet"]`, class A
(ephemeral, explicitly cleared every tick). `bind_intent`/SQLite persistence only happens
**inside** `execute_from_packet.py`. If the process dies between `decide_trade` and
`execute_from_packet`, the OrderIntent is simply lost — no SQLite row was ever created.

**Verdict: SAFE.** No duplicate risk; worst case is a missed trading opportunity for that
tick, recovered on the next tick's fresh decision cycle.

### Scenario B — OrderIntent approved -> restart before execution

If `admit_order_intent()` (sets SQLite state to `approved`) completed but
`execute_owned_order()`'s CAS never ran, the row sits at `approved` forever — but since
`intent_id` is per-tick-unique, no future tick will ever reference that exact row again
(it becomes inert, unreferenced data — minor storage growth, no safety issue). A fresh
attempt on a later tick uses a NEW `intent_id`; the `physical_order_claim` for that
physical shape was never taken by the orphaned attempt, so the new attempt proceeds
normally.

**Verdict: SAFE.**

### Scenario C — Broker order request transmitted -> crash before response (CRITICAL)

At this point `claim_physical_order` + `claim_execution` have already succeeded (SQLite
state = `executing`, physical lease = `active`). A `taskkill /F` here is a Windows
`TerminateProcess` — confirmed to give Python's exception handlers, `finally` blocks, and
`atexit` **zero** chance to run (Section 6).

- **Exact-shape retry**: SAFE. A later tick generating the identical physical order
  (same action/symbol/order_type/qty/price) will have its `claim_physical_order()` call
  find the existing `active` lease under a *different* `intent_id` and be rejected outright
  (`physical_order_already_claimed`) — no duplicate broker submission.
- **Slightly-different retry** (e.g. price recalculated after a market tick): the physical
  fingerprint differs, so this guard does **not** catch it. Protection here would have to
  come from the pending-order reconciliation gate — which this audit found to be WEAK on
  the entry side (Section 7).
- **Operational cost**: the stuck `executing` row + `active` physical lease survive
  restart indefinitely; nothing auto-resolves them. An operator must run
  `scripts/reconcile_intent_state_store.py` before that exact order shape can ever be
  attempted again. No automated broker-truth check specifically resolves "did this crashed
  order actually fill" — the system instead relies on the SEPARATE position-reconciliation
  gate to pick up a resulting fill as a new position on the next restart's first tick.

**Verdict: CONDITIONALLY SAFE** — protects against exact-duplicate dispatch, requires
manual reconciliation to fully recover, and does not protect against a near-identical
retry with different price/qty.

### Scenario D — order executed -> crash before result persistence

Same fail-closed lock behavior as Scenario C (the lease/row structure doesn't distinguish
"crashed before the HTTP call returned" from "crashed after it returned but before
`finish_execution()` ran"). The actual POSITION is independently recovered via broker-truth
reconciliation on the next restart regardless of the SQLite bookkeeping state — so the
trading-safety-critical fact (what position do we actually hold) is fine; only the
intent-ownership bookkeeping is left in a permanently-orphaned state requiring manual
reconciliation.

**Verdict: SAFE for duplicate-prevention**, same manual-reconciliation burden as Scenario C.

### Scenario E — Monitor/Scheduler active -> restart -> startup: same signal, new OrderIntent?

All decision-cycle state is rebuilt fresh every tick from current broker/market data — a
restart is, from the strategy logic's point of view, indistinguishable from a normal new
tick. If the underlying market condition that produced a signal still holds after restart,
the SAME symbol/action can legitimately be re-selected.

- For an **existing position** (exit side): well protected — `build_portfolio_snapshot` +
  `_apply_portfolio_preflight_guard` hard-block all execution on any position mismatch, and
  Monitor's `sell_guard_open_order_pending` additionally blocks a redundant SELL when one is
  already pending.
- For a **new entry** (buy side) where a PRIOR buy order is still pending (unfilled) at the
  broker at restart time: **this is the one concrete gap this audit found.** Pending-order
  data is fetched and used only as a scanner scoring penalty, not a hard preflight block
  analogous to the position-reconciliation gate. A freshly-restarted process's
  scanner/strategist could, in principle, select the same symbol again and submit a second
  entry order before the first either fills or is otherwise reconciled.

**Verdict: CONDITIONALLY SAFE** — solid on the exit/position side, weak on the entry/
pending-order side.

### Scenario F — old runtime shutdown -> new runtime startup: split-brain?

`restart_live_session.py::_stop_existing_session()` kills the old process(es) first,
**waits** (polling, up to `stop_wait_sec`=15s default) for them to actually disappear, and
only then starts the new one — sequential by construction. The main loop additionally has
an independent second safety net: `acquire_live_loop_lock()`'s PID-based single-instance
check would refuse to start a new process if an old one somehow survived the kill. Shadow
loops use the same sequential stop-then-start pattern but lack an equivalent lock-file
safety net (lower stakes — observation-only, no trading).

**Verdict: LOW split-brain risk** for the main trading loop (two independent protections);
slightly higher but low-stakes for shadow loops. A Docker-based redeploy under a single
named service inherits this sequential property naturally, **contingent on fixing the PID-
reuse hazard first** (a stale lock file surviving on a persistent volume across a container
restart could coincidentally match a low, commonly-reused PID like 1/6/7 in the *new*
container's PID namespace, causing a false "already running" block).

---

## 5. Idempotency Audit

```
process-local idempotency:  present (in-memory AllowResult, per-tick state) -- not
                             restart-safe by itself, but not the primary mechanism
file-backed idempotency:    present (recent-buy/sell TTL guards, unknown-quarantine
                             locks) -- restart-safe, atomic writes confirmed
DB-backed idempotency:      present and PRIMARY (SQLiteIntentStateStore CAS,
                             claim_execution + claim_physical_order) -- restart-safe
broker reconciliation:      present for POSITIONS (hard gate, every tick); effectively
                             absent for PENDING/OPEN ORDERS on the entry path
none:                       not applicable -- multiple layers exist

IDEMPOTENCY AFTER PROCESS RESTART:
CONDITIONALLY SAFE
```

Basis: exact-physical-order-shape duplicate dispatch is DB-backed and genuinely
restart-safe (`libs/supervisor/intent_state_store.py::claim_physical_order`,
`execute_owned_order` in `libs/execution/intent_execution_owner.py:27-127`). It is
conditional, not unconditional SAFE, because: (a) a near-identical-but-not-fingerprint-
identical retry is not caught by this guard, (b) no automated reconciliation exists yet
for orphaned leases (explicitly deferred to a not-yet-implemented "Step5D"), and
(c) the entry-side pending-order gap (Scenario E) is a real, if narrower, path to a
non-exact duplicate.

---

## 6. Shutdown Semantics

**No signal handling exists anywhere in the trading runtime.** The only `atexit.register`
hit in the whole codebase is in an unrelated batch-report tool
(`libs/reporting/live_execution_bundle_runner.py:1476`). Every documented stop path
(`restart_live_session.py::_stop_pid`, `start_trading_day.py::_stop_pid`) issues
`taskkill /PID <pid> /F` unconditionally — Windows `TerminateProcess`, which gives Python's
`try/finally`/`atexit` **zero** opportunity to run. The one `try/finally` in
`live_loop_runner.py:43-54` (stop the market-status thread, release the lock) never
executes under this stop path.

**Crash-safety of the actual state stores was independently verified as adequate**: SQLite
transactions roll back cleanly on a kill mid-write (durability guarantee, confirmed no WAL
mode configured — default rollback-journal, appropriate here); `StateStore.save()` uses a
genuine tmp-file + fsync + `os.replace()` atomic pattern; guard-file writers use the same
pattern; the event log is pure append. **The absence of graceful shutdown is therefore not
the primary safety gap** — the DB-backed idempotency layer is what actually protects
against duplicate dispatch. Its absence DOES, however, directly cause the operational
cost described in Scenarios C/D (every hard-kill-during-dispatch produces a stuck lease
requiring manual reconciliation) and is exactly the kind of gap Docker's own default
SIGTERM-then-SIGKILL lifecycle would NOT improve unless a handler is added.

**Recommendation for Section 15 Phase 1**: add a `signal.signal(SIGTERM, ...)` handler in
`live_loop_runner.py` that sets a "stop accepting new ticks" flag and, if a tick is
mid-flight past the dispatch point, waits briefly for `execute_owned_order`'s in-flight
`finish_execution()` to complete before exiting — reducing (not eliminating, since the
underlying protection already exists) how often manual reconciliation is needed. This
gives Docker's default `stop_grace_period` (10s) something real to do.

---

## 7. Startup Semantics

Actual order, freshly-started process (see Section 2's tree for the full chain):
config load -> lock acquire (pure local-file check, no broker/state involvement) ->
market-status listener thread start -> `load_state()` (local `state.json`, possibly stale
vs. broker truth) -> **`build_portfolio_snapshot()`** (live broker position/cash read,
**every tick including tick #1**) -> **`_apply_portfolio_preflight_guard()`** (hard block
on broker-read failure or unresolved position mismatch — `graphs/commander_runtime.py:
4046-4165`) -> only if not blocked: strategist -> scanner -> monitor -> decision ->
execute_from_packet -> reporter.

**Can the runtime submit/allow an order before reconciliation?**

- **Positions: No.** The broker-truth position read and its hard preflight guard are
  unconditional, first-thing-every-tick operations, strictly before any of the seven
  agents are reachable. A broker-read failure or unresolved mismatch sets
  `execution.allowed=False` and returns immediately.
- **Open/pending orders: Yes — this is the concrete gap.** Pending-order data feeds only a
  scanner scoring penalty and a sell-side duplicate-exit guard
  (`sell_guard_open_order_pending`, `monitor_node.py:1887`) — there is no equivalent hard
  preflight gate on the buy/entry side analogous to `_apply_portfolio_preflight_guard`
  that blocks all execution until pending broker orders are enumerated and reconciled.
  `_hydrate_closeout_account_orders()`/`_pending_buy_cancel_intents_from_account_orders()`
  exist but only run on the closeout fast path, not at general startup/every tick.

**STARTUP RECONCILIATION: PARTIAL** (positions: ADEQUATE; open orders: effectively
MISSING as a hard gate).

---

## 8. Configuration / Secrets

| Variable | Canonical read site | Default | Cached or fresh? |
|---|---|---|---|
| `KIWOOM_MODE` | `libs/core/settings.py:128` (`Settings`); re-read directly in `real_executor.py:103` | `mock` | Both — `Settings` cached per-object; the actual gate re-reads `os.getenv` fresh every call |
| `EXECUTION_ENABLED` | `real_executor.py:104`, `_env_flag_true` | `false` | **Fresh every call** |
| `ALLOW_REAL_EXECUTION` | `real_executor.py:113` | `false` | **Fresh every call** |
| `SYMBOL_ALLOWLIST` | `libs/execution/guards/symbol_allowlist.py::parse_symbol_allowlist`; call sites in `real_executor.py`, `execute_from_packet.py` | empty -> guard disabled | **Fresh every call** |
| `MAX_QTY` (alias `MAX_ORDER_QTY`) | `execute_from_packet.py:171-178,283` | `0` -> disabled | **Fresh every call** |
| `MAX_NOTIONAL` (alias `MAX_ORDER_NOTIONAL`) | `execute_from_packet.py:284` | `0` -> disabled | **Fresh every call** |

All hard safety gates are read live via `os.getenv` at point of use, every call — good for
containers (env fixed at container creation is exactly how these are already designed to
be consumed; no hidden import-time caching to worry about for the safety-critical flags).

`.env` (1058 bytes, confirmed present, contents not read per instructions) is loaded by a
manual parser (`libs/core/settings.py::load_env_file`, lines 39-66) that **only sets a key
if not already present in `os.environ`** — real environment variables (e.g. a Docker
Compose `environment:` block) always take precedence over `.env` file contents, exactly the
behavior wanted for a container where `.env` ships baked-in defaults and compose overrides
per-deployment. `config/.env.example` (245 lines) documents the full expected key set, all
defaulting to safe values (`KIWOOM_MODE=mock`, `EXECUTION_ENABLED=false`,
`ALLOW_REAL_EXECUTION=false`, `SYMBOL_ALLOWLIST=` empty, `MAX_ORDER_QTY=0`,
`MAX_ORDER_NOTIONAL=0`). No hardcoded credential values were found anywhere read during
this audit; every credential flows through `Settings.from_env()`'s env-var helpers.

**Secret injection design for containerization (Section 8's requested recommendation)**:
never `COPY` `.env` or any credential into the image (matches the existing observability
Dockerfiles' own practice — they inject no secrets at all, since that stack has none).
Inject via Compose `env_file:` pointing at a host-side `.env` that is itself
`.gitignore`d and lives outside the build context, or via `environment:` referencing
values from the operator's shell/CI secret store — identical pattern to how
`deploy/compose/compose.yaml` already injects non-secret config
(`OBSERVABILITY_EXPOSURE_PROFILE` etc.) via `${VAR:-default}` interpolation, just extended
to credential-bearing values via `env_file:` rather than baked-in `environment:` literals.

---

## 9. Persistent Storage Boundary

```
IMAGE
+-- graphs/, libs/, apps/, scripts/, config/ (minus .env)   -- application code
+-- venv/ dependencies (reinstalled via requirements, not copied from host venv/)
+-- static config defaults (config/.env.example, etc.)

HOST / PERSISTENT VOLUME
+-- data/state.json                              (D -- positions/cash/P&L)
+-- data/state/intent_state.db                   (D -- execution-ownership CAS, SQLite)
+-- data/state/execution_recent_buy_guard.json    (C -- TTL dup guard)
+-- data/state/execution_recent_sell_guard.json   (C -- TTL dup guard)
+-- data/state/execution_unknown_quarantine/      (D -- never-expiring lock dir)
+-- data/state/m13_live_loop.lock                 (liveness marker -- FIX PID-reuse first)
+-- data/state/kiwoom_market_status*.json, broker_cost_profile.json,
|   trading_day_supervisor.json, m28_runtime_lifecycle.json   (B/ancillary)
+-- data/logs/events.jsonl                        (B, ~953MB -- ADD ROTATION FIRST)
+-- data/logs/intents.jsonl                       (C, legacy manual-approval path)
+-- data/logs/kiwoom_account_snapshots/
+-- data/token_cache.json                         (B, cheap to keep)
+-- data/strategy_memory/                         (B/C)
+-- reports/  (all subdirectories)                (durable operator output --
|                                                    ALREADY bind-mounted read-only by the
|                                                    existing observability compose file,
|                                                    independently validating this boundary)
+-- data/evidence_ledger/                         (already recognized by observability compose)

EXCLUDE / CLEAN UP BEFORE FINALIZING VOLUME
+-- data/state/m24_closeout_state.db, m24_guard_precedence.db,
|   data/state/m28_closeout/, m28_launch_hook/, m28_launch_wrapper/, m28_profile_check/,
|   m28_rollout_check/, m28_scheduler_worker/, m28_startup_preflight/,
|   mock_exam_day_check.lock, offhours_*                -- milestone-check fixture output,
|                                                            not live state; remove before
|                                                            the volume boundary is drawn
+-- .pytest-work*/, .pytest_cache/, pytest-cache-files-*  -- pure test scratch

SECRET INJECTION
+-- env_file: pointing at a host .env outside the build context (never COPY into image)
```

**Prior art directly validating this boundary**: `deploy/compose/compose.yaml` already
containerizes the observability API/web pair and read-only bind-mounts exactly
`reports/`, `data/logs/`, `data/state/`, `data/evidence_ledger/` from the host — an
independent, already-shipped config that agrees on the same persistent boundary from the
consumer side. **The live trading runtime itself is not represented anywhere in that
compose file or under `deploy/docker/`** — containerizing it is genuinely new work, not an
extension of something already partially done.

---

## 10. Container Boundary Recommendation

| Option | Verdict |
|---|---|
| A: one `trading-runtime` container, all 7 agents | **Recommended.** Matches the current, confirmed-synchronous, single-process/no-IPC architecture exactly. Zero application-code restructuring needed — pure packaging. |
| B: `trading-runtime` + `scheduler` | The "scheduler" concept (watchdog restart, health polling) is naturally absorbed by Docker's own `restart:` policy + `healthcheck:` + Compose itself — no separate scheduler container needed for the MAIN loop. The 5 shadow loops, already independent low-stakes OS processes today, are the better candidate for their own container (or left outside Docker initially). |
| C: one container per agent (commander/scanner/monitor/executor/...) | **Not recommended at this stage.** No existing IPC/RPC boundary exists between these — they are plain function calls sharing one in-memory dict. Splitting them would require inventing a new state-sharing/messaging layer, a large rewrite unrelated to the actual restart-safety problem this audit was asked to solve. Revisit only if a real driver emerges (see Section 14's future trigger). |

**Recommendation: Option A**, with shadow loops as a separate, lower-priority container
(or deferred).

---

## 11. Existing Observability Docker Integration

**KEEP SEPARATE — separate Compose project** (e.g. `deploy/compose/compose.trading.yaml`
alongside the existing `deploy/compose/compose.yaml` for observability), not merged into
one file/project. Reasoning:

- The existing observability stack already treats `reports/`/`data/logs/`/`data/state/` as
  **read-only** inputs — zero write coupling to the trading runtime today.
- If both stacks lived in one Compose project, an unscoped `docker compose up -d --build`
  (exactly the command this session used to redeploy the dashboard) would rebuild+restart
  **everything**, including the live trading loop — precisely the "UI redeploy must never
  restart trading, and vice versa" failure mode Section 11 explicitly asks to prevent.
- Separate compose files/projects with the observability side continuing to read-only
  bind-mount the trading side's output paths preserves the current, already-correct
  one-way data flow with zero risk of an accidental cross-restart.

---

## 12. Docker Restart Policy

Naive "always restart on crash" is explicitly rejected per the task's own framing, and
this audit's own findings support that caution:

- `restart: always` — would also restart after a deliberate operator `docker stop`
  (e.g., an intentional maintenance halt) — unacceptable for a trading system.
- `restart: unless-stopped` alone — restarts on crash/reboot, not after manual stop, but
  says nothing about WHETHER it's safe to resume dispatching orders immediately. A crash
  caused by a bad patch or a corrupted config would crash-loop indefinitely, repeatedly
  re-entering the tick loop.
- **Recommended: `restart: on-failure:5`** (or similar capped count) — bounds crash-loop
  behavior — **composed with an internal EXECUTION_READY gate** (Section 13) that the tick
  loop itself checks before allowing `execute_from_packet` to actually dispatch, decoupling
  "the container is up" from "the container is allowed to trade." This exact pattern
  ("restart allowed, but execution disabled until readiness/reconciliation passes") is what
  Section 12 explicitly asks for, and the building blocks for it
  (`build_portfolio_snapshot`'s `reader_ok`/`positions_mismatch_detected`/
  `reconciliation_applied` fields, already computed every tick) already exist in the code
  — this is a matter of exposing/gating on them, not inventing new logic.

---

## 13. Health / Readiness Design

No HTTP server exists in the trading-loop process (confirmed absent), so Docker's
`healthcheck:` must use a local `CMD` check (file-based), not an HTTP probe — a different
mechanism than the existing observability API's `urllib.request` healthcheck.

```
LIVENESS
  process alive AND m13_live_loop.lock heartbeat_ts fresher than ~2x sleep_sec
  (reuses the existing heartbeat mechanism, libs/runtime/live_loop_lock.py)

READINESS
  config loaded without error (Settings.from_env() succeeded)
  data/state.json loadable (StateStore.load() succeeded at least once)
  data/state/intent_state.db reachable (SQLite connect succeeds)
  at least one successful build_portfolio_snapshot() this process lifetime
  (reader_ok == True at least once)

EXECUTION_READY
  positions reconciled this lifetime (_apply_portfolio_preflight_guard passed at least once)
  no unexpected orphaned physical_order_claim/EXECUTING rows beyond a known/expected set
  (surface list_active_physical_claims() count as a metric -- code already exists,
  libs/supervisor/intent_state_store.py:681-708, just needs to be exposed)
  EXECUTION_ENABLED / ALLOW_REAL_EXECUTION / SYMBOL_ALLOWLIST / MAX_QTY / MAX_NOTIONAL
  all parse validly (no malformed env values)
```

Implementation shape (design only, not implemented): the tick loop already writes a status
artifact each cycle in spirit (`m13_live_loop.lock` heartbeat); extending this pattern with
a small `data/state/m13_readiness.json` written once per tick, summarizing the last
`build_portfolio_snapshot` health fields, would let a `docker healthcheck` `CMD` be a plain
freshness+content check on that file — no new business logic, just surfacing what
`build_portfolio_snapshot`/`_apply_portfolio_preflight_guard` already compute every cycle.

---

## 14. K8s Decision

```
K8S NOW:
NOT JUSTIFIED
```

- **Single-host operation**: everything currently runs on one Windows machine; no evidence
  of multi-node requirements anywhere in the codebase or operations docs reviewed this
  session.
- **No HA requirement that k8s would actually serve**: trading is gated by KST market
  hours; a single-host outage during market hours is a business-continuity question, not
  solved by k8s's pod-rescheduling (which assumes stateless, horizontally-replicable
  workloads).
- **Statefulness actively conflicts with k8s's core value proposition**: the entire safety
  design rests on ONE authoritative `data/state.json` (timestamp-based "broker truth wins"
  merge, not lock-based, per Section 3.4) and ONE SQLite intent-ownership DB assuming a
  single writer. Running multiple simultaneous pods against this state (k8s's normal
  scaling/rescheduling behavior) would directly violate the single-instance assumption
  the entire Step5C safety architecture is built on, and would make the PID-reuse hazard
  (Section 3, `m13_live_loop.lock`) categorically worse, not better.
- **Docker Compose alone fully addresses the stated operational pain points** (know what's
  alive, know what to restart, avoid stale processes, confirm a patch landed, manage via
  a handful of commands) without any of k8s's operational overhead (cluster management,
  ingress, PVC provisioning) for a single-host, single-writer system.

**Future trigger for reconsidering K8s**: genuinely running multiple INDEPENDENT
strategies/accounts concurrently on isolated symbol universes with fully separate state
(scaling by partition, not by replica), a real multi-region/multi-broker HA requirement, or
the team needing declarative multi-environment orchestration at a scale Compose profiles
no longer serve. None of these are present today.

---

## 15. Migration Plan (design only — nothing in this plan is implemented by this audit)

| Phase | Scope | Verification | Rollback | GO/NO-GO |
|---|---|---|---|---|
| **0. Inventory** | This audit itself | — | — | DONE |
| **1. Restart-safety + state-gap fixes** (code, pre-Docker) | Add hard pending/open-order reconciliation gate on entry path; add SIGTERM fast-drain handler; fix `m13_live_loop.lock` PID-reuse (pair with container/session UUID); add `events.jsonl` rotation; clean M24/M28 fixture files out of `data/state/` | Existing `tests/test_step5c_*`/`tests/test_m24_*` suites + new tests for the entry-side gate | Pure code revert; no runtime/infra change yet | All new + existing safety tests pass; freeze-manifest-style diff confirms nothing unrelated changed |
| **2. Container image** | `Dockerfile.trading-runtime` (mirrors `Dockerfile.api`'s pattern), `compose.trading.yaml` (separate project from observability), all Section 9 persistent paths mounted, secrets via `env_file:`, healthcheck per Section 13 | Image builds clean; smoke-import test; `docker compose config` validates | Delete the new Dockerfile/compose files; zero impact on the existing Windows Task Scheduler deployment (built in parallel, not replacing) | Clean build, smoke import passes |
| **3. Mock-only container runtime** | Run the actual container, `EXECUTION_ENABLED=false`, in parallel with the existing Windows-native deployment on real trading days | Side-by-side output diff (`reports/`, `events.jsonl`) between the two deployments; container healthcheck stays green; manually rehearse Scenarios A-F in the container (real `docker kill`, real `docker restart`) | Stop the container; Windows-native remains system of record throughout | Mock output matches Windows-native for N consecutive days; zero unexplained crash-loops; zero unexpected duplicate-intent findings in `intent_state.db`'s journal |
| **4. Shadow validation** | Container becomes primary mock/shadow runner; Windows-native kept as cold standby | Sustained multi-day/week stability; restart drills performed on purpose at various points in the tick cycle to exercise A-F for real | Revert to Windows-native (kept dormant, not deleted) | N weeks clean shadow operation; every restart drill matches this audit's predictions; operator comfortable with the new command set |
| **5. Controlled real validation** | `EXECUTION_ENABLED=true`/`ALLOW_REAL_EXECUTION=true` for the first time in-container, under a tight `SYMBOL_ALLOWLIST`/`MAX_QTY`/`MAX_NOTIONAL` | Every real trade manually cross-checked against broker's own trade history; explicit review of `intent_state.db` journal for the trial window | `EXECUTION_ENABLED=false` (env-only, restart container) instantly reverts to shadow; or full stop back to Windows-native | Zero duplicate-order incidents, zero unexplained broker discrepancies, operator sign-off |
| **6. Operational freeze** | Container becomes sole production runtime; Windows Task Scheduler deployment formally decommissioned (scripts kept for historical/emergency reference, not deleted); `docs/operations/` updated | Final re-audit confirming Section 4 scenarios still hold under the frozen config | Documented emergency fallback to Windows-native (dormant, not deleted) | Sustained clean operation for an operator-chosen minimum period (e.g. one month) post-cutover |

---

## 16-18. Evidence, Constraints, Sign-off

Every finding above cites the specific file/function/line it came from (see the two
underlying research passes for the complete, unabridged citation set — this document
condenses ~330KB of raw findings into the required report shape). Where a document and the
actual runtime code disagreed (none found this pass beyond the already-known,
already-tracked "no committed live Task Scheduler registration script" gap in Section 2),
the runtime code was treated as authoritative and the drift flagged explicitly rather than
silently resolved.

**Hard safety constraints respected throughout this audit**: no order was executed, no
mock/real mode was changed, `EXECUTION_ENABLED` was not touched, `.env` was not modified,
no broker call was made, no production process was restarted, no container was
restarted, no `docker compose up/down` was run, no Docker image was built, no source file
was modified, no automatic cleanup was performed, no orphan container was touched. This
was a read-only audit; the currently-running observability containers and trading process
were not affected in any way by producing this report.

---

# TRADING RUNTIME CONTAINERIZATION AUDIT COMPLETE

```
CODE CHANGED:       NO
STRATEGY CHANGED:   NO
GUARD LOGIC CHANGED: NO
DOCKERFILE/COMPOSE/SCRIPT CHANGED: NO
PROCESS RESTARTED:  NO
SERVICE AFFECTED:   NO
BROKER CALLS:       0
```
