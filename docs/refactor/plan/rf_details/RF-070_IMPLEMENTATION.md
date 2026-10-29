# RF-070 — 코드 구조/함수 재배치 설계 (T08)

## 실물 함수 RF-070
Source scripts/run_ai_trade_report_batch.py blob 72622e920f606f4607ec5590a59d1fe330023ee5, 547 LOC. Codex B.
- main(argv) L243–544 (302 lines): filesystem report generation, runtime-state read, output side effects and summaries coexist. Preserve public main argv/exit/output location. Do not blindly move entire main into new module.
- _classify_missing_story_input L118–151 (34): simple classifier; KEEP if single role. _resolve_output_paths L86–117 (32): output-path policy helper; KEEP. _build_parser L50–73 (24): CLI parser helper; KEEP.
- Pure extraction candidate: main's per-trade result/status dict projection, without artifact writes and global filesystem reads. TARGET scripts/report_batch_row_projection.py::build_trade_report_batch_row; exact pure statement-run must be marked from current main body by C03 before implementation. Preserve Korean text, json output and ordered skip/error branches. Use fake trade paths in tmp and normal targeted old/new test.
- All other root run_*.py launchers correctly delegating to internal owners are KEEP_OK; avoid migrating public entrypoints.


**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/02_DEVELOPING/CODEX_B/RF-070.md` blob `6e7bb13917b89cb20ae2b4fbc23da573cdbdfe0e`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 142개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `scripts/run_ai_trade_report_batch.py` | 24738 | `72622e920f606f4607ec5590a59d1fe330023ee5` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `scripts/run_ai_trade_report_batch_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `scripts/docker_healthcheck.py` → `scripts/docker_healthcheck.py` | 9485 | `4af77ef95b79` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/launch_with_preflight.py` → `scripts/launch_with_preflight.py` | 317 | `b5b4878ce47a` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/register_mock_exam_tasks_example.bat` → `scripts/register_mock_exam_tasks_example.bat` | 2182 | `c6d788dfca56` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_agent_effectiveness_scorecard.py` → `scripts/run_agent_effectiveness_scorecard.py` | 547 | `6e93af9ede6b` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_agent_pipeline_trace_report.py` → `scripts/run_agent_pipeline_trace_report.py` | 550 | `857e26f6af85` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_ai_trade_report_batch.py` → `scripts/run_ai_trade_report_batch.py` | 24738 | `72622e920f60` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_alpha_hypothesis_competition.py` → `scripts/run_alpha_hypothesis_competition.py` | 544 | `07345f9c8ce3` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_alpha_research_board.py` → `scripts/run_alpha_research_board.py` | 520 | `0d3d3eda47ba` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_attribution_score_range.py` → `scripts/run_attribution_score_range.py` | 529 | `a741eb112c54` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_attribution_score_window.py` → `scripts/run_attribution_score_window.py` | 532 | `93c3da963376` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_baseline_btc_woori_tech.py` → `scripts/run_baseline_btc_woori_tech.py` | 2263 | `bb9106874563` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_baseline_samsung_hynix.py` → `scripts/run_baseline_samsung_hynix.py` | 2029 | `4de2ba7b7cf0` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_broker_trade_reconciliation.py` → `scripts/run_broker_trade_reconciliation.py` | 550 | `129e3e7a9904` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_closeout_maintenance.bat` → `scripts/run_closeout_maintenance.bat` | 619 | `b18fef8f7910` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_closeout_maintenance.py` → `scripts/run_closeout_maintenance.py` | 7534 | `37e655ae6062` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_commander_runtime_once.py` → `scripts/run_commander_runtime_once.py` | 318 | `e46e180504c2` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_conditional_alpha_diagnosis.py` → `scripts/run_conditional_alpha_diagnosis.py` | 541 | `e1b3e3a4126d` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_cumulative_improvement_review.py` → `scripts/run_cumulative_improvement_review.py` | 547 | `3e696acdd8ec` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_daily_uef_evaluation.py` → `scripts/run_daily_uef_evaluation.py` | 6031 | `775228e00cdf` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_decision_story_report.py` → `scripts/run_decision_story_report.py` | 523 | `a18cc4bf5513` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_evaluation_lens_report.py` → `scripts/run_evaluation_lens_report.py` | 526 | `7fbee95af102` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_existing_evidence_mining.py` → `scripts/run_existing_evidence_mining.py` | 532 | `e6623f65ce33` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_frozen_q9_baseline_closeout.py` → `scripts/run_frozen_q9_baseline_closeout.py` | 541 | `2cd5f5f16c6b` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_full_chain_component_review.py` → `scripts/run_full_chain_component_review.py` | 541 | `5f43d58ce0be` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_historical_q9_prior.py` → `scripts/run_historical_q9_prior.py` | 517 | `d6863db08d2d` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_horizon_alignment_review.py` → `scripts/run_horizon_alignment_review.py` | 532 | `f981bc9c3fea` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_horizon_revision_backtest.py` → `scripts/run_horizon_revision_backtest.py` | 535 | `e83395d5b279` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_integrated_trade_diagnosis.py` → `scripts/run_integrated_trade_diagnosis.py` | 538 | `f0f82d35c099` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_integrated_trade_validation.py` → `scripts/run_integrated_trade_validation.py` | 541 | `a09417acf432` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_live_execution_bundle_report.py` → `scripts/run_live_execution_bundle_report.py` | 1522 | `49694a51eee9` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_live_loop.py` → `scripts/run_live_loop.py` | 439 | `81277c4e54ca` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_live_session_summary.py` → `scripts/run_live_session_summary.py` | 316 | `e0f248e6b43f` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_live_session_watch.bat` → `scripts/run_live_session_watch.bat` | 522 | `f6207e8d1dcf` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_live_session_watch.py` → `scripts/run_live_session_watch.py` | 514 | `b1da4f6e23bc` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_log_maintenance.py` → `scripts/run_log_maintenance.py` | 514 | `1c9b15af515d` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_loss_decomposition.py` → `scripts/run_loss_decomposition.py` | 514 | `f771e2ec9347` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m13_live_loop.py` → `scripts/run_m13_live_loop.py` | 331 | `9c843d92ed3f` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m15_matrix.py` → `scripts/run_m15_matrix.py` | 7472 | `8e98949db1a7` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m22_closeout_check.py` → `scripts/run_m22_closeout_check.py` | 523 | `7a06eab05043` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m23_closeout_check.py` → `scripts/run_m23_closeout_check.py` | 523 | `46678e41b5ce` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m23_resilience_closeout_check.py` → `scripts/run_m23_resilience_closeout_check.py` | 556 | `203f0f25c9fd` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m24_closeout_check.py` → `scripts/run_m24_closeout_check.py` | 523 | `68660a2b734d` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m24_guard_precedence_check.py` → `scripts/run_m24_guard_precedence_check.py` | 547 | `e9b9e64fec3e` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m25_closeout_check.py` → `scripts/run_m25_closeout_check.py` | 10700 | `1bb37e630efe` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m25_ops_batch.py` → `scripts/run_m25_ops_batch.py` | 13133 | `6a5dad15357a` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m26_ab_evaluation.py` → `scripts/run_m26_ab_evaluation.py` | 520 | `cad92d042f14` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m26_closeout_check.py` → `scripts/run_m26_closeout_check.py` | 523 | `4b5a1dca8c3f` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m26_dataset_manifest_check.py` → `scripts/run_m26_dataset_manifest_check.py` | 547 | `3d3fdaaaa5df` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m26_promotion_gate_check.py` → `scripts/run_m26_promotion_gate_check.py` | 541 | `4a2ddb4aa0b7` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m26_replay_runner.py` → `scripts/run_m26_replay_runner.py` | 520 | `a9f836bb89cb` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m26_scorecard.py` → `scripts/run_m26_scorecard.py` | 508 | `9fcaa34e66c6` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m27_allocation_policy_check.py` → `scripts/run_m27_allocation_policy_check.py` | 550 | `54eecb4fc313` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m27_closeout_check.py` → `scripts/run_m27_closeout_check.py` | 523 | `dd1ea5f1c4bb` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m27_conflict_resolution_check.py` → `scripts/run_m27_conflict_resolution_check.py` | 556 | `3f615b9fc972` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m27_portfolio_budget_boundary_check.py` → `scripts/run_m27_portfolio_budget_boundary_check.py` | 574 | `43d44cc37157` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m27_portfolio_guard_alert_policy_check.py` → `scripts/run_m27_portfolio_guard_alert_policy_check.py` | 583 | `e5d8a23eb1bf` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m27_portfolio_guard_metrics_check.py` → `scripts/run_m27_portfolio_guard_metrics_check.py` | 568 | `affb4cb4c5af` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m27_portfolio_guard_notify_check.py` → `scripts/run_m27_portfolio_guard_notify_check.py` | 565 | `8175176097e1` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m27_portfolio_guard_notify_query_check.py` → `scripts/run_m27_portfolio_guard_notify_query_check.py` | 583 | `e2cc0f256cba` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m27_portfolio_guard_notify_routing_check.py` → `scripts/run_m27_portfolio_guard_notify_routing_check.py` | 589 | `c32743ec2310` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m27_runtime_portfolio_guard_check.py` → `scripts/run_m27_runtime_portfolio_guard_check.py` | 568 | `62d603d67305` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m28_closeout_check.py` → `scripts/run_m28_closeout_check.py` | 523 | `9fb8181cd4a3` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m28_deploy_launch_template_check.py` → `scripts/run_m28_deploy_launch_template_check.py` | 565 | `8bda2b54018f` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m28_launch_hook_integration_check.py` → `scripts/run_m28_launch_hook_integration_check.py` | 568 | `7e7f81699c1f` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m28_registration_helper_check.py` → `scripts/run_m28_registration_helper_check.py` | 556 | `dcb13febdac4` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m28_rollout_rollback_check.py` → `scripts/run_m28_rollout_rollback_check.py` | 547 | `cc16a13c73bd` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m28_runtime_lifecycle_hooks_check.py` → `scripts/run_m28_runtime_lifecycle_hooks_check.py` | 568 | `cd539b762fd0` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m28_runtime_profile_scaffold_check.py` → `scripts/run_m28_runtime_profile_scaffold_check.py` | 571 | `3af55ec6c704` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m28_scheduler_worker_launch_wrapper_check.py` → `scripts/run_m28_scheduler_worker_launch_wrapper_check.py` | 592 | `5fbc1de6e464` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m28_startup_preflight_check.py` → `scripts/run_m28_startup_preflight_check.py` | 550 | `05a5b750c0f1` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m29_audit_trail_check.py` → `scripts/run_m29_audit_trail_check.py` | 532 | `3d9f4f04899b` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m29_closeout_check.py` → `scripts/run_m29_closeout_check.py` | 523 | `962f76de82b4` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m29_disaster_recovery_drill.py` → `scripts/run_m29_disaster_recovery_drill.py` | 550 | `db2e57b05cec` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m29_incident_timeline_check.py` → `scripts/run_m29_incident_timeline_check.py` | 550 | `0a0d6e14054b` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m29_log_archive_integrity_check.py` → `scripts/run_m29_log_archive_integrity_check.py` | 562 | `495823cd2983` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m30_final_golive_signoff.py` → `scripts/run_m30_final_golive_signoff.py` | 541 | `1b7ff9ab5a27` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m30_post_golive_monitoring_policy.py` → `scripts/run_m30_post_golive_monitoring_policy.py` | 568 | `b92ced7c3069` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m30_quality_gates_bundle.py` → `scripts/run_m30_quality_gates_bundle.py` | 541 | `6a6bf1de9d6b` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m30_release_signoff_checklist.py` → `scripts/run_m30_release_signoff_checklist.py` | 556 | `a48e758d2031` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m31_agent_chain_probe.py` → `scripts/run_m31_agent_chain_probe.py` | 532 | `0a7159d5e81d` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m31_mock_exam_readiness_check.py` → `scripts/run_m31_mock_exam_readiness_check.py` | 556 | `1a2cdbac9d66` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m31_mock_investor_exam_check.py` → `scripts/run_m31_mock_investor_exam_check.py` | 553 | `e012bf83286a` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m31_slo_incident_review_check.py` → `scripts/run_m31_slo_incident_review_check.py` | 556 | `e3410d91feb5` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_m31_weekly_health_summary.py` → `scripts/run_m31_weekly_health_summary.py` | 544 | `1752933c5aad` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_market_regime_rail_review.py` → `scripts/run_market_regime_rail_review.py` | 535 | `56fe73224efe` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_memory_contamination_review.py` → `scripts/run_memory_contamination_review.py` | 541 | `5f940ce05e73` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_mock_exam_closeout.bat` → `scripts/run_mock_exam_closeout.bat` | 375 | `7751a02e6ee6` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_mock_exam_day.py` → `scripts/run_mock_exam_day.py` | 309 | `e0dc9bed6be1` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_mock_exam_preopen.bat` → `scripts/run_mock_exam_preopen.bat` | 1200 | `6ec118bd4c2e` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_mock_exam_session.bat` → `scripts/run_mock_exam_session.bat` | 364 | `ee5cae00f48a` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_mock_exam_session_probe.bat` → `scripts/run_mock_exam_session_probe.bat` | 257 | `d8064d492a8e` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_mock_exam_session_simulated.bat` → `scripts/run_mock_exam_session_simulated.bat` | 119 | `8fdd162549c9` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_mock_exam_session_watchdog.bat` → `scripts/run_mock_exam_session_watchdog.bat` | 254 | `ce190ade65fb` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_monitor_noop_attribution.py` → `scripts/run_monitor_noop_attribution.py` | 532 | `7c838d0fb7ee` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_offhours_full_trace_bundle.py` → `scripts/run_offhours_full_trace_bundle.py` | 547 | `352e0e824e3e` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_offhours_validation_loop.py` → `scripts/run_offhours_validation_loop.py` | 532 | `5a19dda7246d` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_opening_macro_snapshot_collector.py` → `scripts/run_opening_macro_snapshot_collector.py` | 959 | `35a4c504ad2e` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_opening_rank1_deep_dive.py` → `scripts/run_opening_rank1_deep_dive.py` | 383 | `f1611bf0275b` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_opening_rank1_longitudinal.py` → `scripts/run_opening_rank1_longitudinal.py` | 538 | `bc3a6c5b618e` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_opening_rank1_shadow.py` → `scripts/run_opening_rank1_shadow.py` | 520 | `ba1bea665b9a` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_operator_brief_batch.py` → `scripts/run_operator_brief_batch.py` | 4680 | `93d4fbd74e61` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_operator_daily_summary.py` → `scripts/run_operator_daily_summary.py` | 2844 | `e750fb8d800c` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_operator_summary_mining.py` → `scripts/run_operator_summary_mining.py` | 529 | `0665a4801934` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_operator_ui.py` → `scripts/run_operator_ui.py` | 2275 | `c052a8632855` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_opportunity_engine_shadow.py` → `scripts/run_opportunity_engine_shadow.py` | 2076 | `50d878b9b7c2` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_phase5_validation_bundle.py` → `scripts/run_phase5_validation_bundle.py` | 532 | `90a372406275` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_post_exit_shadow_recap.py` → `scripts/run_post_exit_shadow_recap.py` | 526 | `6d3a4e581ffc` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_post_reclaim_offline_research.py` → `scripts/run_post_reclaim_offline_research.py` | 547 | `cac03067001f` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_pytest.cmd` → `scripts/run_pytest.cmd` | 159 | `cf6bcf14bf76` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_pytest.ps1` → `scripts/run_pytest.ps1` | 643 | `5603d9ee7be2` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_pytest.py` → `scripts/run_pytest.py` | 913 | `762041e9254c` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_q10_index_observation_collector.py` → `scripts/run_q10_index_observation_collector.py` | 1412 | `5511f199c94b` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_q12_btc_0855_capture.bat` → `scripts/run_q12_btc_0855_capture.bat` | 343 | `b591fc2fb013` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_q12_historical_policy_review.py` → `scripts/run_q12_historical_policy_review.py` | 544 | `c35aa7be50b0` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_q13_q14_validation.py` → `scripts/run_q13_q14_validation.py` | 514 | `559d7210c48a` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_q8_historical_review.py` → `scripts/run_q8_historical_review.py` | 520 | `c74c3958268d` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_q8_lane_decision_table.py` → `scripts/run_q8_lane_decision_table.py` | 526 | `20d5ac1b0c79` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_q8_shadow_blocker_review.py` → `scripts/run_q8_shadow_blocker_review.py` | 532 | `e88474ac40e4` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_q9_baseline_comparison.py` → `scripts/run_q9_baseline_comparison.py` | 526 | `023c4e3282b6` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_q9_evaluation.py` → `scripts/run_q9_evaluation.py` | 499 | `c8cc267aaa21` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_quant_trade_diagnosis.py` → `scripts/run_quant_trade_diagnosis.py` | 523 | `8e5a549c5cfa` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_rank1_feature_mart.py` → `scripts/run_rank1_feature_mart.py` | 514 | `f5330f81d3c4` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_rank1_prospective_shadow.py` → `scripts/run_rank1_prospective_shadow.py` | 532 | `94baf8429d48` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_report_maintenance.py` → `scripts/run_report_maintenance.py` | 523 | `846e0ec8ad4e` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_reporter_analysis_report.py` → `scripts/run_reporter_analysis_report.py` | 3597 | `73e87214a092` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_run_card_report.py` → `scripts/run_run_card_report.py` | 505 | `a2da21083773` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_same_symbol_sequence.py` → `scripts/run_same_symbol_sequence.py` | 520 | `f5fcf06e42eb` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_scanner_alignment_root_cause_range.py` → `scripts/run_scanner_alignment_root_cause_range.py` | 562 | `7367f593c146` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_scheduled_intelligence.py` → `scripts/run_scheduled_intelligence.py` | 1272 | `7c86d6eb1c64` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_session.py` → `scripts/run_session.py` | 13311 | `430a4d25cc6c` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_short_alpha_discriminator.py` → `scripts/run_short_alpha_discriminator.py` | 535 | `c0ea45904739` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_stage2_authority_review.py` → `scripts/run_stage2_authority_review.py` | 529 | `9a8f04839dc0` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_structural_alpha_batch1.py` → `scripts/run_structural_alpha_batch1.py` | 529 | `613f12561166` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_structural_alpha_batch2.py` → `scripts/run_structural_alpha_batch2.py` | 529 | `652d30a2dccf` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_trade_explain_report.py` → `scripts/run_trade_explain_report.py` | 520 | `f5114c05b3bb` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_uef5_3_dual_run.py` → `scripts/run_uef5_3_dual_run.py` | 505 | `9d4737d5d1fd` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_uef5_historical_recompute.py` → `scripts/run_uef5_historical_recompute.py` | 2318 | `72d6fbbac7db` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_uef6_dedup_detection.py` → `scripts/run_uef6_dedup_detection.py` | 520 | `9d95e8d5fd58` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_uef6_historical_validation.py` → `scripts/run_uef6_historical_validation.py` | 538 | `dd95cf000892` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_uef7_alpha_board_normalization.py` → `scripts/run_uef7_alpha_board_normalization.py` | 550 | `aa3dcf080d7f` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_uef8_fair_comparison_validation.py` → `scripts/run_uef8_fair_comparison_validation.py` | 553 | `512fbdabc308` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/run_uef9_formal_authority.py` → `scripts/run_uef9_formal_authority.py` | 523 | `3092ab2abe1c` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
