# P1.5 Third Pass T3 - ownership matrix (source-grounded, reproducible)

Source commit (reachable, immutable): `ab8563b251c7a2fc8b0409fde36a05bc10918f04`. Machine-readable: [p1_5_third_pass_t3_ownership_matrix.json](p1_5_third_pass_t3_ownership_matrix.json). Regenerate / prove:

    python scripts/refactor/p159_ownership_matrix.py --sha ab8563b251c7a2fc8b0409fde36a05bc10918f04 --write
    python scripts/refactor/p159_ownership_matrix.py --verify

Classes: {'KEEP': 23, 'CANONICAL_OWNER': 169, 'COMPAT_FACADE': 14, 'SAFETY_LOCK': 1}. Flags (independent): {'CONTRACT_CANDIDATE': 27, 'RENAME_CANDIDATE': 52}. `CONTRACT_CANDIDATE` = unconverted positional return > 8 values; `RENAME_CANDIDATE` = mechanically generated Owner function name awaiting review. Neither flag is a claim that a name or contract is defective.

## Summary by package

| Package | modules | CANONICAL_OWNER | COMPAT_FACADE | CONTRACT_CANDIDATE | RENAME_CANDIDATE | max arity | LOC |
|---|---:|---:|---:|---:|---:|---:|---:|
| `apps/operator_ui` | 25 | 13 | 1 | 5 | 6 | 19 | 8270 |
| `graphs` | 1 | 0 | 1 | 0 | 0 | 0 | 3495 |
| `graphs/nodes` | 3 | 0 | 3 | 0 | 0 | 0 | 8588 |
| `libs/reporting` | 8 | 0 | 7 | 0 | 0 | 0 | 9190 |
| `libs/reporting/reporter_bundle_runtime_parts` | 7 | 6 | 0 | 0 | 0 | 5 | 329 |
| `libs/reporting/trade_memory_projection_parts` | 5 | 4 | 0 | 1 | 2 | 16 | 798 |
| `libs/reporting/trade_read_model_parts` | 4 | 3 | 0 | 1 | 2 | 13 | 567 |
| `libs/reporting/trade_report/ai_facade_parts` | 15 | 15 | 0 | 2 | 4 | 13 | 1799 |
| `libs/runtime` | 2 | 0 | 2 | 0 | 0 | 0 | 3919 |
| `libs/runtime/commander` | 34 | 34 | 0 | 6 | 8 | 19 | 6465 |
| `libs/runtime/monitor` | 20 | 19 | 0 | 8 | 18 | 22 | 3052 |
| `libs/runtime/monitor_exit` | 25 | 24 | 0 | 0 | 3 | 8 | 3435 |
| `libs/runtime/monitor_exit/adapters` | 2 | 1 | 0 | 0 | 0 | 0 | 58 |
| `libs/runtime/scanner` | 25 | 24 | 0 | 3 | 5 | 21 | 4786 |
| `libs/runtime/strategist` | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| `libs/runtime/strategist/context` | 13 | 12 | 0 | 1 | 1 | 18 | 2520 |
| `libs/runtime/strategist/llm` | 5 | 4 | 0 | 0 | 0 | 0 | 928 |
| `libs/runtime/strategist/output` | 6 | 5 | 0 | 0 | 2 | 3 | 887 |
| `libs/runtime/strategist/policy` | 6 | 5 | 0 | 0 | 1 | 8 | 1066 |

## Public facades / effect coordinators

| Module | Class | Role | LOC | prod consumers | tests |
|---|---|---|---:|---:|---:|
| `apps/operator_ui/data_access_core.py` | COMPAT_FACADE | Operator UI data-access coordinator (contains LLM brief path) | 3707 | 1 | 0 |
| `graphs/commander_runtime.py` | COMPAT_FACADE | Commander runtime (route/phase authority, runtime ownership) | 3495 | 6 | 20 |
| `graphs/nodes/monitor_node.py` | COMPAT_FACADE | Monitor graph node (OrderIntent / cooldown / entry-exit order) | 1918 | 5 | 27 |
| `graphs/nodes/scanner_node.py` | COMPAT_FACADE | Scanner graph node (canonical ranking + selected rank) | 1993 | 5 | 33 |
| `graphs/nodes/strategist_node.py` | COMPAT_FACADE | Strategist graph node (LLM boundary + state writes) | 4677 | 4 | 32 |
| `libs/reporting/live_execution_bundle_runner.py` | SAFETY_LOCK | Reporter bundle runner effect coordinator | 2788 | 2 | 2 |
| `libs/reporting/trade_memory_surface.py` | COMPAT_FACADE | Reporter memory surface API | 394 | 2 | 1 |
| `libs/reporting/trade_read_model.py` | COMPAT_FACADE | Reporter read-model API | 1357 | 9 | 7 |
| `libs/reporting/trade_report_ai.py` | COMPAT_FACADE | Reporter AI facade (ABI) | 1657 | 12 | 20 |
| `libs/reporting/trade_report_ai_compact_input.py` | COMPAT_FACADE | Reporter compact LLM input API | 419 | 1 | 0 |
| `libs/reporting/trade_report_ai_deterministic.py` | COMPAT_FACADE | Reporter deterministic fallback API | 750 | 1 | 0 |
| `libs/reporting/trade_report_markdown_clean.py` | COMPAT_FACADE | Reporter Markdown facade (ABI) | 1326 | 3 | 10 |
| `libs/reporting/trade_story_pipeline.py` | COMPAT_FACADE | Reporter story pipeline facade (ABI) | 499 | 18 | 11 |
| `libs/runtime/exit_policy.py` | COMPAT_FACADE | Exit policy trigger precedence | 1059 | 5 | 1 |
| `libs/runtime/intraday_monitor_signals.py` | COMPAT_FACADE | Intraday entry signal evaluation | 2860 | 2 | 1 |

## Highest remaining positional-contract hotspots (CONTRACT_CANDIDATE)

| Module | max arity | facade symbols | LOC | prod consumers | tests |
|---|---:|---:|---:|---:|---:|
| `libs/runtime/monitor/entry_cycle_context.py` | 22 | 9 | 134 | 1 | 0 |
| `libs/runtime/monitor/signal_features.py` | 22 | 29 | 294 | 1 | 0 |
| `libs/runtime/scanner/score_feature_projection.py` | 21 | 14 | 259 | 1 | 0 |
| `apps/operator_ui/data_access_brief_market_sections.py` | 19 | 13 | 241 | 1 | 0 |
| `libs/runtime/commander/open_position_inputs_projection.py` | 19 | 8 | 172 | 1 | 0 |
| `libs/runtime/monitor/entry_context.py` | 19 | 10 | 65 | 1 | 0 |
| `libs/runtime/monitor/entry_cascade_projection.py` | 18 | 6 | 278 | 1 | 0 |
| `libs/runtime/strategist/context/node_context_projection.py` | 18 | 20 | 123 | 1 | 0 |
| `apps/operator_ui/data_access_brief_render_sections.py` | 17 | 3 | 199 | 1 | 0 |
| `libs/reporting/trade_memory_projection_parts/memory_status_summary.py` | 16 | 11 | 75 | 1 | 0 |
| `libs/runtime/commander/decision_overlay_projection.py` | 16 | 13 | 194 | 1 | 0 |
| `libs/runtime/scanner/candidate_context_projection.py` | 16 | 7 | 89 | 1 | 0 |
| `libs/runtime/commander/decision_context_projection.py` | 15 | 6 | 254 | 1 | 0 |
| `libs/runtime/commander/policy_normalizers_projection.py` | 15 | 4 | 119 | 1 | 0 |
| `libs/runtime/monitor/exit_decision_projection.py` | 15 | 8 | 175 | 1 | 0 |
