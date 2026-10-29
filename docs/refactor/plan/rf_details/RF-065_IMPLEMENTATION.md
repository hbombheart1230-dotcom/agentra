# RF-065 — 코드 구조/함수 재배치 설계 (T08)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/02_DEVELOPING/CODEX_B/RF-065.md` blob `72bb19104319ddec6d3cab232ee8f159b17df0f1`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 54개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `scripts/research/run_phase5_validation_bundle.py` | 21194 | `7f7b2aa0717131b4de178050dd9b3a55051561ad` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `scripts/research/run_phase5_validation_bundle_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `scripts/research/__init__.py` → `scripts/research/__init__.py` | 77 | `553292b38d53` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/research/daily_profitability_scorecard.py` → `scripts/research/daily_profitability_scorecard.py` | 1702 | `8375e84d03fa` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `scripts/research/run_agent_effectiveness_scorecard.py` → `scripts/research/run_agent_effectiveness_scorecard.py` | 1726 | `db4571d64bf3` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_alpha_hypothesis_competition.py` → `scripts/research/run_alpha_hypothesis_competition.py` | 996 | `86f6ed3625bb` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_alpha_research_board.py` → `scripts/research/run_alpha_research_board.py` | 3130 | `059026ee848a` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_attribution_score_range.py` → `scripts/research/run_attribution_score_range.py` | 1027 | `b7af6023c25b` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_attribution_score_window.py` → `scripts/research/run_attribution_score_window.py` | 859 | `d9f8d204ff42` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_conditional_alpha_diagnosis.py` → `scripts/research/run_conditional_alpha_diagnosis.py` | 927 | `b9a7282fc358` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_cumulative_improvement_review.py` → `scripts/research/run_cumulative_improvement_review.py` | 928 | `a09c63237a02` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_decision_story_report.py` → `scripts/research/run_decision_story_report.py` | 1797 | `23cd0146d0a6` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_evaluation_lens_report.py` → `scripts/research/run_evaluation_lens_report.py` | 1076 | `fe067cc51d7a` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_existing_evidence_mining.py` → `scripts/research/run_existing_evidence_mining.py` | 1202 | `e3ddab2f3c9b` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_frozen_q9_baseline_closeout.py` → `scripts/research/run_frozen_q9_baseline_closeout.py` | 1028 | `b150faf78ecd` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_full_chain_component_review.py` → `scripts/research/run_full_chain_component_review.py` | 1298 | `d7809f942187` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_historical_q9_prior.py` → `scripts/research/run_historical_q9_prior.py` | 1038 | `c4d0db337ebf` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_horizon_alignment_review.py` → `scripts/research/run_horizon_alignment_review.py` | 1276 | `5f0980cd2589` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_horizon_revision_backtest.py` → `scripts/research/run_horizon_revision_backtest.py` | 1372 | `cea96cb51aa3` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_integrated_trade_diagnosis.py` → `scripts/research/run_integrated_trade_diagnosis.py` | 1227 | `95ee0d86e8ba` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_integrated_trade_validation.py` → `scripts/research/run_integrated_trade_validation.py` | 1732 | `6aaabc3e0ecb` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_loss_decomposition.py` → `scripts/research/run_loss_decomposition.py` | 1122 | `c90792643d5d` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_market_regime_rail_review.py` → `scripts/research/run_market_regime_rail_review.py` | 1142 | `bb9c15a77e4c` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_memory_contamination_review.py` → `scripts/research/run_memory_contamination_review.py` | 1147 | `ac697dacbbba` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_monitor_noop_attribution.py` → `scripts/research/run_monitor_noop_attribution.py` | 1285 | `46f7844d4aaa` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_offhours_validation_loop.py` → `scripts/research/run_offhours_validation_loop.py` | 320 | `90a76fa2e0b4` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_opening_rank1_longitudinal.py` → `scripts/research/run_opening_rank1_longitudinal.py` | 1958 | `24b625484f1a` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_opening_rank1_shadow.py` → `scripts/research/run_opening_rank1_shadow.py` | 1143 | `2c080f2bd2aa` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_operator_summary_mining.py` → `scripts/research/run_operator_summary_mining.py` | 919 | `86e7690f0796` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_phase5_validation_bundle.py` → `scripts/research/run_phase5_validation_bundle.py` | 21194 | `7f7b2aa07171` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_post_exit_shadow_recap.py` → `scripts/research/run_post_exit_shadow_recap.py` | 1568 | `b459144a4180` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_post_reclaim_offline_research.py` → `scripts/research/run_post_reclaim_offline_research.py` | 1010 | `84e78c07f326` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_q12_historical_policy_review.py` → `scripts/research/run_q12_historical_policy_review.py` | 865 | `6658ecfafb1c` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_q13_q14_validation.py` → `scripts/research/run_q13_q14_validation.py` | 1060 | `cdf43430420d` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_q8_historical_review.py` → `scripts/research/run_q8_historical_review.py` | 1779 | `41e5270aa29e` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_q8_lane_decision_table.py` → `scripts/research/run_q8_lane_decision_table.py` | 1581 | `1654ecd86d3e` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_q8_shadow_blocker_review.py` → `scripts/research/run_q8_shadow_blocker_review.py` | 1169 | `d823ca828da1` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_q9_baseline_comparison.py` → `scripts/research/run_q9_baseline_comparison.py` | 1074 | `e2ba9b5dd16d` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_q9_evaluation.py` → `scripts/research/run_q9_evaluation.py` | 1040 | `09ba4ea0e3b9` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_quant_trade_diagnosis.py` → `scripts/research/run_quant_trade_diagnosis.py` | 2186 | `879dd66bcb6d` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_rank1_feature_mart.py` → `scripts/research/run_rank1_feature_mart.py` | 1168 | `557b507ad7fc` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_rank1_prospective_shadow.py` → `scripts/research/run_rank1_prospective_shadow.py` | 1312 | `bd12e54a9991` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_run_card_report.py` → `scripts/research/run_run_card_report.py` | 1772 | `5ec2b07dd98b` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_same_symbol_sequence.py` → `scripts/research/run_same_symbol_sequence.py` | 1163 | `0cad026c97fb` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_scanner_alignment_root_cause_range.py` → `scripts/research/run_scanner_alignment_root_cause_range.py` | 939 | `d064b226ef91` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_short_alpha_discriminator.py` → `scripts/research/run_short_alpha_discriminator.py` | 1266 | `651c627558b1` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_stage2_authority_review.py` → `scripts/research/run_stage2_authority_review.py` | 1383 | `53ff55b9c630` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_structural_alpha_batch1.py` → `scripts/research/run_structural_alpha_batch1.py` | 1196 | `bc0a3f03d466` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_structural_alpha_batch2.py` → `scripts/research/run_structural_alpha_batch2.py` | 1203 | `a83f8936eb40` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_trade_explain_report.py` → `scripts/research/run_trade_explain_report.py` | 2271 | `9ad37a64080c` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_uef5_3_dual_run.py` → `scripts/research/run_uef5_3_dual_run.py` | 2270 | `cb91fcb29233` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_uef6_dedup_detection.py` → `scripts/research/run_uef6_dedup_detection.py` | 2008 | `3889a0b94440` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_uef6_historical_validation.py` → `scripts/research/run_uef6_historical_validation.py` | 8517 | `39da8c493db9` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_uef7_alpha_board_normalization.py` → `scripts/research/run_uef7_alpha_board_normalization.py` | 2094 | `aed77bb978b9` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_uef8_fair_comparison_validation.py` → `scripts/research/run_uef8_fair_comparison_validation.py` | 2401 | `4b9f0efc5b15` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |
| `scripts/research/run_uef9_formal_authority.py` → `scripts/research/run_uef9_formal_authority.py` | 1520 | `9e1e6c95fce1` | KEEP_IF: 공개 CLI/스케줄러 진입점, argv/cwd/exit 호환 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
