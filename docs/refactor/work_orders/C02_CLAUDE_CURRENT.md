# C02 — Claude A | 신규 BODY MOVE 8건 A1~A8 · RF-035 Strategist summary reporting
> 2026-10-30 10:40 KST 지팀장 신규 주문. **이전 C02 A20 6건은 09:35 C04 통합·09:46 C05 인수 완료. 10:13 A21은 동일 주문 ALREADY_MOVED로 개발 0.** 과거 A1~A6 재이동·재시험·신규 실적 계상 금지.

## 단일 진입·Owner·전제
- 원격 `integration/p1.5`의 **이 C02 한 파일만** 먼저 읽는다. RF/INDEX/T00/D00/HANDOFF/STATUS/큐 탐색·수정 금지. 기존 `work/p15-a-reporter-pure-20261021` 브랜치의 지정 code/test만 commit/push. B Commander/Strategist/Operator, 실주문·Broker/Guard/Step5C/UEF, 운영/실네트워크/DB/State, frozen oracle/CI/타인 브랜치 수정 금지.
- C03 원격 실측: A `libs/reporting/strategist_llm_summary.py` Git blob **`10331f3a640d34a6043711637367c33c96555b10`**, **869 실라인(~870 splitlines 표시)**. 신규 TARGET 아래 **5개 모두 A 원격 404**. RF-035 summary 파일 독점 owner **Claude A**; B와 원본/목표 경로 교집합 0. A HEAD 전진시 item별 SOURCE body/target blob 재확인, 이미 옮겼다면 `ALREADY_MOVED` (중복 실적·재시험 금지).
- 시작 `CANONICAL_HEAD | ORDER_FILE_BLOB_SHA | OWNER_REMOTE_SHA | ORDER_ID=C02:<ORDER_FILE_BLOB_SHA>:A1..A8` 고정, dirty/원격 blob/Python/pytest/승인 push 점검. 8건 **전부 필수**; 첫 PASS/로컬 커밋/짧은 작업시간으로 종료 금지. 한 item BLOCKED면 나머지 독립 7건 계속. 새 문서가 발행돼도 시작 주문을 소급 무효 처리하지 않는다. 신규 작업 선택권은 C03에게만 있다.

## 공통 BODY MOVE/검증
- SOURCE 실제 함수 몸체를 신규 TARGET 한 곳의 유일 Owner로 **이전하고 삭제**한 뒤 SOURCE의 원명·원서명 thin wrapper만 유지. 원본 `sys` import 존재. TARGET→SOURCE 역import 금지; 동적 helper 참조는 `facade=sys.modules[__name__]`로 호출시점 위임. 원본 UTF-8/Korean/문구/공백, 예외, 리스트·dict alias, None·빈 문자열, 키 정렬·삽입 순서, monkeypatch·callers 보존. A1/A2는 `facade` 불필요(시그니처에서 생략 가능), 나머지는 `facade` 명시 전달. 같은 TARGET 함수들은 A 혼자 순차 적용.
- A1→`libs/reporting/strategist_llm_summary_path_projection.py`; A2→`strategist_llm_summary_sample_counts.py`; A3/A4→`strategist_llm_summary_first_values.py`; A5/A6→`strategist_llm_summary_legacy_watch_status.py`; A7/A8→`strategist_llm_summary_legacy_scores.py` (각 파일 `libs/reporting/` 아래).
- SOURCE 함수 경계 bounded-hunk patch만, 잘린 도구 출력/인코딩 손상 삽입 금지. 이동 전 golden fixture와 이동 후 wrapper/Owner 직접 호출에 대해 각 item 2~4 targeted fixture: 값·UTF-8 bytes·예외·입력 불변·facade helper monkeypatch. code/test `python -m py_compile`, `python -m pytest -q -p no:cacheprovider <아래 신규 테스트 8파일>` normal exit0 1회 또는 pytest 없는 경우 재현 가능한 stdlib smoke exit0. -O/full peer/full suite/hosted CI 의무 아님. 정상 commit/승인 push 후 원격 SOURCE/TARGET/TEST blob 재조회; push 인증 차단만 `PUSH_BLOCKED`, 코드/test 다른 안전 item 계속.

## 신규 A1~A8 · 동일 SOURCE `libs/reporting/strategist_llm_summary.py`
| ID | SOURCE 원함수·원본 라인 | TARGET 함수(신규 상기 모듈) | 이동할 로직 및 회귀 fixture | 신규 TEST |
|---|---|---|---|---|
| **A1** | `_canonical_strategist_path_for_response(source_path: Path) -> Path \| None` L84–100 | `path_projection.py::canonical_strategist_path_for_response(source_path)` | response.json 확인, llm/day/run·category 별 중첩 fallback, 최종 canonical strategist.json 경로; 두 경로/이름 mismatch/Path parity; 파일 존재 검사 추가 금지 | `tests/test_p15_summary_canonical_path_owner.py` |
| **A2** | `_headline_count_from_sample_map(value: Any) -> int` L136–149 | `sample_counts.py::headline_count_from_sample_map(value)` | dict values의 dict row count int(value or 0) 합, 잘못된 항목/예외 skip, 음수·문자열·None·입력불변 | `tests/test_p15_summary_headline_count_owner.py` |
| **A3** | `_first_text(default: str, *values: Any) -> str` L213–220 | `first_values.py::first_text(default,*values,facade)` | `facade._text(value, "")`를 왼쪽부터 호출·첫 truthy 반환, 전부 빈 경우 default, helper monkeypatch 호출 순서·예외 | `tests/test_p15_summary_first_text_owner.py` |
| **A4** | `_first_dict(*values: Any) -> Dict[str, Any]` L225–232 | `first_values.py::first_dict(*values,facade)` | `facade._as_dict` 첫 nonempty map·원본 dict alias, all empty {}, invalid/patch exception parity | `tests/test_p15_summary_first_dict_owner.py` |
| **A5** | `_watch_scope_label(value: Dict[str,Any]) -> str` L244–258 | `legacy_watch_status.py::watch_scope_label(value,*,facade)` | rank/runner-ups/True-False/0/None, ` / ` join 및 Korean `cascade 활성/비활성` 정확 bytes; 기존 `*_clean` 별도 Owner 유지 | `tests/test_p15_summary_legacy_watch_owner.py` |
| **A6** | `_strategy_patch_status(detail: Dict[str,Any]) -> str` L259–276 | `legacy_watch_status.py::strategy_patch_status(detail,*,facade)` | 9 required keys tuple 순서, truthiness/누락·`적용됨`/`일부 누락 (...)` 원문, malformed input 기존 예외; `*_clean` KEEP | `tests/test_p15_summary_legacy_patch_owner.py` |
| **A7** | `_score_label(value:Any)->str` L288–294 | `legacy_scores.py::score_label(value,*,facade)` | `facade._score_value` 후 `{numeric:.2f}.rstrip`, invalid/-inf는 `facade._text`; 0/negative/tie/patch·출력 bytes | `tests/test_p15_summary_legacy_score_label_owner.py` |
| **A8** | `_strategy_score_lines(scores:Dict[str,Any],*,selected:str)->List[str]` L295–305 | `legacy_scores.py::strategy_score_lines(scores,*,selected,facade)` | `facade._score_value/_score_label` 호출시점, score/이름 내림차순, ` (선택)`, 빈 `["- -"]`, Unicode/동률/alias·exception parity; `*_clean` KEEP | `tests/test_p15_summary_legacy_score_lines_owner.py` |

## KEEP·보고
- `render_strategist_llm_summary_markdown` 두 정의(첫 shadowed, 둘째 public), `_render_stage_specific_summary_markdown` shadowed, `build_strategist_llm_summary_payload/generate_strategist_llm_summary` IO/effect, `_market_rail_from_canonical` policy, `_load_canonical_strategist/_read_json` IO **KEEP**, 이동 성과 0. 기존 clean Owners·usage/readout/decision 등 수정 금지; source facade의 다른 helper는 patch seam으로 유지.
- **#11 신규 결과 댓글 1회:** `ORDER_ID | A1..A8 STATUS | SOURCE_BEFORE/AFTER_BLOB+LOC | TARGET_BLOBS | NORMAL_CMD/EXIT | PUSH_REMOTE_SHA | FIRST_BLOCKER/NEXT | START_KST/END_KST/ELAPSED_MIN`. C04 통합·C05 G1/G2/G3/DONE은 각 담당만 수행한다.
