# P1.5 Third Pass T3-A - ownership matrix (source-grounded, generated)

HEAD at generation: `bcb83a6e1834b23aee885359e686deafa9970195`. Machine-readable: [p1_5_third_pass_t3_ownership_matrix.json](p1_5_third_pass_t3_ownership_matrix.json). Columns in JSON: module, class, role, responsibility, loc, public_functions, prod_consumers, test_consumers, max_output_arity, named_record_functions, facade_symbols, side_effect_tokens, action.

Classification rules (explicit): COMPAT_FACADE = public ABI/effect owner kept in place; SAFETY_LOCK = effect coordinator; CANONICAL_OWNER = ledgered Owner or pre-existing responsibility-named Owner; RENAME_CANDIDATE = Owner with an unconverted positional return of arity > 8; UNKNOWN = no static consumer found; KEEP = markers/others.

## Summary by package

| Package | modules | CANONICAL_OWNER | RENAME_CANDIDATE | COMPAT_FACADE | other | max arity (unconverted) | LOC |
|---|---:|---:|---:|---:|---:|---:|---:|
| `apps/operator_ui` | 25 | 7 | 6 | 1 | 11 | 24 | 8179 |
| `graphs` | 1 | 0 | 0 | 1 | 0 | 0 | 3495 |
| `graphs/nodes` | 3 | 0 | 0 | 3 | 0 | 0 | 8588 |
| `libs/reporting` | 8 | 0 | 0 | 7 | 1 | 0 | 9190 |
| `libs/reporting/reporter_bundle_runtime_parts` | 7 | 6 | 0 | 0 | 1 | 5 | 329 |
| `libs/reporting/trade_memory_projection_parts` | 5 | 2 | 2 | 0 | 1 | 30 | 761 |
| `libs/reporting/trade_read_model_parts` | 4 | 2 | 1 | 0 | 1 | 13 | 567 |
| `libs/reporting/trade_report/ai_facade_parts` | 15 | 13 | 2 | 0 | 0 | 13 | 1799 |
| `libs/runtime` | 2 | 0 | 0 | 2 | 0 | 0 | 3919 |
| `libs/runtime/commander` | 34 | 27 | 7 | 0 | 0 | 22 | 6407 |
| `libs/runtime/monitor` | 20 | 11 | 8 | 0 | 1 | 24 | 3021 |
| `libs/runtime/monitor_exit` | 25 | 24 | 0 | 0 | 1 | 8 | 3435 |
| `libs/runtime/monitor_exit/adapters` | 2 | 1 | 0 | 0 | 1 | 0 | 58 |
| `libs/runtime/scanner` | 25 | 21 | 3 | 0 | 1 | 24 | 4758 |
| `libs/runtime/strategist` | 1 | 0 | 0 | 0 | 1 | 0 | 1 |
| `libs/runtime/strategist/context` | 13 | 11 | 1 | 0 | 1 | 18 | 2520 |
| `libs/runtime/strategist/llm` | 5 | 4 | 0 | 0 | 1 | 0 | 928 |
| `libs/runtime/strategist/output` | 6 | 5 | 0 | 0 | 1 | 3 | 887 |
| `libs/runtime/strategist/policy` | 6 | 5 | 0 | 0 | 1 | 8 | 1066 |

## Public facades / effect coordinators

| Module | Class | Role | LOC | prod consumers | tests |
|---|---|---|---:|---:|---:|
| `apps/operator_ui/data_access_core.py` | COMPAT_FACADE | Operator UI data-access coordinator (contains LLM brief path) | 3707 | 6 | 0 |
| `graphs/commander_runtime.py` | COMPAT_FACADE | Commander runtime (route/phase authority, runtime ownership) | 3495 | 15 | 20 |
| `graphs/nodes/monitor_node.py` | COMPAT_FACADE | Monitor graph node (OrderIntent / cooldown / entry-exit order) | 1918 | 11 | 27 |
| `graphs/nodes/scanner_node.py` | COMPAT_FACADE | Scanner graph node (canonical ranking + selected rank) | 1993 | 11 | 33 |
| `graphs/nodes/strategist_node.py` | COMPAT_FACADE | Strategist graph node (LLM boundary + state writes) | 4677 | 13 | 32 |
| `libs/reporting/live_execution_bundle_runner.py` | SAFETY_LOCK | Reporter bundle runner effect coordinator | 2788 | 7 | 2 |
| `libs/reporting/trade_memory_surface.py` | COMPAT_FACADE | Reporter memory surface API | 394 | 7 | 1 |
| `libs/reporting/trade_read_model.py` | COMPAT_FACADE | Reporter read-model API | 1357 | 16 | 7 |
| `libs/reporting/trade_report_ai.py` | COMPAT_FACADE | Reporter AI facade (ABI) | 1657 | 21 | 20 |
| `libs/reporting/trade_report_ai_compact_input.py` | COMPAT_FACADE | Reporter compact LLM input API | 419 | 6 | 0 |
| `libs/reporting/trade_report_ai_deterministic.py` | COMPAT_FACADE | Reporter deterministic fallback API | 750 | 6 | 0 |
| `libs/reporting/trade_report_markdown_clean.py` | COMPAT_FACADE | Reporter Markdown facade (ABI) | 1326 | 10 | 10 |
| `libs/reporting/trade_story_pipeline.py` | COMPAT_FACADE | Reporter story pipeline facade (ABI) | 499 | 25 | 11 |
| `libs/runtime/exit_policy.py` | COMPAT_FACADE | Exit policy trigger precedence | 1059 | 10 | 1 |
| `libs/runtime/intraday_monitor_signals.py` | COMPAT_FACADE | Intraday entry signal evaluation | 2860 | 8 | 1 |

## Highest remaining positional-contract hotspots (named-record / rename candidates)

| Module | max arity | facade symbols | LOC | prod consumers | tests |
|---|---:|---:|---:|---:|---:|
| `libs/reporting/trade_memory_projection_parts/memory_feedback_rebuild.py` | 30 | 12 | 94 | 1 | 0 |
| `apps/operator_ui/data_access_brief_market_sections.py` | 24 | 13 | 210 | 1 | 0 |
| `apps/operator_ui/data_access_brief_monitor_sections.py` | 24 | 8 | 275 | 1 | 0 |
| `libs/runtime/monitor/signal_features.py` | 24 | 33 | 341 | 1 | 0 |
| `libs/runtime/scanner/score_feature_projection.py` | 24 | 14 | 231 | 1 | 0 |
| `libs/runtime/commander/decision_context_projection.py` | 22 | 6 | 225 | 1 | 0 |
| `libs/runtime/commander/decision_context_projection_applied_policy_command.py` | 22 | 1 | 148 | 1 | 0 |
| `libs/runtime/monitor/entry_cycle_context.py` | 22 | 9 | 134 | 1 | 0 |
| `libs/runtime/commander/open_position_inputs_projection.py` | 19 | 8 | 172 | 1 | 0 |
| `libs/runtime/monitor/entry_context.py` | 19 | 10 | 65 | 1 | 0 |
| `libs/runtime/monitor/entry_cascade_projection.py` | 18 | 6 | 278 | 1 | 0 |
| `libs/runtime/strategist/context/node_context_projection.py` | 18 | 20 | 123 | 1 | 0 |
| `apps/operator_ui/data_access_brief_render_sections.py` | 17 | 3 | 199 | 1 | 0 |
| `libs/reporting/trade_memory_projection_parts/memory_status_summary.py` | 16 | 11 | 75 | 1 | 0 |
| `libs/runtime/commander/decision_overlay_projection.py` | 16 | 13 | 194 | 1 | 0 |

## T3-B converted (this change set)

| Historical Owner function | New name | Record | Arity |
|---|---|---|---:|
| `fb_seed_action_entry_decision_seed` | `fallback_report_seed` | `FallbackReportSeed` | 30 |
| `memory_input_commander_memory_policy_daily_packet` | `memory_packets_and_visibility` | `MemoryPacketsAndVisibility` | 30 |
| `memory_input_monitor_guidance_monthly_packet` | `memory_prompt_visibility` | `MemoryPromptVisibility` | 30 |
| `read_select_artifacts_bundle` | `selected_trade_artifacts` | `SelectedTradeArtifacts` | 30 |
| `cp_facts_commander_route_diagnostics` | `compact_story_facts` | `CompactStoryFacts` | 25 |
| `behavior_input_block_buy_when_open_position_buy_closeou` | `commander_behavior_policy_inputs` | `CommanderBehaviorPolicyInputs` | 24 |
| `signal_feature_breakout_buffer_pct_breakout_level` | `breakout_level_features` | `BreakoutLevelFeatures` | 24 |
| `scan_feature_candidate_rank_score_candidate_universe` | `candidate_rank_inputs` | `CandidateRankInputs` | 24 |
| `brief_facts_canonical_monitor_snapshot_execution` | `operator_brief_canonical_facts` | `OperatorBriefCanonicalFacts` | 24 |
| `lifecycle_exit_monitor_context` | `lifecycle_exit_monitor_context` | `LifecycleExitMonitorContext` | 8 |
| `closed_sell_execution_details` | `closed_sell_execution_details` | `ClosedSellExecutionDetails` | 8 |
| `report_generation_policy_gate` | `report_generation_policy_gate` | `ReportGenerationPolicyGate` | 8 |
