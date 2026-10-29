# RF-083 — 코드 구조/함수 재배치 설계 (T06)

## Confirmed T06 status (2026-10-29)
Existing historical docs remain in their canonical topic directories. No Python function extraction applies. Correct path, authoritativeness and links give KEEP_OK(path, reason, source SHA) once. A/B do not edit documents; lead handles any actual link correction.


**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-083.md` blob `ca5fb953058189634a40877ec7a4990c79719677`.
**구현 담당:** **Claude A**, 상대 **Codex B**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 60개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `docs/report_plan/commander_env_migration_phase1.md` → `docs/report_plan/commander_env_migration_phase1.md` | 3130 | `7c70728f188f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/report_plan/commander_env_migration_phase2.md` → `docs/report_plan/commander_env_migration_phase2.md` | 2665 | `f865f686e363` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/report_plan/commander_env_migration_phase_scanner_fallback.md` → `docs/report_plan/commander_env_migration_phase_scanner_fallback.md` | 2230 | `95af736ea793` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/report_plan/commander_env_migration_plan.md` → `docs/report_plan/commander_env_migration_plan.md` | 2550 | `4029d8564ad3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/report_plan/commander_llm_execution_profile_migration_phase4.md` → `docs/report_plan/commander_llm_execution_profile_migration_phase4.md` | 3008 | `b36b57f99b6e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/report_plan/commander_llm_profile_migration_phase3.md` → `docs/report_plan/commander_llm_profile_migration_phase3.md` | 1514 | `c5862f8f6cf9` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/report_plan/env_rules.md` → `docs/report_plan/env_rules.md` | 1356 | `c8f4b67e739e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/report_plan/final_exit_thresholds_consumer_audit_2026_04_09.md` → `docs/report_plan/final_exit_thresholds_consumer_audit_2026_04_09.md` | 3064 | `6b79bb6edda3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/report_plan/post_patch_live_review_2026_04_09.md` → `docs/report_plan/post_patch_live_review_2026_04_09.md` | 3063 | `999bd5a648c5` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/report_plan/report_plan.md` → `docs/report_plan/report_plan.md` | 4177 | `dd6337f8d9e1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/report_plan/reporter_commander_hooks_phase4.md` → `docs/report_plan/reporter_commander_hooks_phase4.md` | 1807 | `873b85a25588` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/report_plan/reporter_feedback_mode_ownership_phase7.md` → `docs/report_plan/reporter_feedback_mode_ownership_phase7.md` | 1676 | `9632760fc67c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/report_plan/reporter_io_contracts_phase2.md` → `docs/report_plan/reporter_io_contracts_phase2.md` | 2251 | `30373def1f29` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/report_plan/reporter_thin_wrappers_phase3.md` → `docs/report_plan/reporter_thin_wrappers_phase3.md` | 1354 | `1c95fc493d6c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/report_plan/strategist_feedback_consumption_phase6.md` → `docs/report_plan/strategist_feedback_consumption_phase6.md` | 1509 | `45aa4f35f367` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/report_plan/strategist_feedback_packet_phase5.md` → `docs/report_plan/strategist_feedback_packet_phase5.md` | 1278 | `8c66de0d91ba` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/report_upgrade_plan/reporter_agentification_execution_plan_2026-04-15.md` → `docs/report_upgrade_plan/reporter_agentification_execution_plan_2026-04-15.md` | 15690 | `f54193fd0e74` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/report_upgrade_plan/reporter_pre_recovery_stabilization_plan_2026-04-15.md` → `docs/report_upgrade_plan/reporter_pre_recovery_stabilization_plan_2026-04-15.md` | 6169 | `1e818e7b46bb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/report_upgrade_plan/reporter_upgrade_execution_close_2026-04-15.md` → `docs/report_upgrade_plan/reporter_upgrade_execution_close_2026-04-15.md` | 3125 | `bd1022f9d401` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategist_output/README.md` → `docs/strategist_output/README.md` | 5159 | `93d07c6bf532` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategist_output/news_query_target_flow_2026-04-28.md` → `docs/strategist_output/news_query_target_flow_2026-04-28.md` | 2451 | `cfbb881ecf34` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategist_output/strategist_explanation_contract_2026-04-25.md` → `docs/strategist_output/strategist_explanation_contract_2026-04-25.md` | 14282 | `5ac227c85ecb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategist_output/strategist_llm_summary_artifact_2026-04-28.md` → `docs/strategist_output/strategist_llm_summary_artifact_2026-04-28.md` | 4540 | `17b5908112e5` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategist_output/strategy_detail_candidate_watch_policy_2026-05-06.md` → `docs/strategist_output/strategy_detail_candidate_watch_policy_2026-05-06.md` | 14549 | `a0f6db7e072b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategy_horizon_feedback/README.md` → `docs/strategy_horizon_feedback/README.md` | 8594 | `843dd03a6f0d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategy_horizon_feedback/horizon_operational_contract_fix_2026-07-24.md` → `docs/strategy_horizon_feedback/horizon_operational_contract_fix_2026-07-24.md` | 3125 | `c344dcdba25b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategy_horizon_feedback/horizon_slot_one_symbol_policy_2026-05-08.md` → `docs/strategy_horizon_feedback/horizon_slot_one_symbol_policy_2026-05-08.md` | 6711 | `442520558700` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategy_horizon_feedback/horizon_slot_report_layout_2026-05-08.md` → `docs/strategy_horizon_feedback/horizon_slot_report_layout_2026-05-08.md` | 5438 | `cf91e17bd2b0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategy_horizon_feedback/llm_reports_4stage_summary_layout_2026-05-08.md` → `docs/strategy_horizon_feedback/llm_reports_4stage_summary_layout_2026-05-08.md` | 2916 | `9ecff2020bce` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategy_horizon_feedback/monitor_chart_logic_review_2026-05-11.md` → `docs/strategy_horizon_feedback/monitor_chart_logic_review_2026-05-11.md` | 2953 | `89d0544d0206` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategy_horizon_feedback/multi_position_minimal_patch_plan_2026-05-08.md` → `docs/strategy_horizon_feedback/multi_position_minimal_patch_plan_2026-05-08.md` | 7503 | `18f8947a059c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategy_horizon_feedback/position_horizon_revision_contract_2026-08-05.md` → `docs/strategy_horizon_feedback/position_horizon_revision_contract_2026-08-05.md` | 3744 | `a15eac1148ee` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategy_horizon_feedback/scanner_monitor_chart_reading_runtime_alignment_2026-05-12.md` → `docs/strategy_horizon_feedback/scanner_monitor_chart_reading_runtime_alignment_2026-05-12.md` | 3640 | `6b942b5fc029` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategy_horizon_feedback/scanner_monitor_role_boundary_patch_plan_2026-05-11.md` → `docs/strategy_horizon_feedback/scanner_monitor_role_boundary_patch_plan_2026-05-11.md` | 6963 | `e26f7981a5c4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategy_horizon_feedback/strategist_4stage_chat_prompt_templates_2026-05-08.md` → `docs/strategy_horizon_feedback/strategist_4stage_chat_prompt_templates_2026-05-08.md` | 15586 | `be57b36a1473` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategy_horizon_feedback/strategist_4stage_llm_flow_draft_2026-05-08.md` → `docs/strategy_horizon_feedback/strategist_4stage_llm_flow_draft_2026-05-08.md` | 33082 | `8a43403268f8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategy_horizon_feedback/strategy_horizon_and_post_exit_shadow_tracking_2026-04-25.md` → `docs/strategy_horizon_feedback/strategy_horizon_and_post_exit_shadow_tracking_2026-04-25.md` | 13026 | `f2a120ef8fa9` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategy_horizon_feedback/strategy_horizon_report_visibility_and_patch_priority_2026-05-11.md` → `docs/strategy_horizon_feedback/strategy_horizon_report_visibility_and_patch_priority_2026-05-11.md` | 8180 | `7469d1e2bcad` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/strategy_horizon_feedback/two_slot_runtime_patch_plan_2026-05-08.md` → `docs/strategy_horizon_feedback/two_slot_runtime_patch_plan_2026-05-08.md` | 13037 | `6fd9aba49ada` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/README.md` → `docs/trade_report_plan/README.md` | 5234 | `edca0e700564` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/ai_trade_report_improvement_plan_2026-04-15.md` → `docs/trade_report_plan/ai_trade_report_improvement_plan_2026-04-15.md` | 8609 | `6ae1a8c0e2f0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/ai_trade_report_operator_readability_improvement_20260428.md` → `docs/trade_report_plan/ai_trade_report_operator_readability_improvement_20260428.md` | 23464 | `f9c78cc3f849` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/ai_trade_report_runtime_debug_2026-04-21.md` → `docs/trade_report_plan/ai_trade_report_runtime_debug_2026-04-21.md` | 3569 | `de90f4d46f3c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/ai_trade_report_target_example_2026-04-15.md` → `docs/trade_report_plan/ai_trade_report_target_example_2026-04-15.md` | 11835 | `c30680d9ad4e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/execution_snapshot_observability_slice_plan_2026-04-16.md` → `docs/trade_report_plan/execution_snapshot_observability_slice_plan_2026-04-16.md` | 1711 | `926870604102` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/golden_trade_matrix_2026-04-16.md` → `docs/trade_report_plan/golden_trade_matrix_2026-04-16.md` | 4809 | `bfd8c1b71a95` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/lifecycle_linkage_close_2026-04-16.md` → `docs/trade_report_plan/lifecycle_linkage_close_2026-04-16.md` | 3134 | `d395f8cdb11d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/live_bundle_lib_extraction_draft_2026-04-16.md` → `docs/trade_report_plan/live_bundle_lib_extraction_draft_2026-04-16.md` | 11485 | `4c6eaa60d19f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/overnight_carry_artifact_contract_2026-04-19.md` → `docs/trade_report_plan/overnight_carry_artifact_contract_2026-04-19.md` | 1548 | `f3b638fc61d4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/overnight_carry_incident_review_2026-04-17_005930.md` → `docs/trade_report_plan/overnight_carry_incident_review_2026-04-17_005930.md` | 2598 | `0a4ff1f118be` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/report_llm_input_output_example_2026-04-19.md` → `docs/trade_report_plan/report_llm_input_output_example_2026-04-19.md` | 13659 | `7cd0eea3a1cc` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/report_regeneration_llm_mode_2026-04-25.md` → `docs/trade_report_plan/report_regeneration_llm_mode_2026-04-25.md` | 4662 | `cd06dd7809f0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/report_runtime_regression_plan_2026-04-16.md` → `docs/trade_report_plan/report_runtime_regression_plan_2026-04-16.md` | 5980 | `b630714cbf53` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/report_surface_pruning_2026-04-16.md` → `docs/trade_report_plan/report_surface_pruning_2026-04-16.md` | 2022 | `4d6ae35ef377` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/reporter_ownership_completion_plan_2026-04-16.md` → `docs/trade_report_plan/reporter_ownership_completion_plan_2026-04-16.md` | 13000 | `56b0b5d88640` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/strategist_prompt_input_example_2026-04-17.md` → `docs/trade_report_plan/strategist_prompt_input_example_2026-04-17.md` | 30241 | `3221c76513b5` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/trade_report_external_report_dependencies_2026-04-16.md` → `docs/trade_report_plan/trade_report_external_report_dependencies_2026-04-16.md` | 5553 | `b68cbc042870` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/trade_report_runtime_guardrails_2026-04-16.md` → `docs/trade_report_plan/trade_report_runtime_guardrails_2026-04-16.md` | 8040 | `6601394e1699` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/trade_report_summary_example_0428.md` → `docs/trade_report_plan/trade_report_summary_example_0428.md` | 4057 | `f8339680c4e2` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/trade_report_plan/trade_report_summary_llm_contract_2026-04-28.md` → `docs/trade_report_plan/trade_report_summary_llm_contract_2026-04-28.md` | 5612 | `527136485cd7` | KEEP_IF: 문서 참조·경로·내용 정본 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
