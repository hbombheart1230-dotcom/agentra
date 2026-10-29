# C02 — Claude A | 신규 실제 BODY MOVE 6건 (A1~A6, 2026-10-30 08시 C03 발행)

## 단일 진입·고정·금지
- **이 C02 한 파일만** 실행 명령으로 읽는다. RF 세부설계·INDEX·T00·D00·STATUS·HANDOFF·큐 문서 탐색/수정 금지. `work/p15-a-reporter-pure-20261021` 자신의 **지정 code/test**만 수정·commit·정상 push. B의 strategist node/Commander/Operator UI, 운영 DB/State, real 주문/계좌, Broker/Guard/Step5C/UEF, 실네트워크, frozen oracle/CI 변경 금지.
- C03 실측 A 원격 HEAD `40c92523bb8bd4511d0d6bdabc1aa80bf15c6987`. SOURCE `libs/reporting/strategist_llm_summary.py` blob **`2c1e24e098655f589317152659a487024b59061e`**, **1121 LOC (wc)**. 신규 TARGET `libs/reporting/strategist_llm_summary_usage_lines.py` 및 `libs/reporting/strategist_llm_summary_strategy_lines.py`는 A HEAD에서 모두 404. integration 동일 SOURCE blob 확인. 다른 HEAD면 먼저 각 함수의 실제 몸체와 목표 blob을 비교해 이미 MOVE된 item은 `ALREADY_MOVED`만 기록하고 재이동하지 않는다.
- 이전 A1~A6 (output quality audit, stage decision, operator readout 2종, strategy detail, quality audit lines)는 A `40c92523`에서 **모두 원격 MOVE 완료**, 원본 1516→1121 LOC, 정상 targeted **67 PASS exit0 (A #11 보고)**. 이 여섯 개는 **새 배정이 아니며 재시험/재실적 금지**.
- 시작에 `CANONICAL_HEAD | ORDER_FILE_BLOB_SHA | OWNER_REMOTE_SHA | ORDER_ID=C02:<ORDER_FILE_BLOB_SHA>:A1,A2,A3,A4,A5,A6` 고정. 한 item 차단돼도 나머지 독립 item 계속. 작업 중 새 C02가 발행돼도 이미 시작한 주문을 소급 실패 처리하지 않는다.

## 공통 정확 구현·호환
- 각 원함수의 **실제 계산 본문 제거** → 지정 신규 TARGET의 단일 Owner 함수에 본문 이동 → 기존 SOURCE 원함수는 **원명/원서명 thin wrapper**만 남긴다. SOURCE의 기존 `sys` import와 `sys.modules[__name__]`를 사용해 `facade=` 전달; TARGET은 SOURCE를 역import하지 않는다. 기존 호출자/monkeypatch는 호출 시점 `facade._as_dict/_as_list/_text/_score_value/_score_label/_json_inline` 참조로 보존. 원래 문자열 bytes·한글·줄 순서·키 순서·예외·입력 불변·fresh list를 유지한다.
- **서로 다른 live 함수의 clean/non-clean 표현을 합치지 않는다.** 같은 TARGET에 여러 함수를 추가할 때 A 한 명이 순차 수정. `def` 경계 bounded-hunk patch, 도구 출력의 `… tokens truncated …` 삽입 금지. 이동 전 golden 입력/출력/예외 캡처 → 이동 후 wrapper/owner parity + use-time facade patch 확인.
- 각 item 아래 2~4 fixture를 **별도 `tests/test_p15_summary_<item>_owner.py`**로 추가한다. 정상 `python -m pytest -q -p no:cacheprovider <6개 새 테스트 경로>` **1회 exit0**, pytest 미설치면 재현 가능한 stdlib unittest smoke exit0. `python -m py_compile`로 변경 code/test 검사. full suite, 모든 `-O`, full peer, hosted CI 강제 금지. 본인 브랜치 commit/push 후 `git ls-remote`와 원격 source/target/test blob 확인; 로컬 commit만 있으면 `PUSH_BLOCKED`이지 G1 아님.

## A1 — memory usage markdown (36 원본 행)
- SOURCE `libs/reporting/strategist_llm_summary.py::_memory_usage_lines(memory: Dict[str, Any]) -> List[str]` L487–522, blob `2c1e24e` → TARGET **신규** `libs/reporting/strategist_llm_summary_usage_lines.py::memory_usage_lines(memory, *, facade)`.
- `available` false 기본 한 줄, active_layers/priority_order/human_summary, applied_to_strategy playbook/risk/scanner/monitor, daily/weekly/monthly/symbol의 operator_summary trade_count/win_rate/avg_return_pct·effect/status 포맷과 순서를 본문 그대로 이동. `facade._as_list/_as_dict/_text` 호출시점 사용.
- TEST `tests/test_p15_summary_memory_lines_owner.py`: (1) unavailable exact fallback; (2) four layers+metrics+applied full lines; (3) missing/non-dict layers·zero metrics·한글; (4) facade helper spy, 원본/Owner 예외·bytes·입력 불변.

## A2 — news usage markdown (16 원본 행)
- SOURCE `libs/reporting/strategist_llm_summary.py::_news_usage_lines(news: Dict[str, Any]) -> List[str]` L523–538 → TARGET `libs/reporting/strategist_llm_summary_usage_lines.py::news_usage_lines(news, *, facade)`.
- unavailable 기본, query_targets **앞 10개**, 검색/수집 **타깃** 문구, 8개 요약/효과/헤드라인/reasoning 줄 원문 보존. `facade._as_list/_text` use-time.
- TEST `tests/test_p15_summary_news_lines_owner.py`: (1) unavailable; (2) 11 targets→10 cap·한글; (3) None/0/empty headline·문자열; (4) patched facade + wrapper/owner parity.

## A3 — clean memory usage markdown (36 원본 행)
- SOURCE `libs/reporting/strategist_llm_summary.py::_memory_usage_lines_clean(memory: Dict[str, Any]) -> List[str]` L790–825 → TARGET `libs/reporting/strategist_llm_summary_usage_lines.py::memory_usage_lines_clean(memory, *, facade)`.
- A1과 별개 실제 호출 경로의 clean 함수 몸체만 이동, 동일 출력처럼 보이는 경우도 **호출자/함수 별도 유지**. active layer, metrics, fallback, 4-layer order, `facade._as_list/_as_dict/_text` use-time.
- TEST `tests/test_p15_summary_memory_clean_owner.py`: (1) unavailable; (2) all layers+metrics; (3) malformed nested/zero; (4) patched helper·A1과 각각 golden parity/입력 불변.

## A4 — clean news usage markdown (16 원본 행)
- SOURCE `libs/reporting/strategist_llm_summary.py::_news_usage_lines_clean(news: Dict[str, Any]) -> List[str]` L826–841 → TARGET `libs/reporting/strategist_llm_summary_usage_lines.py::news_usage_lines_clean(news, *, facade)`.
- A2의 **“검색/수집 타깃”**과 달리 clean의 **“검색/수집 대상”** 문구 정확 보존. query cap 10, headline counts, empty fallback, `facade._as_list/_text` use-time.
- TEST `tests/test_p15_summary_news_clean_owner.py`: (1) unavailable; (2) 11 targets cap; (3) clean/normal label 차이; (4) helper spy·wrapper/owner exact bytes.

## A5 — clean strategy score lines (11 원본 행)
- SOURCE `libs/reporting/strategist_llm_summary.py::_strategy_score_lines_clean(scores: Dict[str, Any], *, selected: str) -> List[str]` L348–358 → TARGET **신규** `libs/reporting/strategist_llm_summary_strategy_lines.py::strategy_score_lines_clean(scores, *, selected, facade)`.
- 빈 scores `["- -"]`, `(_score_value(score), str(name))` 내림차순(동률 포함), selected `" (선택)"` 접미사, `facade._score_value/_score_label` use-time. 기존 `_strategy_score_lines`(non-clean)는 KEEP/이번 이동 금지.
- TEST `tests/test_p15_summary_strategy_score_clean_owner.py`: (1) empty; (2) tie·selected marker·정렬; (3) invalid/None/-inf score; (4) patched score helpers·wrapper/owner parity.

## A6 — rejected strategy lines (16 원본 행)
- SOURCE `libs/reporting/strategist_llm_summary.py::_rejected_strategy_lines(reasons: Dict[str, Any], *, selected: str) -> List[str]` L359–374 → TARGET `libs/reporting/strategist_llm_summary_strategy_lines.py::rejected_strategy_lines(reasons, *, selected, facade)`.
- 이름 정렬, selected 제외, dict/list `facade._json_inline`(ensure_ascii=False/sort_keys) vs scalar `facade._text`, 남은 행 0개 `["- -"]`을 보존.
- TEST `tests/test_p15_summary_rejected_lines_owner.py`: (1) empty/selected-only; (2) sorted keys·selected filter; (3) nested dict/list/한글·malformed; (4) patched json/text helper, wrapper/owner bytes·예외 parity.

## KEEP·보고·인계
- `build_strategist_llm_summary_payload`(IO/aggregation), `generate_strategist_llm_summary`(IO), `render_strategist_llm_summary_markdown`(두 정의: 첫 정의 shadowed, 두 번째 public entry), `_read_json/_load_canonical_strategist/_utc_now_iso`(effect/clock), `_market_rail_from_canonical`(policy boundary)은 **정당 KEEP_EFFECT**, 수정 금지. 공용 `_as_dict/_as_list/_text/_score_value/_score_label/_json_inline` helper도 facade seam으로 KEEP. 신규 구조 MOVE 6개만 계산; 이전 MOVE/KEEP/테스트-only는 신규 실적 0.
- #11 댓글 **한 번**: `ORDER_ID | A1..A6 STATUS | SOURCE_BEFORE/AFTER_BLOB+LOC | TARGET_BLOBS | NORMAL_CMD/EXIT | PUSH_REMOTE_SHA | FIRST_BLOCKER/NEXT`. C04 최소 통합/targeted smoke → C05 G1/G2/G3·DONE; A는 문서·STATUS·이슈 본문을 수정하지 않는다.
