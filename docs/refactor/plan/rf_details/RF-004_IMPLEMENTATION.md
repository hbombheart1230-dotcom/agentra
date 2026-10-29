# RF-004 — 코드 구조/함수 재배치 설계 (T02)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/05_DONE/CODEX_B/RF-004.md` blob `e9028695fbd704209c6a03a907666d5ea3d304d6`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 35개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `apps/api/domain/__init__.py` → `apps/api/domain/__init__.py` | 62 | `b2710a7510da` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/domain/anomalies/__init__.py` → `apps/api/domain/anomalies/__init__.py` | 510 | `c0ac41296223` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/domain/anomalies/factory.py` → `apps/api/domain/anomalies/factory.py` | 1036 | `ce07557a24d1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/domain/anomalies/freshness_rules.py` → `apps/api/domain/anomalies/freshness_rules.py` | 2398 | `56a5bf1d41fe` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/domain/anomalies/integrity_rules.py` → `apps/api/domain/anomalies/integrity_rules.py` | 1055 | `6c75969aba9b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/domain/anomalies/opportunity_rules.py` → `apps/api/domain/anomalies/opportunity_rules.py` | 2232 | `3e3be09910e9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/domain/anomalies/policy.py` → `apps/api/domain/anomalies/policy.py` | 485 | `2597303bf7ad` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/domain/anomalies/trade_cost_rule.py` → `apps/api/domain/anomalies/trade_cost_rule.py` | 1668 | `c228533ff4b2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/domain/anomalies/trade_exit_rule.py` → `apps/api/domain/anomalies/trade_exit_rule.py` | 1700 | `057a3af369c1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/domain/anomalies/trade_rules.py` → `apps/api/domain/anomalies/trade_rules.py` | 699 | `eecfeed9bea4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/domain/anomalies/trade_sequence_rule.py` → `apps/api/domain/anomalies/trade_sequence_rule.py` | 1932 | `34bce956ddf0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/domain/anomaly_rules.py` → `apps/api/domain/anomaly_rules.py` | 487 | `8c71098c4cf5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/domain/llm_operations_projection.py` → `apps/api/domain/llm_operations_projection.py` | 6273 | `a4ee2720750a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/domain/llm_role_catalog.py` → `apps/api/domain/llm_role_catalog.py` | 1491 | `9429746c0397` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/domain/performance_math.py` → `apps/api/domain/performance_math.py` | 2420 | `0541d5652139` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/domain/runtime_status_projection.py` → `apps/api/domain/runtime_status_projection.py` | 10278 | `8a685f25e408` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/domain/scheduled_intelligence_projection.py` → `apps/api/domain/scheduled_intelligence_projection.py` | 6048 | `a9ac9b151f9d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/domain/watchdog_history_projection.py` → `apps/api/domain/watchdog_history_projection.py` | 3882 | `467c5052c159` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/models/__init__.py` → `apps/api/models/__init__.py` | 991 | `6a4303fb770c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/models/anomalies.py` → `apps/api/models/anomalies.py` | 1762 | `fc4f8c7c6ee8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/models/common.py` → `apps/api/models/common.py` | 1078 | `ee7cf13bf2fd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/models/health.py` → `apps/api/models/health.py` | 646 | `ca070dfcfb6c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/models/llm_operations.py` → `apps/api/models/llm_operations.py` | 2837 | `f423b30f7bd0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/models/market.py` → `apps/api/models/market.py` | 1710 | `40b6ac25b821` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/models/operations.py` → `apps/api/models/operations.py` | 1325 | `009237a56572` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/models/opportunities.py` → `apps/api/models/opportunities.py` | 3028 | `092ca066739e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/models/overview.py` → `apps/api/models/overview.py` | 545 | `1b77ee4cded8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/models/patch_notes.py` → `apps/api/models/patch_notes.py` | 1148 | `c16aca2fe040` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/models/performance.py` → `apps/api/models/performance.py` | 1782 | `516c31df33c0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/models/portfolio.py` → `apps/api/models/portfolio.py` | 1021 | `14157c104a0a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/models/profile.py` → `apps/api/models/profile.py` | 484 | `fc9ed38da990` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/models/reports.py` → `apps/api/models/reports.py` | 962 | `73ffdcb46ace` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/models/runtime_status.py` → `apps/api/models/runtime_status.py` | 4645 | `e630d0fda79b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/models/strategies.py` → `apps/api/models/strategies.py` | 1301 | `6dc7c6bdb61e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/models/trades.py` → `apps/api/models/trades.py` | 2914 | `5337e0a3ddfc` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
