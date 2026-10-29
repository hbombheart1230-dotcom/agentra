# RF-034 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@49cd60c4744c23ca556dbb633b197dbce4810d53`, RF 원본 `docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-034.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Claude A 구현 / Codex B read-only. 소유 59개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/reporting/alpha_research_board/builder.py` blob `0302499b8616c8f2daef55f0d1a7711b88069900` (702 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 본문 행수·주의 |
|---|---|---|---|
| `libs/reporting/alpha_research_board/builder.py::_opening_rows` L244-284 | MOVE_BODY | `libs/reporting/alpha_research_board/builder_opening_rows.py::_opening_rows` | 41행 · 순수 후보 |
| `libs/reporting/alpha_research_board/builder.py::_broad_opening` L285-313 | MOVE_BODY | `libs/reporting/alpha_research_board/builder_broad_opening.py::_broad_opening` | 29행 · 순수 후보 |
| `libs/reporting/alpha_research_board/builder.py::_large_cap_candidate` L354-381 | MOVE_BODY | `libs/reporting/alpha_research_board/builder_large_cap_candidate.py::_large_cap_candidate` | 28행 · 순수 후보 |
| `libs/reporting/alpha_research_board/builder.py::_latent` L314-336 | MOVE_BODY | `libs/reporting/alpha_research_board/builder_latent.py::_latent` | 23행 · 순수 후보 |
| `libs/reporting/alpha_research_board/builder.py::_fresh_change` L222-243 | MOVE_BODY | `libs/reporting/alpha_research_board/builder_fresh_change.py::_fresh_change` | 22행 · 순수 후보 |
| `libs/reporting/alpha_research_board/builder.py::_attention_order` L382-401 | MOVE_BODY | `libs/reporting/alpha_research_board/builder_attention_order.py::_attention_order` | 20행 · 순수 후보 |

### _opening_rows — 원본 41행
- **확인된 책임:** `libs/reporting/alpha_research_board/builder.py` L244–284; 직접 호출 helper `_candidate`. 감지된 효과: 없음.
- **목표:** `libs/reporting/alpha_research_board/builder_opening_rows.py::_opening_rows` (Owner Claude A, RF-034). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _broad_opening — 원본 29행
- **확인된 책임:** `libs/reporting/alpha_research_board/builder.py` L285–313; 직접 호출 helper `_candidate`. 감지된 효과: 없음.
- **목표:** `libs/reporting/alpha_research_board/builder_broad_opening.py::_broad_opening` (Owner Claude A, RF-034). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _large_cap_candidate — 원본 28행
- **확인된 책임:** `libs/reporting/alpha_research_board/builder.py` L354–381; 직접 호출 helper `_candidate`. 감지된 효과: 없음.
- **목표:** `libs/reporting/alpha_research_board/builder_large_cap_candidate.py::_large_cap_candidate` (Owner Claude A, RF-034). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _latent — 원본 23행
- **확인된 책임:** `libs/reporting/alpha_research_board/builder.py` L314–336; 직접 호출 helper `_candidate`. 감지된 효과: 없음.
- **목표:** `libs/reporting/alpha_research_board/builder_latent.py::_latent` (Owner Claude A, RF-034). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _fresh_change — 원본 22행
- **확인된 책임:** `libs/reporting/alpha_research_board/builder.py` L222–243; 직접 호출 helper `_candidate`. 감지된 효과: 없음.
- **목표:** `libs/reporting/alpha_research_board/builder_fresh_change.py::_fresh_change` (Owner Claude A, RF-034). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _attention_order — 원본 20행
- **확인된 책임:** `libs/reporting/alpha_research_board/builder.py` L382–401; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/reporting/alpha_research_board/builder_attention_order.py::_attention_order` (Owner Claude A, RF-034). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/reporting/alpha_research_board/__init__.py` | `libs/reporting/alpha_research_board/__init__.py` | `a25cdd9c1b0a` / 148B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/alpha_research_board/builder.py` | `libs/reporting/alpha_research_board/builder.py` | `0302499b8616` / 29104B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/reporting/alpha_research_board/canonical.py` | `libs/reporting/alpha_research_board/canonical.py` | `708e25522005` / 24163B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/alpha_research_board/contracts.py` | `libs/reporting/alpha_research_board/contracts.py` | `a4ce9c60b344` / 5274B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/alpha_research_board/large_cap_review.py` | `libs/reporting/alpha_research_board/large_cap_review.py` | `dafd27f10418` / 3245B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/alpha_research_board/loaders.py` | `libs/reporting/alpha_research_board/loaders.py` | `6dc31abcc33b` / 2771B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/alpha_research_board/remaining_reviews.py` | `libs/reporting/alpha_research_board/remaining_reviews.py` | `a641b46d5880` / 12305B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/alpha_research_board/report.py` | `libs/reporting/alpha_research_board/report.py` | `8d78a86fa402` / 5610B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/alpha_research_board/runtime_validation.py` | `libs/reporting/alpha_research_board/runtime_validation.py` | `5c416628336f` / 8315B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/alpha_research_board/sensitivity.py` | `libs/reporting/alpha_research_board/sensitivity.py` | `6df1cb912b12` / 15279B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/opening_rank1_shadow/__init__.py` | `libs/reporting/opening_rank1_shadow/__init__.py` | `721a51c59ab7` / 91B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/opening_rank1_shadow/candle_provider.py` | `libs/reporting/opening_rank1_shadow/candle_provider.py` | `fbca02731c82` / 3683B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/opening_rank1_shadow/contracts.py` | `libs/reporting/opening_rank1_shadow/contracts.py` | `dbfd0edb01cd` / 757B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/opening_rank1_shadow/episodes.py` | `libs/reporting/opening_rank1_shadow/episodes.py` | `de4ef55e9d9c` / 4200B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/opening_rank1_shadow/extraction.py` | `libs/reporting/opening_rank1_shadow/extraction.py` | `09b772c79e45` / 3345B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/opening_rank1_shadow/five_session_review.py` | `libs/reporting/opening_rank1_shadow/five_session_review.py` | `85cb3f708096` / 6817B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/opening_rank1_shadow/latent_forward.py` | `libs/reporting/opening_rank1_shadow/latent_forward.py` | `76a205900239` / 13687B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/opening_rank1_shadow/latent_watch.py` | `libs/reporting/opening_rank1_shadow/latent_watch.py` | `ce743711f479` / 11538B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/opening_rank1_shadow/market_snapshot.py` | `libs/reporting/opening_rank1_shadow/market_snapshot.py` | `fedec1cc7c4a` / 5277B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/opening_rank1_shadow/metrics.py` | `libs/reporting/opening_rank1_shadow/metrics.py` | `1eafd040278a` / 7844B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/opening_rank1_shadow/observability.py` | `libs/reporting/opening_rank1_shadow/observability.py` | `d2ffda950c9c` / 14241B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/opening_rank1_shadow/pipeline.py` | `libs/reporting/opening_rank1_shadow/pipeline.py` | `e8d7e89ff9b7` / 9050B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/opening_rank1_shadow/report.py` | `libs/reporting/opening_rank1_shadow/report.py` | `5055e0eaba3a` / 7477B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/opening_rank1_shadow/symbol_metadata.py` | `libs/reporting/opening_rank1_shadow/symbol_metadata.py` | `92676f1c44d9` / 2542B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/quant_trade_diagnosis/__init__.py` | `libs/reporting/quant_trade_diagnosis/__init__.py` | `e4e1a2c141e2` / 362B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/quant_trade_diagnosis/builder.py` | `libs/reporting/quant_trade_diagnosis/builder.py` | `85ba3dbfa8a4` / 22993B | 긴 파일: 함수 분리 필요성 1회 판단, 실제 이름 확보 전 무작위 MOVE 금지 |
| `libs/reporting/quant_trade_diagnosis/conditional_alpha.py` | `libs/reporting/quant_trade_diagnosis/conditional_alpha.py` | `2ccb53bf45a6` / 3709B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/quant_trade_diagnosis/markdown.py` | `libs/reporting/quant_trade_diagnosis/markdown.py` | `b3b3173db27f` / 12243B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/quant_trade_diagnosis/writer.py` | `libs/reporting/quant_trade_diagnosis/writer.py` | `ac718eee69ee` / 4513B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/short_alpha_discriminator/__init__.py` | `libs/reporting/short_alpha_discriminator/__init__.py` | `bf27962c6717` / 193B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/short_alpha_discriminator/cohorts.py` | `libs/reporting/short_alpha_discriminator/cohorts.py` | `c4f290ad50b4` / 10596B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/short_alpha_discriminator/contracts.py` | `libs/reporting/short_alpha_discriminator/contracts.py` | `706801b17251` / 638B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/short_alpha_discriminator/metrics.py` | `libs/reporting/short_alpha_discriminator/metrics.py` | `c2a64b2bdec2` / 2606B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/short_alpha_discriminator/opening_casebook.py` | `libs/reporting/short_alpha_discriminator/opening_casebook.py` | `7e6d4b03ca5c` / 11851B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/short_alpha_discriminator/opening_policy_matrix.py` | `libs/reporting/short_alpha_discriminator/opening_policy_matrix.py` | `24b18f6aed3d` / 4591B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/short_alpha_discriminator/pipeline.py` | `libs/reporting/short_alpha_discriminator/pipeline.py` | `eda1a86903d6` / 7436B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/short_alpha_discriminator/profit_lock.py` | `libs/reporting/short_alpha_discriminator/profit_lock.py` | `6fcbab0f61e7` / 3469B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/short_alpha_discriminator/report.py` | `libs/reporting/short_alpha_discriminator/report.py` | `6c73340865e4` / 7898B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/short_alpha_discriminator/scanner_diagnostics.py` | `libs/reporting/short_alpha_discriminator/scanner_diagnostics.py` | `b8de71424ec6` / 3875B | 짧은 단일 책임이면 KEEP_OK |
| `libs/reporting/short_alpha_discriminator/strategist_roi.py` | `libs/reporting/short_alpha_discriminator/strategist_roi.py` | `ed568d3c5ff1` / 2753B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_p15_latent_forward_cache_root_injection.py` | `tests/test_p15_latent_forward_cache_root_injection.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_p15_quant_diagnosis_batch_alignment.py` | `tests/test_p15_quant_diagnosis_batch_alignment.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf034_alpha_board_canonical_status_tables_contract.py` | `tests/test_rf034_alpha_board_canonical_status_tables_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf034_alpha_board_loaders_large_cap_contract.py` | `tests/test_rf034_alpha_board_loaders_large_cap_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf034_alpha_board_runtime_validation_boundaries_contract.py` | `tests/test_rf034_alpha_board_runtime_validation_boundaries_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf034_alpha_board_sensitivity_remaining_reviews_contract.py` | `tests/test_rf034_alpha_board_sensitivity_remaining_reviews_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf034_alpha_board_writer_scope_tmp_root_contract.py` | `tests/test_rf034_alpha_board_writer_scope_tmp_root_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf034_opening_candle_provider_fake_contract.py` | `tests/test_rf034_opening_candle_provider_fake_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf034_opening_episodes_stubbed_contract.py` | `tests/test_rf034_opening_episodes_stubbed_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf034_opening_extraction_contract.py` | `tests/test_rf034_opening_extraction_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf034_opening_five_session_review_tmp_root_contract.py` | `tests/test_rf034_opening_five_session_review_tmp_root_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf034_opening_latent_forward_tmp_root_contract.py` | `tests/test_rf034_opening_latent_forward_tmp_root_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf034_opening_latent_watch_tmp_root_contract.py` | `tests/test_rf034_opening_latent_watch_tmp_root_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf034_opening_metrics_promotion_gates_contract.py` | `tests/test_rf034_opening_metrics_promotion_gates_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf034_opening_observability_contract.py` | `tests/test_rf034_opening_observability_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf034_opening_pipeline_day_status_tmp_root_contract.py` | `tests/test_rf034_opening_pipeline_day_status_tmp_root_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf034_opening_snapshot_metadata_conditional_alpha_contract.py` | `tests/test_rf034_opening_snapshot_metadata_conditional_alpha_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf034_quant_trade_diagnosis_writer_tmp_root_contract.py` | `tests/test_rf034_quant_trade_diagnosis_writer_tmp_root_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf034_short_alpha_pipeline_status_tmp_root_contract.py` | `tests/test_rf034_short_alpha_pipeline_status_tmp_root_contract.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Claude A 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #11에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-034|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
