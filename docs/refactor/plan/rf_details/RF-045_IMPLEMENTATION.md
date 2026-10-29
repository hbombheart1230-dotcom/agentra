# RF-045 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@49cd60c4744c23ca556dbb633b197dbce4810d53`, RF 원본 `docs/refactor/plan/queue/02_DEVELOPING/CODEX_B/RF-045.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Codex B 구현 / Claude A read-only. 소유 24개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/core/event_logger.py` blob `de869be7efe526b83b5d5cf75a4a6908a09e0d87` (634 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 본문 행수·주의 |
|---|---|---|---|
| `libs/core/event_logger.py::_compact_event_payload` L265-456 | MOVE_BODY | `libs/core/event_logger_compact_event_payload.py::_compact_event_payload` | 192행 · 순수 후보 |
| `libs/core/event_logger.py::_compact_candidate_ranking_table` L220-264 | MOVE_BODY | `libs/core/event_logger_compact_candidate_ranking_table.py::_compact_candidate_ranking_table` | 45행 · 순수 후보 |
| `libs/core/event_logger.py::_compact_value` L188-210 | MOVE_BODY | `libs/core/event_logger_compact_value.py::_compact_value` | 23행 · 순수 후보 |

### _compact_event_payload — 원본 192행
- **확인된 책임:** `libs/core/event_logger.py` L265–456; 직접 호출 helper `_payload_size_bytes`, `_event_log_payload_max_bytes`, `_event_log_compaction_enabled`, `_compact_candidate_ranking_table`, `_copy_known_fields`, `_compact_value`. 감지된 효과: 없음.
- **목표:** `libs/core/event_logger_compact_event_payload.py::_compact_event_payload` (Owner Codex B, RF-045). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _compact_candidate_ranking_table — 원본 45행
- **확인된 책임:** `libs/core/event_logger.py` L220–264; 직접 호출 helper `_event_log_compact_top_items`, `_copy_known_fields`, `_symbol_list`, `_compact_rows`. 감지된 효과: 없음.
- **목표:** `libs/core/event_logger_compact_candidate_ranking_table.py::_compact_candidate_ranking_table` (Owner Codex B, RF-045). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _compact_value — 원본 23행
- **확인된 책임:** `libs/core/event_logger.py` L188–210; 직접 호출 helper `_event_log_compact_top_items`. 감지된 효과: 없음.
- **목표:** `libs/core/event_logger_compact_value.py::_compact_value` (Owner Codex B, RF-045). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/core/__init__.py` | `libs/core/__init__.py` | `a58a6f63e75b` / 44B | 짧은 단일 책임이면 KEEP_OK |
| `libs/core/api_response.py` | `libs/core/api_response.py` | `735135397ad5` / 1535B | 짧은 단일 책임이면 KEEP_OK |
| `libs/core/event_logger.py` | `libs/core/event_logger.py` | `de869be7efe5` / 21184B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/core/event_logger_compat.py` | `libs/core/event_logger_compat.py` | `d1631462afdf` / 818B | 짧은 단일 책임이면 KEEP_OK |
| `libs/core/evidence_identity.py` | `libs/core/evidence_identity.py` | `1ac50c223048` / 1288B | 짧은 단일 책임이면 KEEP_OK |
| `libs/core/http_client.py` | `libs/core/http_client.py` | `ebe129012f83` / 3213B | 짧은 단일 책임이면 KEEP_OK |
| `libs/core/log_maintenance.py` | `libs/core/log_maintenance.py` | `8d59f437d16f` / 9775B | 짧은 단일 책임이면 KEEP_OK |
| `libs/core/path_isolation.py` | `libs/core/path_isolation.py` | `cf7c4ee50950` / 9793B | 짧은 단일 책임이면 KEEP_OK |
| `libs/core/settings.py` | `libs/core/settings.py` | `b93f9e35006a` / 5345B | 짧은 단일 책임이면 KEEP_OK |
| `libs/core/symbols.py` | `libs/core/symbols.py` | `f99515c5cab7` / 1618B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_p15_event_logger_caller_bridge.py` | `tests/test_p15_event_logger_caller_bridge.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_p15_event_logger_constructor_matrix.py` | `tests/test_p15_event_logger_constructor_matrix.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_p15_log_move_root_boundary.py` | `tests/test_p15_log_move_root_boundary.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf045_core_contracts.py` | `tests/test_rf045_core_contracts.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf045_core_pure_boundaries.py` | `tests/test_rf045_core_pure_boundaries.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf045_event_logger_compat_attribute_exception.py` | `tests/test_rf045_event_logger_compat_attribute_exception.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf045_event_logger_compat_consumer.py` | `tests/test_rf045_event_logger_compat_consumer.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf045_event_logger_exception_boundary.py` | `tests/test_rf045_event_logger_exception_boundary.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf045_event_logger_real_compat.py` | `tests/test_rf045_event_logger_real_compat.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf045_http_retry_boundary.py` | `tests/test_rf045_http_retry_boundary.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf045_http_retry_method_backoff.py` | `tests/test_rf045_http_retry_method_backoff.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf045_log_inventory_output_boundary.py` | `tests/test_rf045_log_inventory_output_boundary.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf045_owner_c1_inventory.py` | `tests/test_rf045_owner_c1_inventory.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |
| `tests/test_rf045_settings_consumer_exceptions.py` | `tests/test_rf045_settings_consumer_exceptions.py` | `BASELINE` / 0B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Codex B 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #12에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-045|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
