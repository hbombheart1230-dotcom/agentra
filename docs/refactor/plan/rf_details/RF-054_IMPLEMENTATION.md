# RF-054 — 실제 소스 함수→목표 Owner 설계

**기준:** `integration/p1.5@ef0fa5531222d7ad34737712ac56b09c0da80e4b`; 원본 RF `docs/refactor/plan/queue/05_DONE/CLAUDE_A/RF-054.md`; 담당 **Claude A 단독**, 상대는 read-only. 5 경로.

## 1. 실제 def 분석 / 새 파일명·함수명

Git blob `4427c7877b9361724795d9560e54f25b0e3ac943`, SOURCE `libs/performance/strategy_memory.py`, 631줄 확인.

| 현재 SOURCE::함수 | 줄수/행 | TARGET::함수 | 동작 |
|---|---:|---|---|
| `libs/performance/strategy_memory.py::_load_reporter_analysis_digest` | L88–150 / 63 | `libs/performance/strategy_memory_load_reporter_analysis_digest.py::_load_reporter_analysis_digest` | MOVE_BODY; pure 후보 |
| `libs/performance/strategy_memory.py::_build_pattern_performance_snapshot` | L222–251 / 30 | `libs/performance/strategy_memory_build_pattern_performance_snapshot.py::_build_pattern_performance_snapshot` | MOVE_BODY; pure 후보 |
| `libs/performance/strategy_memory.py::_pattern_stats` | L163–191 / 29 | `libs/performance/strategy_memory_pattern_stats.py::_pattern_stats` | MOVE_BODY; pure 후보 |
| `libs/performance/strategy_memory.py::_extract_route_mix_digest` | L62–87 / 26 | `libs/performance/strategy_memory_extract_route_mix_digest.py::_extract_route_mix_digest` | MOVE_BODY; pure 후보 |
| `libs/performance/strategy_memory.py::_resolve_latest_usable_day` | L518–540 / 23 | `libs/performance/strategy_memory_resolve_latest_usable_day.py::_resolve_latest_usable_day` | MOVE_BODY; pure 후보 |

- **_load_reporter_analysis_digest:** 원본 63행 → `libs/performance/strategy_memory_load_reporter_analysis_digest.py::_load_reporter_analysis_digest`; 실제 계산 몸체 이전 및 원명 thin wrapper, 기존 같은 Owner가 있으면 재사용. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.
- **_build_pattern_performance_snapshot:** 원본 30행 → `libs/performance/strategy_memory_build_pattern_performance_snapshot.py::_build_pattern_performance_snapshot`; 실제 계산 몸체 이전 및 원명 thin wrapper, 기존 같은 Owner가 있으면 재사용. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.
- **_pattern_stats:** 원본 29행 → `libs/performance/strategy_memory_pattern_stats.py::_pattern_stats`; 실제 계산 몸체 이전 및 원명 thin wrapper, 기존 같은 Owner가 있으면 재사용. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.
- **_extract_route_mix_digest:** 원본 26행 → `libs/performance/strategy_memory_extract_route_mix_digest.py::_extract_route_mix_digest`; 실제 계산 몸체 이전 및 원명 thin wrapper, 기존 같은 Owner가 있으면 재사용. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.
- **_resolve_latest_usable_day:** 원본 23행 → `libs/performance/strategy_memory_resolve_latest_usable_day.py::_resolve_latest_usable_day`; 실제 계산 몸체 이전 및 원명 thin wrapper, 기존 같은 Owner가 있으면 재사용. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.

## 2. 소유 전체 파일별 SOURCE → TARGET / 사유

| 파일(기존/기본 목표) | bytes / blob | 처리 |
|---|---|---|
| `libs/performance/__init__.py` → `libs/performance/__init__.py` | 724 / `f77659764fb9` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/performance/performance_aggregator.py` → `libs/performance/performance_aggregator.py` | 18403 / `573603cfd898` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/performance/playbook_stats.py` → `libs/performance/playbook_stats.py` | 6769 / `01d36ab68dfe` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/performance/strategy_memory.py` → `libs/performance/strategy_memory.py` | 26184 / `4427c7877b93` | 상기 함수 이동·경계 유지 |
| `tests/test_rf054_058_040_final_residual_contract.py` → `tests/test_rf054_058_040_final_residual_contract.py` | 0 / `BASELINE` | KEEP_IF: 역할·위치·길이 정당하면 통과 |

## 3. C03 전달·개발자 구현·수용

- **C03만** 위 설계 문서/소스를 읽고 목적지 충돌을 확인한 후 정확한 SOURCE·TARGET·fixture를 C01/C02 **본문에 직접 기재**. A/B는 이 RF 문서를 추가로 읽지 않는다.
- 적절한 KEEP는 한 줄 이유+blob으로 즉시 PASS, 반복 테스트/peer 0. 이동은 계산 몸체 원본에서 실제 제거하고 새로운 Owner에 구현, public wrapper 유지; 소비자·부작용 유지.
- 변경 함수만 normal fake before/after test 1회, git body diff 및 target blob/원본 LOC 보고. 개발자는 자기 브랜치 code/test만 push, C04 묶음 통합/C05 기존 DONE 보존·TARGET_GAP 분리.
