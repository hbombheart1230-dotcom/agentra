# RF-050 — 실제 소스 함수→목표 Owner 설계

**기준:** `integration/p1.5@ef0fa5531222d7ad34737712ac56b09c0da80e4b`; 원본 RF `docs/refactor/plan/queue/03_PEER_REVIEW/CLAUDE_A/RF-050.md`; 담당 **Claude A 단독**, 상대는 read-only. 11 경로.

## 1. 실제 def 분석 / 새 파일명·함수명

Git blob `3d3ab4dae19e96f60b5a8019f8213e414db90f45`, SOURCE `libs/llm/model_catalog.py`, 388줄 확인.

| 현재 SOURCE::함수 | 줄수/행 | TARGET::함수 | 동작 |
|---|---:|---|---|
| `libs/llm/model_catalog.py::resolve_policy_llm_slot` | L273–308 / 36 | `libs/llm/model_catalog_resolve_policy_llm_slot.py::resolve_policy_llm_slot` | MOVE_BODY; pure 후보 |

- **resolve_policy_llm_slot:** 원본 36행 → `libs/llm/model_catalog_resolve_policy_llm_slot.py::resolve_policy_llm_slot`; 실제 계산 몸체 이전 및 원명 thin wrapper, 기존 같은 Owner가 있으면 재사용. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.

## 2. 소유 전체 파일별 SOURCE → TARGET / 사유

| 파일(기존/기본 목표) | bytes / blob | 처리 |
|---|---|---|
| `libs/llm/__init__.py` → `libs/llm/__init__.py` | 413 / `35d6bd0b1505` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/llm/json_response.py` → `libs/llm/json_response.py` | 2854 / `e72f5e7053b2` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/llm/llm_router.py` → `libs/llm/llm_router.py` | 5023 / `4cb5f6c449c9` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/llm/model_catalog.py` → `libs/llm/model_catalog.py` | 16048 / `3d3ab4dae19e` | 상기 함수 이동·경계 유지 |
| `libs/llm/model_catalog_store.py` → `libs/llm/model_catalog_store.py` | 13653 / `0095d766b246` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/llm/model_names.py` → `libs/llm/model_names.py` | 569 / `a5cabbd993fa` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/llm/openrouter_client.py` → `libs/llm/openrouter_client.py` | 6849 / `9a46394895ea` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/llm/router.py` → `libs/llm/router.py` | 2207 / `bff4dff444b6` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `tests/test_p15_model_catalog_malformed_cards.py` → `tests/test_p15_model_catalog_malformed_cards.py` | 0 / `BASELINE` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `tests/test_rf050_model_catalog_store_fake_http_contract.py` → `tests/test_rf050_model_catalog_store_fake_http_contract.py` | 0 / `BASELINE` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `tests/test_rf050_openrouter_client_fake_http_contract.py` → `tests/test_rf050_openrouter_client_fake_http_contract.py` | 0 / `BASELINE` | KEEP_IF: 역할·위치·길이 정당하면 통과 |

## 3. C03 전달·개발자 구현·수용

- **C03만** 위 설계 문서/소스를 읽고 목적지 충돌을 확인한 후 정확한 SOURCE·TARGET·fixture를 C01/C02 **본문에 직접 기재**. A/B는 이 RF 문서를 추가로 읽지 않는다.
- 적절한 KEEP는 한 줄 이유+blob으로 즉시 PASS, 반복 테스트/peer 0. 이동은 계산 몸체 원본에서 실제 제거하고 새로운 Owner에 구현, public wrapper 유지; 소비자·부작용 유지.
- 변경 함수만 normal fake before/after test 1회, git body diff 및 target blob/원본 LOC 보고. 개발자는 자기 브랜치 code/test만 push, C04 묶음 통합/C05 기존 DONE 보존·TARGET_GAP 분리.
