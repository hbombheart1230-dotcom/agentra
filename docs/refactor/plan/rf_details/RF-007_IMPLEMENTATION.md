# RF-007 — 함수·신규 모듈 매핑 상세설계 (실물 코드 대조)

**SOURCE:** `integration/p1.5@4b15aefbcaf3a31c2e9ff3710025155d13f152bd`; CSV b46bcb1f29ed3c0a133b059d690173c195c81bf9. **소유:** Codex B 구현, Claude A 읽기 전용 독립 검증. 파일 38개. 원본 RF `docs/refactor/plan/queue/05_DONE/CODEX_B/RF-007.md`.

**KEEP/PASS:** 정확한 목표 디렉터리, 단일 책임, 적절한 길이 또는 공개 호환/효과 경계라면 `KEEP_OK|path|사유 1줄|blob`으로 당회 통과. 동일 SHA 새 테스트/전수 peer 금지. 함수 MOVE만 실제 refactoring 성과.

## 1. 함수별 SOURCE → TARGET / 구현 계약

**실제 함수 분석 대상 없음:** Python 원본이 없거나 원격 본문 조회가 안 됨. 추측 함수명을 새 코드로 구현하지 않는다. 모든 소유 파일의 위치/책임·공개 소비자가 적절하면 KEEP_OK. 구조 부채 확인 시 실제 Git blob 함수명을 지정하고 그 함수만 분리.

## 2. 본 RF 전체 파일별 목표/액션

| SOURCE_PATH | TARGET_PATH | Size/Blob | KEEP/MOVE 구체 사유 |
|---|---|---|---|
| `apps/web/.gitignore` | `apps/web/.gitignore` | 34B `f4e2c6d6b88c` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/e2e/public-profile.mjs` | `apps/web/e2e/public-profile.mjs` | 1830B `20a283d85401` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/e2e/smoke.mjs` | `apps/web/e2e/smoke.mjs` | 5689B `e7d411e8d879` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/index.html` | `apps/web/index.html` | 481B `36cc854c56ae` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/package-lock.json` | `apps/web/package-lock.json` | 96004B `e83055e3dd3f` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/package.json` | `apps/web/package.json` | 803B `fcbb9ef01d61` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/app/App.tsx` | `apps/web/src/app/App.tsx` | 3081B `099f7a5bf969` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/app/navigation.tsx` | `apps/web/src/app/navigation.tsx` | 1401B `ac1614775c9b` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/main.tsx` | `apps/web/src/main.tsx` | 374B `f93bf298d48c` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/shared/api/client.test.ts` | `apps/web/src/shared/api/client.test.ts` | 343B `3cf391fb3b78` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/shared/api/client.ts` | `apps/web/src/shared/api/client.ts` | 1147B `4ab910659d13` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/shared/api/types.ts` | `apps/web/src/shared/api/types.ts` | 2156B `53f3ec96e226` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/shared/api/useApi.ts` | `apps/web/src/shared/api/useApi.ts` | 1189B `b3d63ea0426f` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/shared/components/DataState.tsx` | `apps/web/src/shared/components/DataState.tsx` | 984B `7b657b03131c` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/shared/components/DateRange.tsx` | `apps/web/src/shared/components/DateRange.tsx` | 534B `0365018eb094` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/shared/components/MetricStrip.tsx` | `apps/web/src/shared/components/MetricStrip.tsx` | 642B `c754f9057a05` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/shared/components/PageHeader.tsx` | `apps/web/src/shared/components/PageHeader.tsx` | 407B `27807989ec98` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/shared/components/Panel.tsx` | `apps/web/src/shared/components/Panel.tsx` | 491B `08d325a3c036` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/shared/components/StatusPill.tsx` | `apps/web/src/shared/components/StatusPill.tsx` | 409B `d99ca88a9e52` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/shared/formatters/dates.ts` | `apps/web/src/shared/formatters/dates.ts` | 1043B `da9132b7dbf4` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/shared/formatters/numbers.test.ts` | `apps/web/src/shared/formatters/numbers.test.ts` | 535B `4ae48bccb471` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/shared/formatters/numbers.ts` | `apps/web/src/shared/formatters/numbers.ts` | 1011B `7832cdfe53ac` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/shared/layout/AppShell.tsx` | `apps/web/src/shared/layout/AppShell.tsx` | 3428B `332e42d83647` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/shared/tables/SortableHeaderRow.tsx` | `apps/web/src/shared/tables/SortableHeaderRow.tsx` | 1240B `3416b1b101a7` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/shared/tables/sorting.test.ts` | `apps/web/src/shared/tables/sorting.test.ts` | 1223B `141c1926d28c` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/shared/tables/sorting.ts` | `apps/web/src/shared/tables/sorting.ts` | 1715B `77eecbf3dfbd` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/shared/tables/useSortableRows.ts` | `apps/web/src/shared/tables/useSortableRows.ts` | 585B `b49c5e2fdd87` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/styles/base.css` | `apps/web/src/styles/base.css` | 540B `bda3c78c5caa` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/styles/components.css` | `apps/web/src/styles/components.css` | 25605B `7a7500ad09c9` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/styles/layout.css` | `apps/web/src/styles/layout.css` | 3266B `62e5d3812a0a` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/styles/responsive.css` | `apps/web/src/styles/responsive.css` | 4667B `109baa1ade91` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/styles/tokens.css` | `apps/web/src/styles/tokens.css` | 658B `2dd0826e6c22` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/vite-env.d.ts` | `apps/web/src/vite-env.d.ts` | 38B `11f02fe2a006` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/tsconfig.app.json` | `apps/web/tsconfig.app.json` | 507B `e935337c4f40` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/tsconfig.json` | `apps/web/tsconfig.json` | 119B `1ffef600d959` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/tsconfig.node.json` | `apps/web/tsconfig.node.json` | 188B `ecf159795612` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/vite.config.ts` | `apps/web/vite.config.ts` | 348B `e07ed312cf9b` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/vitest.config.ts` | `apps/web/vitest.config.ts` | 156B `c1433e6ef383` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |

## 3. 개발자 독점 순서와 최소 검증

1. Codex B만 표의 실제 `MOVE_BODY` 순수 함수부터 source→target 본문 이동; 기존 Owner가 있으면 새 파일 중복 없이 기존 파일 사용. 하나의 경계가 막혀도 다음 독립 항목으로 진행. 다른 RF·반대 개발자 소유 파일 쓰기 금지.
2. `KEEP_OK`는 본문/위치/역할을 한 번 확인하고 한 줄 사유+Git SHA로 즉시 종결; 같은 SHA 테스트 재실행하지 않는다. 효과/broker/State·CLI와 frozen oracle은 재배치 자체를 강제하지 않는다.
3. 실제 MOVE는 원본 구현 제거·새 owner 구현·기존 thin wrapper, before/after LOC, 관련 정상 fake pytest/unittest exit0 후 B 허용 브랜치 code/test 정상 push. C04는 delta만 묶음 통합, C05는 기존 DONE 이력을 보존하되 TARGET_GAP 남았으면 구현으로 되돌린다.
4. `RF=RF-007|SOURCE_BLOB|FUNCTION_MOVES|TARGET_PATHS/BLOBS|KEEP_REASON|LOC_DELTA|TEST_CMD/EXIT|PUSH_SHA|TARGET_STATUS` 보고. 실거래/운영 DB/Guard/UEF 등 효과 금지.
