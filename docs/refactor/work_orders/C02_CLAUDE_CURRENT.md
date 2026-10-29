# C02 — Claude A | Strategist LLM **reporting-only** BODY MOVE 6건

## 단일 진입 / 안전 / 실행 계약
- **이 C02 한 파일만** 실행 지시로 읽는다. RF 상세·INDEX·T00·D00·HANDOFF·STATUS·큐 문서는 탐색하거나 수정하지 않는다. 코드와 신규 targeted tests만 자기 브랜치 `work/p15-a-reporter-pure-20261021`에서 정상 commit/push. B의 `graphs/nodes/strategist_node.py`, `libs/contracts`, Operator UI, 실제 LLM 호출/주문/브로커/운영 DB·State/실네트워크/frozen oracle/CI는 변경 금지.
- C03 확인 A HEAD=`a9817a4ba7136768ea37b720a4d3d5c073dedb2d`; SOURCE `libs/reporting/strategist_llm_summary.py` blob=`18bba177d241299a32aa6d95a49f712148ffe78d` (1701 lines, integration과 동일). TARGET `libs/reporting/strategist_llm_summary_stage.py`, `libs/reporting/strategist_llm_summary_usage.py`는 A 원격에서 둘 다 404/미존재. 시작 시 `CANONICAL_HEAD`, `ORDER_FILE_BLOB_SHA`, `OWNER_REMOTE_SHA`, `ORDER_ID=C02:<ORDER_FILE_BLOB_SHA>:A1..A6` 고정. 새 HEAD에서는 원함수/target blob을 먼저 재조회; 이미 이동된 item은 ALREADY_MOVED로만 기록.
- 실제 MOVE 정의: SOURCE의 원함수 계산 본문을 삭제하고 새 TARGET의 **유일한** 구현 함수로 이전; SOURCE에는 동일 원명·원서명 얇은 wrapper만 남긴다. `from libs.reporting import strategist_llm_summary_stage as _stage_owner` / `..._usage as _usage_owner` (모듈 단위 또는 함수 내부 import 가능), `facade=sys.modules[__name__]`로 호출시점 helper/상수 조회. 새 TARGET은 SOURCE를 import하지 말고 전달받은 facade를 사용. `sys` import 추가 가능. 기존 원본의 출력 키 순서, 예외, 문자열 bytes, shallow alias, mutable 객체 fresh 생성, 함수 호출 순서 유지. 기존 함수/테스트의 golden을 이동 전에 fake 입력으로 캡처하고 wrapper·owner 직접 호출과 비교.
- TEST는 각 item당 아래 **2~4 targeted fixture**를 `tests/test_p15_strategist_summary_<item>_owner.py`에 작성; `python -m pytest -q -p no:cacheprovider <이번 신규 파일들>` 정상 1회 exit0 (pytest 불가 시 stdlib unittest smoke). full suite, 모든 -O, hosted CI, full peer 강제 금지. 한 item 차단돼도 나머지 독립 item 진행. py_compile, 정상 push, `git ls-remote` 및 GitHub source/target/test blob 일치 확인. 실패는 TEST_BLOCKED와 PUSH_BLOCKED 구분; 로컬 commit은 원격 G1 아님.

## A1 — stage call-kind inference
- SOURCE `libs/reporting/strategist_llm_summary.py::_infer_call_kind(payload,raw,meta=None)` (L58–88, SOURCE blob `18bba177`) → TARGET `libs/reporting/strategist_llm_summary_stage.py::infer_call_kind(payload,raw,meta=None,*,facade)`.
- 본문: raw→sidecar→payload explicit `call_kind` 우선, stage_component 2/3/4 매핑, selected_symbol/hold/carry payload fallback, 빈 문자열. `_as_dict/_text`는 `facade`에서 호출시점 조회.
- TEST: (1) explicit 우선순위 raw/sidecar/payload; (2) stage_component 2/3/4 매핑; (3) selected/hold/carry 및 빈 fallback; (4) facade helper monkeypatch/입력 불변·원래 예외 parity.

## A2 — stage metadata projection
- SOURCE `libs/reporting/strategist_llm_summary.py::_stage_meta(payload,raw,meta=None)` (L89–113) → TARGET `libs/reporting/strategist_llm_summary_stage.py::stage_meta(payload,raw,meta=None,*,facade)`.
- `_STAGE_META_BY_CALL_KIND` 복제 금지; `facade._STAGE_META_BY_CALL_KIND` use-time. `_as_dict/_infer_call_kind/_first_text`도 facade use-time. 원본 `stage_index`의 truthy-or precedence 및 4개 키 순서 유지.
- TEST: (1) stage2/3/4 기본 메타; (2) raw→sidecar→inferred precedence/0·빈값; (3) unknown kind fallback; (4) patched `_infer_call_kind/_first_text` spy·예외/alias parity.

## A3 — response JSON recovery
- SOURCE `libs/reporting/strategist_llm_summary.py::_parse_response_body(raw)` (L114–145) → TARGET `libs/reporting/strategist_llm_summary_stage.py::parse_response_body(raw)`.
- `parsed_output` 우선, `response_text` JSON dict만, `attempts` **역순** 탐색·malformed JSON 무시·dict shallow copy. `json` TARGET에서 직접 import; 원본 `JSONDecodeError` 이외 예외는 그대로.
- TEST: (1) parsed_output 우선/복사 alias; (2) 정상 JSON dict vs list/scalar; (3) attempts 역순·invalid JSON skip; (4) 비정상 입력 예외/입력 불변/키 순서 parity.

## A4 — memory usage surface
- SOURCE `libs/reporting/strategist_llm_summary.py::_memory_usage_from_canonical(canonical)` (L229–265) → TARGET `libs/reporting/strategist_llm_summary_usage.py::memory_usage_from_canonical(canonical,*,facade)`.
- daily/weekly/monthly/symbol layer 순서, empty row skip, operator_summary, visibility 3칸과 `available` 판정 전체 이동. `_as_dict/_as_list/_text/_compact_operator_summary`는 facade use-time.
- TEST: (1) empty/default; (2) 4 layer+visibility·순서/키; (3) missing/non-dict rows/alias; (4) patched helper spy·예외/원본 불변.

## A5 — news usage surface
- SOURCE `libs/reporting/strategist_llm_summary.py::_news_usage_from_canonical(canonical)` (L266–299) → TARGET `libs/reporting/strategist_llm_summary_usage.py::news_usage_from_canonical(canonical,*,facade)`.
- headline 실제 배열 수→context count→sample-map fallback, `headline_count` 시장/후보 분배, query_targets 우선, 3개 sample cap과 confidence fallback 전체 이동. `_as_dict/_as_list/_text/_headline_count_from_sample_map` facade use-time.
- TEST: (1) empty/default; (2) 배열 count가 context보다 우선; (3) context/sample-map/total 분배와 negative·bad numeric 기존 예외; (4) helper monkeypatch·sample cap/alias·키 순서 parity.

## A6 — news quality audit
- SOURCE `libs/reporting/strategist_llm_summary.py::_news_quality_audit(canonical,news_usage)` (L318–369) → TARGET `libs/reporting/strategist_llm_summary_usage.py::news_quality_audit(canonical,news_usage,*,facade)`.
- 7개 issue 판정 순서, total/market/candidate counts, confidence·summary, weak/partial/ok, query_targets[:10]와 `schema_version`/키 순서 보존. `_as_dict/_as_list/_text` facade use-time.
- TEST: (1) empty→weak/issue 순서; (2) full evidence→ok; (3) market-only/candidate-only/low confidence→partial; (4) patched helper·invalid numeric 기존 예외/입력 불변.

## KEEP / 충돌 / 종료
- SOURCE `_read_json`, `_load_canonical_strategist`(파일 IO), `_utc_now_iso`(시각), `build_strategist_llm_summary_payload`(보고서 조립), `render_strategist_llm_summary_markdown`(공개 렌더 진입), `_market_rail_from_canonical`(market rail policy 호출)는 **정당 KEEP**. 기존 `_headline_count_from_sample_map`, `_compact_operator_summary`, `_first_text`, `_as_dict/_as_list/_text`는 이번에는 공용 facade helper KEEP; 복제 금지. 이전 Reporter feedback/AI review 6개 MOVE는 A SHA `a9817a4`에서 완료됐으므로 재배정·재시험 금지. B의 Strategist **node**/Commander/UI와 파일 교집합 0.
- A1..A6 각각 `ORDER_ID | STATUS | SOURCE_BEFORE/AFTER_BLOB+LOC | TARGET_BLOB | NORMAL_CMD/EXIT | PUSH_REMOTE_SHA | FIRST_BLOCKER/NEXT`를 #11 댓글 **한 번** 보고. G1/G2는 원격 source/test+정상 exit로 구분, C04만 integration 최소 통합·G3 smoke, C05만 RF/STATUS/DONE. 실계좌/실주문 금지.
