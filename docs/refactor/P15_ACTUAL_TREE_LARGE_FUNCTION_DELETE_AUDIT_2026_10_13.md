# P1.5 actual-tree / large-function / deletion-candidate audit — 2026-10-13

**Read-only evidence audit.** Inspected Git SHA: `4cb92916c976f947613f52e8b0c0790addac7eb5` on `refactor/p1.5`. Previous code baseline `bf59c4d` (documentation-only commit at latest HEAD). **This document does not authorize deletes, moves, new trading logic or Wave D.**

Related authorities: [canonical target and historical statuses](P15_CANONICAL_TARGET_TREE_AND_REPORTER_ASIS_2026_10_13.md), [third-pass scope](P15_THIRD_PASS_GPT_REPORTER_INCLUSIVE_DESIGN_2026_10_13.md), [pre-Wave-D order](P15_PRE_WAVE_D_STRUCTURAL_CLOSURE_ORDER_2026_10_13.md).

## Scope and confidence

- Enumerated **all 3,331 Git tree entries / 1,941 tracked Python source files** (tests and tooling included); 1,185 Python files remain when excluding `tests/`, `scripts/` and `docs/` prefixes.
- Inspected contents of **all 118 production Python files at >=20 KB** in that selection and summarized physical top-level function spans. This is a *size-filtered* review, not an exhaustive AST/call-graph scan of every 1,185 source file. Large class methods and functions in smaller source files may be missing; a future local AST census is required before claiming completeness.
- `libs/reporting/` has 466 Python files, 123 directly at its root and **135 under `evaluation/`**. At least 204 files sit under five explicitly research/evaluation-oriented prefixes (`evaluation/`, `baseline_btc_woori_tech/`, `baseline_samsung_hynix/`, `alpha_research_board/` and `opening_rank1_shadow/`). They are **not automatically Reporter agent implementation**, even though physically located under reporting.
- Function sizes are observed *physical source spans* measured by top-level function boundaries; count is approximate (line numbers can include trailing comments/blank lines, decorators excluded). Treat safety constraints rather than a literal LOC threshold as the primary decision factor.

## A. Structural fit — PARTIAL MATCH

**Aligned**: canonical orchestration under `graphs/commander_runtime.py`; named `graphs/nodes/{strategist,scanner,monitor,reporter,executor}_node.py` plus decision/execution bridge; existing `libs/runtime/{commander,strategist,scanner,monitor,monitor_exit}/` Owner packages; central Supervisor approval `libs/risk/supervisor.py`, Step5C durable CAS `libs/supervisor/intent_state_store.py` and guarded `execute_from_packet`/Broker choke; compatible Reporting and Operator UI façades; UI-connected patch notes.

**Missing from the historical representative target tree**:
1. `libs/contracts/agent_outputs.py` is a **3,864-line shared cross-agent output contract** with giant Monitor/Strategist/Scanner/Commander builders; it is vital to source-of-truth and should enter third-pass structural inventory BEFORE Wave D, while keeping schemas, state and output ABI byte-stable. Do **not** scatter authority across agent implementations.
2. `libs/agent/{commander,strategist,scanner,monitor,reporter,executor}.py` are physical API/legacy adapter paths in addition to Graph nodes. `libs/agent/commander.py` explicitly declares a legacy compatibility layer, and `graphs/trading_graph.py` calls itself a M17 baseline and says it avoids hard LangGraph dependency. The two execution surfaces are not evidence that two live LangGraph executors should be installed or that either path is dead.
3. `libs/reporting/live_execution_bundle_runner.py` is a *1,529-line actual giant CLI `main()`*, in addition to the 1,850-line (file total) `intraday_trade_reports.py` whose entry function is only ~202 lines. Bundle CLI per-lifecycle work owns lock, queue, LLM and write order. Legacy diagram should show this distinct responsibility. `libs/agent/reporter.py` is another public Reporter class entry and cannot be deleted based on its name.
4. `graphs/nodes/decide_trade.py` and `libs/runtime/{monitor_minute_ohlcv,monitor_strategy_frame}.py` contain additional significant functions; `libs/reporting/metrics_report_generator.py` also contains a large report generator. They were absent from the first third-pass priority table.
5. Plans marked `[P]` in the original architecture tree were pinned to older inspected SHA `60dfa1c` and are **not live status**: actual second-pass additions include `libs/runtime/monitor/{entry_context,entry_evidence,entry_cycle_context,entry_cascade_projection,signal_features,signal_score_projection,...}.py`; `libs/runtime/scanner/{score_feature_projection,score_policy_projection,selection_evidence_projection,...}.py`; `libs/runtime/commander/{policy_inputs_projection,policy_normalizers_projection,decision_rules_projection,decision_context_projection,...}.py`; and `apps/operator_ui/{data_access_brief_facts,data_access_brief_market_sections,data_access_brief_monitor_sections,data_access_brief_input_projection,data_access_brief_render_sections,data_access_brief_render_fallback}.py`.
6. `libs/runtime/scanner/ranking_core.py` and `apps/operator_ui/data_access_brief_text_rules.py` are **not present**. They are *not mandatory new files*: reuse present rank/source owners and text rules; avoid a second canonical ranking truth. The proposed Reporter `reporter_bundle_runtime_parts/`, `trade_memory_projection_parts/` and `trade_read_model_parts/` remain PENDING and should be created only if cohesion/consumer contracts support them.
7. Some mechanically generated names are semantically weak (for example `selection_evidence_projection_value_te_scanner.py`, `cycle_output_projection_value_state_monitor.py`, `decision_context_projection_applied_policy_command.py`). Keep consumer/import compatibility; rename only after a static + dynamic caller proof.

**Updated logical locator (not a literal exhaustive tree):**

~~~text
graphs/
  commander_runtime.py                              [E] active runtime coordinator
  trading_graph.py                                  [E] M17 graph-shaped baseline/compatibility
  nodes/{commander,strategist,scanner,monitor,reporter,executor}_node.py [E] role surfaces
  nodes/{decide_trade,decision_node,execute_order,execute_from_packet}.py [E/L] bridge and parallel legacy/safety paths

libs/agent/{commander,strategist,scanner,monitor,reporter,executor}.py [E/L] public/legacy adapters, NOT proven dead
libs/contracts/agent_outputs.py                    [E] 7-role shared output-contract builders; giant functions
libs/runtime/{commander,strategist,scanner,monitor,monitor_exit}/ [E] 2nd-pass Owners plus prior code
libs/risk/supervisor.py; libs/supervisor/intent_state_store.py [L] approval / Step5C
libs/execution/; graphs/nodes/execute_from_packet.py [L] admission/CAS/UNKNOWN/BrokerOwner

libs/reporting/
  intraday_trade_reports.py                         [E/L] report-node bundle launch/queue/process
  live_execution_bundle_runner.py                   [E/L] actual per-lifecycle CLI orchestration, outputs, locks
  trade_{memory_surface,read_model,lifecycle_builder,bundle_state}.py [E] Reporter read/projection
  trade_report_{ai,ai_deterministic,ai_compact_input,markdown_clean}.py [E] report API/prompts
  trade_story_pipeline.py                           [E] compatibility story façade
  trade_report/; trade_story_*_parts/               [E] many named/numbered Owners; ABI-sensitive
  evaluation/, baseline_*/, alpha_research_board/, opening_rank1_shadow/ [E] research/UEF, separate concern
apps/operator_ui/                                   [E] UI and operator-brief facts/rendering/LLM
~~~

**Special safety warning:** `graphs/nodes/execute_order.py` source itself describes a “legacy, parallel execution path (LEGACY_REACHABLE)” with extra UNKNOWN quarantine handling; `graphs/nodes/executor_node.py` is an M17 baseline stub. Neither is a safe file-delete candidate without runtime and test reachability proof.

## B. Confirmed significant function-size inventory, including newly discovered scope

LOC approximately at `4cb92916`. **Not** every long file must be split.

| Classification | Function (source path namespace abbreviated) | LOC | Recommendation |
|---|---|---:|---|
| Runtime high payoff | `libs/reporting/live_execution_bundle_runner.py::main` | 1,529 | SPLIT PURE plans, SAFETY_LOCK ordered write/lock/queue/LLM |
| Runtime | `graphs/nodes/scanner_node.py::scanner_node` | 1,262 | SPLIT further, preserve sole canonical rank and tie |
| Runtime | `graphs/nodes/strategist_node.py::strategist_node` | 1,217 | SPLIT PURE only, LLM lock |
| Executor | `graphs/nodes/execute_from_packet.py::execute_from_packet` | 1,192 | SAFETY_LOCK absent immutable real-case evidence |
| Runtime | `graphs/nodes/monitor_node.py::monitor_node` | 1,108 | SPLIT PURE, intent/state ordering lock |
| **Cross-agent newly flagged** | `libs/contracts/agent_outputs.py::build_monitor_output_artifact` | **809** | SPLIT pure schema projections with output parity |
| Reporter | `libs/reporting/trade_memory_surface.py::build_trade_report_memory_surface` | 675 | T1 FIRST |
| Monitor | `libs/runtime/exit_policy.py::evaluate_exit_policy` | 674 | T4, exit precedence lock |
| Reporter | `libs/reporting/trade_read_model.py::build_trade_read_model` | 601 | T1 |
| Reporter | `libs/reporting/trade_report_ai_deterministic.py::fallback_report` | 538 | T1, exact section text |
| Reporter | `libs/reporting/trade_lifecycle_builder.py::_build_trade_lifecycles` | 535 | lifecycle ordering lock |
| **Cross-agent newly flagged** | `libs/contracts/agent_outputs.py::build_strategist_output_artifact` | **530** | schema parity, no ABI move |
| Commander | `graphs/commander_runtime.py::_resolve_commander_behavior_policy` | 530 | T4 pure precedence |
| Reporter | `libs/reporting/metrics_report_generator.py::generate_metrics_report` | **471** | review report I/O/output |
| **Cross-agent newly flagged** | `libs/contracts/agent_outputs.py::build_scanner_output_artifact` | **466** | rank/selected output contract parity |
| Monitor | `libs/runtime/intraday_monitor_signals.py::evaluate_intraday_entry_signal` | 459 | T4 pure signal |
| Decision | `graphs/nodes/decide_trade.py::decide_trade` | **457** | REVIEW / authority/LLM guard |
| Reporter | `libs/reporting/agent_pipeline_trace.py::generate_agent_pipeline_trace_report` | 445 | review trace/persistence |
| Operator UI | `apps/operator_ui/data_access_core.py::_load_operator_brief` | 444 | SAFETY_LOCK real LLM chat/prompt |
| Reporter | `libs/reporting/closeout_maintenance.py::run_closeout_maintenance` | ~442 | SAFETY_LOCK filesystem/lock |
| Reporter | `libs/reporting/trade_bundle_assembly.py::apply_entry_exit_holding_enrichment` | 428 | T1/T2 pure component extraction |
| Reporter | `libs/reporting/trade_report_ai_compact_input.py::compact_story_input_for_llm` | 412 | T1, byte-level prompt lock |
| Reporter | `libs/reporting/trade_bundle_state.py::build_live_trade_bundle_payloads` | 399 | review pure artifact views |
| Monitor | `libs/runtime/monitor_minute_ohlcv.py::_ensure_monitor_minute_ohlcv_for_symbol` | **395** | REVIEW data acquisition / clock |
| Reporter | `libs/reporting/single_trade_report.py::_build_trade_report_inputs` | 391 | review read/provenance |
| Monitor | `libs/runtime/monitor_strategy_frame.py::apply_exit_policy_strategy_frame` | **381** | REVIEW exit policy authority |
| **Cross-agent newly flagged** | `libs/contracts/agent_outputs.py::build_commander_output_artifact` | **358** | output contract parity |
| Reporter research, not Reporter core | `libs/reporting/evaluation/trade_read_model.py::build_q9_trade_read_model` | 401 | EVALUATION/UEF separate scope |
| Reporter big file but shorter functions | `libs/reporting/trade_report_ai.py` | ~1,657 FILE | KEEP public façade; no giant inner function found |
| Reporter big file but shorter functions | `libs/reporting/trade_report_markdown_clean.py` | ~1,326 FILE | KEEP public façade; no giant inner function found |
| Reporter runtime file but shorter functions | `libs/reporting/intraday_trade_reports.py` | ~1,850 FILE | Do not mislabel it a 1,850-line function |

**NOTE:** Next exhaustive local AST sweep must include class methods, nested functions, <20KB production modules, more test/helper directories, dynamic imports, and all 436 Reporter façade ABI symbols. The above is not an assertion that no other long function exists.

## C. Deletion, merge and rename discovery — READ-ONLY candidates, zero approved deletes

| Candidate | Actual source evidence | Status |
|---|---|---|
| **First `render_strategist_llm_summary_markdown` definition** in `libs/reporting/strategist_llm_summary.py` near L1044 | The same top-level name is redefined again near L1526. Under ordinary module load the latter overwrites the first; the first is a likely shadowed body. | **REVIEW HIGH** for function-level deletion only; verify no module-time pre-binding, imports/introspection/coverage dependency and frozen Markdown parity. |
| `libs/agent/{commander,monitor,strategist,scanner,...}` adapters | Legacy/compatibility explicitly described in source; `libs/agent/__init__.py` exposes their types. | **KEEP COMPATIBILITY**, only consider after consumer/reflection/entrypoint audit and deprecation cycle |
| `graphs/trading_graph.py`, `graphs/nodes/executor_node.py` | M17 graph-shaped baseline and stub, may still be used by tests/adapters. | **KEEP/REVIEW**; no static proof of dead code |
| `graphs/nodes/execute_order.py` | Explicit “LEGACY_REACHABLE” parallel execution path. | **SAFETY_LOCK — DO NOT DELETE** |
| `trade_report_ai.py`, `trade_report_markdown_clean.py`, `trade_story_pipeline.py` | Reporting facades with 436 ABI symbol inventory / 330 UNKNOWN static consumer regions in prior audit. | **KEEP** until ABI+dynamic consumer inventory proves safe |
| Numbered `trade_report/*_r3_parts/bodies_01...05.py` and `trade_story_facade_r3_parts/bodies_01.py` | Mechanically named Owners can look redundant but function bodies were moved into them and are ABI-sensitive. | **RENAME/MERGE REVIEW**, not file-deletion candidates without reachability proof |
| `libs/reporting/evaluation/`, `baseline_*/`, `opening_rank1_shadow/` | Research, Q10/Q12/UEF modules, not pure trade Reporter core. | **SEPARATE CONCERN**, do not equate location with unused code or delete |

**No file deletion is approved today.** A complete deletion decision requires independent static consumer/AST import map, module-level side-effect check, dynamic import/string/`getattr`/`__all__`/CLI/service/pytest references, baseline-vs-feature fixtures, path/manifest checks and Codex independent deletion audit. Delete only with a pinned commit/rollback point, otherwise mark `KEEP / UNKNOWN / SAFETY_LOCK`.

## D. Recommended sequencing correction

1. Keep current Claude **T0 + T1 Reporter** assignment intact; avoid restarting it. Source-frozen parity, T1 pure Reporter builders first.
2. Add a **T3.5 or T4.0 cross-agent output-contract pass** for `libs/contracts/agent_outputs.py`; the 809/530/466/358-line output builders are a top-priority omission from previous third-pass list. Before splitting, freeze exact schema/field-order/size/authority provenance; do not change shared API/contract fields.
3. Include `decide_trade`, `monitor_minute_ohlcv`, `monitor_strategy_frame`, `metrics_report_generator` in residual inventory, with safety locks; do not mechanically split locked effects.
4. Mark `[P]`→`[E]` on current architecture status only where files exist; missing named modules are **not obligations** to manufacture replacements. Existing canonical target remains a historical snapshot; use this reconciliation as the latest status overlay.
5. Schedule **separate deletion/duplicate-ownership audit** *after* the third-pass structure stabilizes; do not combine speculative file deletion with T1 Reporter changes. Wave D last for full integration and real frozen report/LLM/Executor parity.
6. Preserve UI-linked `patch_notes.json` and `patch_notes.md` + daily patch on meaningful changes; no live/prod writes, no actual broker/LLM orders, no main merge, no ZIP for this Git documentation-only delivery.

**Audit verdict: STRUCTURAL_DIRECTION_MATCH / FILE_STATUS_PARTIAL / LARGE_FUNCTION_INVENTORY_INCOMPLETE_BEFORE_THIS_AUDIT / SAFE_DELETION_NOT_PROVEN.**
