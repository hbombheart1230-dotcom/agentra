# RF-006 — 함수·신규 모듈 매핑 상세설계 (실물 코드 대조)

**SOURCE:** `integration/p1.5@4b15aefbcaf3a31c2e9ff3710025155d13f152bd`; CSV b46bcb1f29ed3c0a133b059d690173c195c81bf9. **소유:** Codex B 구현, Claude A 읽기 전용 독립 검증. 파일 60개. 원본 RF `docs/refactor/plan/queue/05_DONE/CODEX_B/RF-006.md`.

**KEEP/PASS:** 정확한 목표 디렉터리, 단일 책임, 적절한 길이 또는 공개 호환/효과 경계라면 `KEEP_OK|path|사유 1줄|blob`으로 당회 통과. 동일 SHA 새 테스트/전수 peer 금지. 함수 MOVE만 실제 refactoring 성과.

## 1. 함수별 SOURCE → TARGET / 구현 계약

**실제 함수 분석 대상 없음:** Python 원본이 없거나 원격 본문 조회가 안 됨. 추측 함수명을 새 코드로 구현하지 않는다. 모든 소유 파일의 위치/책임·공개 소비자가 적절하면 KEEP_OK. 구조 부채 확인 시 실제 Git blob 함수명을 지정하고 그 함수만 분리.

## 2. 본 RF 전체 파일별 목표/액션

| SOURCE_PATH | TARGET_PATH | Size/Blob | KEEP/MOVE 구체 사유 |
|---|---|---|---|
| `apps/web/src/features/alerts/AlertsPage.tsx` | `apps/web/src/features/alerts/AlertsPage.tsx` | 2986B `da2efbe762a1` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/alerts/AnomalyTable.tsx` | `apps/web/src/features/alerts/AnomalyTable.tsx` | 2522B `0e828f90cc21` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/alerts/OverviewAlerts.tsx` | `apps/web/src/features/alerts/OverviewAlerts.tsx` | 959B `3ece4e3004b5` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/alerts/SeverityBadge.tsx` | `apps/web/src/features/alerts/SeverityBadge.tsx` | 287B `790ec44ffd70` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/alerts/index.ts` | `apps/web/src/features/alerts/index.ts` | 51B `bbc0bfc2066b` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/alerts/labels.ts` | `apps/web/src/features/alerts/labels.ts` | 1365B `5df280a2bda4` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/alerts/types.ts` | `apps/web/src/features/alerts/types.ts` | 1020B `ce9cb4401c7a` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/data-quality/DataQualityPage.tsx` | `apps/web/src/features/data-quality/DataQualityPage.tsx` | 4483B `abc10052e799` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/llm-operations/LlmOperationsPage.tsx` | `apps/web/src/features/llm-operations/LlmOperationsPage.tsx` | 4944B `4d4c1bbff87b` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/llm-operations/LlmStageChart.tsx` | `apps/web/src/features/llm-operations/LlmStageChart.tsx` | 1337B `27c20564a348` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/llm-operations/ModelRouteTable.tsx` | `apps/web/src/features/llm-operations/ModelRouteTable.tsx` | 2177B `5b881921f1e9` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/llm-operations/RecentCallTable.tsx` | `apps/web/src/features/llm-operations/RecentCallTable.tsx` | 2049B `a7130b1f319d` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/llm-operations/StageUsageTable.tsx` | `apps/web/src/features/llm-operations/StageUsageTable.tsx` | 1802B `db0eca0fa648` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/llm-operations/labels.ts` | `apps/web/src/features/llm-operations/labels.ts` | 1582B `9521b5a2baa6` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/llm-operations/types.ts` | `apps/web/src/features/llm-operations/types.ts` | 1821B `19bb63b828ea` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/market/MarketChart.tsx` | `apps/web/src/features/market/MarketChart.tsx` | 1454B `46f3deb76ed1` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/market/MarketMetricTable.tsx` | `apps/web/src/features/market/MarketMetricTable.tsx` | 1879B `cd401d50c75f` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/market/MarketPage.tsx` | `apps/web/src/features/market/MarketPage.tsx` | 4700B `c083394a37f6` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/market/types.ts` | `apps/web/src/features/market/types.ts` | 1137B `aaffc394dc73` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/operations/DecisionLineagePanel.tsx` | `apps/web/src/features/operations/DecisionLineagePanel.tsx` | 3330B `78ef3dc77756` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/operations/OperationsAlertPanel.tsx` | `apps/web/src/features/operations/OperationsAlertPanel.tsx` | 934B `903d7efd1e8e` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/operations/OperationsComparisonPanel.tsx` | `apps/web/src/features/operations/OperationsComparisonPanel.tsx` | 2005B `ed71051886f4` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/operations/OperationsPage.tsx` | `apps/web/src/features/operations/OperationsPage.tsx` | 3920B `29f511ff16fe` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/operations/OperationsTimeline.tsx` | `apps/web/src/features/operations/OperationsTimeline.tsx` | 1486B `cf1c48ba9939` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/operations/types.ts` | `apps/web/src/features/operations/types.ts` | 993B `d53279e93552` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/opportunities/BlockerChart.tsx` | `apps/web/src/features/opportunities/BlockerChart.tsx` | 1484B `d68787baf386` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/opportunities/OpportunitiesPage.tsx` | `apps/web/src/features/opportunities/OpportunitiesPage.tsx` | 3584B `32bd8f429784` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/opportunities/OpportunityOutcomeTable.tsx` | `apps/web/src/features/opportunities/OpportunityOutcomeTable.tsx` | 2864B `92a1f63df5fc` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/opportunities/OpportunitySignalTable.tsx` | `apps/web/src/features/opportunities/OpportunitySignalTable.tsx` | 2473B `30c3bc83d580` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/opportunities/types.ts` | `apps/web/src/features/opportunities/types.ts` | 2322B `44a222cd02d5` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/overview/OverviewPage.tsx` | `apps/web/src/features/overview/OverviewPage.tsx` | 5364B `dfa67199ac6d` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/overview/PositionTable.tsx` | `apps/web/src/features/overview/PositionTable.tsx` | 2009B `89f4af65427e` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/patch-notes/PatchNotesPage.tsx` | `apps/web/src/features/patch-notes/PatchNotesPage.tsx` | 5885B `edccbc98d9db` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/patch-notes/provenance.test.ts` | `apps/web/src/features/patch-notes/provenance.test.ts` | 1044B `f4902aed7061` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/patch-notes/provenance.ts` | `apps/web/src/features/patch-notes/provenance.ts` | 770B `dbb28e507b5e` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/patch-notes/types.ts` | `apps/web/src/features/patch-notes/types.ts` | 880B `0af04fce55b0` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/performance/PerformanceChart.tsx` | `apps/web/src/features/performance/PerformanceChart.tsx` | 2193B `1bcf2a304f52` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/performance/PerformancePage.tsx` | `apps/web/src/features/performance/PerformancePage.tsx` | 4284B `8a33467e034e` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/performance/types.ts` | `apps/web/src/features/performance/types.ts` | 609B `3f9b3e3c6064` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/reports/ReportsPage.tsx` | `apps/web/src/features/reports/ReportsPage.tsx` | 4281B `0df827ab3c31` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/runtime-status/RuntimeStateBadge.tsx` | `apps/web/src/features/runtime-status/RuntimeStateBadge.tsx` | 300B `ffdb4fd224c9` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/runtime-status/RuntimeStatusContext.tsx` | `apps/web/src/features/runtime-status/RuntimeStatusContext.tsx` | 894B `8f9a391d8a73` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/runtime-status/RuntimeStatusPanel.tsx` | `apps/web/src/features/runtime-status/RuntimeStatusPanel.tsx` | 2212B `13c510defe3a` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/runtime-status/ScheduledArtifactViewer.tsx` | `apps/web/src/features/runtime-status/ScheduledArtifactViewer.tsx` | 2428B `0aa57bafab4f` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/runtime-status/ScheduledIntelligencePanel.tsx` | `apps/web/src/features/runtime-status/ScheduledIntelligencePanel.tsx` | 3462B `a841c92e290d` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/runtime-status/WatchdogHistoryPanel.tsx` | `apps/web/src/features/runtime-status/WatchdogHistoryPanel.tsx` | 4525B `167dc794d94c` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/runtime-status/presentation.test.ts` | `apps/web/src/features/runtime-status/presentation.test.ts` | 1130B `ff64742134cc` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/runtime-status/presentation.ts` | `apps/web/src/features/runtime-status/presentation.ts` | 4751B `046269c4ebb3` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/runtime-status/supervisorPresentation.test.ts` | `apps/web/src/features/runtime-status/supervisorPresentation.test.ts` | 625B `b7dd491cfe09` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/runtime-status/types.ts` | `apps/web/src/features/runtime-status/types.ts` | 3175B `f59abc94845d` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/strategies/StrategiesPage.tsx` | `apps/web/src/features/strategies/StrategiesPage.tsx` | 3476B `1feed8aee558` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/strategies/StrategyChart.tsx` | `apps/web/src/features/strategies/StrategyChart.tsx` | 1483B `364b1665d4c8` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/strategies/StrategyPerformanceTable.tsx` | `apps/web/src/features/strategies/StrategyPerformanceTable.tsx` | 2029B `29146bf6d4e9` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/strategies/types.ts` | `apps/web/src/features/strategies/types.ts` | 869B `a61ea5123e24` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/trades/TradeDetailPanel.tsx` | `apps/web/src/features/trades/TradeDetailPanel.tsx` | 3352B `dc68260e1779` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/trades/TradeTable.tsx` | `apps/web/src/features/trades/TradeTable.tsx` | 2830B `45cd0a5e5633` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/trades/TradesPage.tsx` | `apps/web/src/features/trades/TradesPage.tsx` | 2736B `da7e12e81d2d` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/trades/tradeSort.test.ts` | `apps/web/src/features/trades/tradeSort.test.ts` | 2238B `f5a189b1c7ac` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/trades/tradeSort.ts` | `apps/web/src/features/trades/tradeSort.ts` | 2509B `40ae79ee2a42` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |
| `apps/web/src/features/trades/types.ts` | `apps/web/src/features/trades/types.ts` | 2785B `4c7e9e552054` | KEEP_IF: 기존 공개 CLI/배포/자료 소비자 경로 |

## 3. 개발자 독점 순서와 최소 검증

1. Codex B만 표의 실제 `MOVE_BODY` 순수 함수부터 source→target 본문 이동; 기존 Owner가 있으면 새 파일 중복 없이 기존 파일 사용. 하나의 경계가 막혀도 다음 독립 항목으로 진행. 다른 RF·반대 개발자 소유 파일 쓰기 금지.
2. `KEEP_OK`는 본문/위치/역할을 한 번 확인하고 한 줄 사유+Git SHA로 즉시 종결; 같은 SHA 테스트 재실행하지 않는다. 효과/broker/State·CLI와 frozen oracle은 재배치 자체를 강제하지 않는다.
3. 실제 MOVE는 원본 구현 제거·새 owner 구현·기존 thin wrapper, before/after LOC, 관련 정상 fake pytest/unittest exit0 후 B 허용 브랜치 code/test 정상 push. C04는 delta만 묶음 통합, C05는 기존 DONE 이력을 보존하되 TARGET_GAP 남았으면 구현으로 되돌린다.
4. `RF=RF-006|SOURCE_BLOB|FUNCTION_MOVES|TARGET_PATHS/BLOBS|KEEP_REASON|LOC_DELTA|TEST_CMD/EXIT|PUSH_SHA|TARGET_STATUS` 보고. 실거래/운영 DB/Guard/UEF 등 효과 금지.
