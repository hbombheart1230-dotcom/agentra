# RF-085 — 코드 구조/함수 재배치 설계 (T06)

## T06 operational documentation KEEP reason
Existing operations, runtime, commander control and observability runbook references are intentionally located by domain. Preserve absolute/relative links, incident history and consumer path. Correct single-owner, linked file is KEEP_OK with reason+blob. No code function extraction; no operational process starts or A/B documentation edits.


**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-085.md` blob `fc9367abb7bbdd5bfd0abf63f4fc427f9330adeb`.
**구현 담당:** **Claude A**, 상대 **Codex B**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 104개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `docs/commander_control/README.md` → `docs/commander_control/README.md` | 7361 | `954c0b13d995` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/commander_control/carry_control_model_2026-04-20.md` → `docs/commander_control/carry_control_model_2026-04-20.md` | 4955 | `c87cd1aee533` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/commander_control/carry_control_status_2026-04-20.md` → `docs/commander_control/carry_control_status_2026-04-20.md` | 6674 | `57ccc1da8de8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/commander_control/commander_memory_authority_2026-04-21.md` → `docs/commander_control/commander_memory_authority_2026-04-21.md` | 4335 | `3672c3a90a94` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/commander_control/commander_position_management_policy_2026-04-20.md` → `docs/commander_control/commander_position_management_policy_2026-04-20.md` | 3107 | `8c0bdc815fe0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/commander_control/daily_profit_guard_policy_draft_2026-05-11.md` → `docs/commander_control/daily_profit_guard_policy_draft_2026-05-11.md` | 6085 | `e41303c99e0e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/commander_control/duplicate_buy_and_closeout_guard_2026-04-29.md` → `docs/commander_control/duplicate_buy_and_closeout_guard_2026-04-29.md` | 3717 | `46470b27290a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/commander_control/entry_participation_control_2026-04-27.md` → `docs/commander_control/entry_participation_control_2026-04-27.md` | 9059 | `95369d50ef34` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/commander_control/market_representative_guard_2026-04-28.md` → `docs/commander_control/market_representative_guard_2026-04-28.md` | 3038 | `d133bf76d5e0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/commander_control/monitor_memory_bias_2026-04-21.md` → `docs/commander_control/monitor_memory_bias_2026-04-21.md` | 5433 | `416493d5c507` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/commander_control/scanner_memory_bias_2026-04-21.md` → `docs/commander_control/scanner_memory_bias_2026-04-21.md` | 4414 | `f8568689aa04` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/common_stock_only_universe_close_2026_04_10.md` → `docs/execution_plan/common_stock_only_universe_close_2026_04_10.md` | 3465 | `27a6ac6e1da9` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/entry_blocker_analysis_read_model_close_2026_04_10.md` → `docs/execution_plan/entry_blocker_analysis_read_model_close_2026_04_10.md` | 3122 | `5057b326e6ba` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/entry_blocker_family_breakdown_close_2026_04_11.md` → `docs/execution_plan/entry_blocker_family_breakdown_close_2026_04_11.md` | 2753 | `e1a8ec72718a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/env_minimization_policy.md` → `docs/execution_plan/env_minimization_policy.md` | 7895 | `67f845f4621c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/final_alignment_review_phase_5_4_to_6_2.md` → `docs/execution_plan/final_alignment_review_phase_5_4_to_6_2.md` | 2896 | `e05ec1317e8d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/intraday_report_bundle_single_instance_close_2026_04_13.md` → `docs/execution_plan/intraday_report_bundle_single_instance_close_2026_04_13.md` | 4649 | `2db1ace448c8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/late_session_entry_cutoff_close_2026_04_11.md` → `docs/execution_plan/late_session_entry_cutoff_close_2026_04_11.md` | 2621 | `3aa183ae79a0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/llm_model_policy.md` → `docs/execution_plan/llm_model_policy.md` | 3594 | `a6928f21e2ad` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/narrative_axis_display_policy_2026_04_08.md` → `docs/execution_plan/narrative_axis_display_policy_2026_04_08.md` | 1620 | `bb527f8e59de` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/phase_5_3_2_close_note.md` → `docs/execution_plan/phase_5_3_2_close_note.md` | 10453 | `68656c126d62` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/phase_5_4_closeout.md` → `docs/execution_plan/phase_5_4_closeout.md` | 2254 | `1ffa0bce4b3c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/phase_5_4_codex_tasks.md` → `docs/execution_plan/phase_5_4_codex_tasks.md` | 14252 | `fef70913bfdc` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/phase_5_4_execution_plan.md` → `docs/execution_plan/phase_5_4_execution_plan.md` | 18376 | `58eebe060b62` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/phase_6_1_closeout.md` → `docs/execution_plan/phase_6_1_closeout.md` | 1989 | `af974969285e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/phase_6_2_closeout.md` → `docs/execution_plan/phase_6_2_closeout.md` | 2356 | `39b3de2b4d61` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/phase_6_execution_plan.md` → `docs/execution_plan/phase_6_execution_plan.md` | 2094 | `84a8bbadde9f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/profitability_recovery_day1_diagnostics_close_2026_04_14.md` → `docs/execution_plan/profitability_recovery_day1_diagnostics_close_2026_04_14.md` | 3002 | `2c1829d279c6` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/reclaim_small_tuning_close_2026_04_11.md` → `docs/execution_plan/reclaim_small_tuning_close_2026_04_11.md` | 3837 | `59b2dc3a096f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/report_model_env_cleanup_note.md` → `docs/execution_plan/report_model_env_cleanup_note.md` | 3388 | `b701d80046d1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/report_source_alignment_patch_2026_04_08.md` → `docs/execution_plan/report_source_alignment_patch_2026_04_08.md` | 2121 | `6c05d0f28210` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/runtime_entrypoint_unification.md` → `docs/execution_plan/runtime_entrypoint_unification.md` | 2651 | `453ee3a4039e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/scanner_asset_resolver_normalization_close_2026_04_10.md` → `docs/execution_plan/scanner_asset_resolver_normalization_close_2026_04_10.md` | 3869 | `1bebb5677408` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/execution_plan/strategist_llm_guide.md` → `docs/execution_plan/strategist_llm_guide.md` | 2498 | `0106045ff81f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/kiwoom_truth/README.md` → `docs/kiwoom_truth/README.md` | 3512 | `8e79dee0388c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/kiwoom_truth/kiwoom_data_target_map_2026-04-20.md` → `docs/kiwoom_truth/kiwoom_data_target_map_2026-04-20.md` | 6000 | `c736ea8ad017` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/kiwoom_truth/kiwoom_role_inventory_2026-04-20.md` → `docs/kiwoom_truth/kiwoom_role_inventory_2026-04-20.md` | 5069 | `5c79217a7171` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/kiwoom_truth/kiwoom_scanner_strategist_inventory_2026-04-20.md` → `docs/kiwoom_truth/kiwoom_scanner_strategist_inventory_2026-04-20.md` | 5171 | `ed1a85098d71` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/kiwoom_truth/kiwoom_theme_api_strategy_selection_2026-04-28.md` → `docs/kiwoom_truth/kiwoom_theme_api_strategy_selection_2026-04-28.md` | 4579 | `37d2da8d0220` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/kiwoom_truth/kiwoom_theme_strength_packet_2026-04-27.md` → `docs/kiwoom_truth/kiwoom_theme_strength_packet_2026-04-27.md` | 4572 | `c8b9585d6bdb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/kiwoom_truth/kiwoom_truth_alignment_plan_2026-04-20.md` → `docs/kiwoom_truth/kiwoom_truth_alignment_plan_2026-04-20.md` | 6790 | `f38fb08f3f2f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/kiwoom_truth/kiwoom_truth_current_state_2026-04-20.md` → `docs/kiwoom_truth/kiwoom_truth_current_state_2026-04-20.md` | 9790 | `79127bd35eeb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/kiwoom_truth/kiwoom_truth_next_steps_2026-04-21.md` → `docs/kiwoom_truth/kiwoom_truth_next_steps_2026-04-21.md` | 2069 | `18d8ac054b98` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/observability/evidence_ledger.md` → `docs/observability/evidence_ledger.md` | 1798 | `d364aa869d59` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/operations/2026-09-15_Live_Run_AMBER.md` → `docs/operations/2026-09-15_Live_Run_AMBER.md` | 1363 | `429217ec64eb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime/agent_visibility_runbook.md` → `docs/runtime/agent_visibility_runbook.md` | 8672 | `4d0bd89e9f3d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime/alert_policy_runbook.md` → `docs/runtime/alert_policy_runbook.md` | 5443 | `ee8b133cc507` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime/live_session_process_observation_2026_04_10.md` → `docs/runtime/live_session_process_observation_2026_04_10.md` | 2487 | `dcbfaf00cf1b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime/log_management.md` → `docs/runtime/log_management.md` | 1120 | `c2306896a747` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime/m31_mock_session_monitoring_template.md` → `docs/runtime/m31_mock_session_monitoring_template.md` | 3528 | `7897e8338a3b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime/mock_exam_day_dry_run_runbook.md` → `docs/runtime/mock_exam_day_dry_run_runbook.md` | 6283 | `023c65bdb7c2` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime/report_management.md` → `docs/runtime/report_management.md` | 3251 | `2d36a2d96151` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime/runtime.md` → `docs/runtime/runtime.md` | 16195 | `c9913f579891` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime/runtime_lifecycle_runbook.md` → `docs/runtime/runtime_lifecycle_runbook.md` | 1094 | `32284cce74af` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime/runtime_profile_runbook.md` → `docs/runtime/runtime_profile_runbook.md` | 1324 | `6342cd8523fe` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime/session_process_consolidation_plan.md` → `docs/runtime/session_process_consolidation_plan.md` | 2585 | `8cd9af3cb895` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime/state_contract.md` → `docs/runtime/state_contract.md` | 1319 | `a944bfb679b7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_entrypoint/README.md` → `docs/runtime_entrypoint/README.md` | 3090 | `ab3d2b3a643e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_entrypoint/current_validation_status_2026-04-28.md` → `docs/runtime_entrypoint/current_validation_status_2026-04-28.md` | 6988 | `e56accbc4b5a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_entrypoint/live_validation_checklist_2026-04-28.md` → `docs/runtime_entrypoint/live_validation_checklist_2026-04-28.md` | 7055 | `17de2bf4f8f6` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_entrypoint/m13_live_boundary_audit_2026-04-19.md` → `docs/runtime_entrypoint/m13_live_boundary_audit_2026-04-19.md` | 4306 | `97d548b13f9e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_entrypoint/preopen_readiness_2026-04-29.md` → `docs/runtime_entrypoint/preopen_readiness_2026-04-29.md` | 3188 | `63332d42fc00` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_entrypoint/process_launch_modes_2026-04-19.md` → `docs/runtime_entrypoint/process_launch_modes_2026-04-19.md` | 1958 | `904d98aa3a10` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_entrypoint/strategy_conservatism_review_2026-04-29.md` → `docs/runtime_entrypoint/strategy_conservatism_review_2026-04-29.md` | 10750 | `e3fd234d90ea` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/README.md` → `docs/runtime_memory/README.md` | 14989 | `fcbc26999033` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/daily_summary_2026-04-28.md` → `docs/runtime_memory/daily_summary_2026-04-28.md` | 947 | `4ede30d0c236` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/historical_memory_impact_review_2026-08-13.md` → `docs/runtime_memory/historical_memory_impact_review_2026-08-13.md` | 6408 | `70d7a617f96b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/market_memory_contract_2026-04-19.md` → `docs/runtime_memory/market_memory_contract_2026-04-19.md` | 4330 | `9d2f0771b3ae` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/memory_flow_contract_2026-04-19.md` → `docs/runtime_memory/memory_flow_contract_2026-04-19.md` | 4151 | `f257afed363f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/memory_integrity_cleanup_2026-07-30.md` → `docs/runtime_memory/memory_integrity_cleanup_2026-07-30.md` | 4842 | `6306f3183b6b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/memory_integrity_correction_2026-08-13.md` → `docs/runtime_memory/memory_integrity_correction_2026-08-13.md` | 2935 | `2a67a79f2806` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/memory_packet_schema_2026-04-21.md` → `docs/runtime_memory/memory_packet_schema_2026-04-21.md` | 8127 | `7e5fe351a2e4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/monthly_summary_2026-04.md` → `docs/runtime_memory/monthly_summary_2026-04.md` | 871 | `2d275b0a5bb7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/operator_summary_memory_linkage_2026-04-28.md` → `docs/runtime_memory/operator_summary_memory_linkage_2026-04-28.md` | 5901 | `a6ffa228892a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/position_refresh_contract_2026-04-19.md` → `docs/runtime_memory/position_refresh_contract_2026-04-19.md` | 3629 | `9211137fa109` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/preopen_validation_checklist_2026-04-24.md` → `docs/runtime_memory/preopen_validation_checklist_2026-04-24.md` | 3276 | `2825e5cd0c1c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/reports_usage_matrix_2026-04-19.md` → `docs/runtime_memory/reports_usage_matrix_2026-04-19.md` | 11539 | `316597b00d6d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/script_and_report_reduction_policy_2026-04-19.md` → `docs/runtime_memory/script_and_report_reduction_policy_2026-04-19.md` | 4173 | `6477dbcb2e80` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/strategist_memory_packet_visibility_2026-04-20.md` → `docs/runtime_memory/strategist_memory_packet_visibility_2026-04-20.md` | 12350 | `212bc9d647d4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/symbol_memory_contract_2026-04-19.md` → `docs/runtime_memory/symbol_memory_contract_2026-04-19.md` | 4345 | `46f5c1bde437` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/symbol_memory_redefinition_plan_2026-04-19.md` → `docs/runtime_memory/symbol_memory_redefinition_plan_2026-04-19.md` | 7685 | `0a143845f70b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/symbol_read_model_alignment_2026-04-19.md` → `docs/runtime_memory/symbol_read_model_alignment_2026-04-19.md` | 5003 | `e675a4a2479a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/symbol_summary_000660.md` → `docs/runtime_memory/symbol_summary_000660.md` | 780 | `017118bd0955` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/runtime_memory/weekly_summary_2026-W17.md` → `docs/runtime_memory/weekly_summary_2026-W17.md` | 893 | `b84457ad2147` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/README.md` → `docs/web_observability/README.md` | 5174 | `bbb6dba82cb6` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/combined_milestone_plan_2026-08-14.md` → `docs/web_observability/combined_milestone_plan_2026-08-14.md` | 19693 | `7a248b5a551b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/implementation_status_2026-08-14.md` → `docs/web_observability/implementation_status_2026-08-14.md` | 13973 | `19e93cf564d3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/isolation_and_modularity_contract.md` → `docs/web_observability/isolation_and_modularity_contract.md` | 8065 | `968846ab3fbd` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/m2_source_audit_2026-08-14.md` → `docs/web_observability/m2_source_audit_2026-08-14.md` | 2967 | `3465d39e5572` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/m3_trade_source_audit_2026-08-14.md` → `docs/web_observability/m3_trade_source_audit_2026-08-14.md` | 3281 | `6a8163767f06` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/m4_opportunity_strategy_market_source_audit_2026-08-14.md` → `docs/web_observability/m4_opportunity_strategy_market_source_audit_2026-08-14.md` | 4052 | `7cc8dc7c3a51` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/m5_1_llm_operations_implementation_2026-08-14.md` → `docs/web_observability/m5_1_llm_operations_implementation_2026-08-14.md` | 2775 | `6551055e3045` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/m5_web_ui_implementation_2026-08-14.md` → `docs/web_observability/m5_web_ui_implementation_2026-08-14.md` | 3898 | `f28b3250bd1d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/m6_anomaly_public_profile_implementation_2026-08-14.md` → `docs/web_observability/m6_anomaly_public_profile_implementation_2026-08-14.md` | 4218 | `e3243fcb0423` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/m7_1_main_runtime_visibility_2026-08-27.md` → `docs/web_observability/m7_1_main_runtime_visibility_2026-08-27.md` | 3467 | `295aa3100b91` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/m7_2_host_supervisor_2026-08-27.md` → `docs/web_observability/m7_2_host_supervisor_2026-08-27.md` | 3789 | `1837d2f916f4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/m7_3_scheduled_intelligence_2026-08-27.md` → `docs/web_observability/m7_3_scheduled_intelligence_2026-08-27.md` | 4284 | `78550a8458fd` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/m7_4_cloudflare_private_ingress_2026-08-29.md` → `docs/web_observability/m7_4_cloudflare_private_ingress_2026-08-29.md` | 2902 | `5da50805a749` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/m7_5_operations_command_center_2026-08-30.md` → `docs/web_observability/m7_5_operations_command_center_2026-08-30.md` | 1619 | `caccb1bbe88a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/m7_docker_compose_implementation_2026-08-18.md` → `docs/web_observability/m7_docker_compose_implementation_2026-08-18.md` | 4763 | `4eef93db2939` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/m7_engine_gate_2026-08-26.md` → `docs/web_observability/m7_engine_gate_2026-08-26.md` | 4295 | `b6ace930bfaf` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/m7_prerequisites_and_weekend_plan_2026-08-14.md` → `docs/web_observability/m7_prerequisites_and_weekend_plan_2026-08-14.md` | 4252 | `22c766251561` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/product_data_contract_v1.md` → `docs/web_observability/product_data_contract_v1.md` | 5643 | `11d94426c50d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/web_observability/read_only_ui_docker_kubernetes_review_2026-08-14.md` → `docs/web_observability/read_only_ui_docker_kubernetes_review_2026-08-14.md` | 23397 | `497d49bc8c3b` | KEEP_IF: 문서 참조·경로·내용 정본 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
