# C02 — Claude A | Strategist summary reporting-only BODY MOVE 6건 (A1~A6)

## 단일 진입·소유권·사전 고정
- 이 **C02 한 파일만** 실행 명령으로 읽는다. D00/RF 상세/INDEX/T00/STATUS/HANDOFF/큐 탐색·수정 금지. Claude A의 `work/p15-a-reporter-pure-20261021`에서 **지정한 code/test만** 수정·정상 commit/push. B의 `graphs/nodes/strategist_node.py`, `libs/contracts/agent_outputs.py`, Operator UI 및 실거래/주문·Broker/Guard/Step5C/UEF/운영 DB·State/실네트워크/frozen CI는 절대 수정하지 않는다.
- C03 실측 A HEAD `4c12726f209ece7b6c5942d4dee26aacb5f3bf45`. SOURCE `libs/reporting/strategist_llm_summary.py` **blob `50157713007d4dcae8d39086b5267be1d14f51d7`**, **1516 LOC(wc 기준)**. integration 현재 동일 SOURCE blob. 새 TARGET 4개는 A HEAD에서 404 확인: `libs/reporting/strategist_llm_summary_decision.py`, `strategist_llm_summary_readout.py`, `strategist_llm_summary_strategy.py`, `strategist_llm_summary_quality_lines.py`.
- 이전 A1~A6 (`_infer_call_kind/_stage_meta/_parse_response_body/_memory_usage_from_canonical/_news_usage_from_canonical/_news_quality_audit`)는 **이미 원격 MOVE 완료**: A SHA `4c12726f`, SOURCE 1700→1516 LOC, TARGET `strategist_llm_summary_stage.py`/`_usage.py`; 정상 targeted 85 PASS exit0(A #11 보고). 재이동/재시험/이번 신규 성과 계상 금지.
- 시작 시 `CANONICAL_HEAD`, `ORDER_FILE_BLOB_SHA`, `OWNER_REMOTE_SHA`, `ORDER_ID=C02:<ORDER_FILE_BLOB_SHA>:A1,A2,A3,A4,A5,A6`를 고정. 다른 커밋으로 원본/target이 이미 이동했으면 해당 item `ALREADY_MOVED`만 기록하고 다음 안전 item으로 진행.
- 공통: 원함수 **계산 본문 삭제→TARGET 유일 Owner 실제 MOVE→원명·원서명 thin wrapper**. 기존 facade에 `sys` import 존재, `facade=sys.modules[__name__]`를 새 Owner에 전달; 새 Owner는 source 모듈을 역import하지 않는다. 모든 `_as_dict/_as_list/_text/_first_text/_first_dict/_directive/_stage_meta/_memory_usage_from_canonical` 참조는 **facade에서 호출 시점** 조회(원본 monkeypatch 보존). 기존 문자열 원문·한글·키 순서·예외·mutable fresh object·alias·호출 순서 유지. 원본/Owner/래퍼를 동일 fake 입력으로 golden 비교, 실제 LLM/파일 IO/운영 효과 금지.
- 함수별 아래 **2~4 targeted fixture**를 `tests/test_p15_strategist_summary_<item>_owner.py`에 작성. 각 새 테스트는 wrapper-thin, golden parity, facade helper patch 도달을 포함. 정상 `python -m pytest -q -p no:cacheprovider <6개 신규 테스트 경로>` **1회 exit0**(pytest 불가 시 stdlib unittest smoke exit0); full peer/-O/full-suite/매 RF hosted CI 강제 금지. 한 item 막혀도 나머지 계속. `python -m py_compile`, 자기 브랜치 commit/push, `git ls-remote`와 원격 SOURCE/TARGET/TEST blob 재확인. 로컬 commit은 G1 아님.

## A1 — output quality audit (62 source lines)
- SOURCE `libs/reporting/strategist_llm_summary.py::_strategist_output_quality_audit(*,payload,canonical,stage_decision,strategy_detail,market_rail,news_quality)` L186–247, blob `50157713` → TARGET `libs/reporting/strategist_llm_summary_decision.py::strategist_output_quality_audit(*,payload,canonical,stage_decision,strategy_detail,market_rail,news_quality,facade)` (신규).
- 본문 전체: candidate_watch, memory_usage, stage-specific/market-frame 분기, 8종 issue, `ok/watch/needs_review` 경계, `strategist_output_quality_audit.v1` dict. `facade._as_dict/_memory_usage_from_canonical/_text/_as_list` use-time. `_memory_usage_from_canonical`는 이전 stage/usage Owner wrapper 호출 그대로.
- TEST `tests/test_p15_strategist_summary_output_quality_owner.py`: (1) 모든 증거→ok/키 순서, (2) stage-specific control missing vs market-frame missing, (3) issue 2/3 경계·memory disabled/empty layers·news not ok, (4) patched memory helper·한글/예외/입력 불변 및 wrapper/Owner parity.

## A2 — stage decision projection (62 source lines)
- SOURCE `libs/reporting/strategist_llm_summary.py::_stage_decision_from_payload(payload,raw,meta=None)` L248–309 → TARGET `libs/reporting/strategist_llm_summary_decision.py::stage_decision_from_payload(payload,raw,meta=None,*,facade)`.
- `facade._stage_meta/_text/_as_dict/_as_list/_first_text/_first_dict` use-time; market-frame이면 정확 `{"is_stage_specific": False}`, stage2/3/4 selected/hold/carry, truthy-or `stage_index`, confidence None/0, `raw_payload_keys` sorted 등 순서/예외 보존.
- TEST `tests/test_p15_strategist_summary_stage_decision_owner.py`: (1) market frame early return, (2) stage2 selected_symbol·priority, (3) stage3/4 fallback·malformed index·confidence=0, (4) patched `_stage_meta/_first_dict` spy·입력 불변·기존 예외/키 순서 parity.

## A3 — operator readout (79 source lines)
- SOURCE `libs/reporting/strategist_llm_summary.py::_operator_readout(payload,stage_decision=None)` L310–388 → TARGET `libs/reporting/strategist_llm_summary_readout.py::operator_readout(payload,stage_decision=None,*,facade)`.
- stage-specific 영어 문장과 일반 market-frame 한글 문장 **bytes 그대로**, selected_themes·rationale best/worst·selected_symbol_bias none, good_points/issues/actions/validation 4개 cap 전체 MOVE. `facade._as_dict/_as_list/_text/_directive` use-time.
- TEST `tests/test_p15_strategist_summary_operator_readout_owner.py`: (1) stage-specific reason 유무·영어 원문, (2) empty themes·default actions, (3) best/worst·none bias·cap/순서, (4) facade `_directive` spy·예외/입력 불변·래퍼/Owner parity.

## A4 — operator readout clean (76 source lines)
- SOURCE `libs/reporting/strategist_llm_summary.py::_operator_readout_clean(payload,stage_decision=None)` L397–472 → TARGET `libs/reporting/strategist_llm_summary_readout.py::operator_readout_clean(payload,stage_decision=None,*,facade)`.
- **A3과 구현/문구 합치지 말 것**: clean의 한국어 stage-specific 문구, `"best 諛?worst"` 레거시 문자열, fallback·theme/entry/refresh 순서가 A3과 다르므로 원문 그대로 이동. `facade._as_dict/_as_list/_text/_directive` use-time.
- TEST `tests/test_p15_strategist_summary_operator_readout_clean_owner.py`: (1) stage-specific reason 없음/있음 한국어, (2) themes 없음·policy directive, (3) best/worst/legacy 문자열·none bias·4 cap, (4) helper patch·old/new 문자열 bytes/예외/입력 불변 parity.

## A5 — strategy detail precedence (78 source lines)
- SOURCE `libs/reporting/strategist_llm_summary.py::_strategy_detail_from_sources(payload,canonical)` L481–558 → TARGET `libs/reporting/strategist_llm_summary_strategy.py::strategy_detail_from_sources(payload,canonical,*,facade)`.
- canonical_detail → canonical → strategy_policy.market_policy/scanner_policy → payload의 **필드별 순서**, `_first_text`와 `_first_dict` 우선순위, `final_playbook` fallback, 10개 키 순서 전체 이동. `facade._as_dict/_first_text/_first_dict` use-time.
- TEST `tests/test_p15_strategist_summary_strategy_detail_owner.py`: (1) full canonical 우선, (2) market/scanner fallback, (3) empty/None/0·중첩 dict alias, (4) patched `_first_text/_first_dict` spy·예외·키 순서/입력 불변 parity.

## A6 — quality audit markdown lines (78 source lines)
- SOURCE `libs/reporting/strategist_llm_summary.py::_quality_audit_lines(payload)` L1163–1240 → TARGET `libs/reporting/strategist_llm_summary_quality_lines.py::quality_audit_lines(payload,*,facade)`.
- Market Regime Rail / News Quality / Risk-Off Exceptions / News Event Intelligence / Strategist Output Quality의 heading, blank line, **문자열·순서·불리언 출력** 그대로. 원함수 내부 `_issue_text`, `_watch_text`는 TARGET 함수 내부 nested helper로 함께 MOVE(전역으로 공개하지 않음); `facade._as_dict/_as_list/_text` use-time.
- TEST `tests/test_p15_strategist_summary_quality_lines_owner.py`: (1) empty payload exact lines, (2) 5개 섹션 full evidence·한글·키 순서, (3) watchlist 6개 cap·non-dict rows·malformed inputs, (4) facade helpers patch/예외·입력 불변·wrapper/Owner parity.

## KEEP / 충돌 / 종료
- `_read_json/_load_canonical_strategist`(IO), `_utc_now_iso`(clock), `build_strategist_llm_summary_payload`(orchestration), `generate_strategist_llm_summary`(IO), `render_strategist_llm_summary_markdown`(public render entry)는 **KEEP_EFFECT**. `_market_rail_from_canonical`은 policy 호출 경계 KEEP. `_as_dict/_as_list/_text/_first_text/_first_dict/_directive`는 공용 facade helper KEEP; 이번 6개 MOVE에 포함하지 않는다. `render_strategist_llm_summary_markdown` 이름이 파일에서 두 번 정의됨(L860/L1342): 앞 정의는 shadowed, **둘 다 변경 금지**, 중복 재배정 금지. A와 B의 SOURCE/TARGET 경로 교집합 0.
- A1..A6 각각 `ORDER_ID | STATUS(IMPLEMENTED/ALREADY_MOVED/TEST_BLOCKED/PUSH_BLOCKED/SAFETY_BLOCKED/NOT_RUN) | SOURCE_BEFORE/AFTER_BLOB+LOC | TARGET_BLOB | NORMAL_CMD/EXIT | PUSH_REMOTE_SHA | FIRST_BLOCKER/NEXT`를 #11 댓글 한 번 보고. C04 최소 integration/targeted smoke→C05 G1/G2/G3·DONE 독점. KEEP/기준점 이전 MOVE/테스트-only를 신규 구조 개선 실적으로 세지 않는다.
