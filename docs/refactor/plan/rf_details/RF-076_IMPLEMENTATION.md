# RF-076 — 코드 구조/함수 재배치 설계 (T09)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-076.md` blob `389d7e6699c5bf464c8bcc24c87b70c5c7799cca`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 59개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `tests/test_uef1_work_package_a_canonical_contract.py` | 102520 | `5496edd06fd22861f75aab3bc1e635af56f3725f` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef1_work_package_a_canonical_contract_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_uef2a_forward_policy_contract.py` | 58660 | `7ad443b01983bdb0b16475b1b4d34fdf91f5923b` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef2a_forward_policy_contract_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_uef3a_cost_metric_contract.py` | 53246 | `b5b335308fbd864e6ebea23a02a39c35222cadc6` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef3a_cost_metric_contract_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_uef5_2_historical_recompute.py` | 48661 | `cfe89854f9b5c7b311b29ae8224178fe4eed28e7` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef5_2_historical_recompute_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_uef5_1_clean_evidence_registry.py` | 45576 | `2e8172df1afed222db4992c4d0821d4d1c5f121f` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef5_1_clean_evidence_registry_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_uef4b3_opening_shadow_adapter.py` | 45091 | `8ea308eeb17c2654410e07a1cbad1414589dda64` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef4b3_opening_shadow_adapter_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_uef5_3_dual_run.py` | 42174 | `c72326496c4e9dc8b02e75039dece0cd4ea8c344` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef5_3_dual_run_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_uef4b2_q12_adapter.py` | 39621 | `164f4be88894695ffe70e29a0436580ff8473422` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef4b2_q12_adapter_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_uef4b4_q10_index_adapter.py` | 38279 | `955dfa87f1028825e1b29be00db2c902acbacd1c` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef4b4_q10_index_adapter_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_daily_uef_pipeline.py` | 35699 | `8cd223b95035d77d3509a57242de2d591f49cdb3` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_daily_uef_pipeline_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_step5c_fix3_authoritative_intent.py` | 31535 | `1c868a245834b15bc2b1e6d5b05bbfa83a25c299` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_step5c_fix3_authoritative_intent_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_uef2b_profile_execution.py` | 30833 | `ee87832e27c6520f2a575f6e3a7309eea74ef74a` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef2b_profile_execution_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_uef8_fair_comparison_validation.py` | 30273 | `5d8e8971daf2cf3da1694f722c13e07186369776` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef8_fair_comparison_validation_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_uef3c_aggregation_pipeline.py` | 29198 | `039ce83bf4c83686676fe5e350ae806ba5c1be7d` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef3c_aggregation_pipeline_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_uef4b6_q9_adapter.py` | 28010 | `b73e6af5f92a8a38289d611d7139457160958754` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef4b6_q9_adapter_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_uef6c_historical_validation.py` | 27285 | `38afbc21a504561e12e45f2ed5fc7a0f92b79f36` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef6c_historical_validation_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_uef4b5_q11_adapter.py` | 26454 | `30469ffeb61a64725b862c65c7355d5fbdf85f2f` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef4b5_q11_adapter_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_uef7_alpha_board_normalization.py` | 26373 | `0e5dabc995633af1dc994e1b639533f9a96b509f` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef7_alpha_board_normalization_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_step5c_fix2_ownership_capability.py` | 26021 | `0dfbd83431b7d3ea38443f6bcef18770729e0b84` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_step5c_fix2_ownership_capability_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_step5b_safety_fix.py` | 25108 | `d2f01220f090aa04ef327997a8a409ec13156aff` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_step5b_safety_fix_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_uef2b_engine_primitives.py` | 24414 | `a08ac578313166f2164de64780d6c1b076973087` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef2b_engine_primitives_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_uef3b_cost_metric_engine.py` | 24176 | `febb46005fc44dcdc9fdcb0ff5e0eead2d01b0f9` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef3b_cost_metric_engine_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_step5c_fix5_mutation_failclosed_and_consumer_only.py` | 23489 | `1eb1ef388a3d64d7078ef439eb8a5b48bea2ac7f` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_step5c_fix5_mutation_failclosed_and_consumer_only_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_uef4b1_q10_semiconductor_adapter.py` | 23022 | `0fcd00dd215224c5c4b45d6da59f48557efd597b` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef4b1_q10_semiconductor_adapter_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_uef6_dedup_detection.py` | 21563 | `ce966cc7ac09b2f10425c34d4023734114a30124` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_uef6_dedup_detection_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `tests/test_step5b_fix4.py` | 20817 | `46b3f4b7974ca9bfd40580eec2369c135aca40df` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `tests/test_step5b_fix4_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `tests/test_broker_alignment.py` → `tests/test_broker_alignment.py` | 1396 | `c57d6c711203` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_broker_closed_trade_reconciler.py` → `tests/test_broker_closed_trade_reconciler.py` | 14850 | `f09335312c5e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_broker_cost_profile.py` → `tests/test_broker_cost_profile.py` | 4558 | `2defe185602f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_broker_outcome_fallback_truth.py` → `tests/test_broker_outcome_fallback_truth.py` | 9766 | `ff67aeca804d` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_broker_trade_reconciliation.py` → `tests/test_broker_trade_reconciliation.py` | 2063 | `9a41946e7828` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_build_risk_context.py` → `tests/test_build_risk_context.py` | 1936 | `f5bdb9023e72` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_daily_uef_pipeline.py` → `tests/test_daily_uef_pipeline.py` | 35699 | `8cd223b95035` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_daily_uef_run_status.py` → `tests/test_daily_uef_run_status.py` | 7530 | `c72476fb5949` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_host_supervisor.py` → `tests/test_host_supervisor.py` | 2310 | `0607876ce1a0` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_kiwoom_order_fill_reader.py` → `tests/test_kiwoom_order_fill_reader.py` | 4188 | `63b1f682c09a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m17_risk_decision.py` → `tests/test_m17_risk_decision.py` | 4545 | `988650476873` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_m18_5_risk_off_candidate_count.py` → `tests/test_m18_5_risk_off_candidate_count.py` | 598 | `4af5023f47d8` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_mock_executor.py` → `tests/test_mock_executor.py` | 519 | `99a4384402f9` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_order_client.py` → `tests/test_order_client.py` | 1461 | `bcdc8ec4f8b2` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p0a_e2e_open_order_guard_integrated_chain.py` → `tests/test_p0a_e2e_open_order_guard_integrated_chain.py` | 7335 | `d26a74827784` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p0a_open_order_reconciliation_guard.py` → `tests/test_p0a_open_order_reconciliation_guard.py` | 11513 | `d7f19be16b99` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p0b_step5d_crash_reconciliation.py` → `tests/test_p0b_step5d_crash_reconciliation.py` | 6946 | `33e87d168852` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p166_v1052_candidate_risk_migration.py` → `tests/test_p166_v1052_candidate_risk_migration.py` | 7443 | `eb6367fa9292` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p1_3_broker_read_write_gate.py` → `tests/test_p1_3_broker_read_write_gate.py` | 6777 | `70ae363aa3d5` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_pre_step5c_owner_regressions.py` → `tests/test_pre_step5c_owner_regressions.py` | 4109 | `7ef763f327f5` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_real_executor_disabled.py` → `tests/test_real_executor_disabled.py` | 696 | `69010cd8f845` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_real_executor_mock_mode_allowed.py` → `tests/test_real_executor_mock_mode_allowed.py` | 5283 | `8b6553ef6d37` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_step5b_broker_submission_safety.py` → `tests/test_step5b_broker_submission_safety.py` | 15230 | `1f16f431bed8` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_step5b_fix3.py` → `tests/test_step5b_fix3.py` | 14109 | `152e8b872e38` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_step5b_fix4.py` → `tests/test_step5b_fix4.py` | 20817 | `46b3f4b7974c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_step5b_fix5.py` → `tests/test_step5b_fix5.py` | 15467 | `74fc93f4da68` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_step5b_safety_fix.py` → `tests/test_step5b_safety_fix.py` | 25108 | `d2f01220f090` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_step5c_execution_owner.py` → `tests/test_step5c_execution_owner.py` | 12635 | `068fac993a23` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_step5c_fix1_shared_ownership.py` → `tests/test_step5c_fix1_shared_ownership.py` | 18611 | `a9917fcacd8f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_step5c_fix2_ownership_capability.py` → `tests/test_step5c_fix2_ownership_capability.py` | 26021 | `0dfbd83431b7` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_step5c_fix3_authoritative_intent.py` → `tests/test_step5c_fix3_authoritative_intent.py` | 31535 | `1c868a245834` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_step5c_fix4_broker_semantics_authority.py` → `tests/test_step5c_fix4_broker_semantics_authority.py` | 5197 | `fd0159e432b1` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_step5c_fix5_mutation_failclosed_and_consumer_only.py` → `tests/test_step5c_fix5_mutation_failclosed_and_consumer_only.py` | 23489 | `1eb1ef388a3d` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_supervisor.py` → `tests/test_supervisor.py` | 4727 | `675d90cc8336` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef1_work_package_a_canonical_contract.py` → `tests/test_uef1_work_package_a_canonical_contract.py` | 102520 | `5496edd06fd2` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef2a_boundary_closure_profiles.py` → `tests/test_uef2a_boundary_closure_profiles.py` | 14351 | `316286bf4091` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef2a_forward_policy_contract.py` → `tests/test_uef2a_forward_policy_contract.py` | 58660 | `7ad443b01983` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef2b_engine_primitives.py` → `tests/test_uef2b_engine_primitives.py` | 24414 | `a08ac5783131` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef2b_fix1_regressions.py` → `tests/test_uef2b_fix1_regressions.py` | 19542 | `2861e1693cca` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef2b_profile_execution.py` → `tests/test_uef2b_profile_execution.py` | 30833 | `ee87832e27c6` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef3a_cost_metric_contract.py` → `tests/test_uef3a_cost_metric_contract.py` | 53246 | `b5b335308fbd` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef3b_cost_metric_engine.py` → `tests/test_uef3b_cost_metric_engine.py` | 24176 | `febb46005fc4` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef3c_aggregation_pipeline.py` → `tests/test_uef3c_aggregation_pipeline.py` | 29198 | `039ce83bf4c8` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef4b1_q10_semiconductor_adapter.py` → `tests/test_uef4b1_q10_semiconductor_adapter.py` | 23022 | `0fcd00dd2152` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef4b2_q12_adapter.py` → `tests/test_uef4b2_q12_adapter.py` | 39621 | `164f4be88894` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef4b3_opening_shadow_adapter.py` → `tests/test_uef4b3_opening_shadow_adapter.py` | 45091 | `8ea308eeb17c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef4b4_q10_index_adapter.py` → `tests/test_uef4b4_q10_index_adapter.py` | 38279 | `955dfa87f102` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef4b5_q11_adapter.py` → `tests/test_uef4b5_q11_adapter.py` | 26454 | `30469ffeb61a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef4b6_q9_adapter.py` → `tests/test_uef4b6_q9_adapter.py` | 28010 | `b73e6af5f92a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef5_1_clean_evidence_registry.py` → `tests/test_uef5_1_clean_evidence_registry.py` | 45576 | `2e8172df1afe` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef5_2_historical_recompute.py` → `tests/test_uef5_2_historical_recompute.py` | 48661 | `cfe89854f9b5` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef5_2_session_policy.py` → `tests/test_uef5_2_session_policy.py` | 5709 | `225bff7a25de` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef5_3_dual_run.py` → `tests/test_uef5_3_dual_run.py` | 42174 | `c72326496c4e` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef6_dedup_detection.py` → `tests/test_uef6_dedup_detection.py` | 21563 | `ce966cc7ac09` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef6_lineage_sidecar.py` → `tests/test_uef6_lineage_sidecar.py` | 15674 | `28755c58478f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef6c_historical_validation.py` → `tests/test_uef6c_historical_validation.py` | 27285 | `38afbc21a504` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef7_alpha_board_normalization.py` → `tests/test_uef7_alpha_board_normalization.py` | 26373 | `0e5dabc99563` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef8_fair_comparison_validation.py` → `tests/test_uef8_fair_comparison_validation.py` | 30273 | `5d8e8971daf2` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_uef9_formal_authority.py` → `tests/test_uef9_formal_authority.py` | 11526 | `c351ee2a1d4a` | KEEP_IF: 테스트 단일 소유·오라클 불변 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
