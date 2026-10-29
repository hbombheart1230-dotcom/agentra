# C02 — Claude A | 단일 실행 지시: 6개 독립 함수 BODY MOVE

## 시작·격리·공통 구현 계약
- 작업 브랜치 `work/p15-a-reporter-pure-20261021`에서 **code/test만** 수정·정상 push. 이 문서 한 파일만 실행 지시로 읽고 다른 설계/INDEX/큐/정책/핸드오프 문서를 열지 않는다. B/긴급/통합 브랜치 코드·타인 문서 쓰기, 운영 데이터·State·실계좌·실주문·네트워크·실프로세스·배포·frozen/CI 변경 금지. fixture는 순수 dict, fake, tmp_path만.
- Preflight: 시작 시 `CANONICAL_HEAD=origin/integration/p1.5`, `ORDER_FILE_BLOB_SHA=git rev-parse CANONICAL_HEAD:docs/refactor/work_orders/C02_CLAUDE_CURRENT.md`, `OWNER_REMOTE_SHA=origin/work/p15-a-reporter-pure-20261021`를 기록. `ORDER_ID=C02:<ORDER_FILE_BLOB_SHA>:A1..A6`. 실행 중 발행된 후속 지시서는 현재 회차에 소급 적용하지 않는다.
- C03 실측 A 원격 기준 `c9750e60c4343b587b701a8999c71a17908f98db`: 공통 SOURCE `libs/reporting/live_execution_bundle_runner.py` blob `acbe147ef587bfe092fb6a34e61e369c4c03332b`, **wc -l 2726**(끝 newline split 기준 2727). 아래 6개 원함수의 실제 몸체가 존재하고 6개 TARGET은 이 SHA에서 모두 미존재. 원본이 바뀌었으면 먼저 각 함수의 현재 실제 body와 owner 부재를 확인; 이미 적법 MOVE면 ALREADY_MOVED로 기록하고 재구현/재시험하지 않는다.
- 모든 item은 원래 `def`의 body를 새 단일 Owner `def`로 **실제 이동**하고 원래 이름·원서명의 얇은 wrapper만 남긴다. `from libs.reporting import <새모듈> as <alias>`와 기존 `sys.modules[__name__]`를 사용; target에서 facade를 역import하지 않는다. 기존 helper의 use-time monkeypatch/예외/키 순서/alias/한국어 bytes를 보존하고 원본 body 복제 금지. 함수 본문 변경 전 **원격 실제 파일 bytes**에서 각 2~4 fixture의 golden(output/exception/identity)을 기록한다. truncated 도구 출력을 소스 파일로 재구성하지 말고 함수 hunk만 편집한다. 한 item 실패해도 나머지 안전 item 모두 수행.
- item마다 지정한 신규 `tests/` 파일로 `python -m pytest -q -p no:cacheprovider <file>` **normal exit 0 한 번**, pytest 불가면 `python -m unittest discover -s tests -p '<file>' -v`로 동등한 stdlib fixture exit0. 전체 -O/full peer/hosted CI 불필요. 테스트/인증 차단은 별도 TEST_BLOCKED/PUSH_BLOCKED이며 local-only는 원격 완료 아님.

## A1 — 최근 decision_trace 역순 선택
- SOURCE `libs/reporting/live_execution_bundle_runner.py::_latest_decision_trace_payload(rows, *, event, agent)` L788–804 (17행) → TARGET `libs/reporting/live_execution_bundle_runner_decision_trace.py::latest_decision_trace_payload(rows, *, event, agent)`.
- `reversed(rows)`, stage == decision_trace, event strip 일치, payload.agent lower 일치, 첫 역순 payload.payload dict의 shallow `dict(...)` 반환; 없는 경우 {}. 전체 본문 MOVE, facade 원함수 wrapper 유지. 새 Owner는 외부 IO 없음.
- `tests/test_p15_bundle_decision_trace_owner.py`: (1) 빈/미일치→{}, (2) 동일 agent/event 다수에서 마지막 row 우선, (3) agent 대소문자·공백/비dict payload 제외, (4) 반환 shallow copy(최상위는 원본과 다른 객체, nested alias 유지), 입력 불변·old==wrapper==owner. normal pytest 해당 파일 exit0.

## A2 — 의미 있는 중첩 payload 판정
- SOURCE 같은 파일 `::_has_meaningful_payload(payload)` L836–848 (13행) → TARGET `libs/reporting/live_execution_bundle_runner_meaningful_payload.py::has_meaningful_payload(payload, *, facade)`.
- dict가 아니거나 빈 dict면 False, dict/list 중첩의 `({},[],None,"")` 처리 및 short-circuit 순서를 원문 그대로 MOVE. 재귀는 `facade._has_meaningful_payload(value)` 호출 시점 조회(기존 monkeypatch seam), facade wrapper 유지.
- `tests/test_p15_bundle_meaningful_payload_owner.py`: (1) None/[]/{}/{"x":[]}→False, (2) nested dict/list의 비어있음 vs 값 0/False/문자열을 **변경 전 golden 그대로** 비교, (3) 깊은 중첩/리스트에서 조기 True와 순서, (4) facade recursion spy·원래 예외 및 입력 불변. normal pytest exit0.

## A3 — canonical/normalized/fallback 우선순위
- SOURCE `::_prefer_canonical_payload(canonical_sources, agent, fallback, *, fallback_source, normalized_payload=None, normalized_path="")` L849–877 (29행) → TARGET `libs/reporting/live_execution_bundle_runner_canonical_payload.py::prefer_canonical_payload(canonical_sources, agent, fallback, *, fallback_source, normalized_payload=None, normalized_path="", facade)`.
- normalized meaningful 우선 → canonical meaningful → fallback, 각 return의 tuple(payload,source,path), `dict(fallback)` shallow merge/원래 예외와 path strip을 그대로 MOVE. `facade._has_meaningful_payload` use-time; 원래 signature wrapper 유지. A2 이동과 별개 item이며 A2가 BLOCKED면 현재 facade 기존 함수에 의존하도록 유지한다.
- `tests/test_p15_bundle_canonical_payload_owner.py`: (1) normalized/canonical 모두 있을 때 normalized 우선, (2) normalized 비고 canonical 우선, (3) 모두 비었을 때 fallback_source와 canonical_path, (4) malformed artifacts/paths 및 facade spy·nested alias/입력 불변·old==wrapper==owner. normal pytest exit0.

## A4 — run_id 허용 필터
- SOURCE `::_filter_rows_by_run_ids(rows, run_ids)` L1110–1124 (15행) → TARGET `libs/reporting/live_execution_bundle_runner_run_filter.py::filter_rows_by_run_ids(rows, run_ids)`.
- `list(rows or [])`, run_id 공백 제거 집합, allowed 비었을 때 원래 source_rows 반환, 있을 때 row.get("run_id") 매칭 list comprehension 본문 MOVE. 원함수 wrapper 유지, iterable 소모 순서/비dict row 예외를 임의 완화하지 않는다.
- `tests/test_p15_bundle_run_filter_owner.py`: (1) None/빈 allowed면 원본 row 순서·참조 유지, (2) " r1 "/중복/공백과 r2 filtering, (3) generator run_ids 1회 소모·중복 row 유지, (4) 비dict row 기존 예외 parity/입력 불변. normal pytest exit0.

## A5 — target symbol monitor 이벤트 선별
- SOURCE `::_target_symbol_monitor_rows(rows, *, symbol)` L1125–1143 (19행) → TARGET `libs/reporting/live_execution_bundle_runner_monitor_rows.py::target_symbol_monitor_rows(rows, *, symbol, facade)`.
- `normalize_symbol(symbol or "", allow_test_symbols=True)` → 빈 값이면 [], 각 row의 `_event_row_symbol` 일치 및 `_event_row_name(...).startswith("monitor.")` 조건/원본 순서 그대로 MOVE. target은 `facade.normalize_symbol/_event_row_symbol/_event_row_name`을 호출시점 조회. 원래 signature wrapper 유지.
- `tests/test_p15_bundle_monitor_rows_owner.py`: (1) 빈 symbol→[], (2) 005930 monitor.start/monitor.end만 원순서 선별, (3) 다른 symbol·scanner.*·중복 유지 경계, (4) fake normalize/event helper monkeypatch spy 및 old==wrapper==owner·입력 불변. normal pytest exit0.

## A6 — 기존 거래 run ID로 trade_id 읽기 전용 선택
- SOURCE `::_find_existing_trade_id_for_run_ids(*, reports_root, day, symbol, run_ids)` L1208–1236 (29행) → TARGET `libs/reporting/live_execution_bundle_runner_trade_lookup.py::find_existing_trade_id_for_run_ids(*, reports_root, day, symbol, run_ids, facade)`.
- `Path(reports_root)/trades/day` 존재 확인, requested strip set, normalize_symbol, `iter_trade_dirs` 순회, trade_id의 symbol 포함 여부, `_existing_trade_run_ids` 교집합, `_trade_id_sequence` 숫자 정렬과 trade_id tie-break, 빈 경우 "" 반환을 그대로 MOVE. target은 `facade.Path/normalize_symbol/iter_trade_dirs/_existing_trade_run_ids/_trade_id_sequence` use-time. **실운영 reports_root 절대 접근 금지**, tmp_path 안에서만.
- `tests/test_p15_bundle_trade_lookup_owner.py`: (1) 없는 day root/빈 run_ids→"", (2) tmp trades 아래 seq 02/10이 같은 run에 매칭되면 02 우선, (3) symbol 불일치/빈 symbol·중복 run id·동일 seq tie-break, (4) fake iter_trade_dirs 및 facade helper spy, 파일 sha256 전후 불변/old==wrapper==owner. normal pytest exit0.

## 정당 KEEP / 파일 독점
- `_stable_json_text/_payload_fingerprint/_build_component_fingerprint/_has_substantive_entry_evidence`는 이미 외부 Owner 위임 wrapper라 **다시 MOVE 금지**(SOURCE `acbe147e`). `_iter_jsonl/_read_json`은 파일 IO 경계, `_build_run_snapshots`은 다중 이벤트/IO 조합, `_generate_agent_pipeline_trace_report_fast`와 `main`은 보고서 생성·운영 실행 효과 경계라 이번 순수 MOVE에서 KEEP; 실제 실행 금지. KEEP은 신규 CODE_MOVE 0.
- B Commander/Strategist/Operator UI 원본/target과 A의 위 여섯 파일 교집합 0. C04/C05만 통합·수용·상태 변경.

## 종료·원격 검증
- A1~A6 모두 필수 독립 MOVE. 각 `ORDER_ID | ITEM_STATUS=IMPLEMENTED/ALREADY_MOVED/TEST_BLOCKED/PUSH_BLOCKED/SAFETY_BLOCKED/NOT_RUN | SOURCE_BEFORE/AFTER_BLOB+LOC | TARGET_BLOB | MOVED_FUNCTION | NORMAL_CMD/EXIT | FIRST_BLOCKER/NEXT`를 #11에 **한 번** 보고. 자기 branch 정상 commit/push 후 `git ls-remote`와 GitHub 원격 source/target/test blob 확인. 코드/pytest가 막히면 정확 재개점만 남기고 다른 안전 item 계속. C04 최소 통합·targeted normal smoke, C05 G1/G2/G3/DONE 담당.
