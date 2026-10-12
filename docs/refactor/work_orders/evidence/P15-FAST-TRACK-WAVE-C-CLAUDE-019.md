# P15 Fast Track Wave C — Claude implementation evidence (P1.5.7 / P1.5.8 / P1.5.9 / P1.5.10)

Branch `refactor/p1.5` only; isolated clone `C:\AgentraEvidence\r3_seam_clone` (no other directory modified or deleted). Start SHA `cba2124a85d2a3bf7cef96876920ba4912bd1c5e`. Scrubbed env, no credentials, `PYTHONDONTWRITEBYTECODE=1`; live `C:\Agentra`, Q12, broker, real LLM, Docker untouched; no ZIP; no new branch.
Codex Wave B verdict recorded: [P15-FAST-TRACK-WAVE-B-CODEX-AUDIT-017.md](P15-FAST-TRACK-WAVE-B-CODEX-AUDIT-017.md).

## Before / after
| File | Before | After | Moved | Owners |
|---|---:|---:|---:|---|
| `graphs/commander_runtime.py` | 6,297 | **4,709** (-1,588) | 48 bodies | 8 in `libs/runtime/commander/`: `carry_review_policy`, `fast_path_policy`, `entry_control_policy`, `applied_policy`, `candidate_watch_policy`, `position_projection`, `session_assessments`, `event_projection` (max 314 LOC) |
| `graphs/nodes/execute_from_packet.py` | 4,189 | **4,105** (-84) | 3 bodies | 1: `libs/execution/executor_observability.py` (121 LOC) |
| runtime naming (C2) | - | +5 alias files, 1 helper, 6 call sites | 0 moved | `graphs/pipelines/{live_cycle,runtime_tick,eod_report}.py`, `libs/runtime/entrypoints/live_loop.py`, `scripts/run_live_loop.py`; `live_loop_env` in `entrypoint_common.py` |
| wrapper classification (C4) | - | inventory + note | 0 deleted / 0 consolidated | - |
Totals: 51 bodies moved, 9 new Owners (+5 alias modules), 0 deleted, 0 consolidated, -1,672 LOC in the two modules.

## Gates
| Gate | Result |
|---|---|
| C1: moved-body gate (48 x 3 shapes) + 31 Commander consumer files | 559 passed, 0 production writes |
| C3: moved-body gate + 51 `execute_from_packet` consumer files | 952 passed, 8 failed (`tests/test_step5b_fix4.py` x8 — the known pre-existing baseline failures, identical in the baseline tree) |
| C2: alias tests (7) + 41 entrypoint/runtime consumer files; legacy and canonical CLI `--help` | 469 passed + 7 passed |
| Scope/authority tests: path scope; every non-moved def in the two touched modules AST-identical to the Wave C baseline (guard/admission/CAS/UNKNOWN/broker paths untouched); Owner imports/LLM-role | 4 passed |
| Independent static: `p152_facade_consumer_scan` unchanged (436 / 106 / 330); Owners <=350 | pass |
| Call differential vs `cba2124` baseline, baseline x2 and feature run concurrently (76 files, 903 tests, 4,252 recorded calls, 49/51 moved symbols exercised) | per-test outcomes identical (same 8 known failures); **0 differences among baseline-stable records**; 700 records nondeterministic baseline-vs-baseline (live public market data) |
Not run here (Wave D): full native pytest, Docker, UEF replay, real-fixture executor parity (EX1).

## Trading-authority safety statement
Executor guard order, readiness evidence, Supervisor verdict, admission/CAS, idempotency, UNKNOWN quarantine, BrokerOutcome and every broker mutation path are byte-AST-identical to the baseline (only three observability/read-model functions moved). Commander graph order, fast-path routing, state keys, runtime transitions and reporter hooks are unchanged; no new LLM role. No lock path, state key or CLI was renamed.

## Debt / second-pass candidates
- Giant functions that cannot move mechanically: `_build_commander_decision` 857, `_resolve_commander_behavior_policy` 740, `_assess_open_position_commander_override` 437, `_attach_commander_applied_policy` 396, `_run_commander_runtime_impl` 298 / `_run_integrated_chain_impl` 230 (orchestration, kept by design); executor `execute_from_packet` 1,191, `_normalize_execution` 181, `_evaluate_open_order_reconciliation_guard` 148, `_prepare_request` 124, `_resolve_order_price_for_notional_with_source` 117 (SAFETY_BLOCKED pending real fixtures); Wave B giants (`strategist_node`, `scanner_node`, `monitor_node`, `_evaluate_monitor_entry_candidate`); Operator Brief giants (Wave A).
- Naming second pass: dual-write `runtime_tick_pipeline` state key, canonical tick value, lock default path (single-instance risk) — dual-key migration plan needed.
- Wrapper second pass: 330 UNKNOWN Reporting ABI symbols, 114 duplicate-body groups, legacy adapters: need runtime/consumer proof.
- Pre-existing: yfinance live market-data reads inside offline tests (non-deterministic); `controlled_mock_lanes` write isolation OPEN; real frozen report/LLM parity BLOCKED.
