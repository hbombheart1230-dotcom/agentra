# RF-033 — 코드 구조/함수 재배치 설계 (T00/V3)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-033.md` blob `61185ed08eb5cf71b043194360662f437bb5e518`.
**구현 담당:** **Claude A**, 상대 **Codex B**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 76개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `libs/reporting/baseline_samsung_hynix/forward_validation/reaction_reader.py` | 22637 | `498d4aeb8b26291d83780966be2b11320d305b9c` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/reporting/baseline_samsung_hynix/forward_validation/reaction_reader_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `libs/reporting/baseline_btc_woori_tech/__init__.py` → `libs/reporting/baseline_btc_woori_tech/__init__.py` | 108 | `7a15714ef0fe` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/comparison.py` → `libs/reporting/baseline_btc_woori_tech/comparison.py` | 3830 | `9d5f01d342d5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/contracts.py` → `libs/reporting/baseline_btc_woori_tech/contracts.py` | 1536 | `184f2345a1a3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/crypto_fear_greed.py` → `libs/reporting/baseline_btc_woori_tech/crypto_fear_greed.py` | 3432 | `a16d962e45cf` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/data_provider.py` → `libs/reporting/baseline_btc_woori_tech/data_provider.py` | 13118 | `279f08346f8d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/forward_returns.py` → `libs/reporting/baseline_btc_woori_tech/forward_returns.py` | 2197 | `8d2904c6cfa4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/historical_review.py` → `libs/reporting/baseline_btc_woori_tech/historical_review.py` | 19797 | `e0d52958dd18` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/hypothesis_features.py` → `libs/reporting/baseline_btc_woori_tech/hypothesis_features.py` | 14052 | `7b216156282b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/hypothesis_forward.py` → `libs/reporting/baseline_btc_woori_tech/hypothesis_forward.py` | 4391 | `f2f6e4025653` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/hypothesis_pipeline.py` → `libs/reporting/baseline_btc_woori_tech/hypothesis_pipeline.py` | 14723 | `cf43565e08a9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/input_delivery.py` → `libs/reporting/baseline_btc_woori_tech/input_delivery.py` | 4085 | `42525d032177` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/input_worker.py` → `libs/reporting/baseline_btc_woori_tech/input_worker.py` | 2341 | `2184c9ee5714` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/pipeline.py` → `libs/reporting/baseline_btc_woori_tech/pipeline.py` | 11910 | `16ef443139ba` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/point_in_time_capture.py` → `libs/reporting/baseline_btc_woori_tech/point_in_time_capture.py` | 9445 | `1ad80f308a42` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/report.py` → `libs/reporting/baseline_btc_woori_tech/report.py` | 7896 | `af7818394d7c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/strategy.py` → `libs/reporting/baseline_btc_woori_tech/strategy.py` | 8181 | `48852cba5869` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/trend_context.py` → `libs/reporting/baseline_btc_woori_tech/trend_context.py` | 7536 | `0777474a9918` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/vnext/__init__.py` → `libs/reporting/baseline_btc_woori_tech/vnext/__init__.py` | 68 | `1e1e1e5ac3e8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/vnext/contract.py` → `libs/reporting/baseline_btc_woori_tech/vnext/contract.py` | 1931 | `23050b42ee28` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/vnext/equities.py` → `libs/reporting/baseline_btc_woori_tech/vnext/equities.py` | 2706 | `1a1b8220414f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/vnext/features.py` → `libs/reporting/baseline_btc_woori_tech/vnext/features.py` | 7618 | `35df29fccde3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/vnext/outcomes.py` → `libs/reporting/baseline_btc_woori_tech/vnext/outcomes.py` | 2374 | `78af9428a6f4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/vnext/pipeline.py` → `libs/reporting/baseline_btc_woori_tech/vnext/pipeline.py` | 6882 | `c6d8298ae35a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/vnext/report.py` → `libs/reporting/baseline_btc_woori_tech/vnext/report.py` | 3520 | `d3d8b8a31ec2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/vnext/storage.py` → `libs/reporting/baseline_btc_woori_tech/vnext/storage.py` | 1141 | `23783494b75f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_btc_woori_tech/vnext/time_alignment.py` → `libs/reporting/baseline_btc_woori_tech/vnext/time_alignment.py` | 3584 | `682c1ec92b94` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/__init__.py` → `libs/reporting/baseline_samsung_hynix/__init__.py` | 148 | `637efe8155e8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/contracts.py` → `libs/reporting/baseline_samsung_hynix/contracts.py` | 739 | `a751cabb1025` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/data_provider.py` → `libs/reporting/baseline_samsung_hynix/data_provider.py` | 3877 | `e7afb053d162` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/forward_returns.py` → `libs/reporting/baseline_samsung_hynix/forward_returns.py` | 9248 | `9648a6397f53` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/forward_validation/__init__.py` → `libs/reporting/baseline_samsung_hynix/forward_validation/__init__.py` | 157 | `4a5584b9feab` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/forward_validation/collector_observations.py` → `libs/reporting/baseline_samsung_hynix/forward_validation/collector_observations.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/forward_validation/contracts.py` → `libs/reporting/baseline_samsung_hynix/forward_validation/contracts.py` | 2364 | `398d7953cb7c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/forward_validation/cumulative.py` → `libs/reporting/baseline_samsung_hynix/forward_validation/cumulative.py` | 2966 | `7feb5a2a3653` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/forward_validation/expected_actual.py` → `libs/reporting/baseline_samsung_hynix/forward_validation/expected_actual.py` | 2557 | `af44d9c3dc31` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/forward_validation/index_timeline.py` → `libs/reporting/baseline_samsung_hynix/forward_validation/index_timeline.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/forward_validation/market_inputs.py` → `libs/reporting/baseline_samsung_hynix/forward_validation/market_inputs.py` | 9939 | `d13ca10770d8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/forward_validation/pipeline.py` → `libs/reporting/baseline_samsung_hynix/forward_validation/pipeline.py` | 8233 | `ac5bc7d51cd3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/forward_validation/reaction_reader.py` → `libs/reporting/baseline_samsung_hynix/forward_validation/reaction_reader.py` | 22637 | `498d4aeb8b26` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/forward_validation/report.py` → `libs/reporting/baseline_samsung_hynix/forward_validation/report.py` | 6170 | `c9daf1bf1555` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/forward_validation/scoring.py` → `libs/reporting/baseline_samsung_hynix/forward_validation/scoring.py` | 6496 | `eabadb19de98` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/forward_validation/shadow_comparison.py` → `libs/reporting/baseline_samsung_hynix/forward_validation/shadow_comparison.py` | 6084 | `9ec0ec0b9c7c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/forward_validation/stock_reaction.py` → `libs/reporting/baseline_samsung_hynix/forward_validation/stock_reaction.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/pipeline.py` → `libs/reporting/baseline_samsung_hynix/pipeline.py` | 10118 | `a3b1faaf631d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/q9_comparison.py` → `libs/reporting/baseline_samsung_hynix/q9_comparison.py` | 7057 | `a3d81762f5af` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/report.py` → `libs/reporting/baseline_samsung_hynix/report.py` | 3907 | `6e2cc6b880b4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/strategy.py` → `libs/reporting/baseline_samsung_hynix/strategy.py` | 5844 | `33e578064039` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/reporting/baseline_samsung_hynix/unified_comparison.py` → `libs/reporting/baseline_samsung_hynix/unified_comparison.py` | 12669 | `25b68b9fe499` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `tests/test_p15_btc_forward_report_parity.py` → `tests/test_p15_btc_forward_report_parity.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_collector_observations_extraction.py` → `tests/test_p15_collector_observations_extraction.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_forward_validation_parity_chain.py` → `tests/test_p15_forward_validation_parity_chain.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_index_timeline_extraction.py` → `tests/test_p15_index_timeline_extraction.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_q10_cumulative_malformed_inputs.py` → `tests/test_p15_q10_cumulative_malformed_inputs.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_q10_cumulative_numeric_boundary.py` → `tests/test_p15_q10_cumulative_numeric_boundary.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_q10_forward_pipeline_temp_contract.py` → `tests/test_p15_q10_forward_pipeline_temp_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_q10_preopen_capture_temp_contract.py` → `tests/test_p15_q10_preopen_capture_temp_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_q10_report_missing_value_contract.py` → `tests/test_p15_q10_report_missing_value_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_q9_malformed_rank_contract.py` → `tests/test_p15_q9_malformed_rank_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_q9_offline_optout.py` → `tests/test_p15_q9_offline_optout.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_stock_reaction_extraction.py` → `tests/test_p15_stock_reaction_extraction.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf033_btc_data_provider_fake_yfinance_contract.py` → `tests/test_rf033_btc_data_provider_fake_yfinance_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf033_btc_historical_review_tmp_root_contract.py` → `tests/test_rf033_btc_historical_review_tmp_root_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf033_btc_hypothesis_features_daily_context_contract.py` → `tests/test_rf033_btc_hypothesis_features_daily_context_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf033_btc_input_worker_stubbed_contract.py` → `tests/test_rf033_btc_input_worker_stubbed_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf033_btc_point_in_time_capture_paths_contract.py` → `tests/test_rf033_btc_point_in_time_capture_paths_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf033_btc_vnext_equities_alignment_fake_contract.py` → `tests/test_rf033_btc_vnext_equities_alignment_fake_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf033_btc_vnext_storage_pipeline_tmp_root_contract.py` → `tests/test_rf033_btc_vnext_storage_pipeline_tmp_root_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf033_crypto_fear_greed_fake_http_contract.py` → `tests/test_rf033_crypto_fear_greed_fake_http_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf033_samsung_forward_reaction_reader_contract.py` → `tests/test_rf033_samsung_forward_reaction_reader_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf033_samsung_forward_report_render_contract.py` → `tests/test_rf033_samsung_forward_report_render_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf033_samsung_forward_returns_contract.py` → `tests/test_rf033_samsung_forward_returns_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf033_samsung_forward_scoring_contract.py` → `tests/test_rf033_samsung_forward_scoring_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf033_samsung_forward_shadow_comparison_contract.py` → `tests/test_rf033_samsung_forward_shadow_comparison_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf033_samsung_forward_validation_capture_tmp_root_contract.py` → `tests/test_rf033_samsung_forward_validation_capture_tmp_root_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf033_samsung_market_inputs_and_provider_fake_contract.py` → `tests/test_rf033_samsung_market_inputs_and_provider_fake_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf033_samsung_q9_comparison_stubbed_contract.py` → `tests/test_rf033_samsung_q9_comparison_stubbed_contract.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
