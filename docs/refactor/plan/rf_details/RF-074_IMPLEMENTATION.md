# RF-074 — T09 tests/fixture target and protected callable identity

- SOURCE integration/p1.5@a7654f389fddbc2829f005ab247a96bf295228d8; CSV b46bcb1f29ed3c0a133b059d690173c195c81bf9. Actor Claude A (tests code only, no oracle edits); peer read-only. 75 exclusive historical paths.

Reporter/UI: test_trade_report_ai.py 6204 LOC, 130 tests. Root test discovery/fixtures are authoritative; no cosmetic split.

## Callable mapping: KEEP, not MOVE

- `tests/test_trade_report_ai.py::test_build_ai_trade_report_compact_input_prefers_section_seeds_for_aux_sections` → SAME SOURCE_PATH / SAME callable; KEEP_TEST_ORACLE. Existing test fixture names and assertions must remain stable.
- `tests/test_trade_report_ai.py::test_build_deterministic_trade_report_adds_truth_surface` → SAME SOURCE_PATH / SAME callable; KEEP_TEST_ORACLE. Existing test fixture names and assertions must remain stable.

Test discovery requires root tests/test_*.py, tests/apps/api fixture scope, CI patterns, golden hashes. There is **no new production function body to extract** from these RFs. Correct tests/fixtures are one-line KEEP_OK with path, reason, blob; no rerun for unchanged file.

## Every owned file: source to target and decision

| SOURCE | TARGET | blob / bytes | reason |
|---|---|---|---|
| `tests/test_agent_pipeline_trace_report.py` | `tests/test_agent_pipeline_trace_report.py` | `a2fe99d63ef7` / 31273 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_benchmark_operator_visibility_memory.py` | `tests/test_benchmark_operator_visibility_memory.py` | `73a3d344752d` / 2756 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_check_reporter_upgrade_regression.py` | `tests/test_check_reporter_upgrade_regression.py` | `15138ccc8815` / 3793 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_check_reports_trades_health.py` | `tests/test_check_reports_trades_health.py` | `68dc4024678c` / 6320 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_check_trade_report_runtime_regression.py` | `tests/test_check_trade_report_runtime_regression.py` | `49a86ae3be4a` / 10407 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_controlled_mock_lane_report.py` | `tests/test_controlled_mock_lane_report.py` | `f79163c91111` / 3558 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_daily_report.py` | `tests/test_daily_report.py` | `48b39c669e62` / 29438 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_evaluation_lens_report.py` | `tests/test_evaluation_lens_report.py` | `22d549570e53` / 6302 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_generate_metrics_report.py` | `tests/test_generate_metrics_report.py` | `1a76aa1451ac` / 26315 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_generate_ops_diagnostic_report.py` | `tests/test_generate_ops_diagnostic_report.py` | `a03a8059abb2` / 6127 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_intraday_trade_reports.py` | `tests/test_intraday_trade_reports.py` | `2d66ca3a47fd` / 40160 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_kiwoom_history_receipt_lifecycle.py` | `tests/test_kiwoom_history_receipt_lifecycle.py` | `d7e7a2d2331f` / 15632 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_live_execution_bundle_report.py` | `tests/test_live_execution_bundle_report.py` | `46de2909ae1e` / 173419 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_live_execution_bundle_report_runtime_recovery.py` | `tests/test_live_execution_bundle_report_runtime_recovery.py` | `c054c0e6b7bd` / 8417 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_live_execution_report_context.py` | `tests/test_live_execution_report_context.py` | `d0821bafdca8` / 606 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m13_eod_report.py` | `tests/test_m13_eod_report.py` | `5602fb001b75` / 2580 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m19_6_llm_daily_report.py` | `tests/test_m19_6_llm_daily_report.py` | `889749423627` / 6316 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m23_6_operator_intervention_resume.py` | `tests/test_m23_6_operator_intervention_resume.py` | `de938f561e08` / 2749 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m23_9_commander_resilience_metrics_report.py` | `tests/test_m23_9_commander_resilience_metrics_report.py` | `5a6cff0f0469` / 3481 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m25_3_alert_reporting_closeout.py` | `tests/test_m25_3_alert_reporting_closeout.py` | `b7f57d39992f` / 2297 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m27_5_portfolio_guard_metrics_report.py` | `tests/test_m27_5_portfolio_guard_metrics_report.py` | `512717d0ad9e` / 2304 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_m29_5_monitor_metrics_report.py` | `tests/test_m29_5_monitor_metrics_report.py` | `f0992cf3903e` / 4471 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_operator_summary_broker_day_reconciliation.py` | `tests/test_operator_summary_broker_day_reconciliation.py` | `1e31118f25c5` / 5005 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_operator_summary_memory_linkage.py` | `tests/test_operator_summary_memory_linkage.py` | `a8d6da06e2c0` / 4735 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_operator_summary_mining.py` | `tests/test_operator_summary_mining.py` | `73dd18a60fae` / 3711 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_operator_summary_refresh.py` | `tests/test_operator_summary_refresh.py` | `3873fd70a7a9` / 2308 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_operator_summary_reports.py` | `tests/test_operator_summary_reports.py` | `2efe3ab833ef` / 48860 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_operator_ui.py` | `tests/test_operator_ui.py` | `b3cdc94ee1cf` / 128647 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_operator_ui_data_access_phase2.py` | `tests/test_operator_ui_data_access_phase2.py` | `f0e7e7c57973` / 38694 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_operator_visibility_reports.py` | `tests/test_operator_visibility_reports.py` | `3c6e82b06c0f` / 35072 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p152_direct_story_owner.py` | `tests/test_p152_direct_story_owner.py` | `76daf6448b5c` / 1085 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p152_markdown_clean_operator_labels_owners.py` | `tests/test_p152_markdown_clean_operator_labels_owners.py` | `359e300665da` / 3665 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p152_operator_language_owner.py` | `tests/test_p152_operator_language_owner.py` | `680ab375de76` / 1412 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p152_operator_phrase_owners.py` | `tests/test_p152_operator_phrase_owners.py` | `dc85959812b8` / 1697 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p152_story_facade_compatible_owners.py` | `tests/test_p152_story_facade_compatible_owners.py` | `64b25cd5850a` / 4203 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p152_story_facade_contract_owners.py` | `tests/test_p152_story_facade_contract_owners.py` | `ced4ce78d968` / 2911 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p152_story_facade_human_owners.py` | `tests/test_p152_story_facade_human_owners.py` | `1ae6b205d8da` / 3183 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p152_story_reasoning_owner.py` | `tests/test_p152_story_reasoning_owner.py` | `255303cd07fb` / 2274 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p153_operator_ui_moved_bodies.py` | `tests/test_p153_operator_ui_moved_bodies.py` | `4fcbac6b6c83` / 9725 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p15_b_operator_brief_boundaries.py` | `tests/test_p15_b_operator_brief_boundaries.py` | `75c0850453fb` / 7103 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p15_b_operator_brief_pure_parity.py` | `tests/test_p15_b_operator_brief_pure_parity.py` | `2b104e85ebd1` / 9732 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p15_operator_run_detail_projection.py` | `tests/test_p15_operator_run_detail_projection.py` | `8298fad7ae57` / 13383 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_p15_operator_trade_index_projection.py` | `tests/test_p15_operator_trade_index_projection.py` | `db70b4575b17` / 8465 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_quant_tactic_report.py` | `tests/test_quant_tactic_report.py` | `61f9c18f122b` / 9786 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_report_maintenance.py` | `tests/test_report_maintenance.py` | `d40ad9eb82bb` / 4613 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_report_metadata_alignment.py` | `tests/test_report_metadata_alignment.py` | `070f61e56ff7` / 7627 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_report_trades_continuity.py` | `tests/test_report_trades_continuity.py` | `8deed3d744d3` / 1775 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_reporter_agent_trade_entrypoint.py` | `tests/test_reporter_agent_trade_entrypoint.py` | `b4d3054a38e8` / 2540 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_reporter_analysis_report.py` | `tests/test_reporter_analysis_report.py` | `0f8049d81f4d` / 26595 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_reporter_commander_hooks.py` | `tests/test_reporter_commander_hooks.py` | `9e0949f92640` / 5711 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_reporter_feedback.py` | `tests/test_reporter_feedback.py` | `bf7695542688` / 15399 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_reporter_node.py` | `tests/test_reporter_node.py` | `03d65a937fb1` / 2790 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_reporter_script_wrappers.py` | `tests/test_reporter_script_wrappers.py` | `0a1c846b76e0` / 6509 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_reporter_service.py` | `tests/test_reporter_service.py` | `359434d14873` / 9115 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_reporting_provenance_preference.py` | `tests/test_reporting_provenance_preference.py` | `c691080c3341` / 6343 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_reporting_relocation_imports.py` | `tests/test_reporting_relocation_imports.py` | `39703f9ddb45` / 1939 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_run_ai_trade_report_batch.py` | `tests/test_run_ai_trade_report_batch.py` | `57a6f127682f` / 28088 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_run_operator_brief_batch.py` | `tests/test_run_operator_brief_batch.py` | `b264f014558c` / 359 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_shared_reporter_facade_guard.py` | `tests/test_shared_reporter_facade_guard.py` | `85e822b13bb4` / 4477 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_single_trade_report.py` | `tests/test_single_trade_report.py` | `506baa7be181` / 14098 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_strategist_quant_context_report.py` | `tests/test_strategist_quant_context_report.py` | `269525221a75` / 4676 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_symbol_trade_report.py` | `tests/test_symbol_trade_report.py` | `6970af20dbf6` / 20616 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_trade_explain_report.py` | `tests/test_trade_explain_report.py` | `367eac531676` / 21699 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_trade_report_ai.py` | `tests/test_trade_report_ai.py` | `abceef712416` / 294281 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_trade_report_ai_separated_adapter.py` | `tests/test_trade_report_ai_separated_adapter.py` | `eee38a8208b4` / 2390 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_trade_story_pipeline_enrichment.py` | `tests/test_trade_story_pipeline_enrichment.py` | `431ea2f0f6b7` / 82879 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_work_reporter_r10_artifact_parity.py` | `tests/test_work_reporter_r10_artifact_parity.py` | `980e2f3fe8af` / 9705 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_work_reporter_r10_retained_io_contracts.py` | `tests/test_work_reporter_r10_retained_io_contracts.py` | `6332d2650693` / 14337 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_work_reporter_r11_repo_hygiene.py` | `tests/test_work_reporter_r11_repo_hygiene.py` | `dbfc9940f47a` / 7145 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_work_reporter_r4_facade_bodies.py` | `tests/test_work_reporter_r4_facade_bodies.py` | `3c8821e9c544` / 12433 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_work_reporter_r8_read_contracts.py` | `tests/test_work_reporter_r8_read_contracts.py` | `851bff2fef23` / 4946 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_work_reporter_r8_read_via_callback_parity.py` | `tests/test_work_reporter_r8_read_via_callback_parity.py` | `10eddc7dc323` / 9075 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_work_reporter_renderer_bytes.py` | `tests/test_work_reporter_renderer_bytes.py` | `f17f475cb849` / 3797 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/test_work_reporter_seed_migration.py` | `tests/test_work_reporter_seed_migration.py` | `cabcecfeeaf8` / 32261 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |
| `tests/uef9_synthetic_reports.py` | `tests/uef9_synthetic_reports.py` | `6fbbbae5d3fa` / 2301 | KEEP_TEST_DISCOVERY: preserve fixture namespace, test identity, CI glob |

## Acceptance and delivery

- One-line source blob and correct test owner/path is KEEP_OK; test/fixture refactoring itself not a code-body MOVE metric.
- A/B do not read this RF file. C03 decides KEEP from file/consumers, and adds only new genuine source functions into C01/C02 text when needed.
- No modification to test assertions, skips, xfails, golden snapshots or staged deployment requirements as a shortcut to PASS. Historical prior tests retained; not rerun for identical blob.
