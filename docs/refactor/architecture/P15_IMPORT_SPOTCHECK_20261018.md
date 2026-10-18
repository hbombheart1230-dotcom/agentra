# P1.5 — TECH LEAD source/import spot-check (selected first-party paths)

**Pin:** `5cb90b39d00cee483be292272b893d8e8a4c6e78`. Method: GitHub contents at this SHA, top-of-file imports, docstrings and declared top-level defs/classes; not import/runtime execution, not dynamic/monkeypatch complete, not a call-graph certificate. No repo operations or live trades executed.

| Read source | Directly observed symbols / imports | Architecture conclusion |
|---|---|---|
| `graphs/commander_runtime.py` | imports `run_trading_graph`, `decide_trade`, `execute_from_packet`, commander modules | operational orchestration must remain connected to real execution gate |
| `graphs/nodes/commander_node.py` | imports `run_commander_runtime`; defines `commander_node` | existing thin adapter, not a second Commander |
| `graphs/trading_graph.py` | imports Strategy/Scanner/Monitor/decision/executor graph nodes; explicitly no hard LangGraph | graph-shaped M17 test spine, not proof of LangGraph engine |
| `graphs/nodes/executor_node.py` | defines only `executor_node`, documents stub | never equate with guarded order submission |
| `graphs/nodes/execute_from_packet.py` | `libs.execution.order_lifecycle_policy`, recent order guard, guard broker_mutation, Supervisor, executors | order authority SAFETY_LOCK |
| `libs/approval/service.py` | `ApprovalService`, `IntentStore`, physical fingerprint, IntentStateStore | approval/collision control, effectful |
| `libs/supervisor/two_phase.py` | `OrderIntent`, `Decision`, `TwoPhaseSupervisor`; `libs.risk.supervisor.Supervisor` | no competing approval engine |
| `libs/supervisor/intent_state_store.py` | `SQLiteIntentStateStore`, sqlite3, `resolve_runtime_write_path` | persistent State authority SAFETY_LOCK |
| `libs/execution/intent_execution_owner.py` | `execute_owned_order`, `ExecutionDisabledError`, intent identity, intent State | Step5C ownership and submission path |
| `libs/kiwoom/kiwoom_account_client.py` | `KiwoomAccountClient`, HTTP + token/settings | broker-facing transport under lock |
| `libs/agent/commander.py` | imports legacy Strategist/Scanner/Monitor/Reporter/AgentExecutor classes; compatibility docstring | old M15 facade KEEP |
| `libs/agent/strategist.py` | `Strategist`, `Plan` and legacy docstring | legacy import consumers must remain |
| `libs/agent/scanner.py` | `Scanner` imports universe candidate provider, `scanner_policy` | potential alternate rank facade; no naive deletion |
| `libs/agent/monitor.py` | legacy `Monitor` placeholder | compatibility, not live Monitor |
| `graphs/nodes/strategist_node.py` | LLMRouter, news, market sentiment, memory and evidence logger | role/LLM/effect seam |
| `graphs/nodes/scanner_node.py` | rank selection/scanner projections; runtime scanner owner calls | ranking order critical |
| `graphs/nodes/monitor_node.py` | monitor guard, runner-up, signal/exit and evidence writes | only intent+observability |
| `libs/runtime/intraday_monitor_signals.py` | `libs.agents.monitor.projections.signal_evidence_defaults` plus monitor scoring modules | role move already begun; extracted pure slices only |
| `libs/runtime/commander/integrated_chain_support.py` | reexports runtime commander execution/fast_paths/nodes/shadow_runtime | compatibility facade, preserve callable lookup |
| `libs/contracts/agent_outputs.py` | `AgentOutput(TypedDict)`, runtime dates, decision-observability, per-role contract builders | contract layer runtime-import inversion |
| `libs/reporting/evaluation/daily_uef_pipeline.py` | UEF7/8/9 reporters, run identity, authority; author says canonical publisher | unique UEF effect owner |
| `libs/reporting/trade_report_ai.py` | LLMRouter, model catalog, trade truth, report body helpers | LLM prompt/retries frozen |
| `libs/reporting/live_execution_bundle_runner.py` | `argparse`, `atexit`, `subprocess`, report bundles | effectful, do not bulk rehome |
| `libs/reporting/quant_shadow_candidate_evaluation.py` | JSON readers, quant runtime/shadow forward outcomes | research/evaluation reporting hybrid |
| `libs/research/evidence_ledger.py` | `append_evidence_record`, write-path resolution | research owns an effectful evidence writer |
| `libs/strategies/universe_builder.py` | `build_candidate_universe`, KiwoomConditionReader, MarketRankCandidateGenerator | candidate input builder not independent Scanner rank authority |
| `libs/market_data/receipts.py` | `MarketDataReceipt`, content hash, persist/read raw archive, write/read receipts | provenance I/O and integrity |
| `libs/runtime/live_loop_runner.py` | lease ownership, market hours, Kiwoom status, signal handlers | runtime scheduling effects, protect |
| `libs/runtime/exit_policy.py` | imports monitor_exit exit ladder, chart/PnL projection | monitor exit domain but may be policy-sensitive |
| `apps/operator_ui/data_access_core.py` | reporting read models, `LLMRouter`, UI brief modules | splitting must preserve LLM and rendered output |
| `apps/api/main.py` | `create_app`, API config/middleware | already thin app composition |
| `apps/operator_ui/main.py` | `create_app` | UI app entry is not broker authority |

**Scope limit:** This spot check does not assert every function definition in 3,908 files was parsed. Complete path-level ledger is generated from the actual Git tree; physical migrations require narrow authoritative consumer/identity tests on each changed path.
