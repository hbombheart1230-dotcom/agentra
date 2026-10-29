# RF-007 — 코드 구조/함수 재배치 설계 (T02)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/05_DONE/CODEX_B/RF-007.md` blob `5f8d94c494be5de967590356ea7ad4b6bae3b99a`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 38개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `apps/web/.gitignore` → `apps/web/.gitignore` | 34 | `f4e2c6d6b88c` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/e2e/public-profile.mjs` → `apps/web/e2e/public-profile.mjs` | 1830 | `20a283d85401` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/e2e/smoke.mjs` → `apps/web/e2e/smoke.mjs` | 5689 | `e7d411e8d879` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/index.html` → `apps/web/index.html` | 481 | `36cc854c56ae` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/package-lock.json` → `apps/web/package-lock.json` | 96004 | `e83055e3dd3f` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/package.json` → `apps/web/package.json` | 803 | `fcbb9ef01d61` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/app/App.tsx` → `apps/web/src/app/App.tsx` | 3081 | `099f7a5bf969` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/app/navigation.tsx` → `apps/web/src/app/navigation.tsx` | 1401 | `ac1614775c9b` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/main.tsx` → `apps/web/src/main.tsx` | 374 | `f93bf298d48c` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/shared/api/client.test.ts` → `apps/web/src/shared/api/client.test.ts` | 343 | `3cf391fb3b78` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/shared/api/client.ts` → `apps/web/src/shared/api/client.ts` | 1147 | `4ab910659d13` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/shared/api/types.ts` → `apps/web/src/shared/api/types.ts` | 2156 | `53f3ec96e226` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/shared/api/useApi.ts` → `apps/web/src/shared/api/useApi.ts` | 1189 | `b3d63ea0426f` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/shared/components/DataState.tsx` → `apps/web/src/shared/components/DataState.tsx` | 984 | `7b657b03131c` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/shared/components/DateRange.tsx` → `apps/web/src/shared/components/DateRange.tsx` | 534 | `0365018eb094` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/shared/components/MetricStrip.tsx` → `apps/web/src/shared/components/MetricStrip.tsx` | 642 | `c754f9057a05` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/shared/components/PageHeader.tsx` → `apps/web/src/shared/components/PageHeader.tsx` | 407 | `27807989ec98` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/shared/components/Panel.tsx` → `apps/web/src/shared/components/Panel.tsx` | 491 | `08d325a3c036` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/shared/components/StatusPill.tsx` → `apps/web/src/shared/components/StatusPill.tsx` | 409 | `d99ca88a9e52` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/shared/formatters/dates.ts` → `apps/web/src/shared/formatters/dates.ts` | 1043 | `da9132b7dbf4` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/shared/formatters/numbers.test.ts` → `apps/web/src/shared/formatters/numbers.test.ts` | 535 | `4ae48bccb471` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/shared/formatters/numbers.ts` → `apps/web/src/shared/formatters/numbers.ts` | 1011 | `7832cdfe53ac` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/shared/layout/AppShell.tsx` → `apps/web/src/shared/layout/AppShell.tsx` | 3428 | `332e42d83647` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/shared/tables/SortableHeaderRow.tsx` → `apps/web/src/shared/tables/SortableHeaderRow.tsx` | 1240 | `3416b1b101a7` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/shared/tables/sorting.test.ts` → `apps/web/src/shared/tables/sorting.test.ts` | 1223 | `141c1926d28c` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/shared/tables/sorting.ts` → `apps/web/src/shared/tables/sorting.ts` | 1715 | `77eecbf3dfbd` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/shared/tables/useSortableRows.ts` → `apps/web/src/shared/tables/useSortableRows.ts` | 585 | `b49c5e2fdd87` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/styles/base.css` → `apps/web/src/styles/base.css` | 540 | `bda3c78c5caa` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/styles/components.css` → `apps/web/src/styles/components.css` | 25605 | `7a7500ad09c9` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/styles/layout.css` → `apps/web/src/styles/layout.css` | 3266 | `62e5d3812a0a` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/styles/responsive.css` → `apps/web/src/styles/responsive.css` | 4667 | `109baa1ade91` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/styles/tokens.css` → `apps/web/src/styles/tokens.css` | 658 | `2dd0826e6c22` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/vite-env.d.ts` → `apps/web/src/vite-env.d.ts` | 38 | `11f02fe2a006` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/tsconfig.app.json` → `apps/web/tsconfig.app.json` | 507 | `e935337c4f40` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/tsconfig.json` → `apps/web/tsconfig.json` | 119 | `1ffef600d959` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/tsconfig.node.json` → `apps/web/tsconfig.node.json` | 188 | `ecf159795612` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/vite.config.ts` → `apps/web/vite.config.ts` | 348 | `e07ed312cf9b` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/vitest.config.ts` → `apps/web/vitest.config.ts` | 156 | `c1433e6ef383` | KEEP_IF: 리소스·데이터 소비자 경로 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
