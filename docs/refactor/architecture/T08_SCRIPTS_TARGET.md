# T08 — scripts/ 공개 CLI·진단·유지관리·연구 상세 목표
> 범위 RF-063~071. 실제 파일 418개 (각 SOURCE_PATH↔RF 인벤토리 하단 전수). 공개 entrypoint를 디렉터리 모양 때문에 일괄 이동하지 않는다.

## 목표 구조 — 책임 기준(기존 경로 유지 우선)
```text
scripts/
├── __init__.py
├── diagnostics/       # pure/read-only health, audit, query, benchmark (RF-063)
├── refactor/          # isolated structural evidence/contract tools (RF-064)
├── research/          # non-trading experiments & Q10/Q12 research (RF-065)
├── maintenance/       # bounded repair/cleanup; write permissions audited (RF-066)
├── examples/          # demo-only, no real broker submit (RF-066)
├── check_*.py         # root public/legacy CLI aliases; keep until zero consumers
├── run_*.py           # root actual scheduled launcher/entry: contract-preserving facade
├── generate_*.py      # root compatibility for generators
├── capture_*.py       # preopen/Q10/Q12 snapshot launchers
├── *.ps1, *.cmd, *.bat# external scheduler & Windows public aliases
└── 기타 기존 root helper Python
```

## 세부 개선 목표
| 대표 파일(실존) | 목표 책임/처리 | RF |
|---|---|---|
| `scripts/diagnostics/check_daily_uef_run_status.py`, `check_real_execution_preflight.py`, `query_trade_reason_chain.py` | 진단·조회만 수행, 모듈 내 write side-effect를 분리 | RF-063 |
| `scripts/diagnostics/audit_target_tree_compat.py`, `audit_windows_launchers.py` | public CLI/작업 스케줄러 정합 증거 재사용; 새 자체 감사도구 무분별 증식 금지 | RF-063 |
| `scripts/refactor/*` | 종료된 실험 vs 현재 계약 도구 분리, 과거 SHA 및 오라클 보존 | RF-064 |
| `scripts/research/{run_alpha_research_board,run_opening_rank1_shadow,run_integrated_trade_diagnosis}.py` | 연구·검증 입력/출력 명시, 주문 권한 없음 | RF-065 |
| `scripts/maintenance/{run_log_maintenance,run_report_maintenance,clean_evaluation_test_contamination}.py` | 보존 기한·실행 mode·실제 write 사전 검사 | RF-066 |
| `scripts/check_real_execution_preflight.py`, `launch_with_preflight.py`, `restart_live_session.py` | 외부 scheduler/운영 진입점을 **그대로 유지**, 순수 구현부와 진입 함수를 분리한 경우 동등성 입증 | RF-067/070/071 (각 파일 실제 RF는 아래 인벤토리) |
| `scripts/generate_daily_report.py`, `generate_operator_summary_report.py`, `generate_m28_launch_templates.py` | generator output schema/파일명/경로/바이트 유지 | RF-068 |
| `scripts/capture_preopen_macro_snapshot.py`, `capture_q10_preopen_snapshot.py`, `capture_q12_btc_0855_snapshot.py` | 호출 clock/env read timing, 서식, 산출물 경로 유지 | RF-069 |
| `scripts/cleanup_pytest_artifacts.py`, `cleanup_pytest_artifacts.ps1`, `cleanup_pytest_artifacts.cmd` | 성공 scratch 자동 정리, 실패 기록 제한 보존. 운영 데이터 재귀 삭제 금지 | RF-066/071, 실제 RF 아래 참조 |
| `scripts/restart_live_session.ps1`, `restart_live_session.bat`, `scripts/register_mock_exam_tasks_example.bat` | OS 호출 경계 KEEP / command line arguments parity | RF-070/071, 실제 RF 아래 참조 |

### 처리 지침
1. `scripts/` 루트의 기존 *.py/ps1/bat/cmd는 **외부 소비자 이름과 경로가 정본일 수 있음**. 기존 루트 파일을 삭제하고 하위 파일로만 옮기는 개편 금지.
2. 진단/research에서 Broker write 또는 production data mutate가 나오는 경우 그 코드를 분리하기 전 안전 HOLD. `maintenance/`는 read-only가 아닐 수 있어 실행 권한과 대상 폴더 보존 규칙이 중요.
3. 코드가 하위 directory에 이미 존재한다면 새 파일 중복 생성 대신 기존 implementation Owner가 실제 하나인지 확인. root facade→하위 implementation 위임에 identity, import, CLI help/exit, cwd/env/log parity가 필요.
4. Windows Task Scheduler·Linux systemd·Docker Compose·deploy trading scripts의 literal executable path를 확인하고 **실운영 경로는 기본 KEEP**.
5. 역사 실험/리팩터링 증거는 RETIRE_CANDIDATE로만 표기하고 실제 remove는 PATH 소비자 0+기준선/테스트 보존 증거 후 별도 승인.

## 기존 RF별 파일 수
RF-063: 76 · RF-064: 58 · RF-065: 54 · RF-066: 17 · RF-067: 14 · RF-068: 8 · RF-069: 7 · RF-070: 142 · RF-071: 42

## 현재 소스 파일명 418개 전수 — 파일별 RF
아래 PATH는 **CURRENT SOURCE_PATH**이고, 신규 TARGET_PATH는 상위 표·RF 승인 후 확정한다. 이렇게 표를 분리해 모든 파일을 무조건 새 폴더로 강제하는 일을 방지한다.

<details><summary>scripts/ 전체 파일 목록·RF 열기</summary>

- `scripts/__init__.py` — RF-071
- `scripts/analyze_entry_blockers.py` — RF-071
- `scripts/approval_cli.py` — RF-071
- `scripts/benchmark_operator_visibility_memory.py` — RF-071
- `scripts/build_api_catalog.py` — RF-069
- `scripts/build_default_rules.py` — RF-069
- `scripts/build_uef5_clean_evidence_coverage.py` — RF-069
- `scripts/capture_preopen_macro_snapshot.py` — RF-069
- `scripts/capture_q10_preopen_snapshot.py` — RF-069
- `scripts/capture_q12_btc_0855_snapshot.py` — RF-069
- `scripts/check_alert_policy_v1.py` — RF-067
- `scripts/check_audit_trail_completeness.py` — RF-067
- `scripts/check_daily_uef_run_status.py` — RF-067
- `scripts/check_log_archive_integrity.py` — RF-067
- `scripts/check_metrics_schema_v1.py` — RF-067
- `scripts/check_monitor_gate_patterns.py` — RF-067
- `scripts/check_phase_5_2_5_3_runtime_health.py` — RF-067
- `scripts/check_profitability_recovery_day1.py` — RF-067
- `scripts/check_q9_q12_readiness.py` — RF-067
- `scripts/check_real_execution_preflight.py` — RF-067
- `scripts/check_reporter_upgrade_regression.py` — RF-067
- `scripts/check_reports_trades_health.py` — RF-067
- `scripts/check_runtime_profile.py` — RF-067
- `scripts/check_trade_report_runtime_regression.py` — RF-067
- `scripts/clean_evaluation_test_contamination.py` — RF-071
- `scripts/cleanup_pytest_artifacts.cmd` — RF-071
- `scripts/cleanup_pytest_artifacts.ps1` — RF-071
- `scripts/cleanup_pytest_artifacts.py` — RF-071
- `scripts/collect_opening_rank1_symbol_metadata.py` — RF-069
- `scripts/compact_q9_decision_windows.py` — RF-071
- `scripts/daily_profitability_scorecard.py` — RF-071
- `scripts/demo_m14_mock_order.py` — RF-071
- `scripts/demo_m14_order_status.py` — RF-071
- `scripts/demo_m14_quote_then_order.py` — RF-071
- `scripts/demo_m15_smoke.py` — RF-071
- `scripts/demo_m22_graph_with_hydration.py` — RF-071
- `scripts/demo_m22_skill_flow.py` — RF-071
- `scripts/demo_m22_skill_hydration.py` — RF-071
- `scripts/demo_m7_dry_run_pipeline.py` — RF-071
- `scripts/diagnostics/__init__.py` — RF-063
- `scripts/diagnostics/analyze_entry_blockers.py` — RF-063
- `scripts/diagnostics/audit_target_tree_compat.py` — RF-063
- `scripts/diagnostics/audit_windows_launchers.py` — RF-063
- `scripts/diagnostics/benchmark_operator_visibility_memory.py` — RF-063
- `scripts/diagnostics/check_alert_policy_v1.py` — RF-063
- `scripts/diagnostics/check_audit_trail_completeness.py` — RF-063
- `scripts/diagnostics/check_daily_uef_run_status.py` — RF-063
- `scripts/diagnostics/check_log_archive_integrity.py` — RF-063
- `scripts/diagnostics/check_metrics_schema_v1.py` — RF-063
- `scripts/diagnostics/check_monitor_gate_patterns.py` — RF-063
- `scripts/diagnostics/check_phase_5_2_5_3_runtime_health.py` — RF-063
- `scripts/diagnostics/check_profitability_recovery_day1.py` — RF-063
- `scripts/diagnostics/check_q9_q12_readiness.py` — RF-063
- `scripts/diagnostics/check_real_execution_preflight.py` — RF-063
- `scripts/diagnostics/check_reporter_upgrade_regression.py` — RF-063
- `scripts/diagnostics/check_reports_trades_health.py` — RF-063
- `scripts/diagnostics/check_runtime_profile.py` — RF-063
- `scripts/diagnostics/check_trade_report_runtime_regression.py` — RF-063
- `scripts/diagnostics/generate_m28_launch_templates.py` — RF-063
- `scripts/diagnostics/generate_m28_registration_helpers.py` — RF-063
- `scripts/diagnostics/generate_ops_diagnostic_report.py` — RF-063
- `scripts/diagnostics/query_commander_resilience_events.py` — RF-063
- `scripts/diagnostics/query_intent_state_store.py` — RF-063
- `scripts/diagnostics/query_m25_notification_events.py` — RF-063
- `scripts/diagnostics/query_strategist_llm_events.py` — RF-063
- `scripts/diagnostics/query_trade_reason_chain.py` — RF-063
- `scripts/diagnostics/reconstruct_incident_timeline.py` — RF-063
- `scripts/diagnostics/run_agent_pipeline_trace_report.py` — RF-063
- `scripts/diagnostics/run_m22_closeout_check.py` — RF-063
- `scripts/diagnostics/run_m23_closeout_check.py` — RF-063
- `scripts/diagnostics/run_m23_resilience_closeout_check.py` — RF-063
- `scripts/diagnostics/run_m24_closeout_check.py` — RF-063
- `scripts/diagnostics/run_m24_guard_precedence_check.py` — RF-063
- `scripts/diagnostics/run_m26_ab_evaluation.py` — RF-063
- `scripts/diagnostics/run_m26_closeout_check.py` — RF-063
- `scripts/diagnostics/run_m26_dataset_manifest_check.py` — RF-063
- `scripts/diagnostics/run_m26_promotion_gate_check.py` — RF-063
- `scripts/diagnostics/run_m26_replay_runner.py` — RF-063
- `scripts/diagnostics/run_m26_scorecard.py` — RF-063
- `scripts/diagnostics/run_m27_allocation_policy_check.py` — RF-063
- `scripts/diagnostics/run_m27_closeout_check.py` — RF-063
- `scripts/diagnostics/run_m27_conflict_resolution_check.py` — RF-063
- `scripts/diagnostics/run_m27_portfolio_budget_boundary_check.py` — RF-063
- `scripts/diagnostics/run_m27_portfolio_guard_alert_policy_check.py` — RF-063
- `scripts/diagnostics/run_m27_portfolio_guard_metrics_check.py` — RF-063
- `scripts/diagnostics/run_m27_portfolio_guard_notify_check.py` — RF-063
- `scripts/diagnostics/run_m27_portfolio_guard_notify_query_check.py` — RF-063
- `scripts/diagnostics/run_m27_portfolio_guard_notify_routing_check.py` — RF-063
- `scripts/diagnostics/run_m27_runtime_portfolio_guard_check.py` — RF-063
- `scripts/diagnostics/run_m28_closeout_check.py` — RF-063
- `scripts/diagnostics/run_m28_deploy_launch_template_check.py` — RF-063
- `scripts/diagnostics/run_m28_launch_hook_integration_check.py` — RF-063
- `scripts/diagnostics/run_m28_registration_helper_check.py` — RF-063
- `scripts/diagnostics/run_m28_rollout_rollback_check.py` — RF-063
- `scripts/diagnostics/run_m28_runtime_lifecycle_hooks_check.py` — RF-063
- `scripts/diagnostics/run_m28_runtime_profile_scaffold_check.py` — RF-063
- `scripts/diagnostics/run_m28_scheduler_worker_launch_wrapper_check.py` — RF-063
- `scripts/diagnostics/run_m28_startup_preflight_check.py` — RF-063
- `scripts/diagnostics/run_m29_audit_trail_check.py` — RF-063
- `scripts/diagnostics/run_m29_closeout_check.py` — RF-063
- `scripts/diagnostics/run_m29_disaster_recovery_drill.py` — RF-063
- `scripts/diagnostics/run_m29_incident_timeline_check.py` — RF-063
- `scripts/diagnostics/run_m29_log_archive_integrity_check.py` — RF-063
- `scripts/diagnostics/run_m30_final_golive_signoff.py` — RF-063
- `scripts/diagnostics/run_m30_post_golive_monitoring_policy.py` — RF-063
- `scripts/diagnostics/run_m30_quality_gates_bundle.py` — RF-063
- `scripts/diagnostics/run_m30_release_signoff_checklist.py` — RF-063
- `scripts/diagnostics/run_m31_agent_chain_probe.py` — RF-063
- `scripts/diagnostics/run_m31_mock_exam_readiness_check.py` — RF-063
- `scripts/diagnostics/run_m31_mock_investor_exam_check.py` — RF-063
- `scripts/diagnostics/run_m31_slo_incident_review_check.py` — RF-063
- `scripts/diagnostics/run_m31_weekly_health_summary.py` — RF-063
- `scripts/diagnostics/run_offhours_full_trace_bundle.py` — RF-063
- `scripts/diagnostics/smoke_m20_llm.py` — RF-063
- `scripts/diagnostics/smoke_m22_hydration.py` — RF-063
- `scripts/docker_healthcheck.py` — RF-070
- `scripts/examples/__init__.py` — RF-066
- `scripts/examples/demo_m22_graph_with_hydration.py` — RF-066
- `scripts/examples/demo_m22_skill_flow.py` — RF-066
- `scripts/examples/demo_m7_dry_run_pipeline.py` — RF-066
- `scripts/generate_daily_report.py` — RF-068
- `scripts/generate_m28_launch_templates.py` — RF-068
- `scripts/generate_m28_registration_helpers.py` — RF-068
- `scripts/generate_metrics_report.py` — RF-068
- `scripts/generate_operator_summary_report.py` — RF-068
- `scripts/generate_ops_diagnostic_report.py` — RF-068
- `scripts/generate_strategist_llm_summary.py` — RF-068
- `scripts/generate_symbol_trade_report.py` — RF-068
- `scripts/launch_with_preflight.py` — RF-070
- `scripts/maintenance/__init__.py` — RF-066
- `scripts/maintenance/clean_evaluation_test_contamination.py` — RF-066
- `scripts/maintenance/compact_q9_decision_windows.py` — RF-066
- `scripts/maintenance/organize_llm_reports.py` — RF-066
- `scripts/maintenance/reconcile_intent_state_store.py` — RF-066
- `scripts/maintenance/repair_q9_day_artifacts.py` — RF-066
- `scripts/maintenance/repair_trade_symbol_context.py` — RF-066
- `scripts/maintenance/run_broker_trade_reconciliation.py` — RF-066
- `scripts/maintenance/run_log_maintenance.py` — RF-066
- `scripts/maintenance/run_report_maintenance.py` — RF-066
- `scripts/maintenance/step5d_crash_reconciliation.py` — RF-066
- `scripts/maintenance/sync_legacy_brief_llm.py` — RF-066
- `scripts/maintenance/sync_openrouter_model_catalog.py` — RF-066
- `scripts/organize_llm_reports.py` — RF-071
- `scripts/query_commander_resilience_events.py` — RF-071
- `scripts/query_intent_state_store.py` — RF-071
- `scripts/query_m25_notification_events.py` — RF-071
- `scripts/query_strategist_llm_events.py` — RF-071
- `scripts/query_trade_reason_chain.py` — RF-071
- `scripts/reconcile_intent_state_store.py` — RF-071
- `scripts/reconstruct_incident_timeline.py` — RF-071
- `scripts/refactor/inventory_p15_consumers.py` — RF-064
- `scripts/refactor/monitor_evidence_ast.py` — RF-064
- `scripts/refactor/p152_facade_consumer_scan.py` — RF-064
- `scripts/refactor/p152_integration_acceptance.py` — RF-064
- `scripts/refactor/p152_owner_parity.py` — RF-064
- `scripts/refactor/p152_prelocal_consumer_debt.py` — RF-064
- `scripts/refactor/p152_r3_call_recorder.py` — RF-064
- `scripts/refactor/p152_r3_seam_challenge.py` — RF-064
- `scripts/refactor/p152_snapshot_parity.py` — RF-064
- `scripts/refactor/p156_determinism_plugin.py` — RF-064
- `scripts/refactor/p156_parity_differential.py` — RF-064
- `scripts/refactor/p158_static_purity_closure.py` — RF-064
- `scripts/refactor/p159_ownership_matrix.py` — RF-064
- `scripts/refactor/p15_strategist_s5_runner.py` — RF-064
- `scripts/refactor/p160_ntfs_dir_mtime_diagnostics.py` — RF-064
- `scripts/refactor/p161_agent_output_capture_plugin.py` — RF-064
- `scripts/refactor/p161_agent_output_diagnose.py` — RF-064
- `scripts/refactor/p161_agent_output_freeze.py` — RF-064
- `scripts/refactor/p161_agent_output_freeze_tool.py` — RF-064
- `scripts/refactor/p161_agent_output_variants.py` — RF-064
- `scripts/refactor/p162_scanner_capture_plugin.py` — RF-064
- `scripts/refactor/p162_scanner_node_freeze_tool.py` — RF-064
- `scripts/refactor/p163_monitor_capture_plugin.py` — RF-064
- `scripts/refactor/p163_monitor_freeze_tool.py` — RF-064
- `scripts/refactor/p164_strategist_capture_plugin.py` — RF-064
- `scripts/refactor/p164_strategist_freeze_tool.py` — RF-064
- `scripts/refactor/p165_commander_ui_capture_plugin.py` — RF-064
- `scripts/refactor/p165_commander_ui_freeze_tool.py` — RF-064
- `scripts/refactor/p167_v2053_scanner_context_cases.py` — RF-064
- `scripts/refactor/p169_broad_failure_evidence.py` — RF-064
- `scripts/refactor/p170_v3055_projection_capture_plugin.py` — RF-064
- `scripts/refactor/p172_strategist_s1_057_capture.py` — RF-064
- `scripts/refactor/p172_v4056_scanner_policy_cases.py` — RF-064
- `scripts/refactor/p173_v4056_repeat_guard_cases.py` — RF-064
- `scripts/refactor/render_p15_import_matrix.py` — RF-064
- `scripts/refactor/reporter_facade_guard.py` — RF-064
- `scripts/refactor/shared_candidate_tests.py` — RF-064
- `scripts/refactor/shared_role_contracts.py` — RF-064
- `scripts/refactor/shared_strategist_contracts.py` — RF-064
- `scripts/refactor/shared_uef_baseline.py` — RF-064
- `scripts/refactor/work_monitor_annotation_replay.py` — RF-064
- `scripts/refactor/work_monitor_body_replay.py` — RF-064
- `scripts/refactor/work_monitor_continuous_replay.py` — RF-064
- `scripts/refactor/work_monitor_contracts.py` — RF-064
- `scripts/refactor/work_monitor_current_tree.py` — RF-064
- `scripts/refactor/work_monitor_observation_replay.py` — RF-064
- `scripts/refactor/work_monitor_policy_trace_replay.py` — RF-064
- `scripts/refactor/work_monitor_retained_boundary.py` — RF-064
- `scripts/refactor/work_monitor_scope_accounting.py` — RF-064
- `scripts/refactor/work_reporter_capture.py` — RF-064
- `scripts/refactor/work_reporter_contract_runner.py` — RF-064
- `scripts/refactor/work_reporter_facade_ledger_v2.py` — RF-064
- `scripts/refactor/work_reporter_flow_map.py` — RF-064
- `scripts/refactor/work_reporter_hygiene_check.py` — RF-064
- `scripts/refactor/work_reporter_inventory.py` — RF-064
- `scripts/refactor/work_reporter_r4_extract.py` — RF-064
- `scripts/refactor/work_reporter_split.py` — RF-064
- `scripts/refactor/work_reporter_triage.py` — RF-064
- `scripts/register_mock_exam_tasks_example.bat` — RF-070
- `scripts/repair_q9_day_artifacts.py` — RF-071
- `scripts/repair_trade_symbol_context.py` — RF-071
- `scripts/research/__init__.py` — RF-065
- `scripts/research/daily_profitability_scorecard.py` — RF-065
- `scripts/research/run_agent_effectiveness_scorecard.py` — RF-065
- `scripts/research/run_alpha_hypothesis_competition.py` — RF-065
- `scripts/research/run_alpha_research_board.py` — RF-065
- `scripts/research/run_attribution_score_range.py` — RF-065
- `scripts/research/run_attribution_score_window.py` — RF-065
- `scripts/research/run_conditional_alpha_diagnosis.py` — RF-065
- `scripts/research/run_cumulative_improvement_review.py` — RF-065
- `scripts/research/run_decision_story_report.py` — RF-065
- `scripts/research/run_evaluation_lens_report.py` — RF-065
- `scripts/research/run_existing_evidence_mining.py` — RF-065
- `scripts/research/run_frozen_q9_baseline_closeout.py` — RF-065
- `scripts/research/run_full_chain_component_review.py` — RF-065
- `scripts/research/run_historical_q9_prior.py` — RF-065
- `scripts/research/run_horizon_alignment_review.py` — RF-065
- `scripts/research/run_horizon_revision_backtest.py` — RF-065
- `scripts/research/run_integrated_trade_diagnosis.py` — RF-065
- `scripts/research/run_integrated_trade_validation.py` — RF-065
- `scripts/research/run_loss_decomposition.py` — RF-065
- `scripts/research/run_market_regime_rail_review.py` — RF-065
- `scripts/research/run_memory_contamination_review.py` — RF-065
- `scripts/research/run_monitor_noop_attribution.py` — RF-065
- `scripts/research/run_offhours_validation_loop.py` — RF-065
- `scripts/research/run_opening_rank1_longitudinal.py` — RF-065
- `scripts/research/run_opening_rank1_shadow.py` — RF-065
- `scripts/research/run_operator_summary_mining.py` — RF-065
- `scripts/research/run_phase5_validation_bundle.py` — RF-065
- `scripts/research/run_post_exit_shadow_recap.py` — RF-065
- `scripts/research/run_post_reclaim_offline_research.py` — RF-065
- `scripts/research/run_q12_historical_policy_review.py` — RF-065
- `scripts/research/run_q13_q14_validation.py` — RF-065
- `scripts/research/run_q8_historical_review.py` — RF-065
- `scripts/research/run_q8_lane_decision_table.py` — RF-065
- `scripts/research/run_q8_shadow_blocker_review.py` — RF-065
- `scripts/research/run_q9_baseline_comparison.py` — RF-065
- `scripts/research/run_q9_evaluation.py` — RF-065
- `scripts/research/run_quant_trade_diagnosis.py` — RF-065
- `scripts/research/run_rank1_feature_mart.py` — RF-065
- `scripts/research/run_rank1_prospective_shadow.py` — RF-065
- `scripts/research/run_run_card_report.py` — RF-065
- `scripts/research/run_same_symbol_sequence.py` — RF-065
- `scripts/research/run_scanner_alignment_root_cause_range.py` — RF-065
- `scripts/research/run_short_alpha_discriminator.py` — RF-065
- `scripts/research/run_stage2_authority_review.py` — RF-065
- `scripts/research/run_structural_alpha_batch1.py` — RF-065
- `scripts/research/run_structural_alpha_batch2.py` — RF-065
- `scripts/research/run_trade_explain_report.py` — RF-065
- `scripts/research/run_uef5_3_dual_run.py` — RF-065
- `scripts/research/run_uef6_dedup_detection.py` — RF-065
- `scripts/research/run_uef6_historical_validation.py` — RF-065
- `scripts/research/run_uef7_alpha_board_normalization.py` — RF-065
- `scripts/research/run_uef8_fair_comparison_validation.py` — RF-065
- `scripts/research/run_uef9_formal_authority.py` — RF-065
- `scripts/restart_live_session.bat` — RF-071
- `scripts/restart_live_session.ps1` — RF-071
- `scripts/restart_live_session.py` — RF-071
- `scripts/run_agent_effectiveness_scorecard.py` — RF-070
- `scripts/run_agent_pipeline_trace_report.py` — RF-070
- `scripts/run_ai_trade_report_batch.py` — RF-070
- `scripts/run_alpha_hypothesis_competition.py` — RF-070
- `scripts/run_alpha_research_board.py` — RF-070
- `scripts/run_attribution_score_range.py` — RF-070
- `scripts/run_attribution_score_window.py` — RF-070
- `scripts/run_baseline_btc_woori_tech.py` — RF-070
- `scripts/run_baseline_samsung_hynix.py` — RF-070
- `scripts/run_broker_trade_reconciliation.py` — RF-070
- `scripts/run_closeout_maintenance.bat` — RF-070
- `scripts/run_closeout_maintenance.py` — RF-070
- `scripts/run_commander_runtime_once.py` — RF-070
- `scripts/run_conditional_alpha_diagnosis.py` — RF-070
- `scripts/run_cumulative_improvement_review.py` — RF-070
- `scripts/run_daily_uef_evaluation.py` — RF-070
- `scripts/run_decision_story_report.py` — RF-070
- `scripts/run_evaluation_lens_report.py` — RF-070
- `scripts/run_existing_evidence_mining.py` — RF-070
- `scripts/run_frozen_q9_baseline_closeout.py` — RF-070
- `scripts/run_full_chain_component_review.py` — RF-070
- `scripts/run_historical_q9_prior.py` — RF-070
- `scripts/run_horizon_alignment_review.py` — RF-070
- `scripts/run_horizon_revision_backtest.py` — RF-070
- `scripts/run_integrated_trade_diagnosis.py` — RF-070
- `scripts/run_integrated_trade_validation.py` — RF-070
- `scripts/run_live_execution_bundle_report.py` — RF-070
- `scripts/run_live_loop.py` — RF-070
- `scripts/run_live_session_summary.py` — RF-070
- `scripts/run_live_session_watch.bat` — RF-070
- `scripts/run_live_session_watch.py` — RF-070
- `scripts/run_log_maintenance.py` — RF-070
- `scripts/run_loss_decomposition.py` — RF-070
- `scripts/run_m13_live_loop.py` — RF-070
- `scripts/run_m15_matrix.py` — RF-070
- `scripts/run_m22_closeout_check.py` — RF-070
- `scripts/run_m23_closeout_check.py` — RF-070
- `scripts/run_m23_resilience_closeout_check.py` — RF-070
- `scripts/run_m24_closeout_check.py` — RF-070
- `scripts/run_m24_guard_precedence_check.py` — RF-070
- `scripts/run_m25_closeout_check.py` — RF-070
- `scripts/run_m25_ops_batch.py` — RF-070
- `scripts/run_m26_ab_evaluation.py` — RF-070
- `scripts/run_m26_closeout_check.py` — RF-070
- `scripts/run_m26_dataset_manifest_check.py` — RF-070
- `scripts/run_m26_promotion_gate_check.py` — RF-070
- `scripts/run_m26_replay_runner.py` — RF-070
- `scripts/run_m26_scorecard.py` — RF-070
- `scripts/run_m27_allocation_policy_check.py` — RF-070
- `scripts/run_m27_closeout_check.py` — RF-070
- `scripts/run_m27_conflict_resolution_check.py` — RF-070
- `scripts/run_m27_portfolio_budget_boundary_check.py` — RF-070
- `scripts/run_m27_portfolio_guard_alert_policy_check.py` — RF-070
- `scripts/run_m27_portfolio_guard_metrics_check.py` — RF-070
- `scripts/run_m27_portfolio_guard_notify_check.py` — RF-070
- `scripts/run_m27_portfolio_guard_notify_query_check.py` — RF-070
- `scripts/run_m27_portfolio_guard_notify_routing_check.py` — RF-070
- `scripts/run_m27_runtime_portfolio_guard_check.py` — RF-070
- `scripts/run_m28_closeout_check.py` — RF-070
- `scripts/run_m28_deploy_launch_template_check.py` — RF-070
- `scripts/run_m28_launch_hook_integration_check.py` — RF-070
- `scripts/run_m28_registration_helper_check.py` — RF-070
- `scripts/run_m28_rollout_rollback_check.py` — RF-070
- `scripts/run_m28_runtime_lifecycle_hooks_check.py` — RF-070
- `scripts/run_m28_runtime_profile_scaffold_check.py` — RF-070
- `scripts/run_m28_scheduler_worker_launch_wrapper_check.py` — RF-070
- `scripts/run_m28_startup_preflight_check.py` — RF-070
- `scripts/run_m29_audit_trail_check.py` — RF-070
- `scripts/run_m29_closeout_check.py` — RF-070
- `scripts/run_m29_disaster_recovery_drill.py` — RF-070
- `scripts/run_m29_incident_timeline_check.py` — RF-070
- `scripts/run_m29_log_archive_integrity_check.py` — RF-070
- `scripts/run_m30_final_golive_signoff.py` — RF-070
- `scripts/run_m30_post_golive_monitoring_policy.py` — RF-070
- `scripts/run_m30_quality_gates_bundle.py` — RF-070
- `scripts/run_m30_release_signoff_checklist.py` — RF-070
- `scripts/run_m31_agent_chain_probe.py` — RF-070
- `scripts/run_m31_mock_exam_readiness_check.py` — RF-070
- `scripts/run_m31_mock_investor_exam_check.py` — RF-070
- `scripts/run_m31_slo_incident_review_check.py` — RF-070
- `scripts/run_m31_weekly_health_summary.py` — RF-070
- `scripts/run_market_regime_rail_review.py` — RF-070
- `scripts/run_memory_contamination_review.py` — RF-070
- `scripts/run_mock_exam_closeout.bat` — RF-070
- `scripts/run_mock_exam_day.py` — RF-070
- `scripts/run_mock_exam_preopen.bat` — RF-070
- `scripts/run_mock_exam_session.bat` — RF-070
- `scripts/run_mock_exam_session_probe.bat` — RF-070
- `scripts/run_mock_exam_session_simulated.bat` — RF-070
- `scripts/run_mock_exam_session_watchdog.bat` — RF-070
- `scripts/run_monitor_noop_attribution.py` — RF-070
- `scripts/run_offhours_full_trace_bundle.py` — RF-070
- `scripts/run_offhours_validation_loop.py` — RF-070
- `scripts/run_opening_macro_snapshot_collector.py` — RF-070
- `scripts/run_opening_rank1_deep_dive.py` — RF-070
- `scripts/run_opening_rank1_longitudinal.py` — RF-070
- `scripts/run_opening_rank1_shadow.py` — RF-070
- `scripts/run_operator_brief_batch.py` — RF-070
- `scripts/run_operator_daily_summary.py` — RF-070
- `scripts/run_operator_summary_mining.py` — RF-070
- `scripts/run_operator_ui.py` — RF-070
- `scripts/run_opportunity_engine_shadow.py` — RF-070
- `scripts/run_phase5_validation_bundle.py` — RF-070
- `scripts/run_post_exit_shadow_recap.py` — RF-070
- `scripts/run_post_reclaim_offline_research.py` — RF-070
- `scripts/run_pytest.cmd` — RF-070
- `scripts/run_pytest.ps1` — RF-070
- `scripts/run_pytest.py` — RF-070
- `scripts/run_q10_index_observation_collector.py` — RF-070
- `scripts/run_q12_btc_0855_capture.bat` — RF-070
- `scripts/run_q12_historical_policy_review.py` — RF-070
- `scripts/run_q13_q14_validation.py` — RF-070
- `scripts/run_q8_historical_review.py` — RF-070
- `scripts/run_q8_lane_decision_table.py` — RF-070
- `scripts/run_q8_shadow_blocker_review.py` — RF-070
- `scripts/run_q9_baseline_comparison.py` — RF-070
- `scripts/run_q9_evaluation.py` — RF-070
- `scripts/run_quant_trade_diagnosis.py` — RF-070
- `scripts/run_rank1_feature_mart.py` — RF-070
- `scripts/run_rank1_prospective_shadow.py` — RF-070
- `scripts/run_report_maintenance.py` — RF-070
- `scripts/run_reporter_analysis_report.py` — RF-070
- `scripts/run_run_card_report.py` — RF-070
- `scripts/run_same_symbol_sequence.py` — RF-070
- `scripts/run_scanner_alignment_root_cause_range.py` — RF-070
- `scripts/run_scheduled_intelligence.py` — RF-070
- `scripts/run_session.py` — RF-070
- `scripts/run_short_alpha_discriminator.py` — RF-070
- `scripts/run_stage2_authority_review.py` — RF-070
- `scripts/run_structural_alpha_batch1.py` — RF-070
- `scripts/run_structural_alpha_batch2.py` — RF-070
- `scripts/run_trade_explain_report.py` — RF-070
- `scripts/run_uef5_3_dual_run.py` — RF-070
- `scripts/run_uef5_historical_recompute.py` — RF-070
- `scripts/run_uef6_dedup_detection.py` — RF-070
- `scripts/run_uef6_historical_validation.py` — RF-070
- `scripts/run_uef7_alpha_board_normalization.py` — RF-070
- `scripts/run_uef8_fair_comparison_validation.py` — RF-070
- `scripts/run_uef9_formal_authority.py` — RF-070
- `scripts/smoke_m20_llm.py` — RF-071
- `scripts/smoke_m22_hydration.py` — RF-071
- `scripts/start_operator_ui.ps1` — RF-071
- `scripts/start_q12_preopen.ps1` — RF-071
- `scripts/start_trading_day.py` — RF-071
- `scripts/step5d_crash_reconciliation.py` — RF-071
- `scripts/stop_operator_ui.ps1` — RF-071
- `scripts/sync_legacy_brief_llm.py` — RF-071
- `scripts/sync_openrouter_model_catalog.py` — RF-071
- `scripts/unregister_mock_exam_tasks_example.bat` — RF-071
- `scripts/verify_uef_freeze_manifest.py` — RF-071

</details>

## 최종 판정
각 경로의 실행 소비자, side-effect, owner, keep/move/compat 결정, normal/-O 명령/exit·independent peer·integration SHA 필수 CI를 확보. 이력 도구는 보존·색인하면 DONE 후보이나 운영 런처 경로 변조는 금지. [T00](T00_TARGET_TREE.md), [D00](../../ENGINEERING_DELIVERY_POLICY.md), [STATUS](../plan/STATUS.md).
