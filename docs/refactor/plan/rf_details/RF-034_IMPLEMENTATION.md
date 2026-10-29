# RF-034 — 코드 구조/함수 재배치 설계 (T00/V3)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-034.md` blob `e5df505ef959e2363bf625fe96749b3d5f405439`.
**구현 담당:** **Claude A**, 상대 **Codex B**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 59개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `libs/reporting/alpha_research_board/builder.py` | 29104 | `0302499b8616c8f2daef55f0d1a7711b88069900` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/alpha_research_board/builder_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/alpha_research_board/canonical.py` | 24163 | `708e2552200581b1d7a9bba3723a697a5525c2fe` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/alpha_research_board/canonical_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |
| `libs/reporting/quant_trade_diagnosis/builder.py` | 22993 | `85ba3dbfa8a412ed9de2a4f9db33d5bac62d9f64` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/quant_trade_diagnosis/builder_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `libs/reporting/alpha_research_board/__init__.py` → `libs/reporting/alpha_research_board/__init__.py` | 148 | `a25cdd9c1b0a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/alpha_research_board/builder.py` → `libs/reporting/alpha_research_board/builder.py` | 29104 | `0302499b8616` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/alpha_research_board/canonical.py` → `libs/reporting/alpha_research_board/canonical.py` | 24163 | `708e25522005` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/alpha_research_board/contracts.py` → `libs/reporting/alpha_research_board/contracts.py` | 5274 | `a4ce9c60b344` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/alpha_research_board/large_cap_review.py` → `libs/reporting/alpha_research_board/large_cap_review.py` | 3245 | `dafd27f10418` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/alpha_research_board/loaders.py` → `libs/reporting/alpha_research_board/loaders.py` | 2771 | `6dc31abcc33b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/alpha_research_board/remaining_reviews.py` → `libs/reporting/alpha_research_board/remaining_reviews.py` | 12305 | `a641b46d5880` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/alpha_research_board/report.py` → `libs/reporting/alpha_research_board/report.py` | 5610 | `8d78a86fa402` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/alpha_research_board/runtime_validation.py` → `libs/reporting/alpha_research_board/runtime_validation.py` | 8315 | `5c416628336f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/alpha_research_board/sensitivity.py` → `libs/reporting/alpha_research_board/sensitivity.py` | 15279 | `6df1cb912b12` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/opening_rank1_shadow/__init__.py` → `libs/reporting/opening_rank1_shadow/__init__.py` | 91 | `721a51c59ab7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/opening_rank1_shadow/candle_provider.py` → `libs/reporting/opening_rank1_shadow/candle_provider.py` | 3683 | `fbca02731c82` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/opening_rank1_shadow/contracts.py` → `libs/reporting/opening_rank1_shadow/contracts.py` | 757 | `dbfd0edb01cd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/opening_rank1_shadow/episodes.py` → `libs/reporting/opening_rank1_shadow/episodes.py` | 4200 | `de4ef55e9d9c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/opening_rank1_shadow/extraction.py` → `libs/reporting/opening_rank1_shadow/extraction.py` | 3345 | `09b772c79e45` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/opening_rank1_shadow/five_session_review.py` → `libs/reporting/opening_rank1_shadow/five_session_review.py` | 6817 | `85cb3f708096` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/opening_rank1_shadow/latent_forward.py` → `libs/reporting/opening_rank1_shadow/latent_forward.py` | 13687 | `76a205900239` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/opening_rank1_shadow/latent_watch.py` → `libs/reporting/opening_rank1_shadow/latent_watch.py` | 11538 | `ce743711f479` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/opening_rank1_shadow/market_snapshot.py` → `libs/reporting/opening_rank1_shadow/market_snapshot.py` | 5277 | `fedec1cc7c4a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/opening_rank1_shadow/metrics.py` → `libs/reporting/opening_rank1_shadow/metrics.py` | 7844 | `1eafd040278a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/opening_rank1_shadow/observability.py` → `libs/reporting/opening_rank1_shadow/observability.py` | 14241 | `d2ffda950c9c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/opening_rank1_shadow/pipeline.py` → `libs/reporting/opening_rank1_shadow/pipeline.py` | 9050 | `e8d7e89ff9b7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/opening_rank1_shadow/report.py` → `libs/reporting/opening_rank1_shadow/report.py` | 7477 | `5055e0eaba3a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/opening_rank1_shadow/symbol_metadata.py` → `libs/reporting/opening_rank1_shadow/symbol_metadata.py` | 2542 | `92676f1c44d9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/quant_trade_diagnosis/__init__.py` → `libs/reporting/quant_trade_diagnosis/__init__.py` | 362 | `e4e1a2c141e2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/quant_trade_diagnosis/builder.py` → `libs/reporting/quant_trade_diagnosis/builder.py` | 22993 | `85ba3dbfa8a4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/quant_trade_diagnosis/conditional_alpha.py` → `libs/reporting/quant_trade_diagnosis/conditional_alpha.py` | 3709 | `2ccb53bf45a6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/quant_trade_diagnosis/markdown.py` → `libs/reporting/quant_trade_diagnosis/markdown.py` | 12243 | `b3b3173db27f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/quant_trade_diagnosis/writer.py` → `libs/reporting/quant_trade_diagnosis/writer.py` | 4513 | `ac718eee69ee` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/short_alpha_discriminator/__init__.py` → `libs/reporting/short_alpha_discriminator/__init__.py` | 193 | `bf27962c6717` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/short_alpha_discriminator/cohorts.py` → `libs/reporting/short_alpha_discriminator/cohorts.py` | 10596 | `c4f290ad50b4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/short_alpha_discriminator/contracts.py` → `libs/reporting/short_alpha_discriminator/contracts.py` | 638 | `706801b17251` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/short_alpha_discriminator/metrics.py` → `libs/reporting/short_alpha_discriminator/metrics.py` | 2606 | `c2a64b2bdec2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/short_alpha_discriminator/opening_casebook.py` → `libs/reporting/short_alpha_discriminator/opening_casebook.py` | 11851 | `7e6d4b03ca5c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/short_alpha_discriminator/opening_policy_matrix.py` → `libs/reporting/short_alpha_discriminator/opening_policy_matrix.py` | 4591 | `24b18f6aed3d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/short_alpha_discriminator/pipeline.py` → `libs/reporting/short_alpha_discriminator/pipeline.py` | 7436 | `eda1a86903d6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/short_alpha_discriminator/profit_lock.py` → `libs/reporting/short_alpha_discriminator/profit_lock.py` | 3469 | `6fcbab0f61e7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/short_alpha_discriminator/report.py` → `libs/reporting/short_alpha_discriminator/report.py` | 7898 | `6c73340865e4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/short_alpha_discriminator/scanner_diagnostics.py` → `libs/reporting/short_alpha_discriminator/scanner_diagnostics.py` | 3875 | `b8de71424ec6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/short_alpha_discriminator/strategist_roi.py` → `libs/reporting/short_alpha_discriminator/strategist_roi.py` | 2753 | `ed568d3c5ff1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `tests/test_p15_latent_forward_cache_root_injection.py` → `tests/test_p15_latent_forward_cache_root_injection.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_quant_diagnosis_batch_alignment.py` → `tests/test_p15_quant_diagnosis_batch_alignment.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf034_alpha_board_canonical_status_tables_contract.py` → `tests/test_rf034_alpha_board_canonical_status_tables_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf034_alpha_board_loaders_large_cap_contract.py` → `tests/test_rf034_alpha_board_loaders_large_cap_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf034_alpha_board_runtime_validation_boundaries_contract.py` → `tests/test_rf034_alpha_board_runtime_validation_boundaries_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf034_alpha_board_sensitivity_remaining_reviews_contract.py` → `tests/test_rf034_alpha_board_sensitivity_remaining_reviews_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf034_alpha_board_writer_scope_tmp_root_contract.py` → `tests/test_rf034_alpha_board_writer_scope_tmp_root_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf034_opening_candle_provider_fake_contract.py` → `tests/test_rf034_opening_candle_provider_fake_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf034_opening_episodes_stubbed_contract.py` → `tests/test_rf034_opening_episodes_stubbed_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf034_opening_extraction_contract.py` → `tests/test_rf034_opening_extraction_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf034_opening_five_session_review_tmp_root_contract.py` → `tests/test_rf034_opening_five_session_review_tmp_root_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf034_opening_latent_forward_tmp_root_contract.py` → `tests/test_rf034_opening_latent_forward_tmp_root_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf034_opening_latent_watch_tmp_root_contract.py` → `tests/test_rf034_opening_latent_watch_tmp_root_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf034_opening_metrics_promotion_gates_contract.py` → `tests/test_rf034_opening_metrics_promotion_gates_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf034_opening_observability_contract.py` → `tests/test_rf034_opening_observability_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf034_opening_pipeline_day_status_tmp_root_contract.py` → `tests/test_rf034_opening_pipeline_day_status_tmp_root_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf034_opening_snapshot_metadata_conditional_alpha_contract.py` → `tests/test_rf034_opening_snapshot_metadata_conditional_alpha_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf034_quant_trade_diagnosis_writer_tmp_root_contract.py` → `tests/test_rf034_quant_trade_diagnosis_writer_tmp_root_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf034_short_alpha_pipeline_status_tmp_root_contract.py` → `tests/test_rf034_short_alpha_pipeline_status_tmp_root_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
