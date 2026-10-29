# C01 — Codex B | 미완료 실제 BODY MOVE 5건 (B4/B5/B6/B7/B8)

## 단일 진입·preflight·권한
- **이 C01 한 파일만** 실행 지시로 읽는다. RF 상세·INDEX·T00·D00·HANDOFF·STATUS·큐 문서 탐색/수정 금지. 자기 `work/p15-b-operator-structure-20261022` 브랜치의 지정 code/test만 정상 commit/push. A reporter 코드, 타인 브랜치, 실계좌·실주문·Broker/Guard/UEF·운영 DB/State·실네트워크·frozen oracle/CI 변경 금지.
- C03 확인 B HEAD `6e21dbd710a78a68a23184c3a4909e9b8eed301b`. B1/B2 `_commander_shadow_monitor_gate_details` / `_commander_shadow_context_delta_summary`는 이미 `commander_shadow_evidence.py`로 원격 이동, 정상 targeted 2 PASS exit0(B 보고); B3 `_stage_specific_llm_contract`도 `stage_contracts.py`로 이동 완료. **B1/B2/B3 재이동·재시험·신규 실적 계상 금지.** 이번 미완료 B4/B5/B6와 신규 B7/B8만 실행.
- 시작 시 `CANONICAL_HEAD=integration/p1.5`, `ORDER_FILE_BLOB_SHA`, `OWNER_REMOTE_SHA`, `ORDER_ID=C01:<ORDER_FILE_BLOB_SHA>:B4,B5,B6,B7,B8` 고정. HEAD 전진 시 원함수/target blob을 확인해 이미 MOVE된 item은 ALREADY_MOVED로만 기록. C03 실측 B `graphs/nodes/strategist_node.py` blob `62dbcb0114b1e67525978dc1f0a3d38ea9dc3414`, B `apps/operator_ui/data_access_core.py` blob `0666538f5f6ddd74e3ca8a3fa290c95f044fbdb6`, B `libs/contracts/agent_outputs.py` blob `93e8e866c64c94793c433077bbc31bc51f9a8bbd`.
- 공통 MOVE: **원함수 계산 본문 삭제→target 단일 Owner 실제 이전→원명/원서명 thin wrapper**. 필요한 helper는 `facade=sys.modules[__name__]`로 전달해 호출시점 monkeypatch/키 순서/예외/문자열 bytes/shallow alias/IO 순서 보존. target에서 facade 역import 금지. 이동 전 fake fixture golden 확보, 이동 후 wrapper와 owner 직접 호출 비교. `python -m pytest -q -p no:cacheprovider tests/<new_test>.py` 또는 stdlib unittest 정상 exit0 1회. full peer/-O/전체 CI 강제 금지. 한 item 차단돼도 다른 독립 item 계속. py_compile, 본인 정상 push, `git ls-remote`와 원격 source/target/test blob 확인; 로컬 commit은 G1 아님.
- B4/B5/B6는 기존 서로 다른 source/target; B7/B8은 같은 `agent_outputs.py`의 서로 다른 함수로 동일 신규 target 파일을 B 한 명만 순차 수정. A source와 경로 교집합 0. `… tokens truncated …` 등의 잘린 도구 출력을 소스에 복사하지 말고 bounded-hunk patch 후 py_compile.

## B4 — Strategist token budget
- SOURCE `graphs/nodes/strategist_node.py::_apply_strategist_llm_token_budget(compact, *, memory_usage_disabled)` (B 현재 blob `62dbcb0114b1e67525978dc1f0a3d38ea9dc3414`, L1553–1652, 약 100행) → TARGET `libs/runtime/strategist/context/token_budget.py::apply_frame_token_budget(compact, *, memory_usage_disabled, facade)` (미존재).
- theme_strength dedup, call_kind early return, news/themes/refresh/feedback/memory slicing 본문 이동. `_resolve_strategist_llm_call_kind/_theme_packet_summary_for_llm/_compact_theme_strength_for_llm/_compact_monitor_entry_policy_baseline_for_llm/_slim_refresh_context_for_llm` facade use-time. shallow alias 유지, 임의 deep copy 금지.
- TEST `tests/test_p15_strategist_token_budget_owner.py`: (1) market_strategy_frame early return, (2) selected_symbol news/themes/component_symbols cap, (3) memory disabled·feedback cap, (4) patched helper spy·nested alias/예외 parity. LLM·State effect 실행 금지.

## B5 — Strategist repair message formatting
- SOURCE `graphs/nodes/strategist_node.py::_build_strategist_llm_repair_messages(payload,raw_response)` (같은 B blob, L2018–2129, 약 112행) → TARGET `libs/runtime/strategist/llm/repair_messages.py::build_repair_messages(payload,raw_response, *, facade)` (미존재).
- base/stage contract, parse failure reason, compact input, system/user 두 메시지의 문자열 생성 본문만 이동. `_build_compact_strategist_llm_payload/_resolve_strategist_llm_call_kind/_stage_specific_llm_contract/_classify_llm_parse_failure/json.dumps` facade use-time; `ensure_ascii=False` 및 원래 문자열 bytes/예외 유지. LLMRouter/retry/ledger 호출 금지.
- TEST `tests/test_p15_strategist_repair_messages_owner.py`: (1) malformed raw+한글, (2) selected_symbol kind, (3) empty raw/None, (4) patched facade parse/json spy와 예외 parity.

## B6 — Operator UI read-only trade report index
- SOURCE `apps/operator_ui/data_access_core.py::_trade_report_index(config)` (B blob `0666538f5f6ddd74e3ca8a3fa290c95f044fbdb6`, L616–767, 약 152행) → TARGET `apps/operator_ui/data_access_report_index.py::trade_report_index(config, *, facade)` (미존재).
- 날짜별 roots/dirs 순회, bundle mtime 정렬, lifecycle/AI/brief/provenance/health 읽기, `_project_trade_identity/_project_trade_summary/_project_trade_record/_project_trade_indexes`, by_run_id/by_story_id index 본문을 이동. facade wrapper와 `_trade_report_meta_for_run/_story` 경로 유지; `_read_json/_trade_paths_from_bundle/_existing_trade_path/_project_*/normalize_symbol/_to_epoch`는 use-time facade. 운영 파일 쓰기/실제 보고서 생성 금지.
- TEST `tests/test_p15_ui_trade_report_index_owner.py` (tmp fake root): (1) empty reports→빈 index, (2) mtime·중복 bundle 우선순위, (3) run/story ID 및 malformed JSON, (4) patched `_project_trade_record` spy·키 순서·파일 SHA 불변.

## B7 — Commander shadow no-trade advisory reason
- SOURCE `libs/contracts/agent_outputs.py::_commander_shadow_no_trade_reason_code(state,*,observations,actual_runtime,path)` (B blob `93e8e866`, L950–1025, 약 76행) → TARGET **신규** `libs/contracts/agent_output_parts/commander_shadow_advice.py::no_trade_reason_code(state,*,observations,actual_runtime,path,facade)` (B 원격 404).
- 순수 **shadow advisory** 분류 본문 전부 이동: BUY/SELL→NONE, open position, risk, execution allowed=false, missing data, LLM unstable, repeated/unchanged context, confidence <0.55, wait/low signal 순서·정확 reason tokens 보존. `_dict/_clip/_safe_int`는 facade use-time; 실제 주문·Guard/portfolio 정책 실행 금지. 기존 `_commander_shadow_no_trade_reason_code`는 thin wrapper, 호출자/원시그니처 불변.
- TEST `tests/test_p15_commander_shadow_no_trade_advice_owner.py`: (1) BUY/SELL 우선순위와 empty→DATA_INSUFFICIENT; (2) POSITION_ALREADY_OPEN/RISK_BLOCKED/EXECUTION_BLOCKED 우선순위; (3) missing data/LLM error/repeated/market unchanged/0.5499 vs 0.55; (4) patched `_clip/_safe_int` spy·malformed input 기존 예외/입력 불변·wrapper/owner parity.

## B8 — Commander shadow strategist recommendation
- SOURCE `libs/contracts/agent_outputs.py::_commander_shadow_strategist_recommendation(*,no_trade_reason_code,observations)` (동일 B blob, L1026–1053, 약 28행) → TARGET **동일 신규 파일** `libs/contracts/agent_output_parts/commander_shadow_advice.py::strategist_recommendation(*,no_trade_reason_code,observations)`.
- 기존 SKIP 9종 reason, LLM_UNSTABLE일 때 partial/salvaged/repaired→RETRY_COMPACT, fallback→USE_FALLBACK, error→RETRY_MINIMAL, 그 외 RUN의 **정확한 문자열/분기**만 이동. 원명 thin wrapper, 신규 target에서 source import 금지.
- TEST `tests/test_p15_commander_shadow_strategist_advice_owner.py`: (1) SKIP 9종; (2) LLM_UNSTABLE 상태 5종; (3) unknown/empty→RUN; (4) observations non-dict 기존 예외/입력 불변/old-new key-independent string parity.

## KEEP·종료
- B1/B2/B3는 이미 완료; 기존 `commander_shadow_runtime.py`와 `commander_shadow_evidence.py` 재구현 금지. `build_commander_shadow_artifact`는 shadow report orchestration KEEP; `_commander_shadow_llm_call_advice/_commander_shadow_suggested_action/_commander_shadow_next_action_recommendation`는 이번 범위 밖, 동작 유지. `_run_strategist_frame_llm`(LLM/ledger effect), `strategist_node(state)`(Graph/State effect), UI report writer, Broker/Guard/UEF는 **정당 KEEP/SAFETY_HOLD**. B Strategist source와 integration blob은 다르므로 B4/B5의 함수 hunk만 이동, integration 전체 파일로 덮어쓰기 금지.
- B4/B5/B6/B7/B8 각각 `ORDER_ID | ITEM_STATUS(IMPLEMENTED/ALREADY_MOVED/TEST_BLOCKED/PUSH_BLOCKED/SAFETY_BLOCKED/NOT_RUN) | SOURCE_BEFORE/AFTER_BLOB+LOC | TARGET_BLOB | NORMAL_CMD/EXIT | PUSH_REMOTE_SHA | FIRST_BLOCKER/NEXT`를 #12 댓글 **한 번** 보고. 정상 targeted test exit0와 원격 code/test push를 구별. C04 최소 통합/G3, C05 RF/STATUS/DONE 독점. 문서·이슈 본문/타인 코드 변경 금지.
