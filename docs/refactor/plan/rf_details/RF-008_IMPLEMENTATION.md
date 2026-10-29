# RF-008 — 코드 구조/함수 재배치 설계 (T07)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/05_DONE/CODEX_B/RF-008.md` blob `e63c6bba5ccaa756ddb3ec0abebebccda968d97f`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 1개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**실제 함수 확인:** 아래 함수명·규모는 정본 원본에서 확인한 설계 입력이다. 작업시 최신 원격 SHA에서 원함수 및 이미 이동된 몸체를 먼저 확인한다.

| SOURCE_PATH::함수 | 본문 규모 | TARGET_PATH::함수 | 코드 변경 |
|---|---:|---|---|
| `graphs/nodes/strategist_node.py::_stage_specific_llm_contract` | 약 88행 | `libs/runtime/strategist/llm/stage_contracts.py::build_stage_specific_contract` (RF-018) | 함수 몸체 **실제 MOVE**, 원시그니처 facade wrapper 유지 |
| `graphs/nodes/strategist_node.py::_build_strategist_llm_messages` | 약 277행 | `libs/runtime/strategist/llm/frame_messages.py::build_frame_messages` (RF-018) | 함수 몸체 **실제 MOVE**, 원시그니처 facade wrapper 유지 |
| `graphs/nodes/strategist_node.py::_apply_strategist_llm_token_budget` | 약 100행 | `libs/runtime/strategist/context/token_budget.py::apply_frame_token_budget` (RF-018) | 함수 몸체 **실제 MOVE**, 원시그니처 facade wrapper 유지 |
| `graphs/nodes/strategist_node.py::_build_compact_strategist_llm_payload` | 약 332행 | `libs/runtime/strategist/context/compact_llm_payload.py::build_compact_llm_payload` (RF-018) | 함수 몸체 **실제 MOVE**, 원시그니처 facade wrapper 유지 |
| `graphs/nodes/strategist_node.py::_build_strategist_llm_repair_messages` | 약 112행 | `libs/runtime/strategist/llm/repair_messages.py::build_repair_messages` (RF-018) | 함수 몸체 **실제 MOVE**, 원시그니처 facade wrapper 유지 |

**구현 계약:** 입력/출력 dict 키·순서·문자열 bytes, 예외, fallback, monkeypatch는 기존과 동등. IO/LLM/상태/주문 발생 순서를 바꾸지 않으며 실제 effect boundary는 원래 위치에 남긴다. 새 Owner→facade 역import 금지. 기존 동일 target 함수가 있으면 재활용하고 중복 구현하지 않는다.
**보존 경계:** `_run_strategist_frame_llm`은 실제 LLM 호출·재시도·기록, `_load_strategy_memory_advisory`는 파일/환경·시각, `strategist_node(state)`는 State/Graph·아티팩트. 전체 무조건 MOVE 금지, thin adapter 잔여 부분 추출 여부는 다음 단계에서 검증한다. 신규 목적지는 RF-018(동일 B) 소유.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `graphs/nodes/strategist_node.py` | 185865 | `0f6cda317572727918ee4e39a2c6c0869f244aa3` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `graphs/nodes/strategist_node_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `graphs/nodes/strategist_node.py` → `graphs/nodes/strategist_node.py` | 185865 | `0f6cda317572` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
