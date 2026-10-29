# RF-038 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@49cd60c4744c23ca556dbb633b197dbce4810d53`, RF 원본 `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-038.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Codex B 구현 / Claude A read-only. 소유 39개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/research/conditional_alpha_diagnosis/analysis.py` blob `371b7d8eaca630fdc68a00826cdf3e4250be8c17` (542 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 본문 행수·주의 |
|---|---|---|---|
| `libs/research/conditional_alpha_diagnosis/analysis.py::horizon_cross_sections` L311-369 | MOVE_BODY | `libs/research/conditional_alpha_diagnosis/analysis_horizon_cross_sections.py::horizon_cross_sections` | 59행 · 순수 후보 |
| `libs/research/conditional_alpha_diagnosis/analysis.py::predefined_opening_screens` L177-226 | MOVE_BODY | `libs/research/conditional_alpha_diagnosis/analysis_predefined_opening_screens.py::predefined_opening_screens` | 50행 · 순수 후보 |
| `libs/research/conditional_alpha_diagnosis/analysis.py::precursor_profiles` L437-484 | MOVE_BODY | `libs/research/conditional_alpha_diagnosis/analysis_precursor_profiles.py::precursor_profiles` | 48행 · 순수 후보 |
| `libs/research/conditional_alpha_diagnosis/analysis.py::opening_archetype_analysis` L502-538 | MOVE_BODY | `libs/research/conditional_alpha_diagnosis/analysis_opening_archetype_analysis.py::opening_archetype_analysis` | 37행 · 순수 후보 |
| `libs/research/conditional_alpha_diagnosis/analysis.py::actual_live_cost_cross_sections` L370-400 | MOVE_BODY | `libs/research/conditional_alpha_diagnosis/analysis_actual_live_cost_cross_sections.py::actual_live_cost_cross_sections` | 31행 · 순수 후보 |
| `libs/research/conditional_alpha_diagnosis/analysis.py::research_candidates` L150-176 | MOVE_BODY | `libs/research/conditional_alpha_diagnosis/analysis_research_candidates.py::research_candidates` | 27행 · 순수 후보 |
| `libs/research/conditional_alpha_diagnosis/analysis.py::_group_summary` L83-106 | MOVE_BODY | `libs/research/conditional_alpha_diagnosis/analysis_group_summary.py::_group_summary` | 24행 · 순수 후보 |

### horizon_cross_sections — 원본 59행
- **확인된 책임:** `libs/research/conditional_alpha_diagnosis/analysis.py` L311–369; 직접 호출 helper `_exit_class`, `_holding_bucket`, `_bucket`. 감지된 효과: 없음.
- **목표:** `libs/research/conditional_alpha_diagnosis/analysis_horizon_cross_sections.py::horizon_cross_sections` (Owner Codex B, RF-038). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### predefined_opening_screens — 원본 50행
- **확인된 책임:** `libs/research/conditional_alpha_diagnosis/analysis.py` L177–226; 직접 호출 helper `_group_summary`. 감지된 효과: 없음.
- **목표:** `libs/research/conditional_alpha_diagnosis/analysis_predefined_opening_screens.py::predefined_opening_screens` (Owner Codex B, RF-038). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### precursor_profiles — 원본 48행
- **확인된 책임:** `libs/research/conditional_alpha_diagnosis/analysis.py` L437–484; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/research/conditional_alpha_diagnosis/analysis_precursor_profiles.py::precursor_profiles` (Owner Codex B, RF-038). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### opening_archetype_analysis — 원본 37행
- **확인된 책임:** `libs/research/conditional_alpha_diagnosis/analysis.py` L502–538; 직접 호출 helper `_archetype`, `_mean`. 감지된 효과: 없음.
- **목표:** `libs/research/conditional_alpha_diagnosis/analysis_opening_archetype_analysis.py::opening_archetype_analysis` (Owner Codex B, RF-038). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### actual_live_cost_cross_sections — 원본 31행
- **확인된 책임:** `libs/research/conditional_alpha_diagnosis/analysis.py` L370–400; 직접 호출 helper `_exit_class`, `_holding_bucket`, `_bucket`. 감지된 효과: 없음.
- **목표:** `libs/research/conditional_alpha_diagnosis/analysis_actual_live_cost_cross_sections.py::actual_live_cost_cross_sections` (Owner Codex B, RF-038). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### research_candidates — 원본 27행
- **확인된 책임:** `libs/research/conditional_alpha_diagnosis/analysis.py` L150–176; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/research/conditional_alpha_diagnosis/analysis_research_candidates.py::research_candidates` (Owner Codex B, RF-038). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/research/conditional_alpha_diagnosis/__init__.py` | `libs/research/conditional_alpha_diagnosis/__init__.py` | `cca8a680585c` / 101B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/conditional_alpha_diagnosis/analysis.py` | `libs/research/conditional_alpha_diagnosis/analysis.py` | `371b7d8eaca6` / 24071B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/research/conditional_alpha_diagnosis/attribution.py` | `libs/research/conditional_alpha_diagnosis/attribution.py` | `37064038be0b` / 3854B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/conditional_alpha_diagnosis/cohorts.py` | `libs/research/conditional_alpha_diagnosis/cohorts.py` | `0e536588f20f` / 2212B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/conditional_alpha_diagnosis/contrasts.py` | `libs/research/conditional_alpha_diagnosis/contrasts.py` | `569ad7e565a7` / 4262B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/conditional_alpha_diagnosis/horizons.py` | `libs/research/conditional_alpha_diagnosis/horizons.py` | `11815294d747` / 2785B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/conditional_alpha_diagnosis/loaders.py` | `libs/research/conditional_alpha_diagnosis/loaders.py` | `adb7e6228f07` / 4357B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/conditional_alpha_diagnosis/metrics.py` | `libs/research/conditional_alpha_diagnosis/metrics.py` | `9115fbbe3024` / 2786B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/conditional_alpha_diagnosis/pipeline.py` | `libs/research/conditional_alpha_diagnosis/pipeline.py` | `57a1ada70f12` / 9084B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/conditional_alpha_diagnosis/reactivation.py` | `libs/research/conditional_alpha_diagnosis/reactivation.py` | `d2022636817c` / 8986B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/conditional_alpha_diagnosis/report.py` | `libs/research/conditional_alpha_diagnosis/report.py` | `b646be40a2d9` / 7061B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/conditional_alpha_diagnosis/watch_replay.py` | `libs/research/conditional_alpha_diagnosis/watch_replay.py` | `7bcccfedd612` / 2264B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/integrated_trade_diagnosis/__init__.py` | `libs/research/integrated_trade_diagnosis/__init__.py` | `b240e197b92f` / 99B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/integrated_trade_diagnosis/io.py` | `libs/research/integrated_trade_diagnosis/io.py` | `91e96a7aff88` / 1511B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/integrated_trade_diagnosis/lineage.py` | `libs/research/integrated_trade_diagnosis/lineage.py` | `d4c8b2b1cc4e` / 2792B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/integrated_trade_diagnosis/metrics.py` | `libs/research/integrated_trade_diagnosis/metrics.py` | `e869b633e43b` / 1470B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/integrated_trade_diagnosis/pipeline.py` | `libs/research/integrated_trade_diagnosis/pipeline.py` | `52eefa1fd001` / 7481B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/integrated_trade_diagnosis/policies.py` | `libs/research/integrated_trade_diagnosis/policies.py` | `65d79fe0cd81` / 6837B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/integrated_trade_diagnosis/prospective.py` | `libs/research/integrated_trade_diagnosis/prospective.py` | `c5f800b01afb` / 3798B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/integrated_trade_diagnosis/read_model.py` | `libs/research/integrated_trade_diagnosis/read_model.py` | `c05a7d17750f` / 4816B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/integrated_trade_diagnosis/report.py` | `libs/research/integrated_trade_diagnosis/report.py` | `dcba3b59c843` / 3705B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/integrated_trade_diagnosis/validation.py` | `libs/research/integrated_trade_diagnosis/validation.py` | `e2eebc8836e4` / 3527B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opportunity_engine/__init__.py` | `libs/research/opportunity_engine/__init__.py` | `e7c472f9d7c2` / 108B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opportunity_engine/contracts.py` | `libs/research/opportunity_engine/contracts.py` | `ccbf0d94d23f` / 1276B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opportunity_engine/data_provider.py` | `libs/research/opportunity_engine/data_provider.py` | `745662409903` / 6298B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opportunity_engine/engine.py` | `libs/research/opportunity_engine/engine.py` | `139d3ace0712` / 2644B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opportunity_engine/features.py` | `libs/research/opportunity_engine/features.py` | `d0239fd6884c` / 9859B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opportunity_engine/pipeline.py` | `libs/research/opportunity_engine/pipeline.py` | `ab0435b69a48` / 8110B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opportunity_engine/report.py` | `libs/research/opportunity_engine/report.py` | `a57bcc4367b6` / 6113B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opportunity_engine/simulator.py` | `libs/research/opportunity_engine/simulator.py` | `14f4e60e6354` / 10158B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/post_reclaim_alpha/__init__.py` | `libs/research/post_reclaim_alpha/__init__.py` | `9abf19fd9d1c` / 105B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/post_reclaim_alpha/contracts.py` | `libs/research/post_reclaim_alpha/contracts.py` | `14f48a764832` / 1636B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/post_reclaim_alpha/episodes.py` | `libs/research/post_reclaim_alpha/episodes.py` | `3f4bc4a10806` / 5811B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/post_reclaim_alpha/evaluator.py` | `libs/research/post_reclaim_alpha/evaluator.py` | `41cf026c0484` / 13753B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/post_reclaim_alpha/executable_policy.py` | `libs/research/post_reclaim_alpha/executable_policy.py` | `b0057466f325` / 9985B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/post_reclaim_alpha/executable_report.py` | `libs/research/post_reclaim_alpha/executable_report.py` | `a01f1ff46959` / 4161B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/post_reclaim_alpha/kiwoom_history.py` | `libs/research/post_reclaim_alpha/kiwoom_history.py` | `786324dac8d9` / 15157B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/post_reclaim_alpha/pipeline.py` | `libs/research/post_reclaim_alpha/pipeline.py` | `ad01b4d021a6` / 5230B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/post_reclaim_alpha/report.py` | `libs/research/post_reclaim_alpha/report.py` | `dd7be117a48a` / 4374B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Codex B 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #12에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-038|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
