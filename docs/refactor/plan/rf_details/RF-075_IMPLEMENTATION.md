# RF-075 — T09 tests/fixture target and protected callable identity

- SOURCE integration/p1.5@a7654f389fddbc2829f005ab247a96bf295228d8; CSV b46bcb1f29ed3c0a133b059d690173c195c81bf9. Actor Codex B (tests code only, no oracle edits); peer read-only. 88 exclusive historical paths.

Graph/agents: test_monitor_exit_guard.py 4951 LOC, 114 tests incl confirmation ticks/cooldown guard; keep oracle.

## Callable mapping: KEEP, not MOVE

- `tests/test_monitor_exit_guard.py::test_monitor_exit_requires_confirmation_ticks` → SAME SOURCE_PATH / SAME callable; KEEP_TEST_ORACLE. Existing test fixture names and assertions must remain stable.
- `tests/test_monitor_exit_guard.py::test_monitor_exit_cooldown_suppresses_duplicate_sell_intents` → SAME SOURCE_PATH / SAME callable; KEEP_TEST_ORACLE. Existing test fixture names and assertions must remain stable.

Test discovery requires root tests/test_*.py, tests/apps/api fixture scope, CI patterns, golden hashes. There is **no new production function body to extract** from these RFs. Correct tests/fixtures are one-line KEEP_OK with path, reason, blob; no rerun for unchanged file.

## Every owned file: source to target and decision

| SOURCE | TARGET | blob / bytes | reason |
|---|---|---|---|
| `tests/p15_strategist_s5_cases.py` | `tests/p15_strategist_s5_cases.py` | `ef66859f5e48` / 5726 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_check_monitor_gate_patterns.py` | `tests/test_check_monitor_gate_patterns.py` | `421712927a3a` / 3904 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_commander_contract.py` | `tests/test_commander_contract.py` | `85019c322b1c` / 3204 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_commander_env_migration_phase1.py` | `tests/test_commander_env_migration_phase1.py` | `bda05f38da7a` / 10109 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_commander_env_migration_phase2.py` | `tests/test_commander_env_migration_phase2.py` | `b7661aec2889` / 8732 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_commander_memory_policy.py` | `tests/test_commander_memory_policy.py` | `e566b269e87f` / 13575 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_commander_post_scanner_context.py` | `tests/test_commander_post_scanner_context.py` | `42e9c962c832` / 2036 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_intraday_monitor_signals.py` | `tests/test_intraday_monitor_signals.py` | `abf157bfa16c` / 89986 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m11_2_scanner.py` | `tests/test_m11_2_scanner.py` | `f87b8778e1a8` / 749 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m12_strategist_hook.py` | `tests/test_m12_strategist_hook.py` | `d9430c18590f` / 536 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m17_monitor_emits_intent_only.py` | `tests/test_m17_monitor_emits_intent_only.py` | `74ee86b328e5` / 812 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m18_4_scanner_sentiment_weighting.py` | `tests/test_m18_4_scanner_sentiment_weighting.py` | `cb6fcf4d114b` / 1798 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m18_scanner_global_sentiment_contract.py` | `tests/test_m18_scanner_global_sentiment_contract.py` | `4c2f39525435` / 1377 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m21_commander_runtime_entry.py` | `tests/test_m21_commander_runtime_entry.py` | `889ed4686578` / 188918 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m21_graph_spine_parity.py` | `tests/test_m21_graph_spine_parity.py` | `4b47d0b6f5c8` / 3935 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m22_graph_hydration_wiring.py` | `tests/test_m22_graph_hydration_wiring.py` | `09a486b4bf2b` / 3525 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m22_skill_native_scanner_monitor.py` | `tests/test_m22_skill_native_scanner_monitor.py` | `02ca10bd3a30` / 10936 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m23_4_commander_incident_cooldown_routing.py` | `tests/test_m23_4_commander_incident_cooldown_routing.py` | `3a4bcda97b3a` / 3603 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m23_7_commander_resilience_ops_script.py` | `tests/test_m23_7_commander_resilience_ops_script.py` | `e07070ee427c` / 4146 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m29_2_scanner_feature_integration.py` | `tests/test_m29_2_scanner_feature_integration.py` | `74590409ddee` / 2475 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m29_3_monitor_exit_policy.py` | `tests/test_m29_3_monitor_exit_policy.py` | `20b8bcc4c645` / 25619 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m29_4_monitor_position_sizing.py` | `tests/test_m29_4_monitor_position_sizing.py` | `b01b1fc60b7b` / 5769 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m30_3_post_golive_monitoring_policy.py` | `tests/test_m30_3_post_golive_monitoring_policy.py` | `6af5098ae7d6` / 3145 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_monitor_candidate_cascade.py` | `tests/test_monitor_candidate_cascade.py` | `576ac37c5cde` / 12100 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_monitor_cash_truth.py` | `tests/test_monitor_cash_truth.py` | `13ff89af9fe7` / 299 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_monitor_directional_edge.py` | `tests/test_monitor_directional_edge.py` | `03c2ef3910e1` / 7393 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_monitor_evidence_ast.py` | `tests/test_monitor_evidence_ast.py` | `6895c30ce63d` / 1567 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_monitor_exit_guard.py` | `tests/test_monitor_exit_guard.py` | `c47099961381` / 213847 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_monitor_exit_price_freshness.py` | `tests/test_monitor_exit_price_freshness.py` | `1ffc047be5e2` / 7504 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_monitor_fallback_quality_gate.py` | `tests/test_monitor_fallback_quality_gate.py` | `4768a93c1a6a` / 3309 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_monitor_feedback_adaptive_policy.py` | `tests/test_monitor_feedback_adaptive_policy.py` | `7ff445e6cedd` / 11888 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_monitor_memory_bias.py` | `tests/test_monitor_memory_bias.py` | `eea30fc765c2` / 13936 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_monitor_minute_ohlcv_resilience.py` | `tests/test_monitor_minute_ohlcv_resilience.py` | `0dc245be059b` / 834 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_monitor_noop_attribution.py` | `tests/test_monitor_noop_attribution.py` | `8c6bfabd2d89` / 4510 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_monitor_price_source_resolution.py` | `tests/test_monitor_price_source_resolution.py` | `961187ae11c1` / 713 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p152_ai_facade_market_scanner_labels.py` | `tests/test_p152_ai_facade_market_scanner_labels.py` | `79d8b382c420` / 3703 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p152_monitor_context_owner.py` | `tests/test_p152_monitor_context_owner.py` | `b479329960a8` / 2741 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p152_monitor_diagnostics_owner.py` | `tests/test_p152_monitor_diagnostics_owner.py` | `a0ef101c5ff4` / 1539 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p152_monitor_entry_review_owner.py` | `tests/test_p152_monitor_entry_review_owner.py` | `9a590ffe7f95` / 2154 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p152_monitor_policy_bullets_owner.py` | `tests/test_p152_monitor_policy_bullets_owner.py` | `56e43ff67dbb` / 1376 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p152_monitor_trace_wrappers.py` | `tests/test_p152_monitor_trace_wrappers.py` | `08d1808fac17` / 2236 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p15_b_commander_monitor_boundaries.py` | `tests/test_p15_b_commander_monitor_boundaries.py` | `0bf3dcf867a2` / 6652 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p15_b_commander_monitor_pure_parity.py` | `tests/test_p15_b_commander_monitor_pure_parity.py` | `75fc54f2d928` / 10997 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p15_commander_pure_v1_admission.py` | `tests/test_p15_commander_pure_v1_admission.py` | `3b46831ecdcd` / 9612 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p15_strategist_contract_parsing_move.py` | `tests/test_p15_strategist_contract_parsing_move.py` | `19efe4a8cd68` / 13312 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p15_strategist_s5_helper_moves.py` | `tests/test_p15_strategist_s5_helper_moves.py` | `f70281e541bb` / 18695 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p162_scanner_node_contract_freeze.py` | `tests/test_p162_scanner_node_contract_freeze.py` | `adb011d03d02` / 14055 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p163_monitor_contract_freeze.py` | `tests/test_p163_monitor_contract_freeze.py` | `8e72f8ddb834` / 7449 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p164_strategist_contract_freeze.py` | `tests/test_p164_strategist_contract_freeze.py` | `df5367b9c0c1` / 7782 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p165_commander_ui_contract_freeze.py` | `tests/test_p165_commander_ui_contract_freeze.py` | `f401f539ab26` / 7953 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p167_v2053_scanner_context_migration.py` | `tests/test_p167_v2053_scanner_context_migration.py` | `4fafef4ae4ec` / 6726 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p171_v3055_scanner_projection_migration.py` | `tests/test_p171_v3055_scanner_projection_migration.py` | `2c948370f2ac` / 9924 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p172_strategist_s1_057_migration.py` | `tests/test_p172_strategist_s1_057_migration.py` | `26fa5bfd5957` / 8008 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p172_v4056_scanner_policy_migration.py` | `tests/test_p172_v4056_scanner_policy_migration.py` | `f436fbcf147f` / 9230 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_q9_scanner_quality.py` | `tests/test_q9_scanner_quality.py` | `975d13bae4f6` / 2857 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_scanner_alignment_root_cause.py` | `tests/test_scanner_alignment_root_cause.py` | `008ba6cabd9e` / 5494 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_scanner_bias_integration.py` | `tests/test_scanner_bias_integration.py` | `96dc6927a871` / 3754 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_scanner_candidate_risk.py` | `tests/test_scanner_candidate_risk.py` | `72373d00df9a` / 3995 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_scanner_fallback_policy.py` | `tests/test_scanner_fallback_policy.py` | `eb5d03ad8c3f` / 12846 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_scanner_feature_hydration.py` | `tests/test_scanner_feature_hydration.py` | `809f7b8a2d08` / 8124 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_scanner_live_symbol_filter.py` | `tests/test_scanner_live_symbol_filter.py` | `8d461e2c96a8` / 943 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_scanner_memory_bias.py` | `tests/test_scanner_memory_bias.py` | `c8fcd9daaa33` / 8173 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_scanner_monitor_compatibility.py` | `tests/test_scanner_monitor_compatibility.py` | `505454fea667` / 23765 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_scanner_policy_overlay.py` | `tests/test_scanner_policy_overlay.py` | `6cdf91108ea0` / 17670 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_scanner_practical_selection_engine.py` | `tests/test_scanner_practical_selection_engine.py` | `97ea007ae717` / 7979 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_scanner_quote_hydration_runtime.py` | `tests/test_scanner_quote_hydration_runtime.py` | `2f89453038d5` / 2174 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_scanner_rank_plumbing_fix.py` | `tests/test_scanner_rank_plumbing_fix.py` | `377cd5426c5a` / 12482 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_scanner_strategy_frame_integration.py` | `tests/test_scanner_strategy_frame_integration.py` | `4e74858cb473` / 27777 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_scanner_universe_candidate_metadata.py` | `tests/test_scanner_universe_candidate_metadata.py` | `d7814b1d53fb` / 1542 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_shared_strategist_contracts.py` | `tests/test_shared_strategist_contracts.py` | `3d79529ea12e` / 8218 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_strategist_explanation_contract.py` | `tests/test_strategist_explanation_contract.py` | `4ca8c59bfe1c` / 10467 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_strategist_frame_llm_integration.py` | `tests/test_strategist_frame_llm_integration.py` | `efd9c438915a` / 97383 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_strategist_input_quality_risk_off.py` | `tests/test_strategist_input_quality_risk_off.py` | `6934e842a008` / 1014 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_strategist_llm_summary.py` | `tests/test_strategist_llm_summary.py` | `1fdceb50a7ba` / 12692 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_strategist_output_schema.py` | `tests/test_strategist_output_schema.py` | `40da1bc574ab` / 8945 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_strategist_reasoning_quality.py` | `tests/test_strategist_reasoning_quality.py` | `01240fa94e4b` / 23130 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_strategist_refresh_decision.py` | `tests/test_strategist_refresh_decision.py` | `4d3b409f228c` / 4661 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_work_monitor_annotation_views.py` | `tests/test_work_monitor_annotation_views.py` | `b56336e49d6a` / 4839 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_work_monitor_body_views.py` | `tests/test_work_monitor_body_views.py` | `eb5f9a270456` / 5202 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_work_monitor_continuous.py` | `tests/test_work_monitor_continuous.py` | `8a881ad6c99d` / 7757 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_work_monitor_exit_labels.py` | `tests/test_work_monitor_exit_labels.py` | `29fc0ee1dd4e` / 4493 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_work_monitor_m9_native.py` | `tests/test_work_monitor_m9_native.py` | `b876040777da` / 3118 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_work_monitor_m9_offline.py` | `tests/test_work_monitor_m9_offline.py` | `38965b74a0a3` / 12196 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_work_monitor_observation_views.py` | `tests/test_work_monitor_observation_views.py` | `1efbfc9dc72e` / 5525 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_work_monitor_policy_trace_views.py` | `tests/test_work_monitor_policy_trace_views.py` | `80ae52915f7f` / 7484 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_work_monitor_retained_boundary.py` | `tests/test_work_monitor_retained_boundary.py` | `f4d63d9706e5` / 1496 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_work_monitor_role_contracts.py` | `tests/test_work_monitor_role_contracts.py` | `a5250ec49814` / 9408 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_work_monitor_scope_accounting.py` | `tests/test_work_monitor_scope_accounting.py` | `076bee7dad1f` / 4141 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |

## Acceptance and delivery

- One-line source blob and correct test owner/path is KEEP_OK; test/fixture refactoring itself not a code-body MOVE metric.
- A/B do not read this RF file. C03 decides KEEP from file/consumers, and adds only new genuine source functions into C01/C02 text when needed.
- No modification to test assertions, skips, xfails, golden snapshots or staged deployment requirements as a shortcut to PASS. Historical prior tests retained; not rerun for identical blob.
