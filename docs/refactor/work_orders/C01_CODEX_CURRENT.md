# C01 — Codex B | 실제 함수 몸체 이동·다중 RF 연속 구현

## 실행 진입 계약 — A/B에게 다른 문서 탐색 지시 금지 (최우선)

**A/B 각각 이 파일 하나만 읽고 개발을 수행한다.** `docs/refactor/plan/rf_details/`, `INDEX.md`, D00, C03, Txx, 원본 RF, STATUS를 A/B가 열거나 읽고 작업을 고르게 하지 않는다. 필요한 **SOURCE_PATH::EXACT_FUNCTION → TARGET_PATH::EXACT_FUNCTION, 함수 몸체 처리, 주입해야 할 의존성, 테스트 fixture, KEEP 사유, 담당 독점권, 우선순위 및 재개점은 모두 아래 C01/C02 본문에 완전히 복사**한다. GitHub의 *실제 작업 대상 코드 파일*과 호출자·타깃 파일은 직접 열어 구현할 수 있다. 자기 작업이 끝나도 다음 항목을 순서대로 진행한다.

C03 지팀장이 93개 RF 설계서/실제 source를 읽고 필요한 다음 구현 항목을 이 단일 지시서의 **작업 큐 본문에 인라인 추가**한다. A/B가 상세설계를 찾아가라는 문구는 무효. 지시서에 없는 RF/함수는 새로 추정하지 않고 C03이 배정할 때까지 기존 다른 항목 진행. 각 차수에 4~6개 이상 독립 코드 항목을 유지하며 기존 완료 항목은 제거·추가. 구 구현과 목적지 소유권을 실제 시작 source blob에서 확인하여 중복 개발 금지.


**유일한 진입점:** 이 C01 파일만. 목표는 동결 T00~T09/V3이며 필요한 모든 배정 정보는 이 문서 본문에 이미 포함되어 있다. 허용 브랜치 `work/p15-b-operator-structure-20261022` code/test만 수정, 원격 push 후 #12 보고. 다른 브랜치/원본 RF·CSV·D00·STATUS/HANDOFF·CI·frozen oracle 수정 금지. 한 RF PASS/KEEP/실패 후에도 안전한 다음 RF 연속 수행.

## 시작과 공통 통과 기준

시작 1회 원격 integration HEAD·C01 blob·자기 B HEAD·dirty status만 확인. 최신 SHA에 이미 코드가 추출됐으면 해당 item은 SKIP_COMPLETED (반복 테스트 0). KEEP_OK = 목표 위치/단일 책임/적정 규모/중복 Owner 없음 또는 합리적인 CLI·IO·State 효과 경계. `KEEP_OK|RF|path|사유 한 줄|source blob`으로 통과, 새 테스트 0. 본문 MOVE는 원본에서 실제 삭제 + 새 Owner 함수 구현 + 호출시점 facade wrapper, 중복 복사 금지. 변경 함수만 old/new fake normal unittest 또는 pytest 1회 exit0, 원본 LOC 감소와 새 target blob 기록. pytest 없으면 unittest 사용. push 차단시 오류 1회 기록, 다른 독립 안전 item 계속; 비인가 credential/push 우회 금지.

## B1 (RF-044): Commander Shadow 네 실제 계산 함수

원본 `libs/contracts/agent_outputs.py` (B 기준 blob `d52816cf`, 약1621줄), 상세 RF-044.
1. `_commander_shadow_actual_runtime` → `libs/contracts/agent_output_parts/commander_shadow_runtime.py::build_actual_runtime`.
2. `_commander_shadow_observations` → 같은 `commander_shadow_runtime.py::build_observations`.
3. `_commander_shadow_monitor_gate_details` → `libs/contracts/agent_output_parts/commander_shadow_evidence.py::build_monitor_gate_details`.
4. `_commander_shadow_context_delta_summary` → 같은 `commander_shadow_evidence.py::build_context_delta_summary`.
원래 서명 그대로 thin wrapper 유지. `_dict/_clip/_listify/_safe_int/_gate_pass/_score_from_checks` 호출시점 facade 주입. Cached Strategist, NOOP→WAIT, terminal order, 0.03/1.0/0.05 임계·키순서·None/False 원본과 같아야 한다. `tests/test_rf044_commander_shadow_runtime_owner.py` 및 `tests/test_rf044_commander_shadow_evidence_owner.py`가 미존재면 작성, 있으면 재사용. 합성 dict/fake만 사용.

## B2 (RF-008 + RF-018): Strategist 큰 순수 함수 다섯 개 실제 이동

원본 `graphs/nodes/strategist_node.py` (통합 blob `0f6cda31`, 3628줄) 및 RF-008. 신규 목적지 `libs/runtime/strategist`는 RF-018 **같은 B 담당**. 
1. `_stage_specific_llm_contract` → `libs/runtime/strategist/llm/stage_contracts.py::build_stage_specific_contract`.
2. `_apply_strategist_llm_token_budget` → `libs/runtime/strategist/context/token_budget.py::apply_frame_token_budget`.
3. `_build_strategist_llm_repair_messages` → `libs/runtime/strategist/llm/repair_messages.py::build_repair_messages`.
4. `_build_strategist_llm_messages` → `libs/runtime/strategist/llm/frame_messages.py::build_frame_messages`.
5. `_build_compact_strategist_llm_payload` → `libs/runtime/strategist/context/compact_llm_payload.py::build_compact_llm_payload`.
원본 wrapper 및 monkeypatch use-time 호환; Stage1~4 prompt/JSON 문자열 bytes와 memory-disabled·repair 순서·키순서 보존. 실제 `LLMRouter`, ledger writer, State mutation, broker 호출은 원위치. `tests/test_rf008_strategist_owner_extraction.py` 에 고정 original expected 및 fake facade 테스트. 추가 546줄 `strategist_node`에서 이미 추출된 부분은 KEEP_OK, 아직 분리할 순수 부분은 신규 slice로 만들고 TARGET_GAP을 정확히 기록.

## B3 (RF-001): Operator UI core 원본 축소

RF-001, 원본 `apps/operator_ui/data_access_core.py` (2466줄, blob 참고 `0666538f`).
- `_load_operator_brief` → `apps/operator_ui/data_access_brief_loader.py::load_operator_brief`.
- `_trade_report_index` → `apps/operator_ui/data_access_report_index.py::trade_report_index`.
- `load_run_detail` → `apps/operator_ui/data_access_run_detail.py::load_run_detail`.
기존 UI ReadModel Owner에 동일 코드가 있으면 신규 중복 금지. facade public import/캐시/파일 IO 경로·한국어/키 순서 보존. fake/tmp report fixtures, 운영 데이터 변경 없음.

## B4 (RF-018/045/063/065/070/071): 정당한 KEEP 한 번에 종결 + 다음 실구현

RF-018 `libs/runtime/strategist/llm/stage_reviews.py`(219줄), 단일 책임 context helper; RF-045 EventLogger copy fix 이미 같은 blob이면 SKIP, 작은 `libs/core` utilities KEEP; RF-063 `scripts/diagnostics/analyze_entry_blockers.py`(54줄), RF-065 `scripts/research/daily_profitability_scorecard.py`(40줄), RF-070/071 공개 `scripts/run_*.py` thin entry는 위치/책임 맞으면 KEEP_OK. 운영 `--apply`/실로그 이동은 HOLD, 비실행 확인은 계속. C03이 이 C01 본문에 직접 추가한 새 SOURCE::함수→TARGET::함수 작업만 이어서 MOVE한다. 다른 작업 문서를 탐색하지 않는다.

## B5 (RF-010): Monitor Graph의 순수 후보를 실제 함수 수준 분리

- 원본: `graphs/nodes/monitor_node.py::_evaluate_monitor_entry_candidate` (기준 blob의 L410~430, 약21행).
- 목표: `graphs/nodes/monitor_entry_candidate_projection.py::evaluate_monitor_entry_candidate` (RF-010, B 단독).
- 해당 private 계산의 input/output·기존 전역 참조를 확인해 순수 결과 판단 부분만 MOVE. 기존 `_evaluate_monitor_entry_candidate` signature 얇은 wrapper 유지. `monitor_node` 약499행 전체/실주문/State mutation은 옮기지 말 것.
- 2~4개 fake monitor dict 고정 old/new 결과·예외/monkeypatch 일치, normal targeted unittest/pytest 한 번.

## B6 (RF-011): Commander Runtime의 Monitor Intent 투영 함수 분리

- 원본: `graphs/commander_runtime.py::_intent_from_monitor_state` (기준 blob L1703~1765, 약63행).
- 목표: `graphs/commander_intent_projection.py::intent_from_monitor_state` (RF-011, B 단독).
- 모니터 State의 **읽기 전용 의도 생성**만 해당 Owner로 MOVE, 원본 함수 얇은 wrapper 유지. `_attach_commander_applied_policy` / `_persist_commander` / broker·주문 효과 및 State writer 순서는 절대 이동하지 않는다.
- 기존 입력 State의 intent schema/NOOP/WAIT/null/exception과 동등 fixture 2~4개, 정상 targeted test 한 번. 이후 C01 본문에 남은 다음 ITEM을 계속 수행.

## 보고

`ORDER_BLOB|ITEM/RF|SOURCE_BLOB|MOVED_FUNCTIONS|NEW_OWNER_PATH/BLOB|ORIGINAL_BEFORE_AFTER_LOC|KEEP_OK{reason,blob}|NORMAL_TEST_CMD_EXIT|PUSH_REMOTE_SHA|NEXT`만 #12에 1회. 코드 변경만 B branch에 commit/push, remote 확인. 첫 PASS·첫 KEEP으로 종료하지 않는다.
