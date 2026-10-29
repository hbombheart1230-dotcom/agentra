# RF-047 — 실제 소스 함수→목표 Owner 설계

**기준:** `integration/p1.5@ef0fa5531222d7ad34737712ac56b09c0da80e4b`; 원본 RF `docs/refactor/plan/queue/05_DONE/CLAUDE_A/RF-047.md`; 담당 **Claude A 단독**, 상대는 read-only. 4 경로.

## 1. 실제 def 분석 / 새 파일명·함수명

Git blob `e584b14105858e060197c0bf2607491f33ed80db`, SOURCE `libs/diagnostics/observations.py`, 48줄 확인.

| 현재 SOURCE::함수 | 줄수/행 | TARGET::함수 | 동작 |
|---|---:|---|---|
| `libs/diagnostics/observations.py::numeric_summary` | L27–48 / 22 | `libs/diagnostics/observations_numeric_summary.py::numeric_summary` | MOVE_BODY; pure 후보 |

- **numeric_summary:** 원본 22행 → `libs/diagnostics/observations_numeric_summary.py::numeric_summary`; 실제 계산 몸체 이전 및 원명 thin wrapper, 기존 같은 Owner가 있으면 재사용. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.

## 2. 소유 전체 파일별 SOURCE → TARGET / 사유

| 파일(기존/기본 목표) | bytes / blob | 처리 |
|---|---|---|
| `libs/diagnostics/__init__.py` → `libs/diagnostics/__init__.py` | 337 / `edeb537896df` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/diagnostics/archive_inspection.py` → `libs/diagnostics/archive_inspection.py` | 561 / `299d328c5068` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/diagnostics/cli_capture.py` → `libs/diagnostics/cli_capture.py` | 572 / `adc8a5686da4` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/diagnostics/observations.py` → `libs/diagnostics/observations.py` | 1269 / `e584b1410585` | 상기 함수 이동·경계 유지 |

## 3. C03 전달·개발자 구현·수용

- **C03만** 위 설계 문서/소스를 읽고 목적지 충돌을 확인한 후 정확한 SOURCE·TARGET·fixture를 C01/C02 **본문에 직접 기재**. A/B는 이 RF 문서를 추가로 읽지 않는다.
- 적절한 KEEP는 한 줄 이유+blob으로 즉시 PASS, 반복 테스트/peer 0. 이동은 계산 몸체 원본에서 실제 제거하고 새로운 Owner에 구현, public wrapper 유지; 소비자·부작용 유지.
- 변경 함수만 normal fake before/after test 1회, git body diff 및 target blob/원본 LOC 보고. 개발자는 자기 브랜치 code/test만 push, C04 묶음 통합/C05 기존 DONE 보존·TARGET_GAP 분리.
