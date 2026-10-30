# P1.6 Detailed Implementation Blueprint — future code change map

> STATUS: **DESIGN ONLY / no implementation or testing** (2026-10-12). Branch `design/p1.6-orchestration` was created from `refactor/p1.5@62cdebf`. Further source inspection used **unfrozen** `refactor/p1.5@fb8de628eb56b0941007e90ad2e98b4f684983ba`. At P1.5.11 freeze, the implementation team MUST refresh each path/ABI against the formal freeze SHA before any code change. This document is a precise **proposed edit specification**, not an assertion that the target files exist.

## 1. Objective and hard boundaries

Implement **three comparable orchestration engines** on top of *the exact same frozen P1.5 agent components*; do not rewrite agent calculations. Reference engine: existing Python custom. Candidate engines: LangGraph 1.x, pydantic-graph. Decide KEEP/ADOPT/DEFER from evidence, not popularity. Executor/real trade mutation is outside the initial graph experiment. Do not create new LLM decision points, strategies, security authority, Docker owners or UEF writes.

### Source-verified existing entrypoints
- `graphs/trading_graph.py::run_trading_graph(state, *, strategist=None, hydrate=None, scanner=None, monitor=None, portfolio_guard=None, decide=None, executor=None)`. Its Python `dict` sequence is **strategist → optional hydrate → scanner → monitor → portfolio_guard → decision**, retry loop returns to **optional hydrate → scanner**, and `approve` calls the `executor_node` **stub** setting `execution_pending=True`. The stub does **not** place an order.
- `graphs/commander_runtime.py::run_commander_runtime(state, *, mode=None, phase=None, graph_runner=None, integrated_runner=None, preopen_runner=None, closeout_runner=None, decide=None, execute=None)`. Commander has `graph_spine`, `decision_packet`, `integrated_chain` routes and special phases/fast paths. The **existing `graph_runner` injection point** is the preferred future experimental seam.
- `graphs/pipelines/m13_tick.py::run_m13_tick` selects integrated chain (default) / legacy M10 and market-hours gating; `graphs/pipelines/m13_live_loop.py::run_m13_once` does load→market-status→transient reset→tick→EOD/report→persist. These are **not** graph-equivalent to standalone `run_trading_graph`.
- `graphs/nodes/decision_node.py::decision_node`: `approve/reject/noop/retry_scan` **eligibility only**, not Supervisor approval. `graphs/nodes/portfolio_guard_node.py` alters `intents`, `selected`, `blocked_intents`.
- `graphs/nodes/execute_from_packet.py::execute_from_packet(state)`: broker-capable, Supervisor/guards/readiness/Step5C/UNKNOWN outcome; **NEVER** wire into initial experimental engine.
- Existing Reporter node `graphs/nodes/reporter_node.py` calls real trade artifact generator; do not run it from a replay engine.

## 2. Future ADD file map (specific functions / responsibilities)

These paths are new **proposals** and must remain no larger than the applicable P1.5 new-Owner LOC limit (<=350 physical LOC). No production sources are modified until WO-16.6 authorization.

| Batch | Future file | Exact code to implement |
|---|---|---|
| 16.1 | `graphs/orchestration/__init__.py` | Stable export for offline `run_orchestration_candidate`; **zero import-time engine/broker/LLM actions**. |
| 16.1 | `graphs/orchestration/contracts.py` | `EngineName=Literal["custom","langgraph","pydantic_graph"]`; `OrchestrationRequest` (mode=`graph_spine`, `run_id`, `fixture_id`, `state`, forced `allow_side_effects=False`); `OrchestrationResult` (final state, node visits, failure); `NodeBinding`/ `StatePatch` type declarations. Reference frozen DTOs; no conflicting business DTO owner. |
| 16.1 | `graphs/orchestration/state_bridge.py` | `split_runtime_state()`, `legacy_state_delta()`, `apply_legacy_state_patch()`, `compare_legacy_state()`. Support mutation + deletion + **key absence versus None**. Opaque clients/handles kept out-of-band. Preserve state aliases/ordering and nested decision data exactly. |
| 16.1 | `graphs/orchestration/node_bindings.py` | One injection registry for `strategist/hydrate/scanner/monitor/portfolio_guard/decide/mark_execution_pending`. Post-freeze adapters call P1.5 standalone agent functions; experiment can bind safe existing node facades as fixtures; hard fail on real executor or broker injection. |
| 16.1 | `graphs/orchestration/route_contract.py` | `should_hydrate(state)`; `next_after_decision(state)` pure selector preserving current `use_skill_hydration or skill_runner`, `retry_scan` and `approve` semantics. **No new retry semantics.** |
| 16.2 | `graphs/orchestration/engines/__init__.py` | Package marker; no dependency import to canonical production. |
| 16.2 | `graphs/orchestration/engines/custom.py` | `run_custom(request, bindings)` wraps frozen `run_trading_graph` with injected safe nodes; produce normalized result as reference truth. |
| 16.3 | `graphs/orchestration/engines/langgraph_engine.py` | `build_langgraph(bindings)` using `StateGraph`, explicit edges and conditional routing, `compile()`; `run_langgraph(...)` with isolated state. No graph-side `RetryPolicy` or live checkpointer. |
| 16.4 | `graphs/orchestration/engines/pydantic_engine.py` | `build_pydantic_graph(bindings)` using pinned `pydantic_graph.beta.GraphBuilder`, `@step`, `StepContext`, decision branches, final typed result; `run_pydantic_graph(...)` handles async at outer benchmark only. |
| 16.5 | `graphs/orchestration/runner.py` | `run_orchestration_candidate(request, bindings, engine)`; validates fixture-only input, rejects modes other than graph_spine; lazy import optional engine. |
| 16.5 | `graphs/orchestration/checkpoint_policy.py` | `checkpointable_state()` and `verify_replay_preconditions()`; only serializable **offline decision data**. No broker/auth credential/approval/ownership state. |
| 16.5 | `graphs/orchestration/event_projection.py` | `project_node_visits()` into comparable **observation-only** run/intent lineage; no original `events.jsonl` writer or reporter recomputation. |
| 16.5 | `scripts/benchmark_p16_orchestration.py` | Offline CLI `--fixtures`, `--engine all|custom|langgraph|pydantic_graph`, `--repeat`, `--output <isolated path>`; capture stdout/stderr exit status, frozen SHA/lib version/fixtures and p50/p95/RSS/patch divergences. Never read or write production paths. |
| 16.5 | `tests/p16/fixtures/manifest.json` | Fixture IDs/input SHA/expected route/side-effect blocklist; actual frozen production copy provenance separately classified if available. |
| 16.5 | `tests/p16/conftest.py` | isolated pytest tmp roots, forbidden network/broker/LLM/prod writes, injected pure Agent stubs. |
| 16.5 | `tests/p16/test_state_bridge.py` | absent-vs-None, `decision_detail` deletion, nested mutations, lost `intents` and ranking, opaque handle rejection. |
| 16.5 | `tests/p16/test_graphspine_parity.py` | custom/LangGraph/Pydantic same initial/retry/approve/noop/portfolio guard/hydrate outputs and call order; pure execution_pending marker only. |
| 16.5 | `tests/p16/test_engine_failure_recovery.py` | crashes injected at each node; resume pure state; STOP and retry budgets; zero duplicate side effects. |
| 16.5 | `tests/p16/test_authority_firewall.py` | explicit negative test: `execute_from_packet`, live broker, Supervisor approval mutation, real Reporter and LLM injection cannot be bound. |
| 16.5 | `tests/p16/test_mode_boundaries.py` | `decision_packet`, `integrated_chain`, preopen/closeout, M13 never rerouted by benchmark engine; no implicit live override. |
| 16.5 | `tests/p16/test_dependency_imports.py` | canonical custom imports work with new optional packages absent; Windows and Docker versions checked after P1.5 freeze. |
| 16.6 | `docs/decisions/ADR-0004_P16_Orchestration_Engine_Decision.md` | evidence-based KEEP_CUSTOM / ADOPT_LANGGRAPH / ADOPT_PYDANTIC_GRAPH / DEFER. Created only AFTER measurements. |

## 3. Conditional MODIFY map — NOT automatic in P1.6.1–16.5

| Existing file | Future change only if ADOPT authorized | Preserved behavior |
|---|---|---|
| `graphs/commander_runtime.py` | Use existing `graph_runner` injection seam to call selected runner **for graph_spine only**, under disabled-by-default flag after separate approval. Prefer external binding over changing canonical implementation at first. | Existing default `run_trading_graph`, all integrated-chain/packet branches and Commander decision evidence remain identical. |
| `graphs/trading_graph.py` | Optional compatibility delegate ONLY if consumer-proof + byte/semantic parity; safer default: **no edits**. | Public `run_trading_graph` name/signature/injection points unchanged. |
| `libs/runtime/entrypoints/commander_runtime_once.py` | Add explicit non-live offline/shadow option after acceptance, only if needed. | Existing CLI default unchanged, no scheduler change. |
| `requirements.txt` | Avoid initially; place pinned benchmark dependencies in proposed `requirements-orchestration-bench.txt`, promote selected library only if formally approved. | Existing runtime can boot without optional framework. |
| `docs/unified_runtime_spec.md` | Update after accepted engine decision and operational evidence only. | Historical docs never overwritten. |
| `docs/trading_agent_patch_notes_detailed_update/{patch_notes.json,patch_notes.md}` | Append UI-linked entries per meaningful implementation/document change; add `docs/daily_patch/` delta. | Historical patch history preserved. |

### Must NOT modify in initial P1.6
`graphs/nodes/execute_from_packet.py`, `libs/execution/**`, `libs/risk/supervisor.py`, `libs/runtime/{runtime_ownership,live_loop_runner,runtime_mode}.py`, `graphs/pipelines/{m13_tick,m13_live_loop}.py`, `graphs/nodes/{strategist,scanner,monitor,portfolio_guard,decision,executor,reporter}_node.py`, business owners in `libs/runtime/commander/**`, existing UI/reporter/UEF/Step5C/D/R6.2. Use injection and adapters, not business rewrites.

## 4. Seven agents vs graph wiring (do not conflate)
- **Commander**: outside engine, deterministic mode/phase/cancel routing. No LLM.
- **Strategist**: P1.5 core + existing LLM, but experimental replay uses *recorded output* (never another live LLM call).
- **Scanner**: frozen candidate rank, guidance, soft/hard boundary; read-only fixture.
- **Monitor**: intent-only, no order side effects.
- **Supervisor**: existing policy/approval is independent. `decision_node` is **NOT** the Supervisor; compare Supervisor as separate read-only projection only with valid frozen fixture, never add as an unverified step to custom baseline.
- **Executor**: real mutation owner remains outside graph; experimental endpoint may set only `execution_pending=True` for graph-spine parity.
- **Reporter**: post-run observations on already captured evidence only; never regenerate real reports from shadow.

## 5. Post-freeze readiness gate for these file names
After P1.5.11, verify actual callable functions, state adapter paths, monkeypatch symbols, state key write/delete ledger, exact modal branch graph and witness fixtures. If final P1.5 file locations differ, record a `PATH_DRIFT` addendum and adjust only the proposed targets; **do not** import a guessed Agent package or treat this document as permission to cut over.
