# RF-082 — 코드 구조/함수 재배치 설계 (T06)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-082.md` blob `4230aa6849345392336e0003c916bf1a5a08b5b5`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 115개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `docs/evaluation/README.md` → `docs/evaluation/README.md` | 8127 | `d23b6f403830` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/baseline_btc_woori_tech_control.md` → `docs/evaluation/baseline_btc_woori_tech_control.md` | 5945 | `f48050623ce2` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/baseline_samsung_hynix_control.md` → `docs/evaluation/baseline_samsung_hynix_control.md` | 3593 | `1db86fd47381` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/controlled_mock_four_lane_execution_2026-08-28.md` → `docs/evaluation/controlled_mock_four_lane_execution_2026-08-28.md` | 5055 | `ec090e414b95` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/current_operating_baseline.md` → `docs/evaluation/current_operating_baseline.md` | 11804 | `2e94487dd61a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/horizon_alignment_decision_2026-06-22.md` → `docs/evaluation/horizon_alignment_decision_2026-06-22.md` | 2553 | `0fc4209ea337` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/loss_decomposition_decision_2026-06-22.md` → `docs/evaluation/loss_decomposition_decision_2026-06-22.md` | 3197 | `7121d0cde34a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/opportunity_engine_shadow_plan.md` → `docs/evaluation/opportunity_engine_shadow_plan.md` | 3493 | `4a83dfe0a540` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/q10_korea_lead_market_forward_validation.md` → `docs/evaluation/q10_korea_lead_market_forward_validation.md` | 5018 | `5b8d7960a642` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/q12_vnext_crypto_equity_confirmation.md` → `docs/evaluation/q12_vnext_crypto_equity_confirmation.md` | 6846 | `9576eb8e2aaf` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/q12_vnext_delivery_time_alignment.md` → `docs/evaluation/q12_vnext_delivery_time_alignment.md` | 6189 | `fdd95c5d130a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/q8_closure_lock.md` → `docs/evaluation/q8_closure_lock.md` | 1874 | `bc61db83652f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/q8_final_comprehensive_review_2026-06-20.md` → `docs/evaluation/q8_final_comprehensive_review_2026-06-20.md` | 16141 | `572cc7a004ae` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/q8_handoff_2026-06-19.md` → `docs/evaluation/q8_handoff_2026-06-19.md` | 4591 | `ed7d940f7ca2` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/q9_component_decision_2026-06-22.md` → `docs/evaluation/q9_component_decision_2026-06-22.md` | 4339 | `7af8780b2299` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/q9_day1_opening_calculation_review_2026-06-24.md` → `docs/evaluation/q9_day1_opening_calculation_review_2026-06-24.md` | 6860 | `4794582aabe3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/q9_evaluation_contract.md` → `docs/evaluation/q9_evaluation_contract.md` | 5361 | `83b060777a66` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/q9_fixed_forward_window_protocol_2026-06-23.md` → `docs/evaluation/q9_fixed_forward_window_protocol_2026-06-23.md` | 5839 | `cb981893f59f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/q9_full_chain_evaluation_matrix.md` → `docs/evaluation/q9_full_chain_evaluation_matrix.md` | 10421 | `a999d683a5f9` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/q9_horizon_contract_observability_2026-06-26.md` → `docs/evaluation/q9_horizon_contract_observability_2026-06-26.md` | 2762 | `7944c01b850e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/q9_implementation_roadmap.md` → `docs/evaluation/q9_implementation_roadmap.md` | 9799 | `97e1a728844c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/q9_master_plan.md` → `docs/evaluation/q9_master_plan.md` | 8135 | `f3c29b1bdd5e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/q9_q18_operating_status_2026-08-05.md` → `docs/evaluation/q9_q18_operating_status_2026-08-05.md` | 2870 | `0b555f1946b1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/evaluation/q9_samsung_hynix_five_day_freeze.md` → `docs/evaluation/q9_samsung_hynix_five_day_freeze.md` | 2508 | `34d66f1b3c22` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/README.md` → `docs/offline_alpha/README.md` | 9100 | `e48a821efd04` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/active_research_register_2026-08-07.md` → `docs/offline_alpha/active_research_register_2026-08-07.md` | 5335 | `1d32a21d7ad7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/alpha_hypothesis_competition_v1_contract_2026-07-30.md` → `docs/offline_alpha/alpha_hypothesis_competition_v1_contract_2026-07-30.md` | 2921 | `cf87e9c929d3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/alpha_hypothesis_competition_v1_result_2026-07-30.md` → `docs/offline_alpha/alpha_hypothesis_competition_v1_result_2026-07-30.md` | 3396 | `fdaa2caa9029` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/alpha_research_board_contract_2026-08-21.md` → `docs/offline_alpha/alpha_research_board_contract_2026-08-21.md` | 6264 | `47e699584257` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/alpha_research_board_contract_2026-08-27.md` → `docs/offline_alpha/alpha_research_board_contract_2026-08-27.md` | 3527 | `2270f46fc8cb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/canonical_execution_plan_2026-08-06.md` → `docs/offline_alpha/canonical_execution_plan_2026-08-06.md` | 6458 | `de3ab634ecf5` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/canonical_rank1_feature_mart_2026-08-11.md` → `docs/offline_alpha/canonical_rank1_feature_mart_2026-08-11.md` | 3908 | `5b6426ad1820` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/conditional_alpha_diagnosis_2026-08-06.md` → `docs/offline_alpha/conditional_alpha_diagnosis_2026-08-06.md` | 963 | `53f2eeae3693` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/deep_discriminator_squeeze_2026-08-24.md` → `docs/offline_alpha/deep_discriminator_squeeze_2026-08-24.md` | 11231 | `9f9c56331cf1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/existing_evidence_mining_contract_2026-07-31.md` → `docs/offline_alpha/existing_evidence_mining_contract_2026-07-31.md` | 3132 | `4081cdfd962f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/existing_evidence_mining_result_2026-07-31.md` → `docs/offline_alpha/existing_evidence_mining_result_2026-07-31.md` | 7004 | `c4067c934812` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/five_session_closure_2026-08-07.md` → `docs/offline_alpha/five_session_closure_2026-08-07.md` | 9357 | `457de47bdba7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/immediate_opening_probe_runtime_validation_2026-08-21.md` → `docs/offline_alpha/immediate_opening_probe_runtime_validation_2026-08-21.md` | 3291 | `9650cd6d9d5d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/integrated_conditional_alpha_findings_2026-08-06.md` → `docs/offline_alpha/integrated_conditional_alpha_findings_2026-08-06.md` | 8630 | `80571c19af44` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/integrated_trade_diagnosis_plan_2026-07-31.md` → `docs/offline_alpha/integrated_trade_diagnosis_plan_2026-07-31.md` | 4000 | `c75d3df01eba` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/opening_rank1_controlled_probe_2026-08-14.md` → `docs/offline_alpha/opening_rank1_controlled_probe_2026-08-14.md` | 7741 | `28b11203530c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/opening_rank1_deep_dive_2026-07-31.md` → `docs/offline_alpha/opening_rank1_deep_dive_2026-07-31.md` | 18859 | `5ce46ca9e396` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/opening_rank1_longitudinal_2026-07-31.md` → `docs/offline_alpha/opening_rank1_longitudinal_2026-07-31.md` | 9312 | `71201717370c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/opening_rank1_prospective_validation_2026-07-31.md` → `docs/offline_alpha/opening_rank1_prospective_validation_2026-07-31.md` | 5146 | `63370b557606` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/opening_rank1_same_symbol_sequence_review_2026-07-31.md` → `docs/offline_alpha/opening_rank1_same_symbol_sequence_review_2026-07-31.md` | 11430 | `154fbdeb7d0c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/post_reclaim_executable_policy_v0_2026-07-30.md` → `docs/offline_alpha/post_reclaim_executable_policy_v0_2026-07-30.md` | 2679 | `65f52ed52518` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/post_reclaim_offline_research_2026-07-30.md` → `docs/offline_alpha/post_reclaim_offline_research_2026-07-30.md` | 3506 | `abed3778a066` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/rank1_fixed_candidate_prospective_shadow_2026-08-11.md` → `docs/offline_alpha/rank1_fixed_candidate_prospective_shadow_2026-08-11.md` | 4244 | `70770fb398a4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/rank1_fresh_change_activation_shadow_2026-08-12.md` → `docs/offline_alpha/rank1_fresh_change_activation_shadow_2026-08-12.md` | 6133 | `18ee58af47c4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/rank1_strategy_choice_observability_2026-08-12.md` → `docs/offline_alpha/rank1_strategy_choice_observability_2026-08-12.md` | 4476 | `12d78d2b3b3c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/structural_alpha_batch1_contract_2026-07-30.md` → `docs/offline_alpha/structural_alpha_batch1_contract_2026-07-30.md` | 3002 | `c59b4da5532f` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/structural_alpha_batch1_result_2026-07-30.md` → `docs/offline_alpha/structural_alpha_batch1_result_2026-07-30.md` | 3864 | `1dba3e296794` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/structural_alpha_batch2_contract_2026-07-30.md` → `docs/offline_alpha/structural_alpha_batch2_contract_2026-07-30.md` | 2432 | `5cfe56d99941` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/structural_alpha_batch2_result_2026-07-30.md` → `docs/offline_alpha/structural_alpha_batch2_result_2026-07-30.md` | 2140 | `9d60140c2a92` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/offline_alpha/structural_alpha_search_closure_2026-07-30.md` → `docs/offline_alpha/structural_alpha_search_closure_2026-07-30.md` | 1491 | `bd6c5638a75b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/profitability_recovery/execution_plan.md` → `docs/profitability_recovery/execution_plan.md` | 1238 | `7adefaf19dbb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/profitability_recovery/system_state_and_milestones.md` → `docs/profitability_recovery/system_state_and_milestones.md` | 5832 | `b358c481d685` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13/README.md` → `docs/q13/README.md` | 3287 | `b427e6d2581b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13/code_data_audit_matrix.md` → `docs/q13/code_data_audit_matrix.md` | 11848 | `8c3ae43163e6` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13/observability_patch_2026-07-06.md` → `docs/q13/observability_patch_2026-07-06.md` | 3371 | `2d8246f52535` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13/q13_attribution_score_range_2026-06-01_2026-07-06.md` → `docs/q13/q13_attribution_score_range_2026-06-01_2026-07-06.md` | 3848 | `a38ba9d74ed2` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13/q13_attribution_score_v0_2026-07-06.md` → `docs/q13/q13_attribution_score_v0_2026-07-06.md` | 3042 | `85fba5a50bc8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13/q13_attribution_score_window_2026-06-29_2026-07-06.md` → `docs/q13/q13_attribution_score_window_2026-06-29_2026-07-06.md` | 4161 | `0bbc524d859c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13/q13_entry_timing_attribution_2026-07-06.md` → `docs/q13/q13_entry_timing_attribution_2026-07-06.md` | 3364 | `f1f0fd685d4e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/README.md` → `docs/q13_q14_validation/README.md` | 11759 | `dc134c8b66e2` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/broker_stale_fill_reconciliation_fix_2026-07-22.md` → `docs/q13_q14_validation/broker_stale_fill_reconciliation_fix_2026-07-22.md` | 1861 | `bc9cad5053a5` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/evaluation_integrity_close_2026-07-30.md` → `docs/q13_q14_validation/evaluation_integrity_close_2026-07-30.md` | 3224 | `36bfd649c4a6` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/june_july_integrated_review_2026-07-30.md` → `docs/q13_q14_validation/june_july_integrated_review_2026-07-30.md` | 11225 | `c7bc65a5d065` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/measurement_integrity_fix_2026-07-22.md` → `docs/q13_q14_validation/measurement_integrity_fix_2026-07-22.md` | 2111 | `e4ff09b4c31b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/post_q15_adjustment_retest_close_2026-07-21.md` → `docs/q13_q14_validation/post_q15_adjustment_retest_close_2026-07-21.md` | 3054 | `84fb7d31b0f4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/post_q15_close_decision_2026-07-16.md` → `docs/q13_q14_validation/post_q15_close_decision_2026-07-16.md` | 4337 | `b04f81e8645c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/post_q15_two_day_decision_tree_2026-07-14.md` → `docs/q13_q14_validation/post_q15_two_day_decision_tree_2026-07-14.md` | 9809 | `19431eb9cbd7` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/q15_candidate_filtering_patch_2026-07-10.md` → `docs/q13_q14_validation/q15_candidate_filtering_patch_2026-07-10.md` | 5172 | `6f297fa515dd` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/q15_scanner_score_component_candidate_2026-07-08.md` → `docs/q13_q14_validation/q15_scanner_score_component_candidate_2026-07-08.md` | 6550 | `8ac2a86f5244` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/q16_close_decision_2026-07-24.md` → `docs/q13_q14_validation/q16_close_decision_2026-07-24.md` | 1198 | `dca9af960625` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/q16_cost_horizon_fit_patch_2026-07-21.md` → `docs/q13_q14_validation/q16_cost_horizon_fit_patch_2026-07-21.md` | 4316 | `33310617198a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/q16_day1_review_2026-07-23.md` → `docs/q13_q14_validation/q16_day1_review_2026-07-23.md` | 4771 | `0aacb494956b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/q17_directional_edge_contract_patch_2026-07-24.md` → `docs/q13_q14_validation/q17_directional_edge_contract_patch_2026-07-24.md` | 6549 | `fbeff015082d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/q18_close_decision_2026-07-30.md` → `docs/q13_q14_validation/q18_close_decision_2026-07-30.md` | 6102 | `efb4bd997ce3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/q18_post_reclaim_promotion_review_plan_2026-07-30.md` → `docs/q13_q14_validation/q18_post_reclaim_promotion_review_plan_2026-07-30.md` | 5577 | `68f2c95bebf1` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/q18_validation_audit_2026-07-30.md` → `docs/q13_q14_validation/q18_validation_audit_2026-07-30.md` | 4503 | `8b7122dba90b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/q8_q17_canonical_final_review_2026-07-30.md` → `docs/q13_q14_validation/q8_q17_canonical_final_review_2026-07-30.md` | 14817 | `214841864705` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/q8_q17_close_review_2026-07-29.md` → `docs/q13_q14_validation/q8_q17_close_review_2026-07-29.md` | 9422 | `c0d19c134936` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/q8_q17_cumulative_review_2026-07-27.md` → `docs/q13_q14_validation/q8_q17_cumulative_review_2026-07-27.md` | 2806 | `2dfe8b98cbca` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q13_q14_validation/same_symbol_loss_reentry_control_2026-07-29.md` → `docs/q13_q14_validation/same_symbol_loss_reentry_control_2026-07-29.md` | 2039 | `b69fee45408b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/q14/README.md` → `docs/q14/README.md` | 3047 | `a4eedd906012` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/quant_trade_diagnosis/README.md` → `docs/quant_trade_diagnosis/README.md` | 2658 | `9f54d6d211c5` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/quant_trade_diagnosis/agent_effectiveness_scorecard_framework.md` → `docs/quant_trade_diagnosis/agent_effectiveness_scorecard_framework.md` | 18708 | `51b3727fa457` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/quant_trade_diagnosis/integrated_selection_horizon_sequence_evaluation_2026-07-31.md` → `docs/quant_trade_diagnosis/integrated_selection_horizon_sequence_evaluation_2026-07-31.md` | 12756 | `45aa5ebe31cb` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/quant_trade_diagnosis/quant_trade_diagnosis_report_plan.md` → `docs/quant_trade_diagnosis/quant_trade_diagnosis_report_plan.md` | 7715 | `a56f90e4da52` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/quant_trade_diagnosis/strategist_stage2_effectiveness_review_2026-08-27.md` → `docs/quant_trade_diagnosis/strategist_stage2_effectiveness_review_2026-08-27.md` | 8964 | `f7076ba8e2b4` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/research/evidence/p1_1_real_run_acceptance_2026-09-29/REAL_RUN_CAPTURE_A.json` → `docs/research/evidence/p1_1_real_run_acceptance_2026-09-29/REAL_RUN_CAPTURE_A.json` | 44374 | `9bb585f92e6d` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `docs/research/evidence/p1_1_real_run_acceptance_2026-09-29/REAL_RUN_CAPTURE_A.meta.json` → `docs/research/evidence/p1_1_real_run_acceptance_2026-09-29/REAL_RUN_CAPTURE_A.meta.json` | 803 | `86caeddfb3ff` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `docs/research/evidence/p1_1_real_run_acceptance_2026-09-29/chain_result_run1.json` → `docs/research/evidence/p1_1_real_run_acceptance_2026-09-29/chain_result_run1.json` | 2216 | `175ee0b7eaee` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `docs/research/evidence/p1_1_real_run_acceptance_2026-09-29/run_chain.py` → `docs/research/evidence/p1_1_real_run_acceptance_2026-09-29/run_chain.py` | 4055 | `3ed5b7d41640` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `docs/research/evidence/p1_1_real_run_acceptance_2026-09-29/tamper_tests.py` → `docs/research/evidence/p1_1_real_run_acceptance_2026-09-29/tamper_tests.py` | 3782 | `65a575b0ae00` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `docs/research/q100_research_and_learning_roadmap.md` → `docs/research/q100_research_and_learning_roadmap.md` | 11345 | `a97f06b87765` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/research/q11_opening_alpha_current_state_review.md` → `docs/research/q11_opening_alpha_current_state_review.md` | 49217 | `68b6f31c9e5a` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/research/research_portfolio_freeze_2026-09-16.md` → `docs/research/research_portfolio_freeze_2026-09-16.md` | 20112 | `3d6d1b35759e` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/research/source_material/research_review_2026-09-16.md` → `docs/research/source_material/research_review_2026-09-16.md` | 23788 | `6e86279717ae` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/research/source_material/trading_runtime_containerization_audit_2026-09-17.md` → `docs/research/source_material/trading_runtime_containerization_audit_2026-09-17.md` | 44220 | `d2261f5ae773` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/research/uef2_forward_semantics_inventory.md` → `docs/research/uef2_forward_semantics_inventory.md` | 90963 | `97be0aedeeec` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/research/uef4_legacy_family_inventory.md` → `docs/research/uef4_legacy_family_inventory.md` | 118337 | `93f046af763d` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/research/uef5_1_clean_evidence_registry.md` → `docs/research/uef5_1_clean_evidence_registry.md` | 9657 | `7601ce753651` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/research/uef5_2_historical_recompute.md` → `docs/research/uef5_2_historical_recompute.md` | 11424 | `9d95e72987dd` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/research/uef5_3_historical_dual_run.md` → `docs/research/uef5_3_historical_dual_run.md` | 12562 | `ac00d59ffc6b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/research/uef6_dedup_evidence_lineage_freeze.md` → `docs/research/uef6_dedup_evidence_lineage_freeze.md` | 11320 | `68a942cbe773` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/research/uef7_alpha_board_normalization_freeze.md` → `docs/research/uef7_alpha_board_normalization_freeze.md` | 8615 | `9691454b8f14` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/research/uef8_fair_comparison_validation_freeze.md` → `docs/research/uef8_fair_comparison_validation_freeze.md` | 8690 | `fbbdd1407bd8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/research/uef9_formal_evaluation_authority_freeze.md` → `docs/research/uef9_formal_evaluation_authority_freeze.md` | 9187 | `f08a1c8c540b` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/research/uef_freeze_manifest.md` → `docs/research/uef_freeze_manifest.md` | 4845 | `22929c430100` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/research/uef_p1_1_real_run_acceptance.md` → `docs/research/uef_p1_1_real_run_acceptance.md` | 2427 | `e0d5b4c79169` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/research/uef_p1_2_day1_observation.md` → `docs/research/uef_p1_2_day1_observation.md` | 3894 | `7f8fd6a6f5f8` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/research/unified_evaluation_foundation.md` → `docs/research/unified_evaluation_foundation.md` | 51072 | `5872a39d1765` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `docs/research/unified_evaluation_framework_integrity_review.md` → `docs/research/unified_evaluation_framework_integrity_review.md` | 41554 | `abd341125c53` | KEEP_IF: 문서 참조·경로·내용 정본 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
