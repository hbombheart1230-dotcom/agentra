# C02 — Claude A | Reporter 순수 함수 실제 BODY MOVE 6건

## 단일 진입·preflight·권한
- 이 **C02 한 파일만** 실행 지시로 읽는다. RF 상세/INDEX/T00/D00/STATUS/HANDOFF/큐 탐색·수정 금지. 본인 `work/p15-a-reporter-pure-20261021`의 아래 code/test만 정상 commit/push. 다른 Actor 코드·문서·운영 reports/DB/State/실계좌·주문·Broker/Guard/UEF·실네트워크/CI/frozen oracle 변경 금지. 모든 테스트는 fake/memory/tmp.
- 시작 때 원격 `CANONICAL_HEAD=integration/p1.5`, `ORDER_FILE_BLOB_SHA=git rev-parse <CANONICAL_HEAD>:docs/refactor/work_orders/C02_CLAUDE_CURRENT.md`, `OWNER_REMOTE_SHA=git ls-remote origin refs/heads/work/p15-a-reporter-pure-20261021` 기록. 번호별 `ORDER_ID=C02:<ORDER_FILE_BLOB_SHA>:A1..A6` 고정. 실행 도중 C02가 갱신되어도 시작한 지시 버전을 소급 실패 처리하지 않는다.
- C03 실측 A HEAD `5b145b149f3ac315a57cb7bd21f93cc75d287c12`. SOURCE 1 `libs/reporting/reporter_feedback.py` Git blob `452a23133db9fae99eb42cc21b2dbe1d29c94593`, 463 LOC(wc; split 464). SOURCE 2 `libs/reporting/reporter_ai_review.py` blob `f10f9419f79406f2e46775b99c3009a7e8e25305`, 314 LOC(wc; split 315). `reporter_ai_review_result.py` 기존 Owner blob `39bc26aa0641e3eeffc336f6ffebdef300e80f16`. A HEAD 전진 시 원함수와 target 재조회, 이미 본문 이동된 항목은 `ALREADY_MOVED`로만 기록하고 재이동하지 않는다.
- 목표 파일 `libs/reporting/reporter_feedback_analysis.py`, `libs/reporting/reporter_feedback_summary.py`는 A 원격 **미존재**. A1~A3는 첫 파일에, A4~A5는 두 번째 파일에 **각각 독립 함수**로 단일 Owner 이동. A6는 기존 `reporter_ai_review_result.py`에 함수 추가(기존 normalization 두 함수 변경 금지). A/B 수정 파일 교집합 0.
- 공통 MOVE: **원본 계산 본문 제거→target 함수로 실제 이동→원명/원서명 thin wrapper**. 기존 caller `build_strategist_feedback_packet`·`build_ai_reporter_review` 호출·key order·문자열 bytes·원본 예외·shallow alias 보존. 원본에서 `facade=sys.modules[__name__]`를 넘기고 target은 facade를 역import하지 않으며 helper `_safe_total/_safe_int/_ratio/_clip_str/_normalize_llm_status/required_key_metadata`를 호출시점 `facade`에서 조회하여 monkeypatch 보존. 기존 함수의 golden 결과/예외를 이동 전 fake fixture로 저장 후 wrapper와 owner 직접 호출 비교. 정상 `python -m pytest -q -p no:cacheprovider tests/<item-test>.py` 1회 exit0(없으면 stdlib unittest); full suite/-O/full peer/매-RF CI 강제 금지. 한 항목 TEST/PUSH 차단 시 다른 안전 항목 계속, 원격 push 후 source/target/test blob 확인.

## A1 — Reporter analysis recommendations 우선순위
- SOURCE `libs/reporting/reporter_feedback.py::_extract_reporter_analysis_recommendations(payload)` (blob `452a2313`, L207–216, 10행) → TARGET `libs/reporting/reporter_feedback_analysis.py::extract_reporter_analysis_recommendations(payload)`.
- direct `improvement_suggestions`가 있으면 우선, 아니면 `operator_facing_summary.recommended_actions`, strip·빈 문자열 제외·앞 4개 cap의 **실제 본문** 이동. facade wrapper 유지, 반환 list 순서/기존 비정상 타입 예외 보존.
- TEST `tests/test_p15_feedback_analysis_recommendations_owner.py`: (1) empty→[], (2) direct가 operator보다 우선, (3) 공백·빈값·5개 이상 cap, (4) malformed list/Mapping의 원래 예외 및 입력 불변·old/new/wrapper parity.

## A2 — Blocker ranking
- SOURCE `libs/reporting/reporter_feedback.py::_build_blocker_analysis(blocker_totals)` (같은 blob, L227–241, 15행) → TARGET `libs/reporting/reporter_feedback_analysis.py::build_blocker_analysis(blocker_totals, *, facade)`.
- `_safe_total` 분모, `_safe_int` 변환, `(-count,name)` 정렬, 상위 5개 `blocker/count/ratio` 키 순서 본문 이동. helper facade use-time.
- TEST `tests/test_p15_feedback_blocker_ranking_owner.py`: (1) empty/zero denominator, (2) 동률 이름 정렬, (3) 6개 이상 top5·문자 숫자, (4) patched `_safe_total/_safe_int/_ratio` spy·예외·입력 불변.

## A3 — Route analysis ratios
- SOURCE `libs/reporting/reporter_feedback.py::_build_route_analysis(route_summary)` (같은 blob, L242–258, 17행) → TARGET `libs/reporting/reporter_feedback_analysis.py::build_route_analysis(route_summary, *, facade)`.
- route_selected_total shallow dict, source/run_count/breakdown, monitor_only/cached_strategist/full_cycle 비율과 정확 키 삽입 순서 본문 이동. `_safe_total/_safe_int/_ratio` facade use-time.
- TEST `tests/test_p15_feedback_route_analysis_owner.py`: (1) empty/default, (2) 3-route 정상 비율, (3) zero/None/문자 숫자·nested alias, (4) patched helper spy·잘못된 입력 예외·키 순서 parity.

## A4 — Insight narrative projection
- SOURCE `libs/reporting/reporter_feedback.py::_build_insight_summary(*,route_analysis,blocker_analysis,trade_report_summary=None)` (같은 blob, L268–323, 56행) → TARGET `libs/reporting/reporter_feedback_summary.py::build_insight_summary(*,route_analysis,blocker_analysis,trade_report_summary=None,facade)`.
- route leader/tie·monitor/cached 비율, top blocker, closed-trade win/loss/flat/unknown·avg PnL 문장 연결, no-evidence fallback **영어 원문 문자열 전체** 이동. helper facade use-time. 새 문자열/정책 문구 작성 금지.
- TEST `tests/test_p15_feedback_insight_summary_owner.py`: (1) 모든 입력 비어 fallback 문장, (2) route tie/leader와 top blocker 정확 bytes, (3) closed-trade flat/unknown/avg sample 유무, (4) malformed 타입 예외·helper spy·입력 alias/불변·old/new 문자열 sha256 parity.

## A5 — Confidence level
- SOURCE `libs/reporting/reporter_feedback.py::_build_confidence(*,route_analysis,blocker_analysis,trade_report_summary=None)` (같은 blob, L324–349, 26행) → TARGET `libs/reporting/reporter_feedback_summary.py::build_confidence(*,route_analysis,blocker_analysis,trade_report_summary=None,facade)`.
- route>=50+3 blockers/high, route>=10/medium, closed>=3+broker>=2/high, closed>=1+broker>=1/medium, blocker>=20+2/high, blocker>=5+1/medium, else low의 **기존 순서** 본문 이동. 임계값/우선순위 변경 금지.
- TEST `tests/test_p15_feedback_confidence_owner.py`: (1) zero→low, (2) route 9/10/49/50와 blocker 개수, (3) broker truth/closed trade 1·2·3 경계, (4) blocker 4/5/19/20 및 helper spy·예외·old/new parity.

## A6 — AI review default result construction
- SOURCE `libs/reporting/reporter_ai_review.py::_default_result(*,enabled,status,reason="",model="")` (blob `f10f9419`, L87–106, 20행) → TARGET **기존** `libs/reporting/reporter_ai_review_result.py::default_result(*,enabled,status,reason="",model="",facade)` (현재 Owner blob `39bc26aa`).
- `required_key_metadata({},REPORTER_AI_REVIEW_REQUIRED_KEYS)`, enabled/status/llm_status/model/reason/parse_mode와 빈 AI fields, `ai_evidence_links`의 nested 리스트/딕트 **삽입 순서와 fresh 객체 생성**을 그대로 이동. 원명 wrapper `facade=sys.modules[__name__]`; target은 `facade.required_key_metadata/facade.REPORTER_AI_REVIEW_REQUIRED_KEYS/facade._normalize_llm_status/facade._clip_str` 호출시점 조회. 기존 `normalize_result/normalize_evidence_link_items` 본문/호출자 변경 금지.
- TEST `tests/test_p15_ai_review_default_owner.py`: (1) enabled=False·fallback 기본 결과 전체 키/순서, (2) enabled=True/status ok/model/reason 320 cap, (3) facade required-key/status/clip spy와 기존 예외, (4) 두 번 호출 시 nested 객체 독립·원본 golden JSON bytes·caller wrapper/owner parity.

## KEEP·종료·인계
- `reporter_feedback.py::build_strategist_feedback_packet`는 IO·source precedence·packet assembly·`stable_evidence_id`의 공개 orchestration 경계이므로 KEEP. `_read_json/_load_or_generate_metrics_payload/_build_trade_report_feedback_summary`는 파일/보고서 effect 경계 KEEP. `_safe_int/_safe_total/_ratio`는 공유 facade helper로 KEEP(이번에 별도 복제 금지). `reporter_ai_review.py::build_ai_reporter_review`는 LLM/ledger effect 경계 KEEP. 이미 A 원격에서 MOVE 완료한 feedback 6함수와 AI review input/result 4함수는 재배정/재시험 금지. 위 6건은 미이동 실제 본문이므로 단순 KEEP 대체 금지.
- 6건 각각 `ORDER_ID | ITEM_STATUS(IMPLEMENTED/ALREADY_MOVED/TEST_BLOCKED/PUSH_BLOCKED/SAFETY_BLOCKED/NOT_RUN) | SOURCE_BEFORE/AFTER_BLOB+LOC | TARGET_PATH/BLOB | NORMAL_CMD/EXIT | PUSH_REMOTE_SHA | FIRST_BLOCKER/NEXT`를 #11에 **한 번** 보고. 원격 source/target/test blob 재조회. 이 작업은 기존 RF DONE의 자동 취소/재종결이 아니라 남은 `TARGET_GAP` 실제 개선이다. C04가 정확 SHA 최소 통합·targeted smoke, C05가 G1/G2/G3·STATUS/DONE 권한을 보유한다. A는 문서·RF/STATUS/타인 코드 쓰기 금지.
