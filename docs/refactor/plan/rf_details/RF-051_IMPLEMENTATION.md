# RF-051 — 실제 소스 함수→목표 Owner 설계

**기준:** `integration/p1.5@ef0fa5531222d7ad34737712ac56b09c0da80e4b`; 원본 RF `docs/refactor/plan/queue/05_DONE/CLAUDE_A/RF-051.md`; 담당 **Claude A 단독**, 상대는 read-only. 15 경로.

## 1. 실제 def 분석 / 새 파일명·함수명

Git blob `8523d4ca9b36efca8e060040738a74d5947754c5`, SOURCE `libs/market/global_sentiment.py`, 834줄 확인.

| 현재 SOURCE::함수 | 줄수/행 | TARGET::함수 | 동작 |
|---|---:|---|---|
| `libs/market/global_sentiment.py::compute_global_sentiment_signal` | L666–832 / 167 | `libs/market/global_sentiment_compute_global_sentiment_signal.py::compute_global_sentiment_signal` | MOVE_BODY; pure 후보 |
| `libs/market/global_sentiment.py::_fetch_inputs` | L467–506 / 40 | `libs/market/global_sentiment_fetch_inputs.py::_fetch_inputs` | MOVE_BODY; pure 후보 |
| `libs/market/global_sentiment.py::_normalize_korea_index_packet` | L114–151 / 38 | `libs/market/global_sentiment_normalize_korea_index_packet.py::_normalize_korea_index_packet` | MOVE_BODY; pure 후보 |
| `libs/market/global_sentiment.py::_indicator_from_korea_index` | L250–279 / 30 | `libs/market/global_sentiment_indicator_from_korea_index.py::_indicator_from_korea_index` | MOVE_BODY; pure 후보 |
| `libs/market/global_sentiment.py::_indicator_from_override` | L280–309 / 30 | `libs/market/global_sentiment_indicator_from_override.py::_indicator_from_override` | MOVE_BODY; pure 후보 |
| `libs/market/global_sentiment.py::_fetch_last2_closes_yfinance` | L172–192 / 21 | `libs/market/global_sentiment_fetch_last2_closes_yfinance.py::_fetch_last2_closes_yfinance` | MOVE_BODY; pure 후보 |
| `libs/market/global_sentiment.py::_fetch_korea_index_inputs` | L152–171 / 20 | `libs/market/global_sentiment.py::_fetch_korea_index_inputs` | KEEP_EFFECT_OR_CLASS; ENV |
| `libs/market/global_sentiment.py::_write_macro_indicator_log` | L447–466 / 20 | `libs/market/global_sentiment.py::_write_macro_indicator_log` | KEEP_EFFECT_OR_CLASS; IO, ENV |

- **compute_global_sentiment_signal:** 원본 167행 → `libs/market/global_sentiment_compute_global_sentiment_signal.py::compute_global_sentiment_signal`; 실제 계산 몸체 이전 및 원명 thin wrapper, 기존 같은 Owner가 있으면 재사용. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.
- **_fetch_inputs:** 원본 40행 → `libs/market/global_sentiment_fetch_inputs.py::_fetch_inputs`; 실제 계산 몸체 이전 및 원명 thin wrapper, 기존 같은 Owner가 있으면 재사용. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.
- **_normalize_korea_index_packet:** 원본 38행 → `libs/market/global_sentiment_normalize_korea_index_packet.py::_normalize_korea_index_packet`; 실제 계산 몸체 이전 및 원명 thin wrapper, 기존 같은 Owner가 있으면 재사용. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.
- **_indicator_from_korea_index:** 원본 30행 → `libs/market/global_sentiment_indicator_from_korea_index.py::_indicator_from_korea_index`; 실제 계산 몸체 이전 및 원명 thin wrapper, 기존 같은 Owner가 있으면 재사용. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.
- **_indicator_from_override:** 원본 30행 → `libs/market/global_sentiment_indicator_from_override.py::_indicator_from_override`; 실제 계산 몸체 이전 및 원명 thin wrapper, 기존 같은 Owner가 있으면 재사용. old/new fake fixture·예외·key 순서·monkeypatch 일치 검사, 변경시 normal targeted exit0 1회.

## 2. 소유 전체 파일별 SOURCE → TARGET / 사유

| 파일(기존/기본 목표) | bytes / blob | 처리 |
|---|---|---|
| `libs/market/global_sentiment.py` → `libs/market/global_sentiment.py` | 32052 / `8523d4ca9b36` | 상기 함수 이동·경계 유지 |
| `libs/market/korea_bond_yields.py` → `libs/market/korea_bond_yields.py` | 5187 / `1e996cbfbb49` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/market/korea_index_sanity.py` → `libs/market/korea_index_sanity.py` | 3384 / `5e4d3c0fe5d7` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/market/opening_macro_snapshot_collector.py` → `libs/market/opening_macro_snapshot_collector.py` | 6763 / `a401a7eaf733` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/market/preopen_macro_snapshot.py` → `libs/market/preopen_macro_snapshot.py` | 1728 / `4c52deac5574` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/market/q10_index_observation_collector.py` → `libs/market/q10_index_observation_collector.py` | 28533 / `cbd04a11a584` | 긴 Python: Owner 분리 후보, 실제 함수 확인 후 결정 |
| `libs/market/q10_observation_integrity.py` → `libs/market/q10_observation_integrity.py` | 2823 / `04f5f400131a` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `libs/market/yfinance_support.py` → `libs/market/yfinance_support.py` | 2630 / `03edd32ac579` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `tests/test_rf051_libs_market_bond_sanity_contract.py` → `tests/test_rf051_libs_market_bond_sanity_contract.py` | 0 / `BASELINE` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `tests/test_rf051_libs_market_global_sentiment_residual.py` → `tests/test_rf051_libs_market_global_sentiment_residual.py` | 0 / `BASELINE` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `tests/test_rf051_libs_market_global_sentiment_signal_branches.py` → `tests/test_rf051_libs_market_global_sentiment_signal_branches.py` | 0 / `BASELINE` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `tests/test_rf051_libs_market_q10_collector_residual_contract.py` → `tests/test_rf051_libs_market_q10_collector_residual_contract.py` | 0 / `BASELINE` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `tests/test_rf051_libs_market_q10_integrity_residual.py` → `tests/test_rf051_libs_market_q10_integrity_residual.py` | 0 / `BASELINE` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `tests/test_rf051_market_import_surface_guard.py` → `tests/test_rf051_market_import_surface_guard.py` | 0 / `BASELINE` | KEEP_IF: 역할·위치·길이 정당하면 통과 |
| `tests/test_rf051_market_owner_action_inventory.py` → `tests/test_rf051_market_owner_action_inventory.py` | 0 / `BASELINE` | KEEP_IF: 역할·위치·길이 정당하면 통과 |

## 3. C03 전달·개발자 구현·수용

- **C03만** 위 설계 문서/소스를 읽고 목적지 충돌을 확인한 후 정확한 SOURCE·TARGET·fixture를 C01/C02 **본문에 직접 기재**. A/B는 이 RF 문서를 추가로 읽지 않는다.
- 적절한 KEEP는 한 줄 이유+blob으로 즉시 PASS, 반복 테스트/peer 0. 이동은 계산 몸체 원본에서 실제 제거하고 새로운 Owner에 구현, public wrapper 유지; 소비자·부작용 유지.
- 변경 함수만 normal fake before/after test 1회, git body diff 및 target blob/원본 LOC 보고. 개발자는 자기 브랜치 code/test만 push, C04 묶음 통합/C05 기존 DONE 보존·TARGET_GAP 분리.
