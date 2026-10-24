# T02 — apps/ API·Operator UI·React Web 상세 목표
> 범위: RF-001~RF-007, P1.5.3 및 UI/API 계약. 소스 240개 파일. 새 레이아웃은 소비자 parity 없는 일괄 move 지시가 아니다.

## 목표 패키지 깊이
```text
apps/
├── api/
│   ├── main.py                      # import/HTTP 진입
│   ├── routers/                     # HTTP routing only
│   ├── models/                      # request/response DTO
│   ├── services/                    # readonly read-model assembly
│   ├── adapters/                    # artifact/source adapters
│   ├── domain/                      # pure projections/rules
│   │   └── anomalies/
│   └── infrastructure/              # bounded reader/paths/sanitization
├── operator_ui/
│   ├── main.py                      # stable route entrypoint
│   ├── data_access.py               # canonical stable facade
│   ├── data_access_core.py          # target: thin dispatch/compat only
│   ├── data_access_brief_*.py       # targeted single-purpose Brief pieces (CURRENT)
│   ├── data_access_*_projection.py  # readonly read model owners (CURRENT)
│   ├── static/
│   └── templates/
└── web/
    ├── e2e/
    ├── index.html
    ├── package.json
    └── src/
        ├── app/
        ├── features/{alerts,data-quality,llm-operations,market,operations,opportunities,overview,patch-notes,performance,reports,runtime-status,strategies,trades}/
        ├── shared/{api,components,formatters,layout,tables}/
        └── styles/
```

## 핵심 파일별 목표 경계
| 현재 파일(실존) | 목표 위치/Owner | RF·처리 | 종료 검증 |
|---|---|---|---|
| `apps/api/main.py`, `apps/api/routers/*.py` | 같은 위치 / HTTP facade | RF-005 KEEP | route/API·status·public profile |
| `apps/api/services/{overview,operations,opportunities,reports,trades}.py` | 같은 service owner (pure read) | RF-003 KEEP/SPLIT_BY_PROOF | no broker/State mutate, JSON parity |
| `apps/api/domain/anomalies/{factory,freshness_rules,integrity_rules,policy}.py` | anomalies rule owner | RF-004 KEEP | anomaly fingerprint/shape parity |
| `apps/api/infrastructure/{bounded_reader,paths,public_sanitization,source_roots}.py` | infra readonly gate | RF-005 KEEP | path traversal, bounded I/O, sanitization |
| `apps/api/adapters/{trade_bundle,patch_notes,safe_reports}.py` | adapter only | RF-005 KEEP | provenance/byte schema |
| `apps/operator_ui/main.py`, `data_access.py` | stable public route/facade KEEP | RF-002(`main.py`)/RF-001(`data_access.py`) | old imports, routes, output |
| `apps/operator_ui/data_access_core.py` | minimal dispatcher; substantive readonly owners in pre-existing focused files | RF-001 REFACTOR_PURE | golden Brief text, LLM count/order, no write |
| `apps/operator_ui/data_access_brief_{input_projection,sections_projection,render_sections,render_summary_derivation}.py` | input/read/renderer each one Owner | RF-001, relevant consumer RF | exact serialized artifact; monkeypatch seam |
| `apps/operator_ui/data_access_{run_read_models,trade_read_models,overview_projection,reports}.py` | separate readonly query models | RF-001 KEEP/SPLIT | PnL/truth provenance |
| `apps/operator_ui/templates/{base,operator_brief_detail,overview,run_detail,runs,trade_report_detail}.html` | existing templates KEEP | RF-002 | CSS, route, browser E2E |
| `apps/web/src/app/{App,navigation}.tsx` | shell/navigation | RF-007 | route parity |
| `apps/web/src/features/{patch-notes,runtime-status,trades}/` | feature owned presentational code | RF-006 | npm unit/snapshot, provenance |
| `apps/web/src/shared/api/{client,useApi}.ts` | stable API client | RF-007 | response/parsing; no trading writes |

**소유권 교정:** `apps/web/src/features/**`는 RF-006(DONE), `apps/web/src/{app,shared}`·`e2e`는 RF-007(검증 큐) 소유다. `apps/api/{services,domain,routers+models+adapters+infrastructure}`는 각각 RF-003/004/005, `apps/operator_ui`는 data_access RF-001, main/templates RF-002이다. 범위가 다른 RF의 DONE 코드를 무단 변경하지 않는다.

**제안하는 개선:** 실재하는 `data_access_brief_*.py`를 책임별 재분류·중복 정리하되 새 `common2/`·`parts_r4/`를 만들지 않는다. Operator Brief LLM 생성/캐시·readonly truth의 한 Owner가 확인된 후에만 `data_access_core.py` 파사드를 얇게 한다. 도메인/웹은 무조건 재배치가 아니라 현 패키지 구조를 목표 기본값으로 삼는다.

## 루트 내부 전수 파일 인벤토리
아래는 **현재 SOURCE_PATH** 전체다. 각 파일의 소유 RF는 기준선 CSV 우선이고, 새파일은 해당 경계 RF 승인 전 무단 write 금지. TARGET_PATH가 표시되지 않은 파일은 원칙상 동일 경로 KEEP_CANDIDATE이며 검증 없는 최종 KEEP_VERIFIED는 아니다.

- `apps/api/__init__.py` — RF-005
- `apps/api/adapters/__init__.py` — RF-005
- `apps/api/adapters/llm_artifacts.py` — RF-005
- `apps/api/adapters/llm_event_tail.py` — RF-005
- `apps/api/adapters/market_snapshot.py` — RF-005
- `apps/api/adapters/operator_summary.py` — RF-005
- `apps/api/adapters/opportunity_artifacts.py` — RF-005
- `apps/api/adapters/patch_notes.py` — RF-005
- `apps/api/adapters/performance_summary.py` — RF-005
- `apps/api/adapters/runtime_status_artifacts.py` — RF-005
- `apps/api/adapters/safe_reports.py` — RF-005
- `apps/api/adapters/source_freshness.py` — RF-005
- `apps/api/adapters/trade_bundle.py` — RF-005
- `apps/api/config.py` — RF-005
- `apps/api/domain/__init__.py` — RF-004
- `apps/api/domain/anomalies/__init__.py` — RF-004
- `apps/api/domain/anomalies/factory.py` — RF-004
- `apps/api/domain/anomalies/freshness_rules.py` — RF-004
- `apps/api/domain/anomalies/integrity_rules.py` — RF-004
- `apps/api/domain/anomalies/opportunity_rules.py` — RF-004
- `apps/api/domain/anomalies/policy.py` — RF-004
- `apps/api/domain/anomalies/trade_cost_rule.py` — RF-004
- `apps/api/domain/anomalies/trade_exit_rule.py` — RF-004
- `apps/api/domain/anomalies/trade_rules.py` — RF-004
- `apps/api/domain/anomalies/trade_sequence_rule.py` — RF-004
- `apps/api/domain/anomaly_rules.py` — RF-004
- `apps/api/domain/llm_operations_projection.py` — RF-004
- `apps/api/domain/llm_role_catalog.py` — RF-004
- `apps/api/domain/performance_math.py` — RF-004
- `apps/api/domain/runtime_status_projection.py` — RF-004
- `apps/api/domain/scheduled_intelligence_projection.py` — RF-004
- `apps/api/domain/watchdog_history_projection.py` — RF-004
- `apps/api/infrastructure/__init__.py` — RF-005
- `apps/api/infrastructure/bounded_reader.py` — RF-005
- `apps/api/infrastructure/dates.py` — RF-005
- `apps/api/infrastructure/jsonl_tail.py` — RF-005
- `apps/api/infrastructure/paths.py` — RF-005
- `apps/api/infrastructure/public_middleware.py` — RF-005
- `apps/api/infrastructure/public_sanitization.py` — RF-005
- `apps/api/infrastructure/source_roots.py` — RF-005
- `apps/api/infrastructure/trade_index.py` — RF-005
- `apps/api/main.py` — RF-005
- `apps/api/models/__init__.py` — RF-004
- `apps/api/models/anomalies.py` — RF-004
- `apps/api/models/common.py` — RF-004
- `apps/api/models/health.py` — RF-004
- `apps/api/models/llm_operations.py` — RF-004
- `apps/api/models/market.py` — RF-004
- `apps/api/models/operations.py` — RF-004
- `apps/api/models/opportunities.py` — RF-004
- `apps/api/models/overview.py` — RF-004
- `apps/api/models/patch_notes.py` — RF-004
- `apps/api/models/performance.py` — RF-004
- `apps/api/models/portfolio.py` — RF-004
- `apps/api/models/profile.py` — RF-004
- `apps/api/models/reports.py` — RF-004
- `apps/api/models/runtime_status.py` — RF-004
- `apps/api/models/strategies.py` — RF-004
- `apps/api/models/trades.py` — RF-004
- `apps/api/requirements.txt` — RF-005
- `apps/api/routers/__init__.py` — RF-005
- `apps/api/routers/anomalies.py` — RF-005
- `apps/api/routers/health.py` — RF-005
- `apps/api/routers/llm_operations.py` — RF-005
- `apps/api/routers/market.py` — RF-005
- `apps/api/routers/operations.py` — RF-005
- `apps/api/routers/opportunities.py` — RF-005
- `apps/api/routers/overview.py` — RF-005
- `apps/api/routers/patch_notes.py` — RF-005
- `apps/api/routers/performance.py` — RF-005
- `apps/api/routers/portfolio.py` — RF-005
- `apps/api/routers/profile.py` — RF-005
- `apps/api/routers/runtime_status.py` — RF-005
- `apps/api/routers/strategies.py` — RF-005
- `apps/api/routers/trades.py` — RF-005
- `apps/api/services/__init__.py` — RF-003
- `apps/api/services/anomalies.py` — RF-003
- `apps/api/services/health.py` — RF-003
- `apps/api/services/llm_operations.py` — RF-003
- `apps/api/services/market.py` — RF-003
- `apps/api/services/metric_factory.py` — RF-003
- `apps/api/services/operations.py` — RF-003
- `apps/api/services/opportunities.py` — RF-003
- `apps/api/services/opportunity_projection.py` — RF-003
- `apps/api/services/overview.py` — RF-003
- `apps/api/services/patch_notes.py` — RF-003
- `apps/api/services/performance.py` — RF-003
- `apps/api/services/portfolio.py` — RF-003
- `apps/api/services/profile.py` — RF-003
- `apps/api/services/reports.py` — RF-003
- `apps/api/services/runtime_status.py` — RF-003
- `apps/api/services/scheduled_artifacts.py` — RF-003
- `apps/api/services/strategy_performance.py` — RF-003
- `apps/api/services/trade_fallback_projection.py` — RF-003
- `apps/api/services/trade_fallbacks.py` — RF-003
- `apps/api/services/trade_integrity_projection.py` — RF-003
- `apps/api/services/trade_summary_projection.py` — RF-003
- `apps/api/services/trade_timeline_projection.py` — RF-003
- `apps/api/services/trade_values.py` — RF-003
- `apps/api/services/trades.py` — RF-003
- `apps/operator_ui/__init__.py` — RF-002
- `apps/operator_ui/data_access.py` — RF-001
- `apps/operator_ui/data_access_brief.py` — RF-001
- `apps/operator_ui/data_access_brief_canonical_input.py` — RF-001
- `apps/operator_ui/data_access_brief_compaction.py` — RF-001
- `apps/operator_ui/data_access_brief_evidence_readout_p15.py` — RF-001
- `apps/operator_ui/data_access_brief_facts.py` — RF-001
- `apps/operator_ui/data_access_brief_fallback.py` — RF-001
- `apps/operator_ui/data_access_brief_input_projection.py` — RF-001
- `apps/operator_ui/data_access_brief_input_sections.py` — RF-001
- `apps/operator_ui/data_access_brief_market_sections.py` — RF-001
- `apps/operator_ui/data_access_brief_monitor_notes.py` — RF-001
- `apps/operator_ui/data_access_brief_monitor_sections.py` — RF-001
- `apps/operator_ui/data_access_brief_prompts.py` — RF-001
- `apps/operator_ui/data_access_brief_render_fallback.py` — RF-001
- `apps/operator_ui/data_access_brief_render_helpers.py` — RF-001
- `apps/operator_ui/data_access_brief_render_narrative_helpers.py` — RF-001
- `apps/operator_ui/data_access_brief_render_sections.py` — RF-001
- `apps/operator_ui/data_access_brief_render_summary_derivation.py` — RF-001
- `apps/operator_ui/data_access_brief_sanitation.py` — RF-001
- `apps/operator_ui/data_access_brief_sections_projection.py` — RF-001
- `apps/operator_ui/data_access_brief_source_truth_p15.py` — RF-001
- `apps/operator_ui/data_access_core.py` — RF-001
- `apps/operator_ui/data_access_linkage.py` — RF-001
- `apps/operator_ui/data_access_overview_projection.py` — RF-001
- `apps/operator_ui/data_access_reports.py` — RF-001
- `apps/operator_ui/data_access_run_detail_projection.py` — RF-001
- `apps/operator_ui/data_access_run_read_models.py` — RF-001
- `apps/operator_ui/data_access_runs.py` — RF-001
- `apps/operator_ui/data_access_status.py` — RF-001
- `apps/operator_ui/data_access_symbol_run_chain.py` — RF-001
- `apps/operator_ui/data_access_trade_index_projection.py` — RF-001
- `apps/operator_ui/data_access_trade_read_models.py` — RF-001
- `apps/operator_ui/data_access_value_formatting.py` — RF-001
- `apps/operator_ui/main.py` — RF-002
- `apps/operator_ui/static/operator.css` — RF-002
- `apps/operator_ui/templates/base.html` — RF-002
- `apps/operator_ui/templates/operator_brief_detail.html` — RF-002
- `apps/operator_ui/templates/overview.html` — RF-002
- `apps/operator_ui/templates/run_detail.html` — RF-002
- `apps/operator_ui/templates/runs.html` — RF-002
- `apps/operator_ui/templates/trade_report_detail.html` — RF-002
- `apps/web/.gitignore` — RF-007
- `apps/web/e2e/public-profile.mjs` — RF-007
- `apps/web/e2e/smoke.mjs` — RF-007
- `apps/web/index.html` — RF-007
- `apps/web/package-lock.json` — RF-007
- `apps/web/package.json` — RF-007
- `apps/web/src/app/App.tsx` — RF-007
- `apps/web/src/app/navigation.tsx` — RF-007
- `apps/web/src/features/alerts/AlertsPage.tsx` — RF-006
- `apps/web/src/features/alerts/AnomalyTable.tsx` — RF-006
- `apps/web/src/features/alerts/OverviewAlerts.tsx` — RF-006
- `apps/web/src/features/alerts/SeverityBadge.tsx` — RF-006
- `apps/web/src/features/alerts/index.ts` — RF-006
- `apps/web/src/features/alerts/labels.ts` — RF-006
- `apps/web/src/features/alerts/types.ts` — RF-006
- `apps/web/src/features/data-quality/DataQualityPage.tsx` — RF-006
- `apps/web/src/features/llm-operations/LlmOperationsPage.tsx` — RF-006
- `apps/web/src/features/llm-operations/LlmStageChart.tsx` — RF-006
- `apps/web/src/features/llm-operations/ModelRouteTable.tsx` — RF-006
- `apps/web/src/features/llm-operations/RecentCallTable.tsx` — RF-006
- `apps/web/src/features/llm-operations/StageUsageTable.tsx` — RF-006
- `apps/web/src/features/llm-operations/labels.ts` — RF-006
- `apps/web/src/features/llm-operations/types.ts` — RF-006
- `apps/web/src/features/market/MarketChart.tsx` — RF-006
- `apps/web/src/features/market/MarketMetricTable.tsx` — RF-006
- `apps/web/src/features/market/MarketPage.tsx` — RF-006
- `apps/web/src/features/market/types.ts` — RF-006
- `apps/web/src/features/operations/DecisionLineagePanel.tsx` — RF-006
- `apps/web/src/features/operations/OperationsAlertPanel.tsx` — RF-006
- `apps/web/src/features/operations/OperationsComparisonPanel.tsx` — RF-006
- `apps/web/src/features/operations/OperationsPage.tsx` — RF-006
- `apps/web/src/features/operations/OperationsTimeline.tsx` — RF-006
- `apps/web/src/features/operations/types.ts` — RF-006
- `apps/web/src/features/opportunities/BlockerChart.tsx` — RF-006
- `apps/web/src/features/opportunities/OpportunitiesPage.tsx` — RF-006
- `apps/web/src/features/opportunities/OpportunityOutcomeTable.tsx` — RF-006
- `apps/web/src/features/opportunities/OpportunitySignalTable.tsx` — RF-006
- `apps/web/src/features/opportunities/types.ts` — RF-006
- `apps/web/src/features/overview/OverviewPage.tsx` — RF-006
- `apps/web/src/features/overview/PositionTable.tsx` — RF-006
- `apps/web/src/features/patch-notes/PatchNotesPage.tsx` — RF-006
- `apps/web/src/features/patch-notes/provenance.test.ts` — RF-006
- `apps/web/src/features/patch-notes/provenance.ts` — RF-006
- `apps/web/src/features/patch-notes/types.ts` — RF-006
- `apps/web/src/features/performance/PerformanceChart.tsx` — RF-006
- `apps/web/src/features/performance/PerformancePage.tsx` — RF-006
- `apps/web/src/features/performance/types.ts` — RF-006
- `apps/web/src/features/reports/ReportsPage.tsx` — RF-006
- `apps/web/src/features/runtime-status/RuntimeStateBadge.tsx` — RF-006
- `apps/web/src/features/runtime-status/RuntimeStatusContext.tsx` — RF-006
- `apps/web/src/features/runtime-status/RuntimeStatusPanel.tsx` — RF-006
- `apps/web/src/features/runtime-status/ScheduledArtifactViewer.tsx` — RF-006
- `apps/web/src/features/runtime-status/ScheduledIntelligencePanel.tsx` — RF-006
- `apps/web/src/features/runtime-status/WatchdogHistoryPanel.tsx` — RF-006
- `apps/web/src/features/runtime-status/presentation.test.ts` — RF-006
- `apps/web/src/features/runtime-status/presentation.ts` — RF-006
- `apps/web/src/features/runtime-status/supervisorPresentation.test.ts` — RF-006
- `apps/web/src/features/runtime-status/types.ts` — RF-006
- `apps/web/src/features/strategies/StrategiesPage.tsx` — RF-006
- `apps/web/src/features/strategies/StrategyChart.tsx` — RF-006
- `apps/web/src/features/strategies/StrategyPerformanceTable.tsx` — RF-006
- `apps/web/src/features/strategies/types.ts` — RF-006
- `apps/web/src/features/trades/TradeDetailPanel.tsx` — RF-006
- `apps/web/src/features/trades/TradeTable.tsx` — RF-006
- `apps/web/src/features/trades/TradesPage.tsx` — RF-006
- `apps/web/src/features/trades/tradeSort.test.ts` — RF-006
- `apps/web/src/features/trades/tradeSort.ts` — RF-006
- `apps/web/src/features/trades/types.ts` — RF-006
- `apps/web/src/main.tsx` — RF-007
- `apps/web/src/shared/api/client.test.ts` — RF-007
- `apps/web/src/shared/api/client.ts` — RF-007
- `apps/web/src/shared/api/types.ts` — RF-007
- `apps/web/src/shared/api/useApi.ts` — RF-007
- `apps/web/src/shared/components/DataState.tsx` — RF-007
- `apps/web/src/shared/components/DateRange.tsx` — RF-007
- `apps/web/src/shared/components/MetricStrip.tsx` — RF-007
- `apps/web/src/shared/components/PageHeader.tsx` — RF-007
- `apps/web/src/shared/components/Panel.tsx` — RF-007
- `apps/web/src/shared/components/StatusPill.tsx` — RF-007
- `apps/web/src/shared/formatters/dates.ts` — RF-007
- `apps/web/src/shared/formatters/numbers.test.ts` — RF-007
- `apps/web/src/shared/formatters/numbers.ts` — RF-007
- `apps/web/src/shared/layout/AppShell.tsx` — RF-007
- `apps/web/src/shared/tables/SortableHeaderRow.tsx` — RF-007
- `apps/web/src/shared/tables/sorting.test.ts` — RF-007
- `apps/web/src/shared/tables/sorting.ts` — RF-007
- `apps/web/src/shared/tables/useSortableRows.ts` — RF-007
- `apps/web/src/styles/base.css` — RF-007
- `apps/web/src/styles/components.css` — RF-007
- `apps/web/src/styles/layout.css` — RF-007
- `apps/web/src/styles/responsive.css` — RF-007
- `apps/web/src/styles/tokens.css` — RF-007
- `apps/web/src/vite-env.d.ts` — RF-007
- `apps/web/tsconfig.app.json` — RF-007
- `apps/web/tsconfig.json` — RF-007
- `apps/web/tsconfig.node.json` — RF-007
- `apps/web/vite.config.ts` — RF-007
- `apps/web/vitest.config.ts` — RF-007

## 공통 강제 게이트
- 본 T문서는 **목표 설계**다. 새 폴더를 만들거나 파일을 옮기는 자동 승인서가 아니다. 기존 소비자·동적 import·CLI·테스트·스케줄러·런타임 출력·인증·운영 경계의 parity 증명과 해당 RF 승인 후 실제 이동한다.
- D00/CURRENT 규칙, V3 SAFETY_LOCK, BASE/후보 SHA, 독립 read-only peer 검증, normal/`python -O`, 해당 통합 SHA CI를 유지한다. 과거 FAIL·SKIP은 PASS로 바꾸지 않는다.
- 각 RF 종료 증거: SOURCE_PATH → TARGET_PATH / 단일 Owner / KEEP·MOVE·COMPAT·SAFETY_HOLD·REMOVE_PROVEN / 소비자 / 독립 증거 / 통합 SHA. 없으면 RF DONE 불가.
- [T00 전체 목차](T00_TARGET_TREE.md) · [동결 V3](TREE_V3_FROZEN.md) · [RF 상태](../plan/STATUS.md) · [기준선 소유권 CSV](../plan/FILE_COVERAGE_63182ab2.csv).
