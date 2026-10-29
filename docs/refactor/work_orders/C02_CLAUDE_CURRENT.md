# C02 — Claude A | Reporting/AI 실제 함수 다중 이동·연속 구현

**유일한 진입점:** 이 C02. 동결 T00~T09/V3, [93개 RF 세부 설계 인덱스](../plan/rf_details/INDEX.md) 준수. A 허용 브랜치 `work/p15-a-reporter-pure-20261021` code/test만 수정·push. RF/STATUS/D00/C문서·B 브랜치·frozen oracle·live LLM/실거래/운영 DB/State는 수정 금지. 첫 한 함수 성공·KEEP·차단으로 종료하지 말고 A1~A5 연속 수행.

## 시작/KEEP/테스트 단순화

매회 integration HEAD·C02 blob·A 브랜치 remote HEAD·dirty만 확인. 이미 동일 SHA에서 이전한 함수는 반복 추출/테스트 금지. 목표 위치가 맞고 단일 책임·적절한 크기 또는 정당한 안전/외부 API 경계면 `KEEP_OK|RF|path|한 줄 이유|blob`로 즉시 PASS. MOVE는 기존 source 몸체가 사라지고 target 함수에 구현이 있어야 하며 기존 facade wrapper·use-time patch 경계 보존. 변경한 묶음의 fake old/new 기대 결과·예외 비교, 정상 pytest 또는 stdlib unittest **한 번 exit0**. 모든 RF -O/full CI/반대 peer 전수 금지.

## A1 (RF-031): Reporter AI review 입력·메시지·결과 정규화 실제 MOVE

[RF-031](../plan/rf_details/RF-031_IMPLEMENTATION.md); `libs/reporting/reporter_ai_review.py` A blob 참고 `a8c2507f`, 약500줄.
1. `_build_compact_input(day,out)` 약110줄 → `libs/reporting/reporter_ai_review_input.py::build_compact_input`.
2. `_build_messages(day,compact_input)` 약44줄 → 같은 파일 `build_messages`. `_clip_str/_list_str/json.dumps` 호출시점 patch 전달, 한국어·JSON key/order/prompt bytes·max-items 조건 동일.
3. `_normalize_evidence_link_items` 약21줄 → `libs/reporting/reporter_ai_review_result.py::normalize_evidence_link_items`.
4. `_normalize_result` 약25줄 → 같은 파일 `normalize_result`; `required_key_metadata`, null/default/error/key 순서 기존 그대로.
원본 public/private API 얇은 wrapper 유지. `tests/test_rf031_reporter_ai_review_input_extraction.py`와 `tests/test_rf031_reporter_ai_review_result_owner.py`에 old/new, malformed, spy monkeypatch, 입력 불변 fake fixture. 실제 LLM/파일 writer 이동 금지.

## A2 (RF-041): OpenAI Provider 응답 구조 투영 분리

[RF-041](../plan/rf_details/RF-041_IMPLEMENTATION.md); 원본 `libs/ai/providers/openai_provider.py` 참고 A blob `341296b5`.
- `_extract_chat_content` → `libs/ai/providers/openai_response_projection.py::extract_chat_content`
- `_extract_chat_structured_object` → 같은 파일 `extract_chat_structured_object`
- `_extract_usage` → 같은 파일 `extract_usage`.
- `_extract_chat_message`, `_extract_chat_finish_reason`, `_chat_output_truncated_without_final_answer`도 코드에서 단일 결과 투영 Owner가 적절한지 확인한 뒤 같은 module에 연속 이동(정확 이름·동작 유지).
`_post_json`, `_post_with_retry`, `decide`/사용자 broker 의도 실행은 원위치. 기존 `libs/llm/json_response.py` parsing 중복 구현 금지. structured/text/list/tool-call/reasoning/usage-none fixture, facade/patch seam parity 정상 테스트 1회. `tests/test_rf041_openai_response_projection.py` 미존재면 작성.

## A3 (RF-050/014/015): 정당한 좋은 Owner KEEP 일괄 소진

[RF-050](../plan/rf_details/RF-050_IMPLEMENTATION.md) `libs/llm/json_response.py`(91줄 단일 parser), [RF-014](../plan/rf_details/RF-014_IMPLEMENTATION.md) `libs/agents/scanner/candidate_risk.py`(113줄 위험 기반치), [RF-015](../plan/rf_details/RF-015_IMPLEMENTATION.md) `libs/agents/monitor/projections/cycle_detail_projection.py`(193줄 pure projection). 현재 목표 경로·한 역할·코드 중복 없음이면 **단회 KEEP_OK + blob**. 이미 있는 tests 같은 SHA 반복 금지.

## A4 (RF-061/040): 정상 API Facade 유지하고 내부 과대 함수만 추출

[RF-061](../plan/rf_details/RF-061_IMPLEMENTATION.md) `libs/tools/tool_facade.py`/ `tool_schema.py` 단일 Owner면 KEEP; [RF-040](../plan/rf_details/RF-040_IMPLEMENTATION.md) `libs/agent/commander.py`, `executor.py` 공개 API는 외부 import 호환 유지. 실제 순수 책임과 복잡한 효과 분리; 실주문/executor effect 변경 없음.

## A5: C03이 추가 지정한 A 독점 설계 함수 연속 MOVE

INDEX의 A 전담 상세설계 중 함수명/원본 경계가 **직접 확인된 항목**을 추가 수행. 미실측 함수 이름 임의 추측 금지; 명령서 미완료/blocked 항목을 한 줄 재개점으로 넘겨도 다음 독립 안전 아이템 계속.

## 보고

`ORDER_BLOB|ITEM/RF|SOURCE_BLOB|MOVED_FUNCTIONS|NEW_OWNER_PATH/BLOB|SOURCE_BEFORE_AFTER_LOC|KEEP_OK{reason,blob}|NORMAL_TEST_CMD_EXIT|PUSH_REMOTE_SHA|NEXT`를 #11에 한 번. A branch code/test만 정상 커밋/푸시하고 원격 blob 재조회; BLOCKED를 PASS로 만들지 않는다. 통합·DONE/STATUS는 C04/C05.
