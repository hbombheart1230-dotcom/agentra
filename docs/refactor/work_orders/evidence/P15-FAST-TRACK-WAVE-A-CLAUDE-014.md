# P15 Fast Track Wave A — Claude implementation evidence (Reporting residual + P1.5.3 Operator UI first pass)

Branch `refactor/p1.5` only, isolated clone `C:\AgentraEvidence\r3_seam_clone`. Wave start `fb8de628eb56b0941007e90ad2e98b4f684983ba` (LOC010 code `b0cfc2b5646ff81ec5ce7b738f485a9d22365826`). Pinned wave SHA = the commit carrying this file (reported in chat). Project venv, scrubbed env (no credentials), `PYTHONDONTWRITEBYTECODE=1`; guarded Guard-006 recorder. Live `C:\Agentra`/Q12 untouched; no broker/LLM/production writes; no ZIP produced.

## Mechanism (same for every move)
Public `def` (name, signature/defaults/annotations/decorators/docstring) stays in the original module; body becomes `return <name>_r3_impl(..., facade=_r3_sys.modules[__name__])`. In the responsibility-named Owner each former module global is qualified at its use site as `facade.NAME` (lazy, use-time; no entry capture, no `__getattr__`/exec/re-export; Owner imports neither the original module nor a façade). Only IO-free, clock-free, non-LLM, non-persistence functions >= 7 LOC and <= 320 LOC were moved.

## Before / after LOC
| Module | Wave start | After | Delta |
|---|---:|---:|---:|
| `libs/reporting/trade_report_ai.py` | 1,958 (LOC008 baseline; 1,958 at LOC010) | **1,656** | -302 |
| `libs/reporting/trade_report_markdown_clean.py` | 1,527 | **1,325** | -202 |
| `libs/reporting/trade_story_pipeline.py` | 562 | **498** | -64 |
| *Reporting façades subtotal* | 4,047 | **3,479** | -568 |
| `apps/operator_ui/data_access_core.py` | 6,871 | **4,594** | -2,277 |
| `libs/reporting/operator_period_summary.py` | 3,210 | **1,195** | -2,015 |
| `libs/reporting/operator_visibility.py` | 1,879 | **1,520** | -359 |
| *Operator UI/Brief subtotal* | 11,960 | **7,309** | -4,651 |
New Owners: **32** (A1 10, A2 22), 6,574 physical LOC total, max 343 (`data_access_brief_compaction.py`), none > 350. Moved symbols this wave: 55 (A1) + 136 (A2) = 191.

## Owner map
**A1 Reporting** — Story: `trade_story_facade_parts/dependency_maps.py` (3 maps). AI (`trade_report/ai_facade_parts/`): `dependency_maps` (2), `scanner_selection` (5), `entry_gate_snapshots` (4), `market_context_text` (6), `holding_memory_compaction` (4), `lifecycle_status_labels` (7). Markdown (`trade_report/markdown_clean_parts/`): `report_paths_and_time` (6), `memory_policy_phases` (12), `monitor_artifact_resolution` (6).
**A2 Operator UI/Brief** (`apps/operator_ui/`): `data_access_brief_canonical_input` (canonical trade brief input), `data_access_brief_compaction` (LLM compact input), `data_access_brief_monitor_notes`, `data_access_brief_fallback`, `data_access_brief_sanitation`, `data_access_brief_prompts` (message construction/parsing only), `data_access_run_read_models`, `data_access_symbol_run_chain`, `data_access_trade_read_models`, `data_access_value_formatting` (53 symbols). `libs/reporting/operator_period_summary_parts/`: `markdown_daily_summary`, `markdown_period_symbol_summary`, `residual_positions`, `closeout_reconciliation`, `pattern_naming`, `pattern_buckets_and_performance`, `trade_decision_fields`, `trade_rows_and_metrics`, `operator_readouts`, `period_payloads` (61 symbols). `libs/reporting/operator_visibility_parts/`: `summary_snapshot_and_bundle`, `reason_text_and_time` (22 symbols).
`data_access.py` (compat façade `globals().update(vars(core))`) and every module-level name are unchanged.

## Gates (isolated clone)
| Gate | Result |
|---|---|
| Reporting moved-body gate (ledger now **141** symbols) incl. baseline AST equality after unqualification, exact qualified names, no unresolved global, wrapper contract, **use-time oracle**: stub-call sequence/outcome identical to the pinned baseline function bound to the live module, before-call and mid-call re-patching; dependency-map identity test; 436 ABI; symbol ledger | pass |
| New P1.5.3 gate `tests/test_p153_operator_ui_moved_bodies.py` (ledger `docs/refactor/p1_5_3_operator_ui_moved_bodies_ledger.json`, 136 symbols, baseline pin `fb8de62`): same checks + all module-level declarations retained + Owners <= 350 and never importing the original module | **706 passed** |
| Independent AST: 436 Reporting defs, 0 ABI violations; import cycles in `libs.reporting` 0; no Owner -> façade import | pass |
| Synthetic differential vs baseline `ba6618d` (guarded recorder, 51 Reporting files, A1 symbols): 150,693 calls | 150,692 identical; the 1 difference is the known wall-clock `latency_ms` record |
| Synthetic differential Operator UI (17 consumer files, 247 tests; 136 A2 symbols, 131 exercised): 43,560 calls | per-test outcomes identical; 32 differing records, all `_normalize_operator_brief_payload`, field `prompt_hash` — reproduced **baseline-vs-baseline** (hash of a prompt that embeds run-specific content), i.e. non-deterministic, not a code difference |
| Consolidated focused regression: all `tests/*p152*`, `*p153*`, Reporting consumer files, 18 Operator-UI consumer files, patch-notes sync (71 files) | **2,374 passed, 1 skipped, 1 failed**; production-path write banner **0**. The 1 failure `tests/apps/api/test_isolation.py::test_api_routes_are_get_only` is the known pre-existing API failure, identical on baseline `ba6618d` |
Tests are not weakened: the Reporting moved-body count pin rose 57 -> 141 and its use-time check was strengthened from an event-order invariant to a baseline-function oracle (the invariant wrongly rejected a legitimate callee-before-argument evaluation order).

## Findings / debt (not FINAL)
- Not moved (isolated, SECOND_PASS_DEBT): persistence/IO/clock/LLM-calling functions in `data_access_core.py` (`_load_operator_brief`, `_save_*`, `_sync_*`, artifact path/IO helpers, `_trade_report_index`, `load_overview`, `load_run_detail`...) and oversize single functions (`_build_operator_brief_sections` 846, `_render_operator_brief_markdown` 652, `_load_operator_brief` 442, `_build_operator_brief_input` 426) — cannot fit a <=350 Owner without real decomposition; AI LLM-locked functions unchanged.
- Façade wrappers and numbered `bodies_01..05` Owners remain; AI 1,656 / Markdown 1,325 / Story 498 SIZE_DEFERRED.
- Real frozen report/LLM parity BLOCKED/NOT RUN; full native pytest and `controlled_mock_lanes` write isolation OPEN; Operator Brief `prompt_hash` is non-deterministic (pre-existing).
- CI workflow guard step still asserts R3-era CURRENT markers (stale); Codex/GPT workflow update required. CI also still emits its own ZIP artifacts (not produced by Claude).
- A transient batch of `E` setup errors occurred when two pytest sessions shared the OS temp base directory (`conftest` stale-basetemp cleanup); sessions were then run sequentially. Not a repo defect, noted for audit reproduction: do not run concurrent pytest sessions.
- Operator UI status: **FIRST_PASS_WITH_DEBT** (focused safety + contract gates passed; no real-data snapshots).
