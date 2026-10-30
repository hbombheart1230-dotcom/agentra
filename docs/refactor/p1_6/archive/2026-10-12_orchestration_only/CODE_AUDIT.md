# P1.6 — Static Code Audit and Orchestration Map

Status: SOURCE-INSPECTED / STATIC-ONLY (2026-10-12)  
Repository: `hbombheart1230-dotcom/agentra`, source ref `refactor/p1.5@62cdebf63e295765ca546a0e6ffb569f7aba0bdb`. **No local execution or tests were performed as part of this P1.6 design.**

## 1. What the code actually has
| Surface | Inspected paths | P1.6 consequence |
|---|---|---|
| Canonical Commander | `graphs/commander_runtime.py`, `graphs/nodes/commander_node.py`, `libs/runtime/commander/` | Commander node is a wrapper; preserve routing/state/mode branches, no framework-owned new strategy logic. |
| Graph-shaped baseline | `graphs/trading_graph.py`, `graphs/nodes/{strategist,scanner,monitor,portfolio_guard,decision,executor}_node.py` | **Hand-coded mutable dict graph**; initial Strategist → optional hydration → Scanner → Monitor → portfolio guard → Decision; `retry_scan` loops; approved path can reach graph executor stub. This is not proof that production always uses this path. |
| Production entry/loop | `graphs/pipelines/m13_live_loop.py`, `libs/runtime/live_loop_runner.py`, `libs/runtime/runtime_ownership.py`, `libs/runtime/runtime_mode.py` | Separate tick/lease/drain/host-Docker control. Framework checkpoint cannot take over runtime ownership. |
| Execution-capable packet route | `graphs/nodes/decide_trade.py`, `graphs/nodes/execute_from_packet.py`, `libs/execution/`, `libs/risk/supervisor.py` | Do not treat simple `decision_node` approval as actual Supervisor+Execution approval. Broker mutation must stay in current fenced owner. |
| Agent contracts and adapters | `libs/agent/`, `libs/runtime/{commander,scanner}/`, `libs/contracts/`, `graphs/nodes/` | P1.5 agent extraction is WIP; benchmark must bind to **post-freeze** standalone component boundaries rather than speculative interfaces. |
| Reporter/UI read side | `graphs/nodes/reporter_node.py`, `libs/reporting/`, `apps/operator_ui/` | Report truth, canonical artifacts, UI linked patch notes and LLM enrichment are not to be recomputed by a graph engine. |
| Observability and safety | `libs/runtime/decision_trace.py`, `libs/core/event_logger.py`, `libs/runtime/canonical_artifacts.py`, UEF and P1.5 freeze specs | Preserve run/intent identity, attribution and log sequence; no write or trading-authority leakage. |

`graphs/trading_graph.py` explicitly states it avoids a hard LangGraph dependency. The inspected `requirements.txt` contains `pydantic>=2.7.0` but neither `langgraph` nor `pydantic-graph` as a declared runtime dependency. **Do not infer an installed/active modern graph engine from the project being described as “LangGraph-oriented.”**

## 2. Seven roles: proposed graph mapping (not asserted as current 7-node execution topology)
| Role | Safe node boundary | Unsafe reassignment |
|---|---|---|
| Commander | explicit route, phase, stop/cancel and orchestration decisions | LLM trader, lease ownership replacement, broker command |
| Strategist | existing plan/result adapter; LLM only as already authorized | extra model calls, changed prompts or retry policy |
| Scanner | ranking/result adapter with canonical candidate identity | changing Rank-1 source or converting advice into hard timing |
| Monitor | signal/OrderIntent adapter (intent only) | order submission or exit safety bypass |
| Supervisor | read-only comparison of **existing** approval decision | graph's own simplistic approval as a new real authority |
| Executor | **excluded from initial live-capable benchmark**; existing approval+guard+CAS owner retained | node retries, checkpoint re-entry or direct broker mutation |
| Reporter | consumption of already frozen log/artifact projections | recomputing trade truth or adding order/control authority |

The normative roles are governed by `docs/decisions/ADR-0002_Q_Namespace_Freeze_and_Seven_Node_Lifecycle_Authority.md`; Q labels and data sources are not new agents.

## 3. Highest-risk mismatches to resolve at freeze
1. **Multiple runtime routes:** `graph_spine`, `decision_packet`, `integrated_chain` may have different state mutations/side effects; document per-mode caller graph before evaluating “identical behavior.”
2. **Mutable state:** baseline nodes accept/modify shared `dict`; a new engine's reducer/copy/typed-state semantics can silently alter missing fields, ordering, default values and patch hooks.
3. **Decision vs authority:** `graphs/nodes/decision_node.py` says its approve is only eligible-to-proceed; actual Supervisor, guards and Execution Layer still decide. Do not rename this node `Supervisor` without matching existing contracts.
4. **Retry/resume hazards:** scanner retry and node re-execution must not duplicate LLM, evidence writes or any broker call; checkpoint semantics require explicit per-node side-effect classification.
5. **Ownership:** Host/Docker, SQLite lease, process restart and SIGTERM are orthogonal to a graph engine; keep them outside any shadow graph.
6. **P1.5 unfinished:** current Fast Track Wave A P1.5.2 FINAL OPEN; historical real-report/LLM parity and full-suite write isolation unresolved. New graph results cannot certify these unrelated gates.
7. **Compatibility:** public symbols, monkeypatches, dynamic imports, state keys, raw/DTO surfaces and canonical artifact paths must be frozen and proven, not simplified by framework adapters.

## 4. Focused file/test review anchors for post-freeze benchmark
- Source: `graphs/trading_graph.py`, `graphs/commander_runtime.py`, `graphs/pipelines/m13_live_loop.py`, `libs/runtime/live_loop_runner.py`, `graphs/nodes/decision_node.py`, `graphs/nodes/execute_from_packet.py`.
- Tests: `tests/test_m21_graph_spine_parity.py`, `test_m21_commander_runtime_entry.py`, `test_m13_tick.py`, `test_m13_live_loop.py`, `test_m16_approval_api.py`, `test_supervisor.py`, `test_step5b_broker_submission_safety.py`, `test_uef8_fair_comparison_validation.py`, `test_uef9_formal_authority.py`.
- Docs: P1.5 master plan, Fast Track, P1.5.7 Commander and P1.5.9 Executor packets, P1.5.11 final freeze packet, `docs/architecture/m20_langgraph_orchestration.md` (**historical design**; not proof of installed LangGraph runtime).

**Scope of this audit:** targeted repository directories/files and phase authority; **not** an exhaustive static call graph, empirical performance result or full-suite validation. Fill those gaps after P1.5 freeze rather than inventing them.

## 5. Targeted supplemental source review (2026-10-12)

Checked unfrozen `refactor/p1.5@fb8de628eb56b0941007e90ad2e98b4f684983ba` after original ancestry snapshot (source is moving; not a formal freeze). Key exact observations:

- `graphs/trading_graph.py::run_trading_graph` uses optional `hydrate` and `portfolio_guard` in the initial and retry paths; `approve` reaches `graphs/nodes/executor_node.py` stub, not a real broker. User-facing "7-agent graph" must **not** erase these intermediate nodes.
- `graphs/nodes/decision_node.py` is an eligibility screen; special BUY/SELL intent branches and `state.pop("decision_detail", None)` require explicit parity. This node must not be rebranded as Supervisor's final approval authority.
- `graphs/nodes/portfolio_guard_node.py` may replace `intents` and clear `selected`, so output-value and state-key presence compatibility are hard acceptance gates.
- `graphs/pipelines/m13_tick.py` defaults to integrated-chain orchestration; that live path **is not** equivalent to the isolated graph spine. M13 live load/reset/EOD/persist and SQLite runtime ownership stay untouched.
- `graphs/commander_runtime.py::run_commander_runtime` already provides a `graph_runner` DI seam; a later approved candidate can be evaluated there without rewriting whole Commander.
- `graphs/nodes/execute_from_packet.py` is 4,190 lines at this inspection and holds execution-capable guard/broker semantics; it is excluded from candidate engines. P1.5's Executor decomposition may change details before freeze.
- P1.5 candidate core functions (`run_strategist` etc.) are design targets, not assumed verified final symbols; resolve actual imports at acceptance.

See file-by-file change matrix and pseudo-code in [IMPLEMENTATION_BLUEPRINT.md](IMPLEMENTATION_BLUEPRINT.md) and [STATE_ROUTING_AND_ENGINE_DESIGN.md](STATE_ROUTING_AND_ENGINE_DESIGN.md). No exhaustive dynamic call graph, official benchmark or safety suite was run.
