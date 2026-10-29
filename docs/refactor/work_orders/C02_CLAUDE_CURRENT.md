# C02 — Claude A | RF-035 신규 실제 BODY MOVE 6건 (A1~A6, 2026-10-30 09시 C03 발행)

## 단일 실행 계약
- **이 C02 한 파일만** 진입점으로 읽는다. RF/INDEX/T00/D00/HANDOFF/STATUS/큐 문서를 A가 탐색하거나 수정하지 않는다. 자기 `work/p15-a-reporter-pure-20261021` 브랜치의 아래 지정 code/test만 변경·정상 commit/push. B의 `graphs/nodes/strategist_node.py`, `libs/runtime/strategist/llm/*`, Commander/Operator UI, 운영/실계좌/실주문, Broker/Guard/Step5C/UEF, frozen oracle/CI, 타인 브랜치 변경 금지.
- C03 **실제 원격 측정**: A HEAD `982673cecd12c1eb9bc70b24ca1063fa4b3b14e3`; SOURCE `libs/reporting/strategist_llm_summary.py` Git blob `68b77ae63755613b40096aaf8aa76e523ad2f25f` (파일 `splitlines` 1016개, 끝 newline 포함 `split("\n")` 1017개). integration의 동일 SOURCE blob 확인. 아래 신규 TARGET 5개는 A HEAD에서 **모두 404**. SOURCE 함수/호출 위치와 의존성을 C03이 직접 분석했음. RF-035의 Reporter 파일 독점 Owner=Claude A; Codex B와 원본/목표 파일 교집합 0.
- **이전 A1~A6는 재배정 아님**: #11 `6510742871`의 A19 원격 `982673ce`에서 `_memory_usage_lines/_news_usage_lines` 및 clean 변형, `_strategy_score_lines_clean/_rejected_strategy_lines` 6개가 이미 MOVE 완료. 원본 1121→1016 LOC, 정상 targeted 61 PASS exit0는 **A 보고**. KEEP/기존 MOVE를 새 구조 성과로 중복 계상하지 않는다.
- 시작 시 `CANONICAL_HEAD | ORDER_FILE_BLOB_SHA | OWNER_REMOTE_SHA | ORDER_ID=C02:<ORDER_FILE_BLOB_SHA>:A1..A6` 고정. HEAD가 전진했으면 해당 함수가 이미 thin wrapper인지, TARGET이 존재하는지 먼저 확인하고 `ALREADY_MOVED`면 재이동/재시험 금지. 한 item 실패 시 나머지 독립 안전 item 계속. 새 C02 발행이 진행 중 주문을 소급 무효화하지 않는다.

## 공통 실제 MOVE/patch·검증
- 아래 **원본 def의 실제 본문을 제거**하고 TARGET의 유일 Owner 함수로 옮긴 뒤 SOURCE의 **원명·원서명 얇은 wrapper**만 남긴다. SOURCE에는 `sys`가 이미 import돼 있다. `from libs.reporting import <target module> as _..._owner`를 추가하고 `facade=sys.modules[__name__]`를 호출 시점 전달한다. TARGET은 SOURCE를 역import하지 않는다. 기존 facade monkeypatch·출력 문자열 UTF-8 bytes·한글·공백·키/줄 순서·alias·예외·입력 불변을 보존. `facade._text/_as_dict/_as_list/_quality_audit_lines/_watch_scope_label_clean/_playbook_flow_label/_bullet_lines/_monitor_adjustment_lines/_json_inline` 등 기존 module helper는 **호출 시점** 조회하며 대상별 실제 참조만 사용한다.
- 동일 TARGET(A3/A4)을 A 혼자 순차 변경한다. 함수 경계 bounded-hunk patch만 허용; 잘린 도구 출력/인코딩 손상 삽입 금지. 이동 전 골든 출력·예외를 저장해 이동 후 SOURCE wrapper와 TARGET(facade 명시) 비교, monkeypatch 전달 확인. 각 item 2~4 targeted fixture를 아래 개별 새 test에 구현한다. `python -m py_compile`로 변경 code/test 검사, 정상 `python -m pytest -q -p no:cacheprovider <6개 신규 테스트 경로>` **한 번 exit0** (pytest 불가 시 재현 가능한 stdlib smoke exit0). -O/full peer/전체 suite/매 RF hosted CI 강제 금지.
- 본인 브랜치 commit/push 후 `git ls-remote`와 원격 SOURCE/TARGET/TEST blob 재조회. Git 인증 실패는 `PUSH_BLOCKED`(로컬 commit은 G1 아님)로 분리하고 다른 item 계속. 코드 변경 없이 KEEP 재검증만 하면 MOVE 성과 0.

## A1 — Stage-specific clean Markdown renderer (101 원본 행)
- SOURCE `libs/reporting/strategist_llm_summary.py::_render_stage_specific_summary_markdown_clean(payload: Dict[str, Any]) -> str` L741–839 (실제 본문 99행+경계), blob `68b77ae6` → TARGET **신규** `libs/reporting/strategist_llm_summary_stage_markdown.py::render_stage_specific_summary_markdown_clean(payload, *, facade)`.
- `meta/readout/stage_decision/detail/watch` 추출, monitor_instruction/entry_policy_delta/commander_actionability의 **정렬 키**와 `_json_inline` 직렬화, `runner_up_order/priority_exit_triggers` 및 한글 heading·빈 fallback·`"\n".join(lines)` 전체를 **변경 없이 MOVE**. SOURCE의 `render_strategist_llm_summary_markdown` 두 번째(실제 공개) 정의가 호출하는 기존 `_render_stage_specific_summary_markdown_clean` wrapper 유지. TARGET의 helper 참조는 `facade._as_dict/_as_list/_text/_json_inline/_playbook_flow_label/_watch_scope_label_clean/_quality_audit_lines/_bullet_lines`로 use-time; 새 Owner가 다른 A2~A6 wrapper를 거쳐도 같은 호출시점 의미를 유지.
- TEST `tests/test_p15_summary_stage_markdown_clean_owner.py`: (1) stage2/3/4 populated payload·정확 UTF-8 Markdown 골든; (2) missing/empty nested 값·`- -` fallback; (3) monitor/entry/commander 키 정렬·한국어/JSON escape; (4) facade helper monkeypatch spy·wrapper/owner parity·입력 불변.

## A2 — Directive Markdown line (18 원본 행)
- SOURCE `libs/reporting/strategist_llm_summary.py::_directive_line(label: str, value: Dict[str, Any]) -> str` L452–467 → TARGET **신규** `libs/reporting/strategist_llm_summary_directive_line.py::directive_line(label, value, *, facade)`.
- action/target/target_fields/target_axes/reason의 **원래 None vs empty fallback 우선순위**와 `**{action}** -> ...; reason` 포맷을 정확 MOVE. `facade._text`를 호출 시점 조회. 기존 공개 renderer의 모든 `_directive_line` 호출은 SOURCE wrapper 경유.
- TEST `tests/test_p15_summary_directive_line_owner.py`: (1) empty value; (2) target list+reason, target_fields/axes fallback; (3) action-only/reason-only/None·Unicode; (4) patched `_text` 및 exception/output byte parity.

## A3 — Clean watch-scope label (15 원본 행)
- SOURCE `libs/reporting/strategist_llm_summary.py::_watch_scope_label_clean(value: Dict[str, Any]) -> str` L317–329 → TARGET **신규** `libs/reporting/strategist_llm_summary_watch_status.py::watch_scope_label_clean(value, *, facade)`.
- max_priority_rank/max_runner_ups/cascade_enabled의 `None`·빈 문자열 제외, `False`는 `cascade 비활성`으로 포함, `" / "` 연결을 원문 MOVE. `facade` 인자는 호환 통일용(사용하지 않아도 수용). 원본 non-clean `_watch_scope_label`은 별도 기존 함수로 KEEP, 합치지 않는다.
- TEST `tests/test_p15_summary_watch_scope_clean_owner.py`: (1) empty; (2) rank+runner-up+True; (3) False/0/None/empty 경계; (4) wrapper/owner UTF-8 parity·입력 불변.

## A4 — Clean strategy-patch status (18 원본 행)
- SOURCE `libs/reporting/strategist_llm_summary.py::_strategy_patch_status_clean(detail: Dict[str, Any]) -> str` L332–347 → TARGET `libs/reporting/strategist_llm_summary_watch_status.py::strategy_patch_status_clean(detail, *, facade)`.
- 필수 키 **9개 고정 순서**(pre_llm_playbook, llm_requested_playbook, requested_playbook, requested_playbook_source, final_playbook, tactical_strategy, strategy_scores, rejected_strategy_reasons, candidate_watch_policy), `detail.get` truthiness, `적용됨` 또는 `일부 누락 (...)` 문구 그대로 MOVE. non-clean `_strategy_patch_status`는 KEEP.
- TEST `tests/test_p15_summary_patch_status_clean_owner.py`: (1) 9키 populated; (2) all absent 순서; (3) zero/empty/list/dict truthiness; (4) malformed input 예외 타입 및 wrapper/owner bytes parity.

## A5 — Playbook flow label (12 원본 행)
- SOURCE `libs/reporting/strategist_llm_summary.py::_playbook_flow_label(detail: Dict[str, Any]) -> str` L280–289 → TARGET **신규** `libs/reporting/strategist_llm_summary_playbook_flow.py::playbook_flow_label(detail, *, facade)`.
- pre_llm/requested/final의 빈값 제거·` -> ` 순서·`(source=...)` 접미사·없으면 `-` 유지. `facade._text` use-time. 두 renderer의 기존 wrapper 경로 보존.
- TEST `tests/test_p15_summary_playbook_flow_owner.py`: (1) empty all; (2) three steps+source; (3) partial/malformed/Unicode; (4) `_text` spy·예외/byte parity.

## A6 — Operator compact projection (12 원본 행)
- SOURCE `libs/reporting/strategist_llm_summary.py::_compact_operator_summary(value: Dict[str, Any]) -> Dict[str, Any]` L150–159 → TARGET **신규** `libs/reporting/strategist_llm_summary_operator_projection.py::compact_operator_summary(value, *, facade)`.
- `available=bool(...)`, `status/artifact_path`의 `facade._text(...,"")`, trade_count/closed_trade_count/win_rate/avg_return_pct의 원값과 **7개 키 삽입 순서**를 그대로 MOVE. `build_strategist_llm_summary_payload` 및 기존 usage-owner가 SOURCE `_compact_operator_summary`를 호출하는 patch seam 보존.
- TEST `tests/test_p15_summary_compact_operator_owner.py`: (1) complete dict+key order; (2) empty/None fields·false/zero; (3) non-string/Unicode·alias/입력 불변; (4) patched `_text` 호출시점·예외 parity.

## 정당 KEEP·보고
- `render_strategist_llm_summary_markdown` **두 정의**는 첫 번째가 shadowed legacy, 두 번째가 실제 public renderer: **KEEP_PUBLIC/SHADOWED**, 이번 이동·삭제·함수 병합 금지. `_render_stage_specific_summary_markdown`(non-clean)은 첫 번째 shadowed renderer에서만 참조하므로 **KEEP_SHADOWED**, 신규 MOVE 실적으로 세지 않는다. `build_strategist_llm_summary_payload/generate_strategist_llm_summary`는 파일/집계 효과 경계 **KEEP_EFFECT**. `_read_json/_load_canonical_strategist/_utc_now_iso`는 IO/clock **KEEP_EFFECT**. `_market_rail_from_canonical`은 policy 경계 **KEEP_POLICY**. `_as_dict/_as_list/_text/_json_inline/_bullet_lines` 등 공용 helper는 facade patch seam으로 KEEP. 이 판단은 **A HEAD source blob `68b77ae6`** 기준이며 KEEP은 신규 CODE_MOVE 0.
- #11에 **신규 결과 한 번만**: `ORDER_ID | A1..A6 STATUS | SOURCE_BEFORE/AFTER_LOC+BLOB | TARGET_BLOBS | NORMAL_CMD/EXIT | PUSH_REMOTE_SHA | FIRST_BLOCKER/NEXT`. 구조 변경과 KEEP/기준점 이전 분리는 별도. C04 최소 통합·정확 SHA targeted smoke, C05 G1/G2/G3·DONE 판정에 넘기고 A는 문서/RF/STATUS를 수정하지 않는다.
