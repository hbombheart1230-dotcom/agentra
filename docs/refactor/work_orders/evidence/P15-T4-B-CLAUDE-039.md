# P15 T4-B — Monitor structural decomposition (Claude)

BASE `c338ba34276566b0b5f6de1e7f556778ec917968` (hosted CI 38652142676 SUCCESS) → FREEZE `c50db1749dbad7058fe0c45ab44a9c84cb12fb34` (hosted CI 38655019789 SUCCESS) → CODE `a25ad43ef04d7cbc7969f09e3066a9a2ecf24495`. Scope: `graphs/nodes/monitor_node.py::monitor_node`, `::_evaluate_monitor_entry_candidate`, `libs/runtime/exit_policy.py::evaluate_exit_policy`, `::_build_account_pnl_crosscheck`. No change to Broker, LLM, Supervisor, Executor, Step5C, `main`, live `C:\Agentra`, T3.5/T4-A golden fixtures; REAL_REPORT_PARITY_BLOCKED stays OPEN.

## 1. Freeze before implementation

The BASE contract was captured and committed (`c50db17`) before any implementation edit: 149 captured inputs (monitor_node 50, entry candidate 50, exit policy 49), 2,879 deterministic variants/scenarios (guard states, price perturbations, `execution_pending`, `qty=0`, exit policy off, long hold…), 1,541 ordered effects (event/log/trace/bridge/persistence call-through wrappers with arguments). Replay runs under a frozen clock/uuid/random/network guard, scrubbed environment, disposable cwd/root and `PYTHONHASHSEED=0`; strict variant conservation (inventory re-derived, expected sampled IDs == pinned-BASE IDs == FEATURE IDs, manifest totals) with fail-closed oracle validation; native Windows exact golden, portable mode compares against the same-host pinned BASE (`git archive`). Deterministic fixture parity only — NOT real Reporter/production artifact parity.

## 2. MONITOR_BEFORE_AFTER_LOC

| Function / file | BASE | CODE |
|---|---:|---:|
| `monitor_node` | 1,107 | 498 |
| `_evaluate_monitor_entry_candidate` | 449 | 250 |
| `evaluate_exit_policy` | 673 | 354 |
| `_build_account_pnl_crosscheck` | 186 | 71 |
| `graphs/nodes/monitor_node.py` (file) | 1,917 | 1,159 |
| `libs/runtime/exit_policy.py` (file) | 1,058 | 646 |

## 3. OWNER_MATRIX (15 new Owners, all ≤ 350 LOC; 42 ledger segments, `docs/refactor/p1_5_third_pass_t4b_moved_segments_ledger.json`)

| Owner | LOC | Responsibility (source function) |
|---|---:|---|
| `libs/runtime/monitor_exit/exit_trigger_ladder.py` | 184 | stop-loss, profit-target, VWAP breakdown, intraday-low break, trend strength, trailing stop, time limit early-return checks (`evaluate_exit_policy`) |
| `libs/runtime/monitor_exit/exit_profit_ladder.py` | 231 | opening-gap take profit, volume exhaustion, partial take profit, profit ladder, risk/reward, resistance target checks (`evaluate_exit_policy`) |
| `libs/runtime/monitor_exit/account_pnl_crosscheck.py` | 167 | account evidence, anomaly/mark price, effective price source (`_build_account_pnl_crosscheck`) |
| `libs/runtime/monitor_exit/exit_policy_bias.py` | 64 | strategy-frame + memory-bias application to the base exit policy (`monitor_node`) |
| `libs/runtime/monitor_exit/exit_cycle_guards.py` | 171 | cycle maps, cooldown/lock expiry, sell-guard cascade, exit-signal lock, overnight decision payload (`monitor_node`) |
| `libs/runtime/monitor/entry_candidate_policy.py` | 90 | memory-bias/policy resolution and effective policy trace (`_evaluate_monitor_entry_candidate`) |
| `libs/runtime/monitor/entry_candidate_annotation.py` | 68 | policy and minute-metrics fields on `entry_info` |
| `libs/runtime/monitor/entry_candidate_guards.py` | 89 | market-rail quant evidence, intent cooldown, guard overrides |
| `libs/runtime/monitor/entry_candidate_probe.py` | 54 | opening rank-1 probe observation/selection context |
| `libs/runtime/monitor/entry_cascade_selection.py` | 80 | cascade plan, BUY order price source, intent meta (`monitor_node`) |
| `libs/runtime/monitor/entry_focus_output_projection.py` | 33 | entry focus/candidate evidence for `monitor_output` |
| `libs/runtime/monitor/policy_output_projection.py` | 135 | exit/entry/policy evidence for `monitor_output` |
| `libs/runtime/monitor/scanner_monitor_handoff_projection.py` | 22 | Scanner→Monitor handoff surface |
| `libs/runtime/monitor/cycle_event_payloads.py` | 136 | raw input snapshot, `state_transition`, `cycle_summary`, decision-bridge payloads |
| `libs/runtime/monitor/cycle_log_trace_payloads.py` | 171 | monitor summary log and `entry_exit_decision` trace payloads |

Existing `libs/runtime/monitor/` and `libs/runtime/monitor_exit/` packages are the homes; no folder reorganization (post-T4 architecture visualization gate unchanged). Moves are verbatim statement runs / value expressions; locals enter as explicit parameters, outputs leave as sorted-field NamedTuples, module globals are resolved at use time as `facade.NAME` so existing monkeypatch seams stay valid. Early-return ladder checks return the orchestrator closure's finalized result or `None`; the orchestrator returns it unchanged (`_t4_ret` sentinel), so guard precedence and return identity are preserved. `monitor_output` blocks are built as an insertion-ordered mapping and applied with one `dict.update` at the original position.

## 4. DECISION_PARITY / STATE_EVENT_PARITY

* Frozen replay: full corpus (`verify <fixture> 1`, 149 records, all 2,879 variants) **0 mismatches** on the CODE tree; the CI test replays the sampled set natively on Windows and against the pinned BASE on Linux.
* AST structural parity (`tests/test_p163_t4b_extraction_gates.py`, 10 tests): inlining every Owner call reproduces the BASE AST of all four functions exactly (signature, evaluation order, State writes, event/log/trace calls, control flow, guard precedence, cooldowns, probe branch); every other top-level definition is AST-identical to BASE; only the ledger Owner names are new imports; Owners ≤ 350 LOC without I/O/env/clock tokens, no unresolved globals, no second exit-decision authority.
* Effect order: ordered effect lists (emit/log/trace/bridge/persist call-through wrappers) are part of the frozen digests; State key order and returned-object identity are checked per record.

## 5. Deliberate limits (not extracted)

* `evaluate_exit_policy` keeps the closure definitions and the precedence ladder skeleton, plus the `peak_drawdown` block whose output feeds later checks (354 LOC, down from 673).
* The opening rank-1 probe evaluation call stays in `_evaluate_monitor_entry_candidate` because its argument list reads `KIWOOM_MODE` from the environment; env/IO reads were not moved into pure Owners. Probe reservation/observation recording (file IO) stays at the node boundary.
* The runner-up cascade loop (contains `continue`/`break` interleaved with fallback trace mutation) and the State-write/event/persistence boundaries of `monitor_node` (498 LOC) remain in the orchestrator by design.
* BASE×2/FEATURE×2 harness differential was NOT RUN; replaced by the full existing-suite run below.

## 6. Verification

| Item | Result |
|---|---|
| T4-B structural gates (10) | passed |
| T4-B frozen contract tests (5, portable mode) + full-corpus `verify … 1` | passed / 0 mismatches |
| Existing Monitor-related tests (64 files) | 961 passed |
| Historical P1.5 gates + all `test_p15*`/`test_p16*` (53 files) | 3,092 passed, 1 skipped (Windows-only/privilege-conditional test) |
| T4-A scope gate | stage-pinned to `c338ba3`; T4-A/T3.5 golden fixtures unchanged |
| Production-write leakage | none: tests run in disposable roots; `git status` clean after runs |

## 7. Remaining

T4-B IMPLEMENTED / PENDING independent Codex audit. T4-C, T5 and Wave D NOT STARTED. REAL_REPORT_PARITY_BLOCKED OPEN. NTFS mtime causality P2 OPEN.

## 8. CI

CODE `a25ad43` run 38658426297: Windows smoke SUCCESS, Linux regression CANCELLED by the 20-min job timeout (the added T4-B portable-oracle gate; no test failure). CI-config fix `5c8001c` (regression timeout 20->35 min) run 38660492205: **regression SUCCESS, Windows harness isolation smoke SUCCESS** (includes T4-B Linux gate and Windows native replay accounting). Final documentation commit CI recorded in the report.
