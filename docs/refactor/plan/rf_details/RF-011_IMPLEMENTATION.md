# RF-011 — 함수·신규 모듈 매핑 상세설계 (실물 코드 대조)

**SOURCE:** `integration/p1.5@4b15aefbcaf3a31c2e9ff3710025155d13f152bd`; CSV b46bcb1f29ed3c0a133b059d690173c195c81bf9. **소유:** Codex B 구현, Claude A 읽기 전용 독립 검증. 파일 3개. 원본 RF `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-011.md`.

**KEEP/PASS:** 정확한 목표 디렉터리, 단일 책임, 적절한 길이 또는 공개 호환/효과 경계라면 `KEEP_OK|path|사유 1줄|blob`으로 당회 통과. 동일 SHA 새 테스트/전수 peer 금지. 함수 MOVE만 실제 refactoring 성과.

## 1. 함수별 SOURCE → TARGET / 구현 계약

**읽은 실제 파일:** `graphs/commander_runtime.py` blob `b452e6a5c0ed1b288d31c283b8ad109349404280`, **2975 LOC**. 파이썬 함수 정의와 들여쓰기를 읽어 분리 후보를 잡았다. 아래 target은 코드 작성 전 현재 Owner·소비자 중복을 1회 확인하여 필요 시 기존 Owner를 재사용한다.

| 원본 함수/줄 | 분리판정 | 목표 소스::함수 | 본문 행수·주의 |
|---|---|---|---|
| `graphs/commander_runtime.py::_attach_commander_applied_policy` L732–908 | **KEEP_EFFECT_OR_EXTRACT_PURE_SLICE** | `graphs/commander_runtime.py::_attach_commander_applied_policy` | 177행, STATE |
| `graphs/commander_runtime.py::_assess_open_position_commander_override` L1900–2030 | **KEEP_EFFECT_OR_EXTRACT_PURE_SLICE** | `graphs/commander_runtime.py::_assess_open_position_commander_override` | 131행, STATE |
| `graphs/commander_runtime.py::_intent_from_monitor_state` L1703–1765 | **MOVE_BODY** | `graphs/commander_runtime_intent_from_monitor_state.py::_intent_from_monitor_state` | 63행, 부작용 정적 탐지 없음 |
| `graphs/commander_runtime.py::_persist_commander` L2685–2737 | **KEEP_EFFECT_OR_EXTRACT_PURE_SLICE** | `graphs/commander_runtime.py::_persist_commander` | 53행, STATE |
| `graphs/commander_runtime.py::_apply_portfolio_preflight_guard` L1626–1676 | **KEEP_EFFECT_OR_EXTRACT_PURE_SLICE** | `graphs/commander_runtime.py::_apply_portfolio_preflight_guard` | 51행, STATE |
| `graphs/commander_runtime.py::_run_preopen_phase` L2559–2609 | **KEEP_EFFECT_OR_EXTRACT_PURE_SLICE** | `graphs/commander_runtime.py::_run_preopen_phase` | 51행, STATE |
| `graphs/commander_runtime.py::_apply_commander_cooldown_guard` L1282–1329 | **KEEP_EFFECT_OR_EXTRACT_PURE_SLICE** | `graphs/commander_runtime.py::_apply_commander_cooldown_guard` | 48행, STATE |
| `graphs/commander_runtime.py::_run_closeout_phase` L2610–2647 | **KEEP_EFFECT_OR_EXTRACT_PURE_SLICE** | `graphs/commander_runtime.py::_run_closeout_phase` | 38행, STATE |

### _attach_commander_applied_policy (L732–908)
- **기능 경계:** `graphs/commander_runtime.py::_attach_commander_applied_policy` (177행), 내부 호출 `_runtime_now_epoch`, `_resolve_commander_applied_policy`, `_commander_memory_usage_disabled`, `_normalize_strategist_output_contract`. 감지된 경계: STATE.
- **정확한 목표:** `graphs/commander_runtime.py::_attach_commander_applied_policy`. 부작용/클래스 context의 원본 순서를 KEEP. 코드를 실제 확인해 순수 subsection이 있으면 단독 helper를 목표 Owner로 분리; 한 책임의 필수 effect라면 KEEP_JUSTIFIED 한줄로 끝낸다.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

### _assess_open_position_commander_override (L1900–2030)
- **기능 경계:** `graphs/commander_runtime.py::_assess_open_position_commander_override` (131행), 내부 호출 `_runtime_now_epoch`, `_coerce_int`, `_runtime_float`, `_normalize_position_ratio`, `_row_loss_value`, `_row_refresh_cooldown_remaining`, `_select_open_position_refresh_candidate`. 감지된 경계: STATE.
- **정확한 목표:** `graphs/commander_runtime.py::_assess_open_position_commander_override`. 부작용/클래스 context의 원본 순서를 KEEP. 코드를 실제 확인해 순수 subsection이 있으면 단독 helper를 목표 Owner로 분리; 한 책임의 필수 effect라면 KEEP_JUSTIFIED 한줄로 끝낸다.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

### _intent_from_monitor_state (L1703–1765)
- **기능 경계:** `graphs/commander_runtime.py::_intent_from_monitor_state` (63행), 내부 호출 `_coerce_int`, `_runtime_float`. 감지된 경계: 없음.
- **정확한 목표:** `graphs/commander_runtime_intent_from_monitor_state.py::_intent_from_monitor_state`. 본문의 계산·분기·반환을 목표 Owner에 옮기고 원래 이름/서명 thin wrapper만 유지. consumer import/patch seam/출력 bytes와 예외 보존. 중복 본문 삭제.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

### _persist_commander (L2685–2737)
- **기능 경계:** `graphs/commander_runtime.py::_persist_commander` (53행), 내부 호출 `_build_commander_decision`, `_build_commander_decision_frame`, `_log_commander_event`, `_commander_decision_event_meta`. 감지된 경계: STATE.
- **정확한 목표:** `graphs/commander_runtime.py::_persist_commander`. 부작용/클래스 context의 원본 순서를 KEEP. 코드를 실제 확인해 순수 subsection이 있으면 단독 helper를 목표 Owner로 분리; 한 책임의 필수 effect라면 KEEP_JUSTIFIED 한줄로 끝낸다.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

### _apply_portfolio_preflight_guard (L1626–1676)
- **기능 경계:** `graphs/commander_runtime.py::_apply_portfolio_preflight_guard` (51행), 내부 호출 `_portfolio_preflight_block_payload`, `_allow_closeout_after_portfolio_preflight_block`. 감지된 경계: STATE.
- **정확한 목표:** `graphs/commander_runtime.py::_apply_portfolio_preflight_guard`. 부작용/클래스 context의 원본 순서를 KEEP. 코드를 실제 확인해 순수 subsection이 있으면 단독 helper를 목표 Owner로 분리; 한 책임의 필수 effect라면 KEEP_JUSTIFIED 한줄로 끝낸다.
- **스모크:** 변경한 경우만 고정 입력 전/후 결과·예외·patchable symbol, fake/mock/tmp 정상 targeted pytest/unittest 1회. 테스트하지 않았다면 NOT_RUN.

## 2. 본 RF 전체 파일별 목표/액션

| SOURCE_PATH | TARGET_PATH | Size/Blob | KEEP/MOVE 구체 사유 |
|---|---|---|---|
| `graphs/commander_runtime.py` | `graphs/commander_runtime.py` | 152986B `b452e6a5c0ed` | 위 함수 원본: MOVE_BODY만 추출, 공개 facade 유지 |
| `graphs/nodes/commander_node.py` | `graphs/nodes/commander_node.py` | 550B `1c6a1d64e23d` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |
| `graphs/trading_graph.py` | `graphs/trading_graph.py` | 3199B `dc8d9820bd96` | KEEP_IF: 짧고 단일 owner/올바른 패키지면 한줄 PASS |

## 3. 개발자 독점 순서와 최소 검증

1. Codex B만 표의 실제 `MOVE_BODY` 순수 함수부터 source→target 본문 이동; 기존 Owner가 있으면 새 파일 중복 없이 기존 파일 사용. 하나의 경계가 막혀도 다음 독립 항목으로 진행. 다른 RF·반대 개발자 소유 파일 쓰기 금지.
2. `KEEP_OK`는 본문/위치/역할을 한 번 확인하고 한 줄 사유+Git SHA로 즉시 종결; 같은 SHA 테스트 재실행하지 않는다. 효과/broker/State·CLI와 frozen oracle은 재배치 자체를 강제하지 않는다.
3. 실제 MOVE는 원본 구현 제거·새 owner 구현·기존 thin wrapper, before/after LOC, 관련 정상 fake pytest/unittest exit0 후 B 허용 브랜치 code/test 정상 push. C04는 delta만 묶음 통합, C05는 기존 DONE 이력을 보존하되 TARGET_GAP 남았으면 구현으로 되돌린다.
4. `RF=RF-011|SOURCE_BLOB|FUNCTION_MOVES|TARGET_PATHS/BLOBS|KEEP_REASON|LOC_DELTA|TEST_CMD/EXIT|PUSH_SHA|TARGET_STATUS` 보고. 실거래/운영 DB/Guard/UEF 등 효과 금지.
