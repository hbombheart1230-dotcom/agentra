# RF-048 — 실제 소스 함수→목표 Owner 설계

**기준:** `integration/p1.5@ef0fa5531222d7ad34737712ac56b09c0da80e4b`; 원본 RF `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-048.md`; 담당 **Codex B 단독**, 상대는 read-only. 19 경로.

## 1. 실제 def 분석 / 새 파일명·함수명

Git blob `1d637eaee70ed91512193ad53d7c0173cfd0a439`, SOURCE `libs/execution/readiness_evidence.py`, 759줄 확인.

| 현재 SOURCE::함수 | 줄수/행 | TARGET::함수 | 동작 |
|---|---:|---|---|
| `libs/execution/readiness_evidence.py::append_readiness_evidence` | L466–530 / 65 | `libs/execution/readiness_evidence.py::append_readiness_evidence` | KEEP_EFFECT_OR_CLASS; IO |
| `libs/execution/readiness_evidence.py::__enter__` | L389–434 / 46 | `libs/execution/readiness_evidence.py::__enter__` | KEEP_EFFECT_OR_CLASS; pure 후보 |
| `libs/execution/readiness_evidence.py::_try_create` | L327–360 / 34 | `libs/execution/readiness_evidence.py::_try_create` | KEEP_EFFECT_OR_CLASS; IO |
| `libs/execution/readiness_evidence.py::revalidate_current_safety` | L589–621 / 33 | `libs/execution/readiness_evidence_revalidate_current_safety.py::revalidate_current_safety` | MOVE_BODY; pure 후보 |
| `libs/execution/readiness_evidence.py::_reclaim` | L361–388 / 28 | `libs/execution/readiness_evidence.py::_reclaim` | KEEP_EFFECT_OR_CLASS; IO |
| `libs/execution/readiness_evidence.py::_current_canonical_owner` | L543–565 / 23 | `libs/execution/readiness_evidence_current_canonical_owner.py::_current_canonical_owner` | MOVE_BODY; pure 후보 |
| `libs/execution/readiness_evidence.py::_current_readiness` | L566–588 / 23 | `libs/execution/readiness_evidence.py::_current_readiness` | KEEP_EFFECT_OR_CLASS; ENV |

- **append_readiness_evidence:** 원본 65행 → `libs/execution/readiness_evidence.py::append_readiness_evidence`; 원래 효과/클래스 경계 보존, 순수 계산만 추출하거나 KEEP_OK. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.
- **__enter__:** 원본 46행 → `libs/execution/readiness_evidence.py::__enter__`; 원래 효과/클래스 경계 보존, 순수 계산만 추출하거나 KEEP_OK. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.
- **_try_create:** 원본 34행 → `libs/execution/readiness_evidence.py::_try_create`; 원래 효과/클래스 경계 보존, 순수 계산만 추출하거나 KEEP_OK. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.
- **revalidate_current_safety:** 원본 33행 → `libs/execution/readiness_evidence_revalidate_current_safety.py::revalidate_current_safety`; 실제 계산 몸체 이전 및 원명 thin wrapper, 기존 같은 Owner가 있으면 재사용. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.
- **_reclaim:** 원본 28행 → `libs/execution/readiness_evidence.py::_reclaim`; 원래 효과/클래스 경계 보존, 순수 계산만 추출하거나 KEEP_OK. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.

## 2. 소유 전체 파일별 SOURCE → TARGET / 사유

| 파일(기존/기본 목표) | bytes / blob | 처리 |
|---|---|---|
| `libs/execution/__init__.py` → `libs/execution/__init__.py` | 0 / `e69de29bb2d1` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/execution/execution_readiness.py` → `libs/execution/execution_readiness.py` | 7169 / `5e3cd8499f69` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/execution/executor_observability.py` → `libs/execution/executor_observability.py` | 5565 / `ebd6b502516c` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/execution/executors/__init__.py` → `libs/execution/executors/__init__.py` | 86 / `c0fadddb12bd` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/execution/executors/base.py` → `libs/execution/executors/base.py` | 693 / `5480d9c245cf` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/execution/executors/factory.py` → `libs/execution/executors/factory.py` | 1208 / `a566b234b777` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/execution/executors/mock_executor.py` → `libs/execution/executors/mock_executor.py` | 1381 / `77a4ab777388` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/execution/executors/real_executor.py` → `libs/execution/executors/real_executor.py` | 19224 / `eb0a0953364b` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/execution/guards/__init__.py` → `libs/execution/guards/__init__.py` | 0 / `e69de29bb2d1` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/execution/guards/broker_mutation.py` → `libs/execution/guards/broker_mutation.py` | 7981 / `d0af534731dd` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/execution/guards/symbol_allowlist.py` → `libs/execution/guards/symbol_allowlist.py` | 879 / `eb1a838924f2` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/execution/guards/unknown_quarantine.py` → `libs/execution/guards/unknown_quarantine.py` | 15584 / `30da86eadf06` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/execution/intent_admission.py` → `libs/execution/intent_admission.py` | 1098 / `c8f5333dc672` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/execution/intent_execution_owner.py` → `libs/execution/intent_execution_owner.py` | 7733 / `d25bd066f41a` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/execution/intent_identity.py` → `libs/execution/intent_identity.py` | 9269 / `464717ac96e9` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/execution/order_client.py` → `libs/execution/order_client.py` | 2700 / `286566f70059` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/execution/order_lifecycle_policy.py` → `libs/execution/order_lifecycle_policy.py` | 5661 / `cc5eaa82eed5` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/execution/readiness_evidence.py` → `libs/execution/readiness_evidence.py` | 33989 / `1d637eaee70e` | 상기 함수 이동·경계 유지 |
| `libs/execution/recent_order_guard.py` → `libs/execution/recent_order_guard.py` | 6470 / `1fa5898084b1` | KEEP_IF: 역할·위치·길이 정당하면 통과 |

## 3. C03 전달·개발자 구현·수용

- **C03만** 위 설계 문서/소스를 읽고 목적지 충돌을 확인한 후 정확한 SOURCE·TARGET·fixture를 C01/C02 **본문에 직접 기재**. A/B는 이 RF 문서를 추가로 읽지 않는다.
- 적절한 KEEP는 한 줄 이유+blob으로 즉시 PASS, 반복 테스트/peer 0. 이동은 계산 몸체 원본에서 실제 제거하고 새로운 Owner에 구현, public wrapper 유지; 소비자·부작용 유지.
- 변경 함수만 normal fake before/after test 1회, git body diff 및 target blob/원본 LOC 보고. 개발자는 자기 브랜치 code/test만 push, C04 묶음 통합/C05 기존 DONE 보존·TARGET_GAP 분리.
