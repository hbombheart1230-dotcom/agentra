# C01 — Codex B | 신규 실제 BODY MOVE 6건 (B1~B6, 2026-10-30 08시 C03 발행)

## 단일 진입·고정·금지
- **이 C01 한 파일만** 실행 명령으로 읽는다. RF 상세·INDEX·T00·D00·HANDOFF·STATUS·큐 문서 탐색/수정 금지. 자기 `work/p15-b-operator-structure-20261022` 브랜치의 지정 code/test만 정상 commit/push. A reporting, 실계좌/주문, Broker/Guard/Step5C/UEF, 운영 DB/State, 실네트워크, frozen oracle/CI, 타인 브랜치 변경 금지.
- C03 확인 B HEAD **`4e50fec226809af388268539ff9bc2e1cfda078d`**. `graphs/nodes/strategist_node.py` SOURCE blob **`a6e75945f2d084ebd80166ac8a68bdc1b7655f8f`** (3554 LOC), `libs/runtime/strategist/llm/adjustment_directives.py` blob **`148a531f206bb9cec6fdde90bea1b7a1fea4a361`** (311 LOC). 신규 TARGET 4개는 B 원격에서 모두 404 확인. B HEAD가 달라지면 item별 source 함수 본문/target blob 재확인 후 이미 MOVE면 `ALREADY_MOVED`만 기록.
- 이전 B5/B6/B7/B8: repair messages B5 `ddf5e58c`, UI report index B6 + Commander advisory B7/B8 `4e50fec2` **원격 완료**. #12 B6~B8은 정상 targeted **3 PASS (B 보고)**. 이 네 개 및 과거 B1~B4 재이동·재시험·신규 실적 계상 금지. B 최신 `agent_outputs.py`와 `data_access_core.py`는 현재 C03 GitHub 텍스트 조회가 인코딩 오류/비텍스트 응답이므로 **이번 신규 SOURCE로 사용하지 않는다**; 이를 소스 손상 확정이나 통합 PASS로 추정하지 않는다. C04는 B 이전 완료 파일을 통합 전 실제 bytes·compile·targeted smoke로 별도 검증.
- 시작 `CANONICAL_HEAD | ORDER_FILE_BLOB_SHA | OWNER_REMOTE_SHA | ORDER_ID=C01:<ORDER_FILE_BLOB_SHA>:B1,B2,B3,B4,B5,B6` 고정. 한 item 막혀도 다른 독립 안전 item 계속. 작업 중 새 C01 발행은 시작 주문을 소급 실패 처리하지 않는다.

## 공통 MOVE/테스트/푸시
- 각 SOURCE 실제 계산/문자열 본문을 삭제하고 지정 TARGET에 **유일 Owner**로 이동; 기존 SOURCE 원명·원서명 **thin wrapper**만 유지. B1~B4는 `graphs/nodes/strategist_node.py`에서 새 모듈을 import한 뒤 원서명으로 delegate; B5/B6는 `adjustment_directives.py`의 `*_r3_impl` 원서명을 유지해 새 모듈로 delegate. B5/B6 target은 facade를 역import하지 않고 원래 전달받은 `facade` 그대로 전달. monkeypatch/use-time helper, 문자열 bytes, dict/list alias, 예외/정렬/순서 보존. 기존 source와 새 target의 **중복 계산 본문 금지**.
- B1~B3 같은 `stage_prompt_contracts.py`, B4 별도 `stage_call_kind.py`, B5/B6 각각 별도 target. 모두 **B 단독 소유**. `def` 범위 bounded-hunk patch, 잘린 도구 출력 소스에 삽입 금지. golden fixture 전후 parity·입력 불변·thin wrapper 확인. 각 item 아래 2~4 targeted fixture를 새 test에 추가. 정상 `python -m pytest -q -p no:cacheprovider <6개 새 테스트 경로>` 1회 exit0 또는 pytest 부재 시 stdlib unittest smoke exit0; `python -m py_compile`. full suite/매번 -O/full peer/hosted CI 강제 금지. 본인 정상 push 후 `git ls-remote`·원격 SOURCE/TARGET/TEST blob 재확인; Git 인증 실패는 `PUSH_BLOCKED`로 분리하고 나머지 안전 item 계속.

## B1 — Stage role boundary text (19 원본 행)
- SOURCE `graphs/nodes/strategist_node.py::_stage_specific_role_boundary(call_kind: str) -> str` L609–627, blob `a6e75945` → TARGET **신규** `libs/runtime/strategist/llm/stage_prompt_contracts.py::stage_specific_role_boundary(call_kind)`.
- selected-symbol/stale-hold/EOD-carry/default의 **정확 영어 문자열 bytes**, order/gate 권한 금지 문구와 branch precedence를 몸체 그대로 MOVE. no LLM call.
- TEST `tests/test_p15_stage_role_boundary_owner.py`: (1) selected_symbol; (2) stale hold; (3) EOD carry; (4) unknown/empty default + wrapper/owner exact string parity.

## B2 — Stage task requirement text (22 원본 행)
- SOURCE `graphs/nodes/strategist_node.py::_stage_specific_task_requirement(call_kind: str) -> str` L628–649 → TARGET `libs/runtime/strategist/llm/stage_prompt_contracts.py::stage_specific_task_requirement(call_kind)`.
- 4개 call kind별 필수 출력 필드·Stage3 horizon 제한·Stage4 flatten/carry 문구, 공백/쉼표/끝 공백까지 원문 유지. B1과 병합하지 않는다.
- TEST `tests/test_p15_stage_task_requirement_owner.py`: (1) Stage2 fields; (2) Stage3 same-session; (3) Stage4 carry; (4) default playbook + old/new exact bytes.

## B3 — Stage user requirement text (28 원본 행)
- SOURCE `graphs/nodes/strategist_node.py::_stage_specific_user_requirement(call_kind: str) -> str` L650–677 → TARGET `libs/runtime/strategist/llm/stage_prompt_contracts.py::stage_specific_user_requirement(call_kind)`.
- Stage2 **no direct BUY/SELL**, Stage3 no SELL/overnight, Stage4 hard closeout/Guard, default explicit adjustment directive 문자열 정확 보존. 정책을 바꾸거나 약화하지 않는다.
- TEST `tests/test_p15_stage_user_requirement_owner.py`: (1) Stage2 no BUY/SELL; (2) Stage3 no SELL; (3) Stage4 no bypass; (4) default exact bytes/old-new parity.

## B4 — Resolve strategist call kind (42 원본 행)
- SOURCE `graphs/nodes/strategist_node.py::_resolve_strategist_llm_call_kind(payload: Dict[str, Any]) -> str` L1485–1526 → TARGET **신규** `libs/runtime/strategist/llm/stage_call_kind.py::resolve_strategist_llm_call_kind(payload)`.
- commander_refresh_context.requested true일 때 **closeout/EOD/overnight → hold/position/carry_state → selected_symbol** 우선순위, false일 때 explicit `resolved_call_kind` 우선, 허용 4종만 통과, 나머지 market_strategy_frame fallback. 입력 mutate 금지.
- TEST `tests/test_p15_stage_call_kind_owner.py`: (1) closeout vs hold precedence; (2) hold/carry_state; (3) selected requested; (4) explicit/invalid/None payload·wrapper/owner parity.

## B5 — Infer policy adjustment direction (36 원본 행)
- SOURCE `libs/runtime/strategist/llm/adjustment_directives.py::_infer_policy_adjustment_direction_r3_impl(baseline_summary,current_summary,*,facade)` L11–46, blob `148a531f` → TARGET **신규** `libs/runtime/strategist/llm/adjustment_directives_infer_policy_adjustment_direction_r3.py::_infer_policy_adjustment_direction_r3_impl(baseline_summary,current_summary,*,facade)`.
- higher-is-tighter 4개, lower-is-tighter 3개, min_extended_from_vwap_pct 특례의 `float(value or 0.0)` 비교·`tighten/relax/mixed/none` 판정 전체 MOVE. facade 인자는 그대로 수용(미사용도 시그니처 보존), dict 아닌 입력→빈 맵, 숫자 변환 예외 parity.
- TEST `tests/test_p15_adjustment_direction_owner.py`: (1) tighten/relax; (2) mixed/none; (3) min_extended special/zero; (4) malformed numeric ValueError·wrapper/owner parity.

## B6 — Rejected tactical strategy reasons (32 원본 행)
- SOURCE `libs/runtime/strategist/llm/adjustment_directives.py::_normalize_rejected_strategy_reasons_r3_impl(raw,*,tactical_strategy,strategy_scores,facade)` L271–302 → TARGET **신규** `libs/runtime/strategist/llm/adjustment_directives_normalize_rejected_strategy_reasons_.py::_normalize_rejected_strategy_reasons_r3_impl(raw,*,tactical_strategy,strategy_scores,facade)` (RF-018 설계의 정확 target 명칭).
- canonical tactic key + allowed `facade._TACTICAL_STRATEGIES`·selected 제외·최대 6개 직접 reason, 없으면 `facade._unit_score` 내림차순 top4 fallback, score<=selected vs clamp 이유 token 전체 MOVE. TARGET에서 `Dict` 타입을 import하거나 future annotations 선언, `facade.canonical_tactic_key/_clean_directive_reason/_unit_score` **use-time** 호출.
- TEST `tests/test_p15_adjustment_rejected_reasons_owner.py`: (1) direct canonical reasons 6 cap; (2) selected/unknown/empty reason skip; (3) score fallback tie/top4/boundary; (4) patched facade helpers·malformed inputs/old-new exception parity.

## KEEP·종료·인계
- `_build_strategist_llm_messages`는 대형 메시지 조립 경계지만 **이번 범위 외 KEEP/DEFER**; `_run_strategist_frame_llm`(LLM/ledger), `strategist_node(state)`(Graph/State), `_load_recent_strategy_feedback`(IO), Broker/Guard/UEF, stage contract builder(기존 Owner) **KEEP_EFFECT/SAFETY_HOLD**. 기존 `_stage_specific_llm_contract`는 별도 기존 contract delegation KEEP. 이번 6개는 순수 문구/정규화만 이동; order/Guard 정책/실행 변경 없음.
- #12 댓글 **한 번**: `ORDER_ID | B1..B6 STATUS | SOURCE_BEFORE/AFTER_BLOB+LOC | TARGET_BLOBS | NORMAL_CMD/EXIT | PUSH_REMOTE_SHA | FIRST_BLOCKER/NEXT`. C04 최소 통합/targeted smoke → C05 G1/G2/G3·DONE. B는 문서·STATUS·이슈 본문·타인 코드를 수정하지 않는다.
