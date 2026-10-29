# RF-044 — 코드 구조/함수 재배치 설계 (T00/V3)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/02_DEVELOPING/CODEX_B/RF-044.md` blob `133e3a0b313007ffc72eda2622c0258b6512a8f3`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 27개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**실제 함수 확인:** 아래 함수명·규모는 정본 원본에서 확인한 설계 입력이다. 작업시 최신 원격 SHA에서 원함수 및 이미 이동된 몸체를 먼저 확인한다.

| SOURCE_PATH::함수 | 본문 규모 | TARGET_PATH::함수 | 코드 변경 |
|---|---:|---|---|
| `libs/contracts/agent_outputs.py::_commander_shadow_actual_runtime` | 약 86행 | `libs/contracts/agent_output_parts/commander_shadow_runtime.py::build_actual_runtime` (RF-044) | 함수 몸체 **실제 MOVE**, 원시그니처 facade wrapper 유지 |
| `libs/contracts/agent_outputs.py::_commander_shadow_observations` | 약 57행 | `libs/contracts/agent_output_parts/commander_shadow_runtime.py::build_observations` (RF-044) | 함수 몸체 **실제 MOVE**, 원시그니처 facade wrapper 유지 |
| `libs/contracts/agent_outputs.py::_commander_shadow_monitor_gate_details` | 약 69행 | `libs/contracts/agent_output_parts/commander_shadow_evidence.py::build_monitor_gate_details` (RF-044) | 함수 몸체 **실제 MOVE**, 원시그니처 facade wrapper 유지 |
| `libs/contracts/agent_outputs.py::_commander_shadow_context_delta_summary` | 약 76행 | `libs/contracts/agent_output_parts/commander_shadow_evidence.py::build_context_delta_summary` (RF-044) | 함수 몸체 **실제 MOVE**, 원시그니처 facade wrapper 유지 |

**구현 계약:** 입력/출력 dict 키·순서·문자열 bytes, 예외, fallback, monkeypatch는 기존과 동등. IO/LLM/상태/주문 발생 순서를 바꾸지 않으며 실제 effect boundary는 원래 위치에 남긴다. 새 Owner→facade 역import 금지. 기존 동일 target 함수가 있으면 재활용하고 중복 구현하지 않는다.
**순서:** Runtime/Observations 2개 → Gate/Context 2개. `_dict/_clip/_listify/_safe_int/_gate_pass/_score_from_checks`는 사용시점 facade injected. 보호된 주문/State writer 호출 금지.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `libs/contracts/agent_outputs.py` | 105768 | `e8d75387e80214189fe118e2920f63867d9f7bf0` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/contracts/agent_outputs_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `libs/contracts/agent_output_parts/__init__.py` → `libs/contracts/agent_output_parts/__init__.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/contracts/agent_output_parts/scanner_projections.py` → `libs/contracts/agent_output_parts/scanner_projections.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/contracts/agent_output_parts/strategist_projections.py` → `libs/contracts/agent_output_parts/strategist_projections.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/contracts/agent_output_values.py` → `libs/contracts/agent_output_values.py` | 2974 | `76e489f8e250` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/contracts/agent_outputs.py` → `libs/contracts/agent_outputs.py` | 105768 | `e8d75387e802` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/contracts/commander_output_context.py` → `libs/contracts/commander_output_context.py` | 5901 | `54586a7e388c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/contracts/commander_output_fields.py` → `libs/contracts/commander_output_fields.py` | 12764 | `e9b19abbf355` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/contracts/commander_output_policy.py` → `libs/contracts/commander_output_policy.py` | 9820 | `8c7c22df1bad` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/contracts/monitor_output_context.py` → `libs/contracts/monitor_output_context.py` | 9268 | `0e411e0c47fe` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/contracts/monitor_output_decision.py` → `libs/contracts/monitor_output_decision.py` | 14857 | `21245ff83c2e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/contracts/monitor_output_exit_fields.py` → `libs/contracts/monitor_output_exit_fields.py` | 15387 | `d548a7d397f1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/contracts/monitor_output_fields.py` → `libs/contracts/monitor_output_fields.py` | 6631 | `c495e5e89ae3` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/contracts/monitor_output_memory_bias.py` → `libs/contracts/monitor_output_memory_bias.py` | 7836 | `e239a989df00` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/contracts/monitor_output_policy_fields.py` → `libs/contracts/monitor_output_policy_fields.py` | 8498 | `537b3c8aec2c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/contracts/scanner_output_context.py` → `libs/contracts/scanner_output_context.py` | 15144 | `01ae899da227` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/contracts/scanner_output_fields.py` → `libs/contracts/scanner_output_fields.py` | 16973 | `48a01db19627` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/contracts/strategist_output_context.py` → `libs/contracts/strategist_output_context.py` | 15238 | `e1dbc70cb915` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/contracts/strategist_output_fields.py` → `libs/contracts/strategist_output_fields.py` | 14766 | `e4d21e24d121` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/contracts/strategist_output_plan_fields.py` → `libs/contracts/strategist_output_plan_fields.py` | 8255 | `51ac73644568` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `tests/test_p15_scanner_projection_extraction.py` → `tests/test_p15_scanner_projection_extraction.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_p15_strategist_projection_extraction.py` → `tests/test_p15_strategist_projection_extraction.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf044_contract_facade.py` → `tests/test_rf044_contract_facade.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf044_contract_state_serialization.py` → `tests/test_rf044_contract_state_serialization.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf044_executor_error_serialization.py` → `tests/test_rf044_executor_error_serialization.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf044_executor_input_immutability.py` → `tests/test_rf044_executor_input_immutability.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf044_owner_c1_inventory.py` → `tests/test_rf044_owner_c1_inventory.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/test_rf044_supervisor_blocked_consumer.py` → `tests/test_rf044_supervisor_blocked_consumer.py` | BASELINE_ONLY | `BASELINE_ONLY` | KEEP_IF: 테스트 단일 소유·오라클 불변 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
