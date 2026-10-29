# RF-063 — 코드 구조/함수 재배치 설계 (T08)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/02_DEVELOPING/CODEX_B/RF-063.md` blob `83b2a5fbf16504769d10cd06631ff7cd3604ac76`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 76개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `scripts/diagnostics/check_trade_report_runtime_regression.py` | 23752 | `d320eb12a97e4d5a41a3f4ee3146edfa195c2b6f` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `scripts/diagnostics/check_trade_report_runtime_regression_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `scripts/diagnostics/__init__.py` → `scripts/diagnostics/__init__.py` | 80 | `3e353daf883a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/analyze_entry_blockers.py` → `scripts/diagnostics/analyze_entry_blockers.py` | 1981 | `4d343359ed95` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/audit_target_tree_compat.py` → `scripts/diagnostics/audit_target_tree_compat.py` | 6960 | `4fc3e7e12ace` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/audit_windows_launchers.py` → `scripts/diagnostics/audit_windows_launchers.py` | 9132 | `f9bf40b819f9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/benchmark_operator_visibility_memory.py` → `scripts/diagnostics/benchmark_operator_visibility_memory.py` | 14145 | `d4cb6717e52f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/check_alert_policy_v1.py` → `scripts/diagnostics/check_alert_policy_v1.py` | 11959 | `1dfc6fa273c6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/check_audit_trail_completeness.py` → `scripts/diagnostics/check_audit_trail_completeness.py` | 12311 | `1df9947a268f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/check_daily_uef_run_status.py` → `scripts/diagnostics/check_daily_uef_run_status.py` | 8402 | `4a648f346abf` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/check_log_archive_integrity.py` → `scripts/diagnostics/check_log_archive_integrity.py` | 8024 | `d1f0b80eb488` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/check_metrics_schema_v1.py` → `scripts/diagnostics/check_metrics_schema_v1.py` | 3615 | `2c493ba7ba5b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/check_monitor_gate_patterns.py` → `scripts/diagnostics/check_monitor_gate_patterns.py` | 15205 | `66c3af5614d0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/check_phase_5_2_5_3_runtime_health.py` → `scripts/diagnostics/check_phase_5_2_5_3_runtime_health.py` | 4445 | `e095bee3edae` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/check_profitability_recovery_day1.py` → `scripts/diagnostics/check_profitability_recovery_day1.py` | 1689 | `7014ecdaeae5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/check_q9_q12_readiness.py` → `scripts/diagnostics/check_q9_q12_readiness.py` | 12149 | `68349976f3e9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/check_real_execution_preflight.py` → `scripts/diagnostics/check_real_execution_preflight.py` | 1612 | `468ee8c6291c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/check_reporter_upgrade_regression.py` → `scripts/diagnostics/check_reporter_upgrade_regression.py` | 8995 | `ab585cf1618d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/check_reports_trades_health.py` → `scripts/diagnostics/check_reports_trades_health.py` | 11469 | `90853b7c3ec2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/check_runtime_profile.py` → `scripts/diagnostics/check_runtime_profile.py` | 317 | `4f54d8456897` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/check_trade_report_runtime_regression.py` → `scripts/diagnostics/check_trade_report_runtime_regression.py` | 23752 | `d320eb12a97e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/generate_m28_launch_templates.py` → `scripts/diagnostics/generate_m28_launch_templates.py` | 316 | `a5d753107ebc` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/generate_m28_registration_helpers.py` → `scripts/diagnostics/generate_m28_registration_helpers.py` | 320 | `a85b80282e6f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/generate_ops_diagnostic_report.py` → `scripts/diagnostics/generate_ops_diagnostic_report.py` | 13078 | `2e39f6482f09` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/query_commander_resilience_events.py` → `scripts/diagnostics/query_commander_resilience_events.py` | 6864 | `caebd5b1466a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/query_intent_state_store.py` → `scripts/diagnostics/query_intent_state_store.py` | 7959 | `4e4dc6b3d032` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/query_m25_notification_events.py` → `scripts/diagnostics/query_m25_notification_events.py` | 6371 | `ec1f122a6087` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/query_strategist_llm_events.py` → `scripts/diagnostics/query_strategist_llm_events.py` | 7570 | `c45516931dcb` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/query_trade_reason_chain.py` → `scripts/diagnostics/query_trade_reason_chain.py` | 9082 | `89ff494d90d9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/reconstruct_incident_timeline.py` → `scripts/diagnostics/reconstruct_incident_timeline.py` | 13437 | `c47b817cef0c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/run_agent_pipeline_trace_report.py` → `scripts/diagnostics/run_agent_pipeline_trace_report.py` | 2427 | `3a7ff4a2cb0a` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m22_closeout_check.py` → `scripts/diagnostics/run_m22_closeout_check.py` | 6221 | `898d8a38563a` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m23_closeout_check.py` → `scripts/diagnostics/run_m23_closeout_check.py` | 5426 | `fdde6c82bfc9` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m23_resilience_closeout_check.py` → `scripts/diagnostics/run_m23_resilience_closeout_check.py` | 6614 | `ac1769bf5ae4` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m24_closeout_check.py` → `scripts/diagnostics/run_m24_closeout_check.py` | 5805 | `50d26a9e72c5` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m24_guard_precedence_check.py` → `scripts/diagnostics/run_m24_guard_precedence_check.py` | 10004 | `0dc07534aab2` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m26_ab_evaluation.py` → `scripts/diagnostics/run_m26_ab_evaluation.py` | 8461 | `864f845cd2e6` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m26_closeout_check.py` → `scripts/diagnostics/run_m26_closeout_check.py` | 10697 | `4a87f8bdf0c1` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m26_dataset_manifest_check.py` → `scripts/diagnostics/run_m26_dataset_manifest_check.py` | 8638 | `a0afae27c395` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m26_promotion_gate_check.py` → `scripts/diagnostics/run_m26_promotion_gate_check.py` | 5801 | `0f36bcd74c9f` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m26_replay_runner.py` → `scripts/diagnostics/run_m26_replay_runner.py` | 8666 | `5fbf5c871588` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m26_scorecard.py` → `scripts/diagnostics/run_m26_scorecard.py` | 11539 | `da20247c7177` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m27_allocation_policy_check.py` → `scripts/diagnostics/run_m27_allocation_policy_check.py` | 3185 | `bb39094be47f` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m27_closeout_check.py` → `scripts/diagnostics/run_m27_closeout_check.py` | 8163 | `1f48a79ecff8` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m27_conflict_resolution_check.py` → `scripts/diagnostics/run_m27_conflict_resolution_check.py` | 4510 | `3d550fe97901` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m27_portfolio_budget_boundary_check.py` → `scripts/diagnostics/run_m27_portfolio_budget_boundary_check.py` | 5812 | `e8c050b18e8a` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m27_portfolio_guard_alert_policy_check.py` → `scripts/diagnostics/run_m27_portfolio_guard_alert_policy_check.py` | 6070 | `d340b7342257` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m27_portfolio_guard_metrics_check.py` → `scripts/diagnostics/run_m27_portfolio_guard_metrics_check.py` | 5030 | `f3751d59752b` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m27_portfolio_guard_notify_check.py` → `scripts/diagnostics/run_m27_portfolio_guard_notify_check.py` | 4316 | `c3e8678e2c57` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m27_portfolio_guard_notify_query_check.py` → `scripts/diagnostics/run_m27_portfolio_guard_notify_query_check.py` | 5206 | `9bdbd55e66cc` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m27_portfolio_guard_notify_routing_check.py` → `scripts/diagnostics/run_m27_portfolio_guard_notify_routing_check.py` | 3645 | `00c44050c0c9` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m27_runtime_portfolio_guard_check.py` → `scripts/diagnostics/run_m27_runtime_portfolio_guard_check.py` | 6593 | `4cae92c3e054` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m28_closeout_check.py` → `scripts/diagnostics/run_m28_closeout_check.py` | 314 | `9119936d8524` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m28_deploy_launch_template_check.py` → `scripts/diagnostics/run_m28_deploy_launch_template_check.py` | 328 | `919b8b510c18` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m28_launch_hook_integration_check.py` → `scripts/diagnostics/run_m28_launch_hook_integration_check.py` | 329 | `9491c6db48ff` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m28_registration_helper_check.py` → `scripts/diagnostics/run_m28_registration_helper_check.py` | 325 | `1e7c66fd9b7b` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m28_rollout_rollback_check.py` → `scripts/diagnostics/run_m28_rollout_rollback_check.py` | 322 | `eade3a22a5e2` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m28_runtime_lifecycle_hooks_check.py` → `scripts/diagnostics/run_m28_runtime_lifecycle_hooks_check.py` | 329 | `71ff5a5e2b2f` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m28_runtime_profile_scaffold_check.py` → `scripts/diagnostics/run_m28_runtime_profile_scaffold_check.py` | 330 | `3da6c59af90b` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m28_scheduler_worker_launch_wrapper_check.py` → `scripts/diagnostics/run_m28_scheduler_worker_launch_wrapper_check.py` | 337 | `7f7197add746` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m28_startup_preflight_check.py` → `scripts/diagnostics/run_m28_startup_preflight_check.py` | 323 | `a3d81e20b308` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m29_audit_trail_check.py` → `scripts/diagnostics/run_m29_audit_trail_check.py` | 10409 | `f5fc3a2801c3` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m29_closeout_check.py` → `scripts/diagnostics/run_m29_closeout_check.py` | 7470 | `ac491cb4ec89` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m29_disaster_recovery_drill.py` → `scripts/diagnostics/run_m29_disaster_recovery_drill.py` | 11948 | `a8a340b97a61` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m29_incident_timeline_check.py` → `scripts/diagnostics/run_m29_incident_timeline_check.py` | 7786 | `780a678e8c37` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m29_log_archive_integrity_check.py` → `scripts/diagnostics/run_m29_log_archive_integrity_check.py` | 7725 | `630c3ec0f0cc` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m30_final_golive_signoff.py` → `scripts/diagnostics/run_m30_final_golive_signoff.py` | 9423 | `20c5ba5c9d94` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m30_post_golive_monitoring_policy.py` → `scripts/diagnostics/run_m30_post_golive_monitoring_policy.py` | 9974 | `589258e35c4c` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m30_quality_gates_bundle.py` → `scripts/diagnostics/run_m30_quality_gates_bundle.py` | 8887 | `6cb8fe651fd2` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m30_release_signoff_checklist.py` → `scripts/diagnostics/run_m30_release_signoff_checklist.py` | 9897 | `b9bcdba3e46d` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m31_agent_chain_probe.py` → `scripts/diagnostics/run_m31_agent_chain_probe.py` | 317 | `61a7b16844ec` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m31_mock_exam_readiness_check.py` → `scripts/diagnostics/run_m31_mock_exam_readiness_check.py` | 14712 | `721630febbfa` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m31_mock_investor_exam_check.py` → `scripts/diagnostics/run_m31_mock_investor_exam_check.py` | 16810 | `e4e7e5c56a04` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m31_slo_incident_review_check.py` → `scripts/diagnostics/run_m31_slo_incident_review_check.py` | 15348 | `e70a3e791dcc` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_m31_weekly_health_summary.py` → `scripts/diagnostics/run_m31_weekly_health_summary.py` | 13605 | `1a9d7fb0e803` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/run_offhours_full_trace_bundle.py` → `scripts/diagnostics/run_offhours_full_trace_bundle.py` | 12770 | `4161d643ddaf` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/diagnostics/smoke_m20_llm.py` → `scripts/diagnostics/smoke_m20_llm.py` | 5736 | `2fd95adef7bc` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/diagnostics/smoke_m22_hydration.py` → `scripts/diagnostics/smoke_m22_hydration.py` | 2570 | `3ab6d2e3eb5a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
