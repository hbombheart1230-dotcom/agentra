# RF-005 — 코드 구조/함수 재배치 설계 (T02)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/05_DONE/CODEX_B/RF-005.md` blob `9bb7f560dc66130440574b35b67ae46a33ea43cb`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 40개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `apps/api/__init__.py` → `apps/api/__init__.py` | 123 | `222a8eceaa9b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/adapters/__init__.py` → `apps/api/adapters/__init__.py` | 81 | `c20632b6a35f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/adapters/llm_artifacts.py` → `apps/api/adapters/llm_artifacts.py` | 4303 | `62a7fed5e46d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/adapters/llm_event_tail.py` → `apps/api/adapters/llm_event_tail.py` | 3123 | `4ef7d1c40dee` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/adapters/market_snapshot.py` → `apps/api/adapters/market_snapshot.py` | 623 | `82945743b8eb` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/adapters/operator_summary.py` → `apps/api/adapters/operator_summary.py` | 1861 | `aaec22e97d7a` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/adapters/opportunity_artifacts.py` → `apps/api/adapters/opportunity_artifacts.py` | 1947 | `fccbfc4bffa6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/adapters/patch_notes.py` → `apps/api/adapters/patch_notes.py` | 925 | `28c95f4e40a8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/adapters/performance_summary.py` → `apps/api/adapters/performance_summary.py` | 2152 | `ebb10eefa05d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/adapters/runtime_status_artifacts.py` → `apps/api/adapters/runtime_status_artifacts.py` | 4450 | `34a97896a2b1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/adapters/safe_reports.py` → `apps/api/adapters/safe_reports.py` | 2778 | `682ab0126905` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/adapters/source_freshness.py` → `apps/api/adapters/source_freshness.py` | 802 | `fbb7b59f652b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/adapters/trade_bundle.py` → `apps/api/adapters/trade_bundle.py` | 2485 | `0a673c31eb18` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/config.py` → `apps/api/config.py` | 3290 | `3f61a1ba0a31` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/infrastructure/__init__.py` → `apps/api/infrastructure/__init__.py` | 651 | `03870250d3dd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/infrastructure/bounded_reader.py` → `apps/api/infrastructure/bounded_reader.py` | 961 | `213235d7a29e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/infrastructure/dates.py` → `apps/api/infrastructure/dates.py` | 818 | `466873879a10` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/infrastructure/jsonl_tail.py` → `apps/api/infrastructure/jsonl_tail.py` | 1243 | `0ecba6343d20` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/infrastructure/paths.py` → `apps/api/infrastructure/paths.py` | 973 | `6e6718dcf7c0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/infrastructure/public_middleware.py` → `apps/api/infrastructure/public_middleware.py` | 1455 | `5c1661775fd2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/infrastructure/public_sanitization.py` → `apps/api/infrastructure/public_sanitization.py` | 1342 | `5f87608f2ef1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/infrastructure/source_roots.py` → `apps/api/infrastructure/source_roots.py` | 735 | `824211ae42a8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/infrastructure/trade_index.py` → `apps/api/infrastructure/trade_index.py` | 3102 | `579667f81ab5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/main.py` → `apps/api/main.py` | 1991 | `19650cb9f2cf` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/requirements.txt` → `apps/api/requirements.txt` | 49 | `efd6330dbb44` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `apps/api/routers/__init__.py` → `apps/api/routers/__init__.py` | 42 | `fd597acf13cf` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/routers/anomalies.py` → `apps/api/routers/anomalies.py` | 552 | `c7e1bd9f65f5` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/routers/health.py` → `apps/api/routers/health.py` | 572 | `1f8cd64a17d2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/routers/llm_operations.py` → `apps/api/routers/llm_operations.py` | 593 | `888758d91656` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/routers/market.py` → `apps/api/routers/market.py` | 1242 | `81878cac5e07` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/routers/operations.py` → `apps/api/routers/operations.py` | 470 | `18a4ef7a9709` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/routers/opportunities.py` → `apps/api/routers/opportunities.py` | 1333 | `2d96c990e894` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/routers/overview.py` → `apps/api/routers/overview.py` | 709 | `0b0360caa576` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/routers/patch_notes.py` → `apps/api/routers/patch_notes.py` | 421 | `8255a782e583` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/routers/performance.py` → `apps/api/routers/performance.py` | 1416 | `0d994af2599b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/routers/portfolio.py` → `apps/api/routers/portfolio.py` | 687 | `3a16e4315a39` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/routers/profile.py` → `apps/api/routers/profile.py` | 425 | `2e0ad0133be4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/routers/runtime_status.py` → `apps/api/routers/runtime_status.py` | 2010 | `edd135e7c17d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/routers/strategies.py` → `apps/api/routers/strategies.py` | 869 | `6accc2774950` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `apps/api/routers/trades.py` → `apps/api/routers/trades.py` | 2487 | `f0fd4879c24e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
