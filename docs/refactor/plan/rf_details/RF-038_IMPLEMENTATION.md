# RF-038 — 코드 구조/함수 재배치 설계 (T00/V3)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-038.md` blob `65551bc1ec2ee87fa228cd2737d5316a9bc503bc`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 39개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `libs/research/conditional_alpha_diagnosis/analysis.py` | 24071 | `371b7d8eaca630fdc68a00826cdf3e4250be8c17` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `libs/research/conditional_alpha_diagnosis/analysis_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `libs/research/conditional_alpha_diagnosis/__init__.py` → `libs/research/conditional_alpha_diagnosis/__init__.py` | 101 | `cca8a680585c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/conditional_alpha_diagnosis/analysis.py` → `libs/research/conditional_alpha_diagnosis/analysis.py` | 24071 | `371b7d8eaca6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/conditional_alpha_diagnosis/attribution.py` → `libs/research/conditional_alpha_diagnosis/attribution.py` | 3854 | `37064038be0b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/conditional_alpha_diagnosis/cohorts.py` → `libs/research/conditional_alpha_diagnosis/cohorts.py` | 2212 | `0e536588f20f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/conditional_alpha_diagnosis/contrasts.py` → `libs/research/conditional_alpha_diagnosis/contrasts.py` | 4262 | `569ad7e565a7` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/conditional_alpha_diagnosis/horizons.py` → `libs/research/conditional_alpha_diagnosis/horizons.py` | 2785 | `11815294d747` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/conditional_alpha_diagnosis/loaders.py` → `libs/research/conditional_alpha_diagnosis/loaders.py` | 4357 | `adb7e6228f07` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/conditional_alpha_diagnosis/metrics.py` → `libs/research/conditional_alpha_diagnosis/metrics.py` | 2786 | `9115fbbe3024` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/conditional_alpha_diagnosis/pipeline.py` → `libs/research/conditional_alpha_diagnosis/pipeline.py` | 9084 | `57a1ada70f12` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/conditional_alpha_diagnosis/reactivation.py` → `libs/research/conditional_alpha_diagnosis/reactivation.py` | 8986 | `d2022636817c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/conditional_alpha_diagnosis/report.py` → `libs/research/conditional_alpha_diagnosis/report.py` | 7061 | `b646be40a2d9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/conditional_alpha_diagnosis/watch_replay.py` → `libs/research/conditional_alpha_diagnosis/watch_replay.py` | 2264 | `7bcccfedd612` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/integrated_trade_diagnosis/__init__.py` → `libs/research/integrated_trade_diagnosis/__init__.py` | 99 | `b240e197b92f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/integrated_trade_diagnosis/io.py` → `libs/research/integrated_trade_diagnosis/io.py` | 1511 | `91e96a7aff88` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/integrated_trade_diagnosis/lineage.py` → `libs/research/integrated_trade_diagnosis/lineage.py` | 2792 | `d4c8b2b1cc4e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/integrated_trade_diagnosis/metrics.py` → `libs/research/integrated_trade_diagnosis/metrics.py` | 1470 | `e869b633e43b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/integrated_trade_diagnosis/pipeline.py` → `libs/research/integrated_trade_diagnosis/pipeline.py` | 7481 | `52eefa1fd001` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/integrated_trade_diagnosis/policies.py` → `libs/research/integrated_trade_diagnosis/policies.py` | 6837 | `65d79fe0cd81` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/integrated_trade_diagnosis/prospective.py` → `libs/research/integrated_trade_diagnosis/prospective.py` | 3798 | `c5f800b01afb` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/integrated_trade_diagnosis/read_model.py` → `libs/research/integrated_trade_diagnosis/read_model.py` | 4816 | `c05a7d17750f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/integrated_trade_diagnosis/report.py` → `libs/research/integrated_trade_diagnosis/report.py` | 3705 | `dcba3b59c843` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/integrated_trade_diagnosis/validation.py` → `libs/research/integrated_trade_diagnosis/validation.py` | 3527 | `e2eebc8836e4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opportunity_engine/__init__.py` → `libs/research/opportunity_engine/__init__.py` | 108 | `e7c472f9d7c2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opportunity_engine/contracts.py` → `libs/research/opportunity_engine/contracts.py` | 1276 | `ccbf0d94d23f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opportunity_engine/data_provider.py` → `libs/research/opportunity_engine/data_provider.py` | 6298 | `745662409903` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opportunity_engine/engine.py` → `libs/research/opportunity_engine/engine.py` | 2644 | `139d3ace0712` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opportunity_engine/features.py` → `libs/research/opportunity_engine/features.py` | 9859 | `d0239fd6884c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opportunity_engine/pipeline.py` → `libs/research/opportunity_engine/pipeline.py` | 8110 | `ab0435b69a48` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opportunity_engine/report.py` → `libs/research/opportunity_engine/report.py` | 6113 | `a57bcc4367b6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opportunity_engine/simulator.py` → `libs/research/opportunity_engine/simulator.py` | 10158 | `14f4e60e6354` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/post_reclaim_alpha/__init__.py` → `libs/research/post_reclaim_alpha/__init__.py` | 105 | `9abf19fd9d1c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/post_reclaim_alpha/contracts.py` → `libs/research/post_reclaim_alpha/contracts.py` | 1636 | `14f48a764832` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/post_reclaim_alpha/episodes.py` → `libs/research/post_reclaim_alpha/episodes.py` | 5811 | `3f4bc4a10806` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/post_reclaim_alpha/evaluator.py` → `libs/research/post_reclaim_alpha/evaluator.py` | 13753 | `41cf026c0484` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/post_reclaim_alpha/executable_policy.py` → `libs/research/post_reclaim_alpha/executable_policy.py` | 9985 | `b0057466f325` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/post_reclaim_alpha/executable_report.py` → `libs/research/post_reclaim_alpha/executable_report.py` | 4161 | `a01f1ff46959` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/post_reclaim_alpha/kiwoom_history.py` → `libs/research/post_reclaim_alpha/kiwoom_history.py` | 15157 | `786324dac8d9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/post_reclaim_alpha/pipeline.py` → `libs/research/post_reclaim_alpha/pipeline.py` | 5230 | `ad01b4d021a6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/post_reclaim_alpha/report.py` → `libs/research/post_reclaim_alpha/report.py` | 4374 | `dd7be117a48a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
