# P1.5 — ALL 26 libs/ first-level packages: owner/disposition

**Pinned tree:** `5cb90b39d00cee483be292272b893d8e8a4c6e78` | Python package count by tracked files | **Owner is architectural proposal, not migration authorization**.

| Existing package | Files | Disposition | Technical responsibility |
|---|---:|---|---|
| `libs/agent/` | 14 | `LEGACY_COMPAT_KEEP` | legacy role adapters, public constructors/signatures stay |
| `libs/agents/` | 115 | `KEEP_CANONICAL_PARTIAL` | 4 role public surfaces; add real callable surfaces by verified adaptation |
| `libs/runtime/` | 319 | `SPLIT_BY_OWNER_AFTER_PARITY` | role-specific internals vs genuinely shared orchestration primitives |
| `libs/reporting/` | 500 | `KEEP_MIXED_PENDING_CONSUMER_PROOF` | Reporter/read-model vs research/evaluation evidence, publisher/effect locks |
| `libs/research/` | 110 | `KEEP_RESEARCH` | alpha/feedback/diagnosis/shadow research, no order authority |
| `libs/strategies/` | 21 | `KEEP_STRATEGY` | universe/candidates/policy; scanner ranks, no competing rank owner |
| `libs/execution/` | 19 | `SAFETY_LOCK` | admission, Step5C/CAS, order broker guards/execution |
| `libs/read/` | 17 | `KEEP_READ_ADAPTER` | read-only Kiwoom/market input adapters |
| `libs/contracts/` | 16 | `KEEP_CONTRACTS_REFACTOR_INTERNAL` | DTO/serializer ABI; agent_outputs 105,768B; import-inversion debt |
| `libs/news/` | 12 | `KEEP_DOMAIN` | news acquisition/sentiment data |
| `libs/core/` | 10 | `KEEP_FOUNDATION` | settings/log/path isolation/symbols/http |
| `libs/llm/` | 8 | `EFFECT_BOUNDARY_KEEP` | router/provider/model/JSON parsing; preserve prompts/retries/call count |
| `libs/market/` | 8 | `KEEP_MARKET` | global sentiment and market indicators |
| `libs/ai/` | 6 | `KEEP_AI_POLICY` | intent schema/strategist configuration |
| `libs/catalog/` | 6 | `KEEP_CATALOG` | API catalog/planner/request builder |
| `libs/skills/` | 6 | `KEEP_SKILLS` | IO adapters and catalog skill contract |
| `libs/kiwoom/` | 5 | `SAFETY_LOCK` | token/account HTTP and broker-facing client |
| `libs/diagnostics/` | 4 | `KEEP_DIAGNOSTICS` | read-only probes |
| `libs/performance/` | 4 | `KEEP_MEMORY` | strategy-memory/performance feedback |
| `libs/supervisor/` | 4 | `SAFETY_LOCK` | two phase, intent state SQLite, durable stores |
| `libs/risk/` | 3 | `SAFETY_LOCK` | Supervisor/AllowResult and risk intent |
| `libs/storage/` | 3 | `KEEP_STORAGE` | state persistence/proposal store; path isolation |
| `libs/tools/` | 3 | `KEEP_TOOLS` | bounded utilities |
| `libs/approval/` | 2 | `SAFETY_LOCK` | ApprovalService, no duplicate approvals |
| `libs/data_quality/` | 2 | `KEEP_QUALITY` | signal availability/quality contract |
| `libs/market_data/` | 2 | `KEEP_PROVENANCE` | content-addressed market receipts, archive integrity |

## Cross-package decisions (explicit)
- `libs/reporting/` **500** files: `evaluation/135`, `trade_report/85`, `baseline_btc_woori_tech/26`, `baseline_samsung_hynix/19`, `opening_rank1_shadow/14`, other report/read-model modules. Keep UEF publisher and evaluated evidence at their current canonical paths; *logical* Q10/Q12 research ownership belongs to Research but physical migration is BLOCKED pending dynamic consumer and serialized output parity. Neither Reporter nor a new Evaluator agent gains trading authority.
- `libs/runtime/` **319** files: nested `strategist/44`, `commander/40`, `monitor_exit/32`, `monitor/30`, `scanner/29`, `entrypoints/21`, `quant/18`, `mock_exam_day/7`, `controlled_mock_lanes/6` plus **92 direct** modules. The existing sliced owner modules stay put until proven single-callable migration; runtime loop/lease/clock/state writers remain cross-cutting primitives or safety locks.
- `libs/agents/` **115**: `reporter/67`, `scanner/20`, `monitor/19`, `strategist/8`, direct `__init__.py` 1. Existing actual role peers 4/7; missing Commander, Supervisor, Executor surfaces (not missing their real engines). No empty packages.
- `libs/research/` **110**: 12 named research subpackages including `rank1_feature_mart`, `conditional_alpha_diagnosis`, `integrated_trade_diagnosis`, `opening_rank1_deep_dive`, `opportunity_engine`, `structural_alpha`. Keep distinct from production rank/execution and deterministic UEF publisher.
- `libs/agent/` **14**: legacy M15 `commander.py`, `strategist.py`, `scanner.py`, `monitor.py`, `reporter.py`, `executor.py` etc; public imports/monkeypatch may rely on these. Treat as compatibility adapters, not alternate canonical engines; no blanket delete.
- `libs/contracts/agent_outputs.py` **105768B** currently imports `libs.runtime.dates`, `decision_observability`, `commander_memory_application_trace`, Strategist visibility, and per-role output contexts. Preserve TypedDict and output construction ABI; separate pure DTO from enrichment later, with exact binary/serialized equality.
- `libs/execution/`, `libs/approval/`, `libs/supervisor/`, `libs/risk/`, `libs/kiwoom/` form ONE existing effect/approval chain, **not** five interchangeable facades. `ApprovalService` imports `IntentStore` + intent state + order fingerprint; `TwoPhaseSupervisor` imports `Supervisor` + normalized intent. Keep these paths unchanged.
- `libs/market_data/receipts.py` is real I/O provenance storage and `libs/research/evidence_ledger.py` appends evidence logs. Their filenames may suggest pure 'data' but they **write**, so no casual function move.

## Other root responsibility, full coverage
| Folder | Tracked files | Owner and disposition |
|---|---:|---|
| `graphs/` | 45 | operational Commander and nodes; leave guarded execute; graph-shaped M17 stub distinct |
| `apps/` | 235 | `api/100`, `web/98`, `operator_ui/37`; frontend/query adapters not trading authority |
| `scripts/` | 415 | `root/213`, `diagnostics/76`, `refactor/55`, `research/54`, `maintenance/13`, `examples/4`; scheduled/CLI wrappers cannot be removed without external consumer proof |
| `tests/` | 640 | `root/588`, `fixtures/31`, `apps/20`, `deploy/1`; preserve discovery and baselines, isolation by session |
| `docs/` | 1269 | historical evidence; classify/archive by index, **no mass rename** while links and tests reference paths |
| `deploy/` | 33 | Docker/compose/trading scheduler entrypoints, keep stable |
| `data/` | 25 | eval/specs/originals; avoid moving source specs and private values into Git |
| `config/` | 8 | environment/runtime/skills registry; public example only |
| `.github/` | 7 | CI and branch integration gates |

## Size-first targeted candidates (NO blanket movement)
```text
202774B graphs/nodes/strategist_node.py         -> libs/agents/strategist/{context,output,policy}/ [pure sections only]
183181B graphs/nodes/execute_from_packet.py      -> NO MOVE, order authority SAFETY_LOCK
162853B apps/operator_ui/data_access_core.py     -> apps/operator_ui/data_access_* existing split modules; old facade KEEP
152986B graphs/commander_runtime.py              -> libs/runtime/commander/* pure orchestration helpers ONLY; public entry separate
135937B libs/runtime/intraday_monitor_signals.py -> libs/agents/monitor/projections/* pure read/signal only; old path kept
130855B libs/reporting/live_execution_bundle_runner.py -> NO MOVE in P1.5; report effect/locking orchestration
105768B libs/contracts/agent_outputs.py          -> internal per-role builders separate only after ABI + byte parity
 79823B graphs/nodes/monitor_node.py             -> bounded pure sections, never OrderIntent submit
 64858B graphs/nodes/scanner_node.py             -> owned rank/projections only, preserve Top-1 order
 65080B graphs/nodes/decide_trade.py             -> NO auto-move; authority/State+time decision, targeted future scope
 59649B graphs/nodes/update_state_after_execution.py -> State mutation, KEEP until separately approved
```
