# Scripts Bulk Migration — 2026-10-15

## Result

- Branch `refactor/agentra-target-tree`, PR #5. Base `b8d36f7b6e0b62fb91f0cb8e637fa6dbc5faad12`.
- Reused `2026-10-15_scripts_config_inventory.json`; processed all **157** Research/Diagnostics/Maintenance candidates without re-inventorying the checkout.
- **138 implementations relocated**, **19 held**. Research **53**, Diagnostics **73**, Maintenance **12**.
- 151 Python candidates: all baseline imports passed, 148 baseline CLI checks passed. Six Windows files considered and held because this Linux environment cannot validate Windows/Scheduler behavior.
- 48 Operations and 2 original T4-owned Scripts files unchanged. Config 8 files, protected agent/runtime/broker/guard code, deployments and Reporting Batch 1/2 untouched. Reporting Batch 3 remains paused.
- Physical Scripts files: 216 → 357 (138 canonical implementation files and 3 package markers added; old CLIs retained). No `operations/` boilerplate or code moves.

## Compatibility and wrapper cost

- All moved files have an existing executable `__main__` CLI. Old locations are public manual/module CLI contracts; no path-retirement policy was provided. 109 have static incoming references; 29 have no observed static caller, which is insufficient to remove their manual CLI.
- Retained **138 new thin wrappers**, 14 lines each (**1,932 lines**). This is a deliberate compatibility cost, not a claim that the root directory is empty. Existing 3 example wrappers remain, giving **141 root compatibility wrappers** in total.
- CLI wrappers use `runpy.run_module(..., run_name="__main__")` so original main-guard behavior and argv handling survive, including imported main functions. Import wrappers alias the canonical module object, preserving public/private globals and monkeypatch locations.
- Root Python files: **42 with local function/class implementations**, **8 existing forwarding entrypoints**, **141 compatibility wrappers**, **1 package marker**. **20 non-Python Windows/shell files** remain untouched. Definitions are AST-based to avoid calling pre-existing forwarding launchers full implementations.
- Root/path changes only: 128 recognized repo-root expressions adjusted one level deeper; 11 scripts without an existing sys.path bootstrap receive a 7-line direct-execution bootstrap. Three import-free package markers added.
- Reversing only these recorded bootstrap edits reproduces original Git blob bytes for all **138** files (including BOM preservation). Business logic changes: **0 lines**. Existing call sites, CLI options and policy values are unchanged.

## Validation

- AST syntax: all 138 canonical implementations and 138 wrappers parse. Original 151 Python candidates parsed before mutation.
- Fresh-process old-first and new-first imports: **276 checks passed**. Each verifies module identity, public/private local callable exports, the signatures of **505 functions/classes**, and any existing ROOT/REPO_ROOT/PROJECT_ROOT value against the original source compiled in an isolated module.
- Repository-CWD CLI `--help`: **552 parity checks** (138 × old/new × direct/module), including identical exit code, stdout and stderr against the actual pre-migration script execution.
- Outside-CWD direct execution: **276 parity checks** (138 × old/new), with only the safety guard on PYTHONPATH, proving repository-root bootstrap works without a repo PYTHONPATH binding.
- Total accepted CLI parity checks: **828 passed**. Help/static/import is intentional for commands that can write artifacts or execute operational workflows; no claim of live research/production execution.
- Existing relevant pytest selected from the prior inventory references: **74 files / 300 tests passed**, no failures/skips/errors. These exercise real local functions and CLI error cases with isolated fixtures. The broader initial inventory selection also exposed UEF5 integration limitations below; affected scripts were held rather than changing protected libraries/tests.
- Guard blocks Python network calls and requests/curl_cffi transport, and forbids writes outside `/tmp/agentra-bulk`. The final pytest mode permits test subprocesses but preserves network and write guards. All tests and validation artifact writes occur under temp. No order submission, external data collection, or operational file writes.
- Initial guard setup needed two corrections: allow `/dev/null` and resolve fd-relative unlink paths against `/proc/self/fd/<dir_fd>`; these were harness defects, not application changes. Final 300-test run passed with protections retained.
- Successful pytest scratch trees/cache and validation runtime directories are cleaned after recording results; summarized evidence remains in this committed manifest/report.
- Full repository suite, live CLI main paths, Windows Scheduler and Docker execution are not run. No assertions or repository tests are disabled or edited.

## T4 / remote safety

- Initial T4 `8acedae23e64c11b958556e7835b4ebf5e404e73`; rechecked latest T4 `c61caab0a94d6e40b015709b720d0266cf0f1d9a`. Merge base `2f95bba429636ee15ae9a399cc4ff7c4e6dcd5cb`.
- Concurrent T4 changes were limited to new strategist refactor tools and contract fixtures/tests; moved old/new path intersection remains zero. No T4 files checked out or copied.
- T4 code conflicts: **0**. The only permitted shared paths are append-only UI patch-note JSON/Markdown. Future integration must preserve both branches’ histories and check duplicate entries.
- Remote target branch was still the base HEAD before final documentation. Push uses the same existing branch without force, merge, Ready transition or auto-merge. Draft/manual-review workflow remains unchanged; GitHub API metadata access is unavailable, so isDraft is not independently revalidated.

## Held candidates (19; originals remain byte-identical)

| Original path | Category | Actual blocking evidence |
| --- | --- | --- |
| `scripts/build_uef5_clean_evidence_coverage.py` | RESEARCH | Related UEF5 integration tests require absent reports/evaluation/opportunity_engine_shadow and flag existing production imports in untouched libs; preserve original file until baseline/live-artifact validation is available. CLI/import passed but integration gate is unresolved. |
| `scripts/cleanup_pytest_artifacts.cmd` | MAINTENANCE | Windows batch/PowerShell launcher: no Windows interpreter or scheduler available; retain original path and sibling/working-directory contract |
| `scripts/cleanup_pytest_artifacts.ps1` | MAINTENANCE | Windows batch/PowerShell launcher: no Windows interpreter or scheduler available; retain original path and sibling/working-directory contract |
| `scripts/cleanup_pytest_artifacts.py` | MAINTENANCE | Ignores --help and executes deletion logic. Retain actual cleanup entrypoint rather than certify a no-op against current filesystem. |
| `scripts/restart_live_session.bat` | MAINTENANCE | Windows batch/PowerShell launcher: no Windows interpreter or scheduler available; retain original path and sibling/working-directory contract |
| `scripts/restart_live_session.ps1` | MAINTENANCE | Windows batch/PowerShell launcher: no Windows interpreter or scheduler available; retain original path and sibling/working-directory contract |
| `scripts/run_baseline_btc_woori_tech.py` | RESEARCH | Invoked by start_trading_day.py and start_q12_preopen.ps1; live scheduled research producer remains in place. |
| `scripts/run_baseline_samsung_hynix.py` | RESEARCH | Invoked by start_trading_day.py and referenced by Windows stop/start task process matching; preserve operational implementation path. |
| `scripts/run_closeout_maintenance.bat` | MAINTENANCE | Windows batch/PowerShell launcher: no Windows interpreter or scheduler available; retain original path and sibling/working-directory contract |
| `scripts/run_closeout_maintenance.py` | MAINTENANCE | run_closeout_maintenance.bat / run_mock_exam_closeout.bat scheduled maintenance chain; preserve implementation path. |
| `scripts/run_daily_uef_evaluation.py` | RESEARCH | Windows daily_uef_evaluation_task.xml and automatic daily evaluation contract; retain scheduled entrypoint implementation. |
| `scripts/run_m15_matrix.py` | DIAGNOSTICS | Baseline import/CLI validation failed before migration: ^   File "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/subprocess.py", line 1026, in __init__     self._execute_child(args, executable, preexec_fn, close_fds,   File "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/subprocess.py", line 1823, in _execute_child     sys.audit("subprocess.Popen", executable, args, cwd, env)   File "/tmp/agentra-bulk/guard/sitecustomize.py", line 18, in audit     deny(event+' forbidden')   File "/tmp/agentra-bulk/guard/sitecustomize.py", line 7, in deny     raise MigrationSafetyError(reason) sitecustomize.MigrationSafetyError: subprocess.Popen forbidden  |
| `scripts/run_m25_closeout_check.py` | DIAGNOSTICS | Imported by operational run_m25_ops_batch.py; leave operational batch dependency untouched. |
| `scripts/run_opening_rank1_deep_dive.py` | RESEARCH | Baseline import/CLI validation failed before migration: ^   File "/workspace/agentra/libs/research/opening_rank1_deep_dive/pipeline.py", line 182, in run_opening_rank1_deep_dive     result_analysis = analyze(cases)                       ^^^^^^^^^^^^^^   File "/workspace/agentra/libs/research/opening_rank1_deep_dive/analysis.py", line 375, in analyze     "outlier_sensitivity": outlier_sensitivity(enriched),                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^   File "/workspace/agentra/libs/research/opening_rank1_deep_dive/analysis.py", line 136, in outlier_sensitivity     "top1_return_pct": round(descending[0], 4),                              ~~~~~~~~~~^^^ IndexError: list index out of range  |
| `scripts/run_opportunity_engine_shadow.py` | RESEARCH | Invoked by start_trading_day.py and Windows process matching; preserve operational implementation path. |
| `scripts/run_pytest.py` | DIAGNOSTICS | Baseline import/CLI validation failed before migration: Traceback (most recent call last):   File "/workspace/agentra/scripts/run_pytest.py", line 27, in <module>     raise SystemExit(main(sys.argv[1:]))                      ^^^^^^^^^^^^^^^^^^   File "/workspace/agentra/scripts/run_pytest.py", line 12, in main     raise FileNotFoundError(f"Python executable not found: {python_exe}") FileNotFoundError: Python executable not found: /workspace/agentra/venv/Scripts/python.exe  |
| `scripts/run_uef5_historical_recompute.py` | RESEARCH | Related UEF5 integration tests require absent reports/evaluation/opportunity_engine_shadow and flag existing production imports in untouched libs; preserve original file until baseline/live-artifact validation is available. CLI/import passed but integration gate is unresolved. |
| `scripts/stop_operator_ui.ps1` | MAINTENANCE | Windows batch/PowerShell launcher: no Windows interpreter or scheduler available; retain original path and sibling/working-directory contract |
| `scripts/verify_uef_freeze_manifest.py` | DIAGNOSTICS | Related UEF5 integration tests require absent reports/evaluation/opportunity_engine_shadow and flag existing production imports in untouched libs; preserve original file until baseline/live-artifact validation is available. CLI/import passed but integration gate is unresolved. |

The three UEF5 holds passed import/CLI checks, but their reference suites require absent `reports/evaluation/opportunity_engine_shadow` history and flag production imports in untouched libs. No synthetic production dataset, contract relaxation or unrelated code fix was introduced. Frozen verification itself passed; integration readiness is not claimed.

## Moved implementations (138)

| Old public CLI/import (wrapper retained) | New canonical path | Category |
| --- | --- | --- |
| `scripts/analyze_entry_blockers.py` | `scripts/diagnostics/analyze_entry_blockers.py` | DIAGNOSTICS |
| `scripts/benchmark_operator_visibility_memory.py` | `scripts/diagnostics/benchmark_operator_visibility_memory.py` | DIAGNOSTICS |
| `scripts/check_alert_policy_v1.py` | `scripts/diagnostics/check_alert_policy_v1.py` | DIAGNOSTICS |
| `scripts/check_audit_trail_completeness.py` | `scripts/diagnostics/check_audit_trail_completeness.py` | DIAGNOSTICS |
| `scripts/check_daily_uef_run_status.py` | `scripts/diagnostics/check_daily_uef_run_status.py` | DIAGNOSTICS |
| `scripts/check_log_archive_integrity.py` | `scripts/diagnostics/check_log_archive_integrity.py` | DIAGNOSTICS |
| `scripts/check_metrics_schema_v1.py` | `scripts/diagnostics/check_metrics_schema_v1.py` | DIAGNOSTICS |
| `scripts/check_monitor_gate_patterns.py` | `scripts/diagnostics/check_monitor_gate_patterns.py` | DIAGNOSTICS |
| `scripts/check_phase_5_2_5_3_runtime_health.py` | `scripts/diagnostics/check_phase_5_2_5_3_runtime_health.py` | DIAGNOSTICS |
| `scripts/check_profitability_recovery_day1.py` | `scripts/diagnostics/check_profitability_recovery_day1.py` | DIAGNOSTICS |
| `scripts/check_q9_q12_readiness.py` | `scripts/diagnostics/check_q9_q12_readiness.py` | DIAGNOSTICS |
| `scripts/check_real_execution_preflight.py` | `scripts/diagnostics/check_real_execution_preflight.py` | DIAGNOSTICS |
| `scripts/check_reporter_upgrade_regression.py` | `scripts/diagnostics/check_reporter_upgrade_regression.py` | DIAGNOSTICS |
| `scripts/check_reports_trades_health.py` | `scripts/diagnostics/check_reports_trades_health.py` | DIAGNOSTICS |
| `scripts/check_runtime_profile.py` | `scripts/diagnostics/check_runtime_profile.py` | DIAGNOSTICS |
| `scripts/check_trade_report_runtime_regression.py` | `scripts/diagnostics/check_trade_report_runtime_regression.py` | DIAGNOSTICS |
| `scripts/clean_evaluation_test_contamination.py` | `scripts/maintenance/clean_evaluation_test_contamination.py` | MAINTENANCE |
| `scripts/compact_q9_decision_windows.py` | `scripts/maintenance/compact_q9_decision_windows.py` | MAINTENANCE |
| `scripts/daily_profitability_scorecard.py` | `scripts/research/daily_profitability_scorecard.py` | RESEARCH |
| `scripts/generate_m28_launch_templates.py` | `scripts/diagnostics/generate_m28_launch_templates.py` | DIAGNOSTICS |
| `scripts/generate_m28_registration_helpers.py` | `scripts/diagnostics/generate_m28_registration_helpers.py` | DIAGNOSTICS |
| `scripts/generate_ops_diagnostic_report.py` | `scripts/diagnostics/generate_ops_diagnostic_report.py` | DIAGNOSTICS |
| `scripts/organize_llm_reports.py` | `scripts/maintenance/organize_llm_reports.py` | MAINTENANCE |
| `scripts/query_commander_resilience_events.py` | `scripts/diagnostics/query_commander_resilience_events.py` | DIAGNOSTICS |
| `scripts/query_intent_state_store.py` | `scripts/diagnostics/query_intent_state_store.py` | DIAGNOSTICS |
| `scripts/query_m25_notification_events.py` | `scripts/diagnostics/query_m25_notification_events.py` | DIAGNOSTICS |
| `scripts/query_strategist_llm_events.py` | `scripts/diagnostics/query_strategist_llm_events.py` | DIAGNOSTICS |
| `scripts/query_trade_reason_chain.py` | `scripts/diagnostics/query_trade_reason_chain.py` | DIAGNOSTICS |
| `scripts/reconcile_intent_state_store.py` | `scripts/maintenance/reconcile_intent_state_store.py` | MAINTENANCE |
| `scripts/reconstruct_incident_timeline.py` | `scripts/diagnostics/reconstruct_incident_timeline.py` | DIAGNOSTICS |
| `scripts/repair_q9_day_artifacts.py` | `scripts/maintenance/repair_q9_day_artifacts.py` | MAINTENANCE |
| `scripts/repair_trade_symbol_context.py` | `scripts/maintenance/repair_trade_symbol_context.py` | MAINTENANCE |
| `scripts/run_agent_effectiveness_scorecard.py` | `scripts/research/run_agent_effectiveness_scorecard.py` | RESEARCH |
| `scripts/run_agent_pipeline_trace_report.py` | `scripts/diagnostics/run_agent_pipeline_trace_report.py` | DIAGNOSTICS |
| `scripts/run_alpha_hypothesis_competition.py` | `scripts/research/run_alpha_hypothesis_competition.py` | RESEARCH |
| `scripts/run_alpha_research_board.py` | `scripts/research/run_alpha_research_board.py` | RESEARCH |
| `scripts/run_attribution_score_range.py` | `scripts/research/run_attribution_score_range.py` | RESEARCH |
| `scripts/run_attribution_score_window.py` | `scripts/research/run_attribution_score_window.py` | RESEARCH |
| `scripts/run_broker_trade_reconciliation.py` | `scripts/maintenance/run_broker_trade_reconciliation.py` | MAINTENANCE |
| `scripts/run_conditional_alpha_diagnosis.py` | `scripts/research/run_conditional_alpha_diagnosis.py` | RESEARCH |
| `scripts/run_cumulative_improvement_review.py` | `scripts/research/run_cumulative_improvement_review.py` | RESEARCH |
| `scripts/run_decision_story_report.py` | `scripts/research/run_decision_story_report.py` | RESEARCH |
| `scripts/run_evaluation_lens_report.py` | `scripts/research/run_evaluation_lens_report.py` | RESEARCH |
| `scripts/run_existing_evidence_mining.py` | `scripts/research/run_existing_evidence_mining.py` | RESEARCH |
| `scripts/run_frozen_q9_baseline_closeout.py` | `scripts/research/run_frozen_q9_baseline_closeout.py` | RESEARCH |
| `scripts/run_full_chain_component_review.py` | `scripts/research/run_full_chain_component_review.py` | RESEARCH |
| `scripts/run_historical_q9_prior.py` | `scripts/research/run_historical_q9_prior.py` | RESEARCH |
| `scripts/run_horizon_alignment_review.py` | `scripts/research/run_horizon_alignment_review.py` | RESEARCH |
| `scripts/run_horizon_revision_backtest.py` | `scripts/research/run_horizon_revision_backtest.py` | RESEARCH |
| `scripts/run_integrated_trade_diagnosis.py` | `scripts/research/run_integrated_trade_diagnosis.py` | RESEARCH |
| `scripts/run_integrated_trade_validation.py` | `scripts/research/run_integrated_trade_validation.py` | RESEARCH |
| `scripts/run_log_maintenance.py` | `scripts/maintenance/run_log_maintenance.py` | MAINTENANCE |
| `scripts/run_loss_decomposition.py` | `scripts/research/run_loss_decomposition.py` | RESEARCH |
| `scripts/run_m22_closeout_check.py` | `scripts/diagnostics/run_m22_closeout_check.py` | DIAGNOSTICS |
| `scripts/run_m23_closeout_check.py` | `scripts/diagnostics/run_m23_closeout_check.py` | DIAGNOSTICS |
| `scripts/run_m23_resilience_closeout_check.py` | `scripts/diagnostics/run_m23_resilience_closeout_check.py` | DIAGNOSTICS |
| `scripts/run_m24_closeout_check.py` | `scripts/diagnostics/run_m24_closeout_check.py` | DIAGNOSTICS |
| `scripts/run_m24_guard_precedence_check.py` | `scripts/diagnostics/run_m24_guard_precedence_check.py` | DIAGNOSTICS |
| `scripts/run_m26_ab_evaluation.py` | `scripts/diagnostics/run_m26_ab_evaluation.py` | DIAGNOSTICS |
| `scripts/run_m26_closeout_check.py` | `scripts/diagnostics/run_m26_closeout_check.py` | DIAGNOSTICS |
| `scripts/run_m26_dataset_manifest_check.py` | `scripts/diagnostics/run_m26_dataset_manifest_check.py` | DIAGNOSTICS |
| `scripts/run_m26_promotion_gate_check.py` | `scripts/diagnostics/run_m26_promotion_gate_check.py` | DIAGNOSTICS |
| `scripts/run_m26_replay_runner.py` | `scripts/diagnostics/run_m26_replay_runner.py` | DIAGNOSTICS |
| `scripts/run_m26_scorecard.py` | `scripts/diagnostics/run_m26_scorecard.py` | DIAGNOSTICS |
| `scripts/run_m27_allocation_policy_check.py` | `scripts/diagnostics/run_m27_allocation_policy_check.py` | DIAGNOSTICS |
| `scripts/run_m27_closeout_check.py` | `scripts/diagnostics/run_m27_closeout_check.py` | DIAGNOSTICS |
| `scripts/run_m27_conflict_resolution_check.py` | `scripts/diagnostics/run_m27_conflict_resolution_check.py` | DIAGNOSTICS |
| `scripts/run_m27_portfolio_budget_boundary_check.py` | `scripts/diagnostics/run_m27_portfolio_budget_boundary_check.py` | DIAGNOSTICS |
| `scripts/run_m27_portfolio_guard_alert_policy_check.py` | `scripts/diagnostics/run_m27_portfolio_guard_alert_policy_check.py` | DIAGNOSTICS |
| `scripts/run_m27_portfolio_guard_metrics_check.py` | `scripts/diagnostics/run_m27_portfolio_guard_metrics_check.py` | DIAGNOSTICS |
| `scripts/run_m27_portfolio_guard_notify_check.py` | `scripts/diagnostics/run_m27_portfolio_guard_notify_check.py` | DIAGNOSTICS |
| `scripts/run_m27_portfolio_guard_notify_query_check.py` | `scripts/diagnostics/run_m27_portfolio_guard_notify_query_check.py` | DIAGNOSTICS |
| `scripts/run_m27_portfolio_guard_notify_routing_check.py` | `scripts/diagnostics/run_m27_portfolio_guard_notify_routing_check.py` | DIAGNOSTICS |
| `scripts/run_m27_runtime_portfolio_guard_check.py` | `scripts/diagnostics/run_m27_runtime_portfolio_guard_check.py` | DIAGNOSTICS |
| `scripts/run_m28_closeout_check.py` | `scripts/diagnostics/run_m28_closeout_check.py` | DIAGNOSTICS |
| `scripts/run_m28_deploy_launch_template_check.py` | `scripts/diagnostics/run_m28_deploy_launch_template_check.py` | DIAGNOSTICS |
| `scripts/run_m28_launch_hook_integration_check.py` | `scripts/diagnostics/run_m28_launch_hook_integration_check.py` | DIAGNOSTICS |
| `scripts/run_m28_registration_helper_check.py` | `scripts/diagnostics/run_m28_registration_helper_check.py` | DIAGNOSTICS |
| `scripts/run_m28_rollout_rollback_check.py` | `scripts/diagnostics/run_m28_rollout_rollback_check.py` | DIAGNOSTICS |
| `scripts/run_m28_runtime_lifecycle_hooks_check.py` | `scripts/diagnostics/run_m28_runtime_lifecycle_hooks_check.py` | DIAGNOSTICS |
| `scripts/run_m28_runtime_profile_scaffold_check.py` | `scripts/diagnostics/run_m28_runtime_profile_scaffold_check.py` | DIAGNOSTICS |
| `scripts/run_m28_scheduler_worker_launch_wrapper_check.py` | `scripts/diagnostics/run_m28_scheduler_worker_launch_wrapper_check.py` | DIAGNOSTICS |
| `scripts/run_m28_startup_preflight_check.py` | `scripts/diagnostics/run_m28_startup_preflight_check.py` | DIAGNOSTICS |
| `scripts/run_m29_audit_trail_check.py` | `scripts/diagnostics/run_m29_audit_trail_check.py` | DIAGNOSTICS |
| `scripts/run_m29_closeout_check.py` | `scripts/diagnostics/run_m29_closeout_check.py` | DIAGNOSTICS |
| `scripts/run_m29_disaster_recovery_drill.py` | `scripts/diagnostics/run_m29_disaster_recovery_drill.py` | DIAGNOSTICS |
| `scripts/run_m29_incident_timeline_check.py` | `scripts/diagnostics/run_m29_incident_timeline_check.py` | DIAGNOSTICS |
| `scripts/run_m29_log_archive_integrity_check.py` | `scripts/diagnostics/run_m29_log_archive_integrity_check.py` | DIAGNOSTICS |
| `scripts/run_m30_final_golive_signoff.py` | `scripts/diagnostics/run_m30_final_golive_signoff.py` | DIAGNOSTICS |
| `scripts/run_m30_post_golive_monitoring_policy.py` | `scripts/diagnostics/run_m30_post_golive_monitoring_policy.py` | DIAGNOSTICS |
| `scripts/run_m30_quality_gates_bundle.py` | `scripts/diagnostics/run_m30_quality_gates_bundle.py` | DIAGNOSTICS |
| `scripts/run_m30_release_signoff_checklist.py` | `scripts/diagnostics/run_m30_release_signoff_checklist.py` | DIAGNOSTICS |
| `scripts/run_m31_agent_chain_probe.py` | `scripts/diagnostics/run_m31_agent_chain_probe.py` | DIAGNOSTICS |
| `scripts/run_m31_mock_exam_readiness_check.py` | `scripts/diagnostics/run_m31_mock_exam_readiness_check.py` | DIAGNOSTICS |
| `scripts/run_m31_mock_investor_exam_check.py` | `scripts/diagnostics/run_m31_mock_investor_exam_check.py` | DIAGNOSTICS |
| `scripts/run_m31_slo_incident_review_check.py` | `scripts/diagnostics/run_m31_slo_incident_review_check.py` | DIAGNOSTICS |
| `scripts/run_m31_weekly_health_summary.py` | `scripts/diagnostics/run_m31_weekly_health_summary.py` | DIAGNOSTICS |
| `scripts/run_market_regime_rail_review.py` | `scripts/research/run_market_regime_rail_review.py` | RESEARCH |
| `scripts/run_memory_contamination_review.py` | `scripts/research/run_memory_contamination_review.py` | RESEARCH |
| `scripts/run_monitor_noop_attribution.py` | `scripts/research/run_monitor_noop_attribution.py` | RESEARCH |
| `scripts/run_offhours_full_trace_bundle.py` | `scripts/diagnostics/run_offhours_full_trace_bundle.py` | DIAGNOSTICS |
| `scripts/run_offhours_validation_loop.py` | `scripts/research/run_offhours_validation_loop.py` | RESEARCH |
| `scripts/run_opening_rank1_longitudinal.py` | `scripts/research/run_opening_rank1_longitudinal.py` | RESEARCH |
| `scripts/run_opening_rank1_shadow.py` | `scripts/research/run_opening_rank1_shadow.py` | RESEARCH |
| `scripts/run_operator_summary_mining.py` | `scripts/research/run_operator_summary_mining.py` | RESEARCH |
| `scripts/run_phase5_validation_bundle.py` | `scripts/research/run_phase5_validation_bundle.py` | RESEARCH |
| `scripts/run_post_exit_shadow_recap.py` | `scripts/research/run_post_exit_shadow_recap.py` | RESEARCH |
| `scripts/run_post_reclaim_offline_research.py` | `scripts/research/run_post_reclaim_offline_research.py` | RESEARCH |
| `scripts/run_q12_historical_policy_review.py` | `scripts/research/run_q12_historical_policy_review.py` | RESEARCH |
| `scripts/run_q13_q14_validation.py` | `scripts/research/run_q13_q14_validation.py` | RESEARCH |
| `scripts/run_q8_historical_review.py` | `scripts/research/run_q8_historical_review.py` | RESEARCH |
| `scripts/run_q8_lane_decision_table.py` | `scripts/research/run_q8_lane_decision_table.py` | RESEARCH |
| `scripts/run_q8_shadow_blocker_review.py` | `scripts/research/run_q8_shadow_blocker_review.py` | RESEARCH |
| `scripts/run_q9_baseline_comparison.py` | `scripts/research/run_q9_baseline_comparison.py` | RESEARCH |
| `scripts/run_q9_evaluation.py` | `scripts/research/run_q9_evaluation.py` | RESEARCH |
| `scripts/run_quant_trade_diagnosis.py` | `scripts/research/run_quant_trade_diagnosis.py` | RESEARCH |
| `scripts/run_rank1_feature_mart.py` | `scripts/research/run_rank1_feature_mart.py` | RESEARCH |
| `scripts/run_rank1_prospective_shadow.py` | `scripts/research/run_rank1_prospective_shadow.py` | RESEARCH |
| `scripts/run_report_maintenance.py` | `scripts/maintenance/run_report_maintenance.py` | MAINTENANCE |
| `scripts/run_run_card_report.py` | `scripts/research/run_run_card_report.py` | RESEARCH |
| `scripts/run_same_symbol_sequence.py` | `scripts/research/run_same_symbol_sequence.py` | RESEARCH |
| `scripts/run_scanner_alignment_root_cause_range.py` | `scripts/research/run_scanner_alignment_root_cause_range.py` | RESEARCH |
| `scripts/run_short_alpha_discriminator.py` | `scripts/research/run_short_alpha_discriminator.py` | RESEARCH |
| `scripts/run_stage2_authority_review.py` | `scripts/research/run_stage2_authority_review.py` | RESEARCH |
| `scripts/run_structural_alpha_batch1.py` | `scripts/research/run_structural_alpha_batch1.py` | RESEARCH |
| `scripts/run_structural_alpha_batch2.py` | `scripts/research/run_structural_alpha_batch2.py` | RESEARCH |
| `scripts/run_trade_explain_report.py` | `scripts/research/run_trade_explain_report.py` | RESEARCH |
| `scripts/run_uef5_3_dual_run.py` | `scripts/research/run_uef5_3_dual_run.py` | RESEARCH |
| `scripts/run_uef6_dedup_detection.py` | `scripts/research/run_uef6_dedup_detection.py` | RESEARCH |
| `scripts/run_uef6_historical_validation.py` | `scripts/research/run_uef6_historical_validation.py` | RESEARCH |
| `scripts/run_uef7_alpha_board_normalization.py` | `scripts/research/run_uef7_alpha_board_normalization.py` | RESEARCH |
| `scripts/run_uef8_fair_comparison_validation.py` | `scripts/research/run_uef8_fair_comparison_validation.py` | RESEARCH |
| `scripts/run_uef9_formal_authority.py` | `scripts/research/run_uef9_formal_authority.py` | RESEARCH |
| `scripts/smoke_m20_llm.py` | `scripts/diagnostics/smoke_m20_llm.py` | DIAGNOSTICS |
| `scripts/smoke_m22_hydration.py` | `scripts/diagnostics/smoke_m22_hydration.py` | DIAGNOSTICS |
| `scripts/step5d_crash_reconciliation.py` | `scripts/maintenance/step5d_crash_reconciliation.py` | MAINTENANCE |
| `scripts/sync_legacy_brief_llm.py` | `scripts/maintenance/sync_legacy_brief_llm.py` | MAINTENANCE |
| `scripts/sync_openrouter_model_catalog.py` | `scripts/maintenance/sync_openrouter_model_catalog.py` | MAINTENANCE |

## Final publication audit

- Patch-note targeted pytest: **5 passed**, one dependency deprecation warning. Existing JSON entries and order and the entire old Markdown prefix preserved; entry_count increased by exactly one.
- 284 changed paths; only approved shared changelog documents overlap T4. All Operations, Config and 19 held originals match base Git blobs.
- Safety guard rejected eight transport attempts during validation; no successful external collection or order submission.
- Successful pytest scratch/cache, CLI runtime trees and outside-CWD temporary directory cleaned under `/tmp/agentra-bulk`; summarized ledger and logs retained.
