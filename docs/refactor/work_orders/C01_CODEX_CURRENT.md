# C01 — Codex B | 원격 실측 미완료 함수 BODY MOVE 5건

## 단일 진입·고정 preflight
- 이 **C01 한 파일만** 실행 지시로 읽고, 아래 명시된 code/test 외 RF/INDEX/T00/D00/HANDOFF/STATUS/큐 문서 탐색·수정 금지. 자기 브랜치 `work/p15-b-operator-structure-20261022`에서만 정상 commit/push. A/긴급/통합 브랜치 코드 쓰기, 실계좌·실주문·Broker/Guard/UEF·운영 State/DB·실네트워크·frozen oracle/CI 수정 금지.
- 시작 시 원격 `CANONICAL_HEAD=integration/p1.5`, `ORDER_FILE_BLOB_SHA=git rev-parse <CANONICAL_HEAD>:docs/refactor/work_orders/C01_CODEX_CURRENT.md`, `OWNER_REMOTE_SHA=git ls-remote origin refs/heads/work/p15-b-operator-structure-20261022` 고정. `ORDER_ID=C01:<ORDER_FILE_BLOB_SHA>:B1,B2,B4,B5,B6` 각각 기록. 도중 새 지시서 발행은 기존 시작 버전을 소급 실패시키지 않는다.
- C03 실측 B HEAD `914ab22f4a434bd951a8061d5fe489e1f22ee3e6`. 직전 B3 `_stage_specific_llm_contract`는 새 Owner `stage_contracts.py`로 원격 이동·targeted 정상 exit0 완료, **재실행/신규 MOVE 계상 금지**. 남은 5개만 실행. B HEAD가 전진했으면 source wrapper/target blob을 재조회해 실제 완료 item은 `ALREADY_MOVED`, 나머지 안전 item 계속.
- 공통 MOVE: **원본 계산 본문 삭제→target 단일 Owner 함수에 실제 이전→원명/원서명 thin wrapper**. target에서 facade 역import 금지. 필요한 helper는 `facade=sys.modules[__name__]`를 넘겨 호출시점 조회하여 monkeypatch/예외/키 순서/한국어 prompt bytes/shallow alias/IO 순서를 보존. 변경 전 원본 fixture golden 확보 후 wrapper·owner 비교. 대상 정상 `python -m pytest -q -p no:cacheprovider tests/<new_test>.py` 또는 stdlib unittest exit0 1회. `-O`/full peer/전체 CI 필수 아님. 한 item 차단돼도 나머지 4개 독립 안전 item 진행. Git 인증/pytest 문제는 `PUSH_BLOCKED`/`TEST_BLOCKED`로 분리; local-only는 원격 G1 아님.

## B1 — Commander monitor gate 근거
- SOURCE `libs/contracts/agent_outputs.py::_commander_shadow_monitor_gate_details(state)` (B blob `1bab58ba5c23614d912d506d2520f31b46b51c41`, 원함수 L940–1008) → TARGET `libs/contracts/agent_output_parts/commander_shadow_evidence.py::build_monitor_gate_details(state, *, facade)` (B 원격 미존재).
- `monitor_entry.metrics/thresholds`, passed/failed checks, pullback 우선순위, observed_features, entry_score/entry_block_reason 본문 전부 이동. 원명 wrapper; `_dict/_clip/_gate_pass/_score_from_checks`는 facade use-time.
- TEST `tests/test_p15_commander_shadow_gate_owner.py`: (1) empty state 기본값, (2) pullback false와 passed_checks 우선순위, (3) 8개 초과 checks 절단·threshold/price fallback, (4) patched `_gate_pass` spy·예외·입력 불변. old/new/owner 키 순서 일치.

## B2 — Commander prior/current delta
- SOURCE `libs/contracts/agent_outputs.py::_commander_shadow_context_delta_summary(state, *, observations)` (동일 B blob, L1009–1084) → TARGET `libs/contracts/agent_output_parts/commander_shadow_evidence.py::build_context_delta_summary(state, *, observations, facade)`.
- symbol/playbook/regime/sentiment/VIX/score 변화 및 0.03/1.0/0.05 경계·fallback·last_llm_status 본문 이동. 원명 wrapper; `_dict/_clip` facade use-time. B1과 동일 target 파일을 **B 한 사람만** 순차 수정, 앞선 함수 보존.
- TEST `tests/test_p15_commander_shadow_delta_owner.py`: (1) prior 없음, (2) sentiment 0.029/0.030, (3) VIX 0.99/1.0와 score 0.049/0.05, (4) 비수치 예외/clip spy/입력 불변. key order/JSON bytes parity.

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

## KEEP·원격 종료
- B3 stage contract 이미 이동됨; `_run_strategist_frame_llm`(LLM/ledger effect), `strategist_node(state)`(Graph/State effect), UI report writer, Commander runtime 기존 Owner는 **정당 KEEP**, 재이동/중복 구현 금지. B Strategist 소스와 integration 소스 blob은 다르므로 **B 함수 hunk만 변경**, integration 전체 파일 덮어쓰기 금지. 잘린 출력 `… tokens truncated …`를 파일로 복사하지 말고 bounded-hunk patch·py_compile.
- B1/B2/B4/B5/B6 각각 `ORDER_ID | ITEM_STATUS(IMPLEMENTED/ALREADY_MOVED/TEST_BLOCKED/PUSH_BLOCKED/SAFETY_BLOCKED/NOT_RUN) | SOURCE_BEFORE/AFTER_BLOB+LOC | TARGET_BLOB | NORMAL_CMD/EXIT | PUSH_REMOTE_SHA | FIRST_BLOCKER/NEXT`를 #12 댓글 **한 번** 보고. `git ls-remote`와 원격 source/target/test blob 확인. C04 최소 통합/G3, C05 STATUS/DONE 독점; 문서·이슈 본문 수정 금지.
