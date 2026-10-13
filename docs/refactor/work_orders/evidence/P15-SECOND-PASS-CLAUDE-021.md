# P15 Second Pass — Claude implementation evidence (S1 Monitor, S2 Scanner, S3 Commander, S4 Operator UI, S5 Strategist, S6 deferred)

Branch `refactor/p1.5` only; isolated clone `C:\AgentraEvidence\r3_seam_clone`; baseline clone `C:\AgentraEvidence\r3_diff_base` at the design commit `60dfa1c4cd7ca62d127251a4051b3404a86f6932` (code `1f7add2b0f9b5a33399da27edcdd2f390bdf911b`). Scrubbed env, no credentials, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONHASHSEED=0` for the differential; live `C:\Agentra`, Q12 worktrees, broker, real LLM, Docker, scheduler and production data untouched; no ZIP.

## Method
Intra-function extract-method driven by a dataflow planner: a segment moves only if it is a contiguous effect-free statement run (or the pure RHS of a `state[...] = expr` assignment) with provably explicit inputs/outputs. Rejected: return/break/continue/yield/await/global/del, state writes, event/log/IO/persist/provider/LLM calls, clock/env/uuid/random reads, and in-place mutation of anything except caller-fresh local containers (`x = {}`/`[]`/`dict(...)`, depth-1 only). Owner bodies are the original statements verbatim; module globals resolve at use time as `facade.NAME` (TEMPORARY_COMPATIBILITY, keeps monkeypatch seams). Owners import only `__future__`. Original functions stay sequencers that call Owners and keep every effectful statement and trigger precedence. Per-segment ledger: [p1_5_second_pass_moved_segments_ledger.json](../../p1_5_second_pass_moved_segments_ledger.json).

## Before / after
| File | Before | After | Segments | Moved LOC | Owners |
|---|---:|---:|---:|---:|---|
| `graphs/nodes/monitor_node.py` | 3,595 | 1,918 | 33 | 1,769 | 13 (`libs/runtime/monitor`, max 286) |
| `libs/runtime/intraday_monitor_signals.py` | 3,608 | 2,860 | 12 | 783 | 5 (max 310) |
| `libs/runtime/exit_policy.py` | 1,604 | 1,059 | 9 | 570 | 3 (`libs/runtime/monitor_exit`, max 273) |
| `graphs/nodes/scanner_node.py` | 2,653 | 1,993 | 13 | 696 | 5 (`libs/runtime/scanner`, max 252) |
| `graphs/commander_runtime.py` | 4,710 | 3,495 | 22 | 1,277 | 9 (`libs/runtime/commander`, max 225) |
| `apps/operator_ui/data_access_core.py` | 4,595 | 3,707 | 18 | 936 | 6 (`apps/operator_ui/data_access_brief_*`, max 275) |
| `graphs/nodes/strategist_node.py` | 5,145 | 4,677 | 13 | 502 | 4 (`libs/runtime/strategist/{context,policy,output}`, max 252) |
Totals: 120 segments, 6,533 LOC moved, 45 Owner modules (all ≤350), 13 giant functions split.

Function sizes: `monitor_node` 2,634→1,107; `_evaluate_monitor_entry_candidate` 658→449; `evaluate_intraday_entry_signal` 1,229→458; `evaluate_exit_policy` 1,234→673; `scanner_node` 1,944→1,261; `_build_commander_decision` 857→195; `_resolve_commander_behavior_policy` 740→528; `_assess_open_position_commander_override` 437→155; `_attach_commander_applied_policy` 396→297; `_build_operator_brief_sections` 846→341; `_build_operator_brief_input` 426→314; `_render_operator_brief_markdown` 652→351; `strategist_node` 1,705→1,216.

## Gates
| Gate | Result |
|---|---|
| `tests/test_p156_second_pass_extraction_gates.py` (ledger, inline-reconstruct to baseline AST, unmoved defs identical, no unresolved globals/imports, ≤350 LOC, no env/clock/IO tokens, fresh-container mutation only, scope/authority) | passed (sensitivity: a tampered Owner constant is detected) |
| Consumer suites, 140 files, 2,950 tests, baseline×2 + feature×2 concurrent | per-test outcomes identical in all four; 2 failures, both pre-existing baseline failures: `tests/apps/api/test_isolation.py::test_api_routes_are_get_only`, `tests/test_scanner_rank_plumbing_fix.py::test_canonical_scanner_rank_for_runner_up_symbol` |
| Node/function call differential with post-call argument (State) hashing: 1,131 recorded calls on 13 functions | 921 byte-identical; 201 non-deterministic on one side (wall-clock, uuid, `source_signature` mtime, payload-char counts, live-market float noise), 139 of those equal within tolerance; 9 stable-looking mismatches were re-run alone, sequentially per tree: identical (artefact of two baseline processes sharing one clone directory, i.e. the known `controlled_mock_lanes` write-isolation item) |
| Production writes | 0 (isolated clones; TEMP redirected) |
| Trading-authority invariants | no file under `libs/execution`, `libs/broker`, `libs/supervisor`, `libs/risk`, `libs/llm`, `execute_from_packet`, `decide_trade`, `update_state_after_execution` changed; Wave C scope guard re-pinned to its own end SHA |

## Boundary statements
- **Strategist:** `_run_strategist_frame_llm`, `_build_compact_strategist_llm_payload`, `_build_strategist_llm_messages`, prompt/model/token/retry/timeout/call order untouched; window 3890–4039 (frame preparation and LLM invocation) was excluded from extraction.
- **Scanner:** canonical ranking window (1629–1788) untouched; single ranking owner and stable tie order unchanged.
- **Operator UI:** `_load_operator_brief` (LLM chat/retry) untouched; Brief Markdown/JSON are produced by the same statements.
- **Commander:** `_run_commander_runtime_impl` / `_run_integrated_chain_impl` untouched.

## BLOCKED / DEFERRED / debt
- S6 Supervisor/Executor/common: SAFETY_LOCK; no immutable real-case fixtures and no provably pure read-model → no change.
- Real frozen report/LLM request-response parity, Operator Brief byte parity against frozen real artifacts, and rank-1/tie fixtures with immutable snapshots: BLOCKED / NOT RUN (only repository tests and recorded-call differential were possible).
- `facade` injection is TEMPORARY_COMPATIBILITY; Owner names are mechanically derived and should be curated; each remaining orchestrator is still 150–1,200 LOC (effectful statements intentionally retained).
- Runs with many outputs (up to 24) are tuple-return seams; a typed result record would be a later cleanup.
- Pre-existing: 8 `test_step5b_fix4.py` failures (EXECUTION_DISABLED), `controlled_mock_lanes` write isolation OPEN, yfinance reads inside offline tests, full native pytest/Docker/UEF are Wave D.
