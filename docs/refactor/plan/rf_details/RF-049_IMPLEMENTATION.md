# RF-049 — 실제 소스 함수→목표 Owner 설계

**기준:** `integration/p1.5@ef0fa5531222d7ad34737712ac56b09c0da80e4b`; 원본 RF `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-049.md`; 담당 **Claude A 단독**, 상대는 read-only. 5 경로.

## 1. 실제 def 분석 / 새 파일명·함수명

Git blob `faabbc131114bd8e1fb05cf7d8ccb1d15292b703`, SOURCE `libs/kiwoom/kiwoom_token_client.py`, 165줄 확인.

| 현재 SOURCE::함수 | 줄수/행 | TARGET::함수 | 동작 |
|---|---:|---|---|
| `libs/kiwoom/kiwoom_token_client.py::_refresh_token` | L101–150 / 50 | `libs/kiwoom/kiwoom_token_client.py::_refresh_token` | KEEP_EFFECT_OR_CLASS; pure 후보 |
| `libs/kiwoom/kiwoom_token_client.py::ensure_token` | L53–100 / 48 | `libs/kiwoom/kiwoom_token_client.py::ensure_token` | KEEP_EFFECT_OR_CLASS; pure 후보 |

- **_refresh_token:** 원본 50행 → `libs/kiwoom/kiwoom_token_client.py::_refresh_token`; 원래 효과/클래스 경계 보존, 순수 계산만 추출하거나 KEEP_OK. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.
- **ensure_token:** 원본 48행 → `libs/kiwoom/kiwoom_token_client.py::ensure_token`; 원래 효과/클래스 경계 보존, 순수 계산만 추출하거나 KEEP_OK. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.

## 2. 소유 전체 파일별 SOURCE → TARGET / 사유

| 파일(기존/기본 목표) | bytes / blob | 처리 |
|---|---|---|
| `libs/kiwoom/__init__.py` → `libs/kiwoom/__init__.py` | 0 / `e69de29bb2d1` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/kiwoom/kiwoom_account_client.py` → `libs/kiwoom/kiwoom_account_client.py` | 3337 / `1723430c1bad` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/kiwoom/kiwoom_token_client.py` → `libs/kiwoom/kiwoom_token_client.py` | 6610 / `faabbc131114` | 상기 함수 이동·경계 유지 |
| `libs/kiwoom/token_cache.py` → `libs/kiwoom/token_cache.py` | 2793 / `01b5ab0fd201` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/kiwoom/token_refresh_guard.py` → `libs/kiwoom/token_refresh_guard.py` | 2834 / `01e3adbd3607` | KEEP_IF: 역할·위치·길이 정당하면 통과 |

## 3. C03 전달·개발자 구현·수용

- **C03만** 위 설계 문서/소스를 읽고 목적지 충돌을 확인한 후 정확한 SOURCE·TARGET·fixture를 C01/C02 **본문에 직접 기재**. A/B는 이 RF 문서를 추가로 읽지 않는다.
- 적절한 KEEP는 한 줄 이유+blob으로 즉시 PASS, 반복 테스트/peer 0. 이동은 계산 몸체 원본에서 실제 제거하고 새로운 Owner에 구현, public wrapper 유지; 소비자·부작용 유지.
- 변경 함수만 normal fake before/after test 1회, git body diff 및 target blob/원본 LOC 보고. 개발자는 자기 브랜치 code/test만 push, C04 묶음 통합/C05 기존 DONE 보존·TARGET_GAP 분리.
