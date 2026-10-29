# RF-033 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@49cd60c4744c23ca556dbb633b197dbce4810d53`, RF 원본 `docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-033.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Claude A 구현 / Codex B read-only. 소유 76개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/reporting/baseline_samsung_hynix/forward_validation/reaction_reader.py` blob `498d4aeb8b26291d83780966be2b11320d305b9c` (468 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 본문 행수·주의 |
|---|---|---|---|
| `libs/reporting/baseline_samsung_hynix/forward_validation/reaction_reader.py::load_index_timeline` L271-297 | MOVE_BODY | `libs/reporting/baseline_samsung_hynix/forward_validation/reaction_reader_load_index_timeline.py::load_index_timeline` | 27행 · 순수 후보 |

### load_index_timeline — 원본 27행
- **확인된 책임:** `libs/reporting/baseline_samsung_hynix/forward_validation/reaction_reader.py` L271–297; 직접 호출 helper `_number`. 감지된 효과: 없음.
- **목표:** `libs/reporting/baseline_samsung_hynix/forward_validation/reaction_reader_load_index_timeline.py::load_index_timeline` (Owner Claude A, RF-033). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/reporting/baseline_btc_woori_tech/__init__.py` | `libs/reporting/baseline_btc_woori_tech/__init__.py` | `7a15714ef0fe` / 108B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/comparison.py` | `libs/reporting/baseline_btc_woori_tech/comparison.py` | `9d5f01d342d5` / 3830B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/contracts.py` | `libs/reporting/baseline_btc_woori_tech/contracts.py` | `184f2345a1a3` / 1536B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/crypto_fear_greed.py` | `libs/reporting/baseline_btc_woori_tech/crypto_fear_greed.py` | `a16d962e45cf` / 3432B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/data_provider.py` | `libs/reporting/baseline_btc_woori_tech/data_provider.py` | `279f08346f8d` / 13118B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/forward_returns.py` | `libs/reporting/baseline_btc_woori_tech/forward_returns.py` | `8d2904c6cfa4` / 2197B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/historical_review.py` | `libs/reporting/baseline_btc_woori_tech/historical_review.py` | `e0d52958dd18` / 19797B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/hypothesis_features.py` | `libs/reporting/baseline_btc_woori_tech/hypothesis_features.py` | `7b216156282b` / 14052B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/hypothesis_forward.py` | `libs/reporting/baseline_btc_woori_tech/hypothesis_forward.py` | `f2f6e4025653` / 4391B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/hypothesis_pipeline.py` | `libs/reporting/baseline_btc_woori_tech/hypothesis_pipeline.py` | `cf43565e08a9` / 14723B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/input_delivery.py` | `libs/reporting/baseline_btc_woori_tech/input_delivery.py` | `42525d032177` / 4085B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/input_worker.py` | `libs/reporting/baseline_btc_woori_tech/input_worker.py` | `2184c9ee5714` / 2341B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/pipeline.py` | `libs/reporting/baseline_btc_woori_tech/pipeline.py` | `16ef443139ba` / 11910B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/point_in_time_capture.py` | `libs/reporting/baseline_btc_woori_tech/point_in_time_capture.py` | `1ad80f308a42` / 9445B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/report.py` | `libs/reporting/baseline_btc_woori_tech/report.py` | `af7818394d7c` / 7896B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/strategy.py` | `libs/reporting/baseline_btc_woori_tech/strategy.py` | `48852cba5869` / 8181B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/trend_context.py` | `libs/reporting/baseline_btc_woori_tech/trend_context.py` | `0777474a9918` / 7536B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/vnext/__init__.py` | `libs/reporting/baseline_btc_woori_tech/vnext/__init__.py` | `1e1e1e5ac3e8` / 68B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/vnext/contract.py` | `libs/reporting/baseline_btc_woori_tech/vnext/contract.py` | `23050b42ee28` / 1931B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/vnext/equities.py` | `libs/reporting/baseline_btc_woori_tech/vnext/equities.py` | `1a1b8220414f` / 2706B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/vnext/features.py` | `libs/reporting/baseline_btc_woori_tech/vnext/features.py` | `35df29fccde3` / 7618B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/vnext/outcomes.py` | `libs/reporting/baseline_btc_woori_tech/vnext/outcomes.py` | `78af9428a6f4` / 2374B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/vnext/pipeline.py` | `libs/reporting/baseline_btc_woori_tech/vnext/pipeline.py` | `c6d8298ae35a` / 6882B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/vnext/report.py` | `libs/reporting/baseline_btc_woori_tech/vnext/report.py` | `d3d8b8a31ec2` / 3520B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/vnext/storage.py` | `libs/reporting/baseline_btc_woori_tech/vnext/storage.py` | `23783494b75f` / 1141B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_btc_woori_tech/vnext/time_alignment.py` | `libs/reporting/baseline_btc_woori_tech/vnext/time_alignment.py` | `682c1ec92b94` / 3584B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/__init__.py` | `libs/reporting/baseline_samsung_hynix/__init__.py` | `637efe8155e8` / 148B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/contracts.py` | `libs/reporting/baseline_samsung_hynix/contracts.py` | `a751cabb1025` / 739B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/data_provider.py` | `libs/reporting/baseline_samsung_hynix/data_provider.py` | `e7afb053d162` / 3877B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/forward_returns.py` | `libs/reporting/baseline_samsung_hynix/forward_returns.py` | `9648a6397f53` / 9248B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/forward_validation/__init__.py` | `libs/reporting/baseline_samsung_hynix/forward_validation/__init__.py` | `4a5584b9feab` / 157B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/forward_validation/collector_observations.py` | `libs/reporting/baseline_samsung_hynix/forward_validation/collector_observations.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/forward_validation/contracts.py` | `libs/reporting/baseline_samsung_hynix/forward_validation/contracts.py` | `398d7953cb7c` / 2364B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/forward_validation/cumulative.py` | `libs/reporting/baseline_samsung_hynix/forward_validation/cumulative.py` | `7feb5a2a3653` / 2966B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/forward_validation/expected_actual.py` | `libs/reporting/baseline_samsung_hynix/forward_validation/expected_actual.py` | `af44d9c3dc31` / 2557B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/forward_validation/index_timeline.py` | `libs/reporting/baseline_samsung_hynix/forward_validation/index_timeline.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/forward_validation/market_inputs.py` | `libs/reporting/baseline_samsung_hynix/forward_validation/market_inputs.py` | `d13ca10770d8` / 9939B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/forward_validation/pipeline.py` | `libs/reporting/baseline_samsung_hynix/forward_validation/pipeline.py` | `ac5bc7d51cd3` / 8233B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/forward_validation/reaction_reader.py` | `libs/reporting/baseline_samsung_hynix/forward_validation/reaction_reader.py` | `498d4aeb8b26` / 22637B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/reporting/baseline_samsung_hynix/forward_validation/report.py` | `libs/reporting/baseline_samsung_hynix/forward_validation/report.py` | `c9daf1bf1555` / 6170B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/forward_validation/scoring.py` | `libs/reporting/baseline_samsung_hynix/forward_validation/scoring.py` | `eabadb19de98` / 6496B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/forward_validation/shadow_comparison.py` | `libs/reporting/baseline_samsung_hynix/forward_validation/shadow_comparison.py` | `9ec0ec0b9c7c` / 6084B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/forward_validation/stock_reaction.py` | `libs/reporting/baseline_samsung_hynix/forward_validation/stock_reaction.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/pipeline.py` | `libs/reporting/baseline_samsung_hynix/pipeline.py` | `a3b1faaf631d` / 10118B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/q9_comparison.py` | `libs/reporting/baseline_samsung_hynix/q9_comparison.py` | `a3d81762f5af` / 7057B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/report.py` | `libs/reporting/baseline_samsung_hynix/report.py` | `6e2cc6b880b4` / 3907B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/strategy.py` | `libs/reporting/baseline_samsung_hynix/strategy.py` | `33e578064039` / 5844B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/baseline_samsung_hynix/unified_comparison.py` | `libs/reporting/baseline_samsung_hynix/unified_comparison.py` | `25b68b9fe499` / 12669B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_p15_btc_forward_report_parity.py` | `tests/test_p15_btc_forward_report_parity.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_p15_collector_observations_extraction.py` | `tests/test_p15_collector_observations_extraction.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_p15_forward_validation_parity_chain.py` | `tests/test_p15_forward_validation_parity_chain.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_p15_index_timeline_extraction.py` | `tests/test_p15_index_timeline_extraction.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_p15_q10_cumulative_malformed_inputs.py` | `tests/test_p15_q10_cumulative_malformed_inputs.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_p15_q10_cumulative_numeric_boundary.py` | `tests/test_p15_q10_cumulative_numeric_boundary.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_p15_q10_forward_pipeline_temp_contract.py` | `tests/test_p15_q10_forward_pipeline_temp_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_p15_q10_preopen_capture_temp_contract.py` | `tests/test_p15_q10_preopen_capture_temp_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_p15_q10_report_missing_value_contract.py` | `tests/test_p15_q10_report_missing_value_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_p15_q9_malformed_rank_contract.py` | `tests/test_p15_q9_malformed_rank_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_p15_q9_offline_optout.py` | `tests/test_p15_q9_offline_optout.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_p15_stock_reaction_extraction.py` | `tests/test_p15_stock_reaction_extraction.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf033_btc_data_provider_fake_yfinance_contract.py` | `tests/test_rf033_btc_data_provider_fake_yfinance_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf033_btc_historical_review_tmp_root_contract.py` | `tests/test_rf033_btc_historical_review_tmp_root_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf033_btc_hypothesis_features_daily_context_contract.py` | `tests/test_rf033_btc_hypothesis_features_daily_context_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf033_btc_input_worker_stubbed_contract.py` | `tests/test_rf033_btc_input_worker_stubbed_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf033_btc_point_in_time_capture_paths_contract.py` | `tests/test_rf033_btc_point_in_time_capture_paths_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf033_btc_vnext_equities_alignment_fake_contract.py` | `tests/test_rf033_btc_vnext_equities_alignment_fake_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf033_btc_vnext_storage_pipeline_tmp_root_contract.py` | `tests/test_rf033_btc_vnext_storage_pipeline_tmp_root_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf033_crypto_fear_greed_fake_http_contract.py` | `tests/test_rf033_crypto_fear_greed_fake_http_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf033_samsung_forward_reaction_reader_contract.py` | `tests/test_rf033_samsung_forward_reaction_reader_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf033_samsung_forward_report_render_contract.py` | `tests/test_rf033_samsung_forward_report_render_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf033_samsung_forward_returns_contract.py` | `tests/test_rf033_samsung_forward_returns_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf033_samsung_forward_scoring_contract.py` | `tests/test_rf033_samsung_forward_scoring_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf033_samsung_forward_shadow_comparison_contract.py` | `tests/test_rf033_samsung_forward_shadow_comparison_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf033_samsung_forward_validation_capture_tmp_root_contract.py` | `tests/test_rf033_samsung_forward_validation_capture_tmp_root_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf033_samsung_market_inputs_and_provider_fake_contract.py` | `tests/test_rf033_samsung_market_inputs_and_provider_fake_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf033_samsung_q9_comparison_stubbed_contract.py` | `tests/test_rf033_samsung_q9_comparison_stubbed_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Claude A 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #11에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-033|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
