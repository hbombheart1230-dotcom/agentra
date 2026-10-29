# C02 — Claude A | Reporting/AI 실제 함수 다중 이동·연속 구현

## 실행 진입 계약 — A/B에게 다른 문서 탐색 지시 금지 (최우선)

**A/B 각각 이 파일 하나만 읽고 개발을 수행한다.** `docs/refactor/plan/rf_details/`, `INDEX.md`, D00, C03, Txx, 원본 RF, STATUS를 A/B가 열거나 읽고 작업을 고르게 하지 않는다. 필요한 **SOURCE_PATH::EXACT_FUNCTION → TARGET_PATH::EXACT_FUNCTION, 함수 몸체 처리, 주입해야 할 의존성, 테스트 fixture, KEEP 사유, 담당 독점권, 우선순위 및 재개점은 모두 아래 C01/C02 본문에 완전히 복사**한다. GitHub의 *실제 작업 대상 코드 파일*과 호출자·타깃 파일은 직접 열어 구현할 수 있다. 자기 작업이 끝나도 다음 항목을 순서대로 진행한다.

C03 지팀장이 93개 RF 설계서/실제 source를 읽고 필요한 다음 구현 항목을 이 단일 지시서의 **작업 큐 본문에 인라인 추가**한다. A/B가 상세설계를 찾아가라는 문구는 무효. 지시서에 없는 RF/함수는 새로 추정하지 않고 C03이 배정할 때까지 기존 다른 항목 진행. 각 차수에 4~6개 이상 독립 코드 항목을 유지하며 기존 완료 항목은 제거·추가. 구 구현과 목적지 소유권을 실제 시작 source blob에서 확인하여 중복 개발 금지.


**유일한 진입점:** 이 C02 파일만. 동결 T00~T09/V3에 따라 아래 작업 큐에 직접 명시된 구현만 수행한다. A 허용 브랜치 `work/p15-a-reporter-pure-20261021` code/test만 수정·push. RF/STATUS/D00/C문서·B 브랜치·frozen oracle·live LLM/실거래/운영 DB/State는 수정 금지. 첫 한 함수 성공·KEEP·차단으로 종료하지 말고 A1~A5 연속 수행.

## 시작/KEEP/테스트 단순화

매회 integration HEAD·C02 blob·A 브랜치 remote HEAD·dirty만 확인. 이미 동일 SHA에서 이전한 함수는 반복 추출/테스트 금지. 목표 위치가 맞고 단일 책임·적절한 크기 또는 정당한 안전/외부 API 경계면 `KEEP_OK|RF|path|한 줄 이유|blob`로 즉시 PASS. MOVE는 기존 source 몸체가 사라지고 target 함수에 구현이 있어야 하며 기존 facade wrapper·use-time patch 경계 보존. 변경한 묶음의 fake old/new 기대 결과·예외 비교, 정상 pytest 또는 stdlib unittest **한 번 exit0**. 모든 RF -O/full CI/반대 peer 전수 금지.

## A1 (RF-031): Reporter AI review 입력·메시지·결과 정규화 실제 MOVE

RF-031; `libs/reporting/reporter_ai_review.py` A blob 참고 `a8c2507f`, 약500줄.
1. `_build_compact_input(day,out)` 약110줄 → `libs/reporting/reporter_ai_review_input.py::build_compact_input`.
2. `_build_messages(day,compact_input)` 약44줄 → 같은 파일 `build_messages`. `_clip_str/_list_str/json.dumps` 호출시점 patch 전달, 한국어·JSON key/order/prompt bytes·max-items 조건 동일.
3. `_normalize_evidence_link_items` 약21줄 → `libs/reporting/reporter_ai_review_result.py::normalize_evidence_link_items`.
4. `_normalize_result` 약25줄 → 같은 파일 `normalize_result`; `required_key_metadata`, null/default/error/key 순서 기존 그대로.
원본 public/private API 얇은 wrapper 유지. `tests/test_rf031_reporter_ai_review_input_extraction.py`와 `tests/test_rf031_reporter_ai_review_result_owner.py`에 old/new, malformed, spy monkeypatch, 입력 불변 fake fixture. 실제 LLM/파일 writer 이동 금지.

## A2 (RF-041): OpenAI Provider 응답 구조 투영 분리

RF-041; 원본 `libs/ai/providers/openai_provider.py` 참고 A blob `341296b5`.
- `_extract_chat_content` → `libs/ai/providers/openai_response_projection.py::extract_chat_content`
- `_extract_chat_structured_object` → 같은 파일 `extract_chat_structured_object`
- `_extract_usage` → 같은 파일 `extract_usage`.
- `_extract_chat_message`, `_extract_chat_finish_reason`, `_chat_output_truncated_without_final_answer`도 코드에서 단일 결과 투영 Owner가 적절한지 확인한 뒤 같은 module에 연속 이동(정확 이름·동작 유지).
`_post_json`, `_post_with_retry`, `decide`/사용자 broker 의도 실행은 원위치. 기존 `libs/llm/json_response.py` parsing 중복 구현 금지. structured/text/list/tool-call/reasoning/usage-none fixture, facade/patch seam parity 정상 테스트 1회. `tests/test_rf041_openai_response_projection.py` 미존재면 작성.

## A3 (RF-050/014/015): 정당한 좋은 Owner KEEP 일괄 소진

RF-050 `libs/llm/json_response.py`(91줄 단일 parser), RF-014 `libs/agents/scanner/candidate_risk.py`(113줄 위험 기반치), RF-015 `libs/agents/monitor/projections/cycle_detail_projection.py`(193줄 pure projection). 현재 목표 경로·한 역할·코드 중복 없음이면 **단회 KEEP_OK + blob**. 이미 있는 tests 같은 SHA 반복 금지.

## A4 (RF-061/040): 정상 API Facade 유지하고 내부 과대 함수만 추출

RF-061 `libs/tools/tool_facade.py`/ `tool_schema.py` 단일 Owner면 KEEP; RF-040 `libs/agent/commander.py`, `executor.py` 공개 API는 외부 import 호환 유지. 실제 순수 책임과 복잡한 효과 분리; 실주문/executor effect 변경 없음.

## A5 확장 — RF-016 및 RF-050의 이미 맞는 작은 Owner 즉시 KEEP

- `libs/agents/strategist/context/news_compaction.py`: news/message compaction이라는 한 책임이며 기존 `_compact_global_signal_for_llm_r3_impl` 약111행·뉴스 보조 함수는 **기존 Owner에서 적절하게 분리되어 있으면 KEEP_OK**. 함수별 파일을 무조건 더 만들지 않는다.
- `libs/llm/json_response.py`: 91행·JSON response parsing 단일 책임이면 KEEP_OK. 이 파일과 OpenAI provider `_extract_chat_structured_object`의 중복 parser가 있다면 중복 기능 제거만 수행.
- 위 두 파일은 정확한 blob과 한 줄 사유만 제출. PASS/재시험 0, 변경 성과에 포함하지 않는다.

## A6: C03이 C02 본문에 직접 넣은 A 독점 함수 연속 MOVE

C03이 이 C02 본문에 직접 인라인으로 추가한 A 전담 SOURCE::함수→TARGET::함수 작업을 순서대로 이어서 수행한다. 미실측 함수 이름 임의 추측 금지; 명령서 미완료/blocked 항목을 한 줄 재개점으로 넘겨도 다음 독립 안전 아이템 계속.

## 보고

`ORDER_BLOB|ITEM/RF|SOURCE_BLOB|MOVED_FUNCTIONS|NEW_OWNER_PATH/BLOB|SOURCE_BEFORE_AFTER_LOC|KEEP_OK{reason,blob}|NORMAL_TEST_CMD_EXIT|PUSH_REMOTE_SHA|NEXT`를 #11에 한 번. A branch code/test만 정상 커밋/푸시하고 원격 blob 재조회; BLOCKED를 PASS로 만들지 않는다. 통합·DONE/STATUS는 C04/C05.
