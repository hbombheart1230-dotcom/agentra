# RF-006 — 코드 구조/함수 재배치 설계 (T02)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/05_DONE/CODEX_B/RF-006.md` blob `d393a5e345dba7578852b68ff7e963e9aca3a06a`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 60개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `apps/web/src/features/alerts/AlertsPage.tsx` → `apps/web/src/features/alerts/AlertsPage.tsx` | 2986 | `da2efbe762a1` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/alerts/AnomalyTable.tsx` → `apps/web/src/features/alerts/AnomalyTable.tsx` | 2522 | `0e828f90cc21` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/alerts/OverviewAlerts.tsx` → `apps/web/src/features/alerts/OverviewAlerts.tsx` | 959 | `3ece4e3004b5` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/alerts/SeverityBadge.tsx` → `apps/web/src/features/alerts/SeverityBadge.tsx` | 287 | `790ec44ffd70` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/alerts/index.ts` → `apps/web/src/features/alerts/index.ts` | 51 | `bbc0bfc2066b` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/alerts/labels.ts` → `apps/web/src/features/alerts/labels.ts` | 1365 | `5df280a2bda4` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/alerts/types.ts` → `apps/web/src/features/alerts/types.ts` | 1020 | `ce9cb4401c7a` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/data-quality/DataQualityPage.tsx` → `apps/web/src/features/data-quality/DataQualityPage.tsx` | 4483 | `abc10052e799` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/llm-operations/LlmOperationsPage.tsx` → `apps/web/src/features/llm-operations/LlmOperationsPage.tsx` | 4944 | `4d4c1bbff87b` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/llm-operations/LlmStageChart.tsx` → `apps/web/src/features/llm-operations/LlmStageChart.tsx` | 1337 | `27c20564a348` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/llm-operations/ModelRouteTable.tsx` → `apps/web/src/features/llm-operations/ModelRouteTable.tsx` | 2177 | `5b881921f1e9` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/llm-operations/RecentCallTable.tsx` → `apps/web/src/features/llm-operations/RecentCallTable.tsx` | 2049 | `a7130b1f319d` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/llm-operations/StageUsageTable.tsx` → `apps/web/src/features/llm-operations/StageUsageTable.tsx` | 1802 | `db0eca0fa648` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/llm-operations/labels.ts` → `apps/web/src/features/llm-operations/labels.ts` | 1582 | `9521b5a2baa6` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/llm-operations/types.ts` → `apps/web/src/features/llm-operations/types.ts` | 1821 | `19bb63b828ea` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/market/MarketChart.tsx` → `apps/web/src/features/market/MarketChart.tsx` | 1454 | `46f3deb76ed1` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/market/MarketMetricTable.tsx` → `apps/web/src/features/market/MarketMetricTable.tsx` | 1879 | `cd401d50c75f` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/market/MarketPage.tsx` → `apps/web/src/features/market/MarketPage.tsx` | 4700 | `c083394a37f6` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/market/types.ts` → `apps/web/src/features/market/types.ts` | 1137 | `aaffc394dc73` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/operations/DecisionLineagePanel.tsx` → `apps/web/src/features/operations/DecisionLineagePanel.tsx` | 3330 | `78ef3dc77756` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/operations/OperationsAlertPanel.tsx` → `apps/web/src/features/operations/OperationsAlertPanel.tsx` | 934 | `903d7efd1e8e` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/operations/OperationsComparisonPanel.tsx` → `apps/web/src/features/operations/OperationsComparisonPanel.tsx` | 2005 | `ed71051886f4` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/operations/OperationsPage.tsx` → `apps/web/src/features/operations/OperationsPage.tsx` | 3920 | `29f511ff16fe` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/operations/OperationsTimeline.tsx` → `apps/web/src/features/operations/OperationsTimeline.tsx` | 1486 | `cf1c48ba9939` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/operations/types.ts` → `apps/web/src/features/operations/types.ts` | 993 | `d53279e93552` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/opportunities/BlockerChart.tsx` → `apps/web/src/features/opportunities/BlockerChart.tsx` | 1484 | `d68787baf386` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/opportunities/OpportunitiesPage.tsx` → `apps/web/src/features/opportunities/OpportunitiesPage.tsx` | 3584 | `32bd8f429784` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/opportunities/OpportunityOutcomeTable.tsx` → `apps/web/src/features/opportunities/OpportunityOutcomeTable.tsx` | 2864 | `92a1f63df5fc` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/opportunities/OpportunitySignalTable.tsx` → `apps/web/src/features/opportunities/OpportunitySignalTable.tsx` | 2473 | `30c3bc83d580` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/opportunities/types.ts` → `apps/web/src/features/opportunities/types.ts` | 2322 | `44a222cd02d5` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/overview/OverviewPage.tsx` → `apps/web/src/features/overview/OverviewPage.tsx` | 5364 | `dfa67199ac6d` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/overview/PositionTable.tsx` → `apps/web/src/features/overview/PositionTable.tsx` | 2009 | `89f4af65427e` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/patch-notes/PatchNotesPage.tsx` → `apps/web/src/features/patch-notes/PatchNotesPage.tsx` | 5885 | `edccbc98d9db` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/patch-notes/provenance.test.ts` → `apps/web/src/features/patch-notes/provenance.test.ts` | 1044 | `f4902aed7061` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/patch-notes/provenance.ts` → `apps/web/src/features/patch-notes/provenance.ts` | 770 | `dbb28e507b5e` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/patch-notes/types.ts` → `apps/web/src/features/patch-notes/types.ts` | 880 | `0af04fce55b0` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/performance/PerformanceChart.tsx` → `apps/web/src/features/performance/PerformanceChart.tsx` | 2193 | `1bcf2a304f52` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/performance/PerformancePage.tsx` → `apps/web/src/features/performance/PerformancePage.tsx` | 4284 | `8a33467e034e` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/performance/types.ts` → `apps/web/src/features/performance/types.ts` | 609 | `3f9b3e3c6064` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/reports/ReportsPage.tsx` → `apps/web/src/features/reports/ReportsPage.tsx` | 4281 | `0df827ab3c31` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/runtime-status/RuntimeStateBadge.tsx` → `apps/web/src/features/runtime-status/RuntimeStateBadge.tsx` | 300 | `ffdb4fd224c9` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/runtime-status/RuntimeStatusContext.tsx` → `apps/web/src/features/runtime-status/RuntimeStatusContext.tsx` | 894 | `8f9a391d8a73` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/runtime-status/RuntimeStatusPanel.tsx` → `apps/web/src/features/runtime-status/RuntimeStatusPanel.tsx` | 2212 | `13c510defe3a` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/runtime-status/ScheduledArtifactViewer.tsx` → `apps/web/src/features/runtime-status/ScheduledArtifactViewer.tsx` | 2428 | `0aa57bafab4f` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/runtime-status/ScheduledIntelligencePanel.tsx` → `apps/web/src/features/runtime-status/ScheduledIntelligencePanel.tsx` | 3462 | `a841c92e290d` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/runtime-status/WatchdogHistoryPanel.tsx` → `apps/web/src/features/runtime-status/WatchdogHistoryPanel.tsx` | 4525 | `167dc794d94c` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/runtime-status/presentation.test.ts` → `apps/web/src/features/runtime-status/presentation.test.ts` | 1130 | `ff64742134cc` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/runtime-status/presentation.ts` → `apps/web/src/features/runtime-status/presentation.ts` | 4751 | `046269c4ebb3` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/runtime-status/supervisorPresentation.test.ts` → `apps/web/src/features/runtime-status/supervisorPresentation.test.ts` | 625 | `b7dd491cfe09` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/runtime-status/types.ts` → `apps/web/src/features/runtime-status/types.ts` | 3175 | `f59abc94845d` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/strategies/StrategiesPage.tsx` → `apps/web/src/features/strategies/StrategiesPage.tsx` | 3476 | `1feed8aee558` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/strategies/StrategyChart.tsx` → `apps/web/src/features/strategies/StrategyChart.tsx` | 1483 | `364b1665d4c8` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/strategies/StrategyPerformanceTable.tsx` → `apps/web/src/features/strategies/StrategyPerformanceTable.tsx` | 2029 | `29146bf6d4e9` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/strategies/types.ts` → `apps/web/src/features/strategies/types.ts` | 869 | `a61ea5123e24` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/trades/TradeDetailPanel.tsx` → `apps/web/src/features/trades/TradeDetailPanel.tsx` | 3352 | `dc68260e1779` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/trades/TradeTable.tsx` → `apps/web/src/features/trades/TradeTable.tsx` | 2830 | `45cd0a5e5633` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/trades/TradesPage.tsx` → `apps/web/src/features/trades/TradesPage.tsx` | 2736 | `da7e12e81d2d` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/trades/tradeSort.test.ts` → `apps/web/src/features/trades/tradeSort.test.ts` | 2238 | `f5a189b1c7ac` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/trades/tradeSort.ts` → `apps/web/src/features/trades/tradeSort.ts` | 2509 | `40ae79ee2a42` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `apps/web/src/features/trades/types.ts` → `apps/web/src/features/trades/types.ts` | 2785 | `4c7e9e552054` | KEEP_IF: 리소스·데이터 소비자 경로 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
