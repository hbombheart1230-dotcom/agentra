# RF-073 — 코드 구조/함수 재배치 설계 (T09)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-073.md` blob `019698a0c5590c4356e73b95f67a4c1d0d5249dd`.
**구현 담당:** **Claude A**, 상대 **Codex B**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 21개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `tests/apps/api/artifact_fixtures.py` → `tests/apps/api/artifact_fixtures.py` | 15729 | `884b49d8bae3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/apps/api/conftest.py` → `tests/apps/api/conftest.py` | 716 | `9c51380616aa` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/apps/api/test_anomalies.py` → `tests/apps/api/test_anomalies.py` | 3548 | `b6140320df87` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/apps/api/test_bounded_reader.py` → `tests/apps/api/test_bounded_reader.py` | 1018 | `1db8496be368` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/apps/api/test_health.py` → `tests/apps/api/test_health.py` | 1603 | `39d76e837bb6` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/apps/api/test_isolation.py` → `tests/apps/api/test_isolation.py` | 6058 | `e22d24d1d215` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/apps/api/test_jsonl_tail.py` → `tests/apps/api/test_jsonl_tail.py` | 582 | `ed3624528eac` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/apps/api/test_llm_operations.py` → `tests/apps/api/test_llm_operations.py` | 4128 | `72bb736b046c` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/apps/api/test_market.py` → `tests/apps/api/test_market.py` | 1730 | `24dc205fca0d` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/apps/api/test_operations.py` → `tests/apps/api/test_operations.py` | 3161 | `7c666af5d0d6` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/apps/api/test_opportunities.py` → `tests/apps/api/test_opportunities.py` | 1851 | `1307eeece7c3` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/apps/api/test_patch_notes.py` → `tests/apps/api/test_patch_notes.py` | 3477 | `ff46628735f4` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/apps/api/test_paths.py` → `tests/apps/api/test_paths.py` | 1640 | `81f3aaf374cd` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/apps/api/test_performance.py` → `tests/apps/api/test_performance.py` | 4336 | `4366dda5b110` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/apps/api/test_portfolio_overview.py` → `tests/apps/api/test_portfolio_overview.py` | 3291 | `7dc62d8fc461` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/apps/api/test_public_profile.py` → `tests/apps/api/test_public_profile.py` | 3781 | `f10f4ac498d4` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/apps/api/test_runtime_status.py` → `tests/apps/api/test_runtime_status.py` | 12614 | `1a8d5f687caf` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/apps/api/test_strategies.py` → `tests/apps/api/test_strategies.py` | 1685 | `a82c291d04a6` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/apps/api/test_trade_reports.py` → `tests/apps/api/test_trade_reports.py` | 1762 | `e0eb3fc1f65d` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/apps/api/test_trades.py` → `tests/apps/api/test_trades.py` | 4569 | `3b1e14fb228f` | KEEP_IF: 테스트 단일 소유·오라클 불변 |
| `tests/deploy/test_m7_compose_contract.py` → `tests/deploy/test_m7_compose_contract.py` | 5464 | `a803109895dd` | KEEP_IF: 테스트 단일 소유·오라클 불변 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
