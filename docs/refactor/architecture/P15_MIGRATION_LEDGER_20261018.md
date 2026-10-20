> **PINNED SOURCE-MIGRATION DESIGN LEDGER — NOT A CURRENT TASK LIST (2026-10-20).** Callable/path claims in this ledger were sampled at `5cb90b39`, and are not independently verified at latest integration HEAD. Actual migration slices require a new exact-SHA work packet under [D00](../../ENGINEERING_DELIVERY_POLICY.md), [TREE_V3](TREE_V3_FROZEN.md), and [Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20). Preserve the ledger as historical design evidence.

# P1.5 — TECH LEAD migration ledger (actionable paths; NOT automated migration)

**Evidence:** source headers, imports and top-level callable declarations from integration `5cb90b39d00cee483be292272b893d8e8a4c6e78`; old V1..V4 Scanner approvals and frozen V3; commit-specific tests still required. **This is scoped design authority, not a claim of exhaustive Python AST edges.**

| Wave | Exact source / callable | Target or disposition | Source-derived import/consumer fact | Required gate |
|---|---|---|---|---|
| 0 | `graphs/trading_graph.py::run_trading_graph` | KEEP M17 graph baseline | imports strategist/scanner/monitor/decision/executor STUB; expressly no hard LangGraph dep | prevent operational graph substitution |
| 0 | `graphs/commander_runtime.py::run_commander_runtime` | KEEP operational facade | imports graph spine, `decide_trade`, `execute_from_packet`, runtime commander support | full call-time/State/execute route parity |
| 0 | `graphs/nodes/commander_node.py::commander_node` | KEEP thin graph adapter | direct imports `run_commander_runtime` | callable & monkeypatch compatibility |
| 0 | `graphs/nodes/execute_from_packet.py` | **SAFETY_LOCK KEEP** | imports `libs.execution.guards`, `Supervisor`, executors and persisted artifacts | Broker/CAS/UNKNOWN/never-double-submit |
| 0 | `graphs/nodes/executor_node.py::executor_node` | KEEP STUB | no Broker import, graph test stage | don't grant actual order authority |
| 0 | `libs/supervisor/intent_state_store.py::SQLiteIntentStateStore` | **SAFETY_LOCK KEEP** | sqlite3 durable ownership, `resolve_runtime_write_path` | transaction/restart/collision parity |
| 0 | `libs/execution/intent_execution_owner.py::execute_owned_order` | **SAFETY_LOCK KEEP** | imports `ExecutionDisabledError`, `intent_identity`, `IntentStateMachine`, readiness evidence | Step5C and error handling |
| 0 | `libs/approval/service.py::ApprovalService` | **SAFETY_LOCK KEEP** | imports `IntentStore`, physical fingerprint, intent state | single Supervisor approval authority |
| 0 | `libs/supervisor/two_phase.py::TwoPhaseSupervisor` | **SAFETY_LOCK KEEP** | imports `libs.risk.supervisor.Supervisor`, normalize intent, Settings | identical allow/deny/unknown traces |
| 0 | `libs/kiwoom/kiwoom_account_client.py::KiwoomAccountClient` | **SAFETY_LOCK KEEP** | imports HTTP, token client and Settings | real transport untouched |
| 0 | `libs/reporting/evaluation/daily_uef_pipeline.py` | KEEP unique UEF publisher | imports UEF7/8/9 authority + reporters | UEF9 genuine 7/84; no alternate writer |
| 0 | `libs/market_data/receipts.py::write_receipt` | KEEP provenance IO | content addressed archive and receipt read/write | lossless provenance/never fabricate input |
| 1 | `libs/agent/{commander,strategist,scanner,monitor,reporter,executor}.py` | `LEGACY_COMPAT_KEEP`; document target public reexports | legacy commander imports legacy role classes; monitor only placeholder | import/class identity, construction, monkeypatch, callers |
| 1 | `libs/agents/commander/` not present | propose ONE real public contract; source owner stays `graphs.commander_runtime` | no directory; legacy adapter existing | no import-time effects + callable parity; separate explicit approval |
| 1 | `libs/agents/monitor/` implicit namespace | KEEP current namespace until marker risk assessed | 19 actual files with no `__init__.py` | test namespace/monkeypatch/import semantics before any marker |
| 1 | `libs/agents/supervisor/` missing | plan **pure interface/Protocol only**, not re-export live gate by default | real owners `libs/risk` / `libs/supervisor` / `libs/approval` | explicit approval, import no effects/no alternate approve route |
| 1 | `libs/agents/executor/` missing | plan **pure interface/Protocol only**, no `execute_from_packet` eager import | real order owner graph node remains | explicit approval, no new order submission route |
| 2 | `graphs/nodes/strategist_node.py` | bounded pure context/output calls → `libs/agents/strategist/`; old facade KEEP | imports AI settings, LLMRouter, news, research ledger, runtime strategist | prompt count/wording, env timing, provider failure, State/bytes |
| 2 | `graphs/nodes/scanner_node.py` | bounded projections/policy → `libs/agents/scanner/`; old facade KEEP | uses runtime scanner and already moved candidate_risk/context/policy/projections | strict candidate ranking/Top-1 tie/bias identity |
| 2 | `graphs/nodes/monitor_node.py` | bounded read-only views → `libs/agents/monitor/`; old facade KEEP | imports signal/entry guard, exit and event writers | OrderIntent-only, event and State order |
| 2 | `libs/runtime/intraday_monitor_signals.py` | move ONLY detached pure projections → `libs/agents/monitor/projections/` | existing imports `libs.agents.monitor.projections.signal_evidence_defaults`; many monitor helpers | no env/clock/IO re-evaluation, score bytes |
| 2 | `graphs/commander_runtime.py` | pure routing/value transforms → `libs/runtime/commander/` after manual call graph | imports `libs.runtime.commander.integrated_chain_support` which already exports nodes/execution/fast paths | call-time facade identity; frozen classifier INVALID for migration |
| 3 | `libs/contracts/agent_outputs.py::AgentOutput` and builders | retain facade; split pure schema vs per-role output builder in `libs/contracts/` | runtime observability imports discovered IN contracts | outputs, serialization, circular import inversion |
| 3 | `libs/reporting/live_execution_bundle_runner.py` | KEEP effects; optionally extract pure formatting separately | `atexit`, `subprocess`, report generator imports | no job count/process/lock/output change; HOLD physical moves |
| 3 | `libs/reporting/trade_report_ai.py` | keep entry/LLM calls; pure text format in existing trade_report/ | imports `LLMRouter`, model catalog, parse JSON, report truth | prompts, request count and exact final narrative |
| 3 | `libs/reporting/evaluation/` 135 files | KEEP frozen UEF 5–9 publisher/evaluation owner | daily orchestrator imports UEF 7/8/9 run IDs/digests | replay, deterministic evidence, version authority |
| 3 | `libs/reporting/baseline_{btc_woori_tech,samsung_hynix}/` (45 files) | **logical research owner**, physical KEEP until consumer proof | Q12 BTC / Q10 lead-market evidence | separate prospective vs retrospective provenance |
| 3 | `libs/research/evidence_ledger.py::append_evidence_record` | KEEP research-owned IO, not pure helper | uses runtime write path and time/env | no unauthorized production write |
| 4 | `apps/operator_ui/data_access_core.py` | keep public facade; bounded delegation to existing `data_access_brief*` modules | imports reporting truth/read models and LLMRouter, 30 root helpers | read-only, exact brief/HTML/JSON/parity, no early LLM |
| 4 | `apps/api/main.py::create_app` | KEEP HTTP composition | imports relative config and middleware | public route/response compatibility |
| 4 | `libs/runtime/live_loop_runner.py` | KEEP runtime runner/scheduler | imports lock, market hours, Kiwoom status, lease/store | shutdown, heartbeat, idempotency, no extra worker |
| 5 | `graphs/nodes/decide_trade.py` | **NO AUTO MOVE** until separately reviewed | imports intent schema, exit policy, cost profile, circuit breaker, env/time | decision authority, NOOP, override, threshold |
| 5 | `graphs/nodes/update_state_after_execution.py` | KEEP State mutation until state boundary acceptance | imports reason trace, horizon, loss reentry | write order, replay, cash/positions |
| 6 | `scripts/` 415 / `docs/` 1269 / `tests/` 640 | KEEP paths; archive by INDEX/metadata only | external task scheduler, import, CI and link consumers unknown | external launcher/pytest discovery/restore proof before deletion |

**Batch policy:** FIRST decide exact callable+source+target+facade; THEN trace import consumers + injected facade + module identity + dynamic access; THEN single-slice parity/negative test + normal/-O + CI; THEN independent auditor + integrator cherry-pick. No whole role branch merges, blanket `libs/reporting/` move, wildcard allowlists, universal AST classifier or cosmetic dir creation.
