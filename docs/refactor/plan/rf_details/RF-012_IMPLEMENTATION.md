# RF-012 — 함수·신규 모듈 매핑 상세설계 (실물 코드 대조)

**SOURCE:** `integration/p1.5@4b15aefbcaf3a31c2e9ff3710025155d13f152bd`; CSV b46bcb1f29ed3c0a133b059d690173c195c81bf9. **소유:** Codex B 구현, Claude A 읽기 전용 독립 검증. 파일 37개. 원본 RF `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-012.md`.

**KEEP/PASS:** 정확한 목표 디렉터리, 단일 책임, 적절한 길이 또는 공개 호환/효과 경계라면 `KEEP_OK|path|사유 1줄|blob`으로 당회 통과. 동일 SHA 새 테스트/전수 peer 금지. 함수 MOVE만 실제 refactoring 성과.

## 1. 함수별 SOURCE → TARGET / 구현 계약

**읽은 실제 파일:** `graphs/nodes/execute_from_packet.py` blob `1a10af59e5e9b4035f1c7403e5aeb814f65c8e3a`, **4106 LOC**. 파이썬 함수 정의와 들여쓰기를 읽어 분리 후보를 잡았다. 아래 target은 코드 작성 전 현재 Owner·소비자 중복을 1회 확인하여 필요 시 기존 Owner를 재사용한다.

| 원본 함수/줄 | 분리판정 | 목표 소스::함수 | 본문 행수·주의 |
|---|---|---|---|
| `graphs/nodes/execute_from_packet.py::execute_from_packet` L2915–4106 | **KEEP_EFFECT_OR_EXTRACT_PURE_SLICE** | `graphs/nodes/execute_from_packet.py::execute_from_packet` | 1192행, BROKER, STATE |
| `graphs/nodes/execute_from_packet.py::_evaluate_open_order_reconciliation_guard` L2046–2195 | **KEEP_EFFECT_OR_EXTRACT_PURE_SLICE** | `graphs/nodes/execute_from_packet.py::_evaluate_open_order_reconciliation_guard` | 150행, BROKER, CLOCK/ENV |
| `graphs/nodes/execute_from_packet.py::_prepare_request` L2593–2718 | **KEEP_EFFECT_OR_EXTRACT_PURE_SLICE** | `graphs/nodes/execute_from_packet.py::_prepare_request` | 126행, BROKER |
| `graphs/nodes/execute_from_packet.py::_resolve_order_price_for_notional_with_source` L1660–1778 | **MOVE_BODY** | `graphs/nodes/execute_from_packet_resolve_order_price_for_notional_with_.py::_resolve_order_price_for_notional_with_source` | 119행, 부작용 정적 탐지 없음 |
| `graphs/nodes/execute_from_packet.py::_attempt_unfilled_order_recovery` L942–1039 | **KEEP_EFFECT_OR_EXTRACT_PURE_SLICE** | `graphs/nodes/execute_from_packet.py::_attempt_unfilled_order_recovery` | 98행, BROKER |
| `graphs/nodes/execute_from_packet.py::_order_entry_chart_guard_snapshot` L608–702 | **MOVE_BODY** | `graphs/nodes/execute_from_packet_order_entry_chart_guard_snapshot.py::_order_entry_chart_guard_snapshot` | 95행, 부작용 정적 탐지 없음 |
| `graphs/nodes/execute_from_packet.py::_update_recent_sell_order_guard` L1526–1612 | **MOVE_BODY** | `graphs/nodes/execute_from_packet_update_recent_sell_order_guard.py::_update_recent_sell_order_guard` | 87행, 부작용 정적 탐지 없음 |
| `graphs/nodes/execute_from_packet.py::_build_order_from_intent` L2345–2422 | **KEEP_EFFECT_OR_EXTRACT_PURE_SLICE** | `graphs/nodes/execute_from_packet.py::_build_order_from_intent` | 78행, BROKER |

### execute_from_packet (L2915–4106)
- **기능 경계:** `graphs/nodes/execute_from_packet.py::execute_from_packet` (1192행), 내부 호출 `_import_event_logger`, `_import_api_catalog`, `_import_supervisor`, `_import_get_executor`, `_mark_submission_dispatched`, `_quote_snapshot_for_order`, `_extract_order_symbol`, `_augment_quote_snapshot_with_spread`, `_extract_upper_limit_quote_snapshot`, `_coerce_float`. 감지된 경계: BROKER, STATE.
- **정확한 목표:** `graphs/nodes/execute_from_packet.py::execute_from_packet`. 부작용/클래스 context의 원본 순서를 KEEP. 코드를 실제 확인해 순수 subsection이 있으면 단독 helper를 목표 Owner로 분리; 한 책임의 필수 effect라면 KEEP_JUSTIFIED 한줄로 끝낸다.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

### _evaluate_open_order_reconciliation_guard (L2046–2195)
- **기능 경계:** `graphs/nodes/execute_from_packet.py::_evaluate_open_order_reconciliation_guard` (150행), 내부 호출 `_is_trueish`, `_coerce_int`. 감지된 경계: BROKER, CLOCK/ENV.
- **정확한 목표:** `graphs/nodes/execute_from_packet.py::_evaluate_open_order_reconciliation_guard`. 부작용/클래스 context의 원본 순서를 KEEP. 코드를 실제 확인해 순수 subsection이 있으면 단독 helper를 목표 Owner로 분리; 한 책임의 필수 effect라면 KEEP_JUSTIFIED 한줄로 끝낸다.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

### _prepare_request (L2593–2718)
- **기능 경계:** `graphs/nodes/execute_from_packet.py::_prepare_request` (126행), 내부 호출 `_import_request_builder`, `_import_settings`. 감지된 경계: BROKER.
- **정확한 목표:** `graphs/nodes/execute_from_packet.py::_prepare_request`. 부작용/클래스 context의 원본 순서를 KEEP. 코드를 실제 확인해 순수 subsection이 있으면 단독 helper를 목표 Owner로 분리; 한 책임의 필수 effect라면 KEEP_JUSTIFIED 한줄로 끝낸다.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

### _resolve_order_price_for_notional_with_source (L1660–1778)
- **기능 경계:** `graphs/nodes/execute_from_packet.py::_resolve_order_price_for_notional_with_source` (119행), 내부 호출 `_extract_order_symbol`, `_coerce_float`, `_positive_price_from_row`, `_symbol_matches_row`, `_extract_market_quotes_safe`, `_canonical_artifact_row`. 감지된 경계: 없음.
- **정확한 목표:** `graphs/nodes/execute_from_packet_resolve_order_price_for_notional_with_.py::_resolve_order_price_for_notional_with_source`. 본문의 계산·분기·반환을 목표 Owner에 옮기고 원래 이름/서명 thin wrapper만 유지. consumer import/patch seam/출력 bytes와 예외 보존. 중복 본문 삭제.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

### _attempt_unfilled_order_recovery (L942–1039)
- **기능 경계:** `graphs/nodes/execute_from_packet.py::_attempt_unfilled_order_recovery` (98행), 내부 호출 `_extract_order_symbol`, `_coerce_int`, `_build_cancel_order_for_unfilled`, `_normalize_execution`, `_prepare_request`, `_propagate_cancel_unknown_outcome`, `_execution_market_open_for_recovery`. 감지된 경계: BROKER.
- **정확한 목표:** `graphs/nodes/execute_from_packet.py::_attempt_unfilled_order_recovery`. 부작용/클래스 context의 원본 순서를 KEEP. 코드를 실제 확인해 순수 subsection이 있으면 단독 helper를 목표 Owner로 분리; 한 책임의 필수 effect라면 KEEP_JUSTIFIED 한줄로 끝낸다.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

## 2. 본 RF 전체 파일별 목표/액션

| SOURCE_PATH | TARGET_PATH | Size/Blob | KEEP/MOVE 구체 사유 |
|---|---|---|---|
| `graphs/nodes/assemble_decision_packet.py` | `graphs/nodes/assemble_decision_packet.py` | 2738B `dbcae63ac548` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/build_decision_context.py` | `graphs/nodes/build_decision_context.py` | 19640B `d5e6362add5f` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/build_execution_readiness.py` | `graphs/nodes/build_execution_readiness.py` | 8049B `a17d56a521b0` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/build_market_snapshot.py` | `graphs/nodes/build_market_snapshot.py` | 4127B `af11f9d64d6f` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/build_open_order_snapshot.py` | `graphs/nodes/build_open_order_snapshot.py` | 2303B `995c2931b439` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/build_portfolio_snapshot.py` | `graphs/nodes/build_portfolio_snapshot.py` | 21537B `d6afacc15ef3` | 큰 Python 함수 추가 실사: 서로 다른 실제 책임 확인 후 이름 붙여 분리 |
| `graphs/nodes/build_risk_context.py` | `graphs/nodes/build_risk_context.py` | 1532B `c3e466816184` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/build_snapshots.py` | `graphs/nodes/build_snapshots.py` | 802B `a0e20a2084b8` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/decide_trade.py` | `graphs/nodes/decide_trade.py` | 65080B `6fa69e96f787` | 큰 Python 함수 추가 실사: 서로 다른 실제 책임 확인 후 이름 붙여 분리 |
| `graphs/nodes/decision_node.py` | `graphs/nodes/decision_node.py` | 8203B `172f5ac1243c` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/ensure_token.py` | `graphs/nodes/ensure_token.py` | 786B `d20d8b2ff32c` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/execute_from_packet.py` | `graphs/nodes/execute_from_packet.py` | 183181B `1a10af59e5e9` | 위 함수 원본: MOVE_BODY만 추출, 공개 facade 유지 |
| `graphs/nodes/execute_order.py` | `graphs/nodes/execute_order.py` | 6641B `1e23bc4d3461` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/executor_node.py` | `graphs/nodes/executor_node.py` | 381B `832c6a30e43b` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/hydrate_skill_results_node.py` | `graphs/nodes/hydrate_skill_results_node.py` | 11820B `a23a588a3e8f` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/load_state.py` | `graphs/nodes/load_state.py` | 412B `ceb1fb61542a` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/log_decision_trace.py` | `graphs/nodes/log_decision_trace.py` | 1709B `d74e0605fe92` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/plan_api.py` | `graphs/nodes/plan_api.py` | 572B `c73adc21da72` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/portfolio_guard_node.py` | `graphs/nodes/portfolio_guard_node.py` | 4608B `7ec264a1a52a` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/prepare_api_call.py` | `graphs/nodes/prepare_api_call.py` | 1608B `1529fa5897a5` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/prepare_order_dry_run.py` | `graphs/nodes/prepare_order_dry_run.py` | 1995B `75741376e535` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/read_account_balance.py` | `graphs/nodes/read_account_balance.py` | 1032B `867bd3c1bb38` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/reporter_node.py` | `graphs/nodes/reporter_node.py` | 1501B `214758d222cd` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/risk_cash_truth.py` | `graphs/nodes/risk_cash_truth.py` | 2914B `bc3bd5ea679e` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/save_state.py` | `graphs/nodes/save_state.py` | 398B `17d867a0de46` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/skill_contracts.py` | `graphs/nodes/skill_contracts.py` | 14604B `bf0e50987cd6` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/nodes/update_state_after_execution.py` | `graphs/nodes/update_state_after_execution.py` | 59649B `100952d946fe` | 큰 Python 함수 추가 실사: 서로 다른 실제 책임 확인 후 이름 붙여 분리 |
| `graphs/pipelines/eod_report.py` | `graphs/pipelines/eod_report.py` | 533B `72ce931dc964` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/pipelines/live_cycle.py` | `graphs/pipelines/live_cycle.py` | 638B `6fdd06135875` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/pipelines/m10_live_pipeline.py` | `graphs/pipelines/m10_live_pipeline.py` | 1403B `f220b5769e71` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/pipelines/m11_2_live_pipeline.py` | `graphs/pipelines/m11_2_live_pipeline.py` | 1175B `41766fe275b2` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/pipelines/m11_live_pipeline.py` | `graphs/pipelines/m11_live_pipeline.py` | 1056B `784b4a44a849` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/pipelines/m13_eod_report.py` | `graphs/pipelines/m13_eod_report.py` | 4849B `632214d0eab2` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/pipelines/m13_live_loop.py` | `graphs/pipelines/m13_live_loop.py` | 8571B `72eb87ffd808` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/pipelines/m13_tick.py` | `graphs/pipelines/m13_tick.py` | 2140B `944e61a860f2` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/pipelines/offhours_validation.py` | `graphs/pipelines/offhours_validation.py` | 9295B `9a5c7576f93c` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/pipelines/runtime_tick.py` | `graphs/pipelines/runtime_tick.py` | 508B `184a43571dbd` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |

## 3. 개발자 독점 순서와 최소 검증

1. Codex B만 표의 실제 `MOVE_BODY` 순수 함수부터 source→target 본문 이동; 기존 Owner가 있으면 새 파일 중복 없이 기존 파일 사용. 하나의 경계가 막혀도 다음 독립 항목으로 진행. 다른 RF·반대 개발자 소유 파일 쓰기 금지.
2. `KEEP_OK`는 본문/위치/역할을 한 번 확인하고 한 줄 사유+Git SHA로 즉시 종결; 같은 SHA 테스트 재실행하지 않는다. 효과/broker/State·CLI와 frozen oracle은 재배치 자체를 강제하지 않는다.
3. 실제 MOVE는 원본 구현 제거·새 owner 구현·기존 thin wrapper, before/after LOC, 관련 정상 fake pytest/unittest exit0 후 B 허용 브랜치 code/test 정상 push. C04는 delta만 묶음 통합, C05는 기존 DONE 이력을 보존하되 TARGET_GAP 남았으면 구현으로 되돌린다.
4. `RF=RF-012|SOURCE_BLOB|FUNCTION_MOVES|TARGET_PATHS/BLOBS|KEEP_REASON|LOC_DELTA|TEST_CMD/EXIT|PUSH_SHA|TARGET_STATUS` 보고. 실거래/운영 DB/Guard/UEF 등 효과 금지.
