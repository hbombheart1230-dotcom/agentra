# P1.6 State / Router / Engine Design — code-level specification

**DESIGN ONLY**; no Python added. Verify all APIs again against frozen P1.5.11 and pinned library versions.

## 1. Compatibility state + public experimental interface

```python
# PROPOSED: graphs/orchestration/contracts.py (illustrative, not executable)
EngineName = Literal["custom", "langgraph", "pydantic_graph"]

@dataclass(frozen=True)
class OrchestrationRequest:
    run_id: str
    fixture_id: str
    state: Mapping[str, Any]
    mode: Literal["graph_spine"] = "graph_spine"
    allow_side_effects: Literal[False] = False

@dataclass(frozen=True)
class NodeVisit:
    node: str
    ordinal: int
    decision: str | None
    reason: str | None
    input_sha256: str
    output_sha256: str

@dataclass(frozen=True)
class OrchestrationResult:
    engine: EngineName
    final_state: Mapping[str, Any]
    visits: tuple[NodeVisit, ...]
    status: Literal["completed", "failed", "blocked"]
    error_code: str | None = None
```

Prefer P1.5's accepted canonical AgentInput/Result for individual agents. These proposed dataclasses describe the graph *experiment envelope*, not replacement business DTOs.

```python
# PROPOSED GraphBindings interface; all handlers MUST be fake / safe offline
GraphBindings(
    strategist: Callable[[dict], dict],
    hydrate: Callable[[dict], dict],
    scanner: Callable[[dict], dict],
    monitor: Callable[[dict], dict],
    portfolio_guard: Callable[[dict], dict],
    decide: Callable[[dict], dict],
    mark_execution_pending: Callable[[dict], dict],
)
# NEVER provide execute_from_packet, real broker, approval write API, live Reporter.
```

Function requirements for proposed `state_bridge.py`:
- `split_runtime_state(state, fixture_manifest)` = separate serializable, allowlisted values from injected callable/logger/client handles; **reject** live bearer tokens, account secrets and production-path inputs, rather than stringify unknown objects.
- `legacy_state_delta(before, after)` = record SET, DELETE and mutating nested paths; recursively compare with explicit type equality. Source may mutate input in-place, so take a **safe fixture snapshot** before invocation.
- `apply_legacy_state_patch(state, changes)` = accurately reconstruct legacy dict including missing vs `None`; do not force defaults.
- `compare_legacy_state(expected, actual, declared_exclusions)` = failure ledger; exempt only measured nondeterministic timestamps already documented in frozen baseline, never rank/intent/decision/safety fields.

Do NOT serialize/copy real `EventLogger`, `Supervisor`, `executor`, `skill_runner`, sockets, futures, credentials or locks. Inject safe stand-ins at use time. This also protects monkeypatch seams.

## 2. Exact graph-spine transitions confirmed from code

```text
START → strategist
strategist
   ├ if bool(use_skill_hydration) or bool(skill_runner) → hydrate → scanner
   └ otherwise                                       → scanner
scanner → monitor → portfolio_guard → decision
decision
   ├ retry_scan → optional hydrate → scanner → monitor → portfolio_guard → decision
   │                  (Strategist is NOT rerun)
   ├ approve    → graph Executor **STUB** (execution_pending=True) → END
   └ reject/noop/anything else → END
```

**Source nuance:** `decision_node` itself updates `retry_count_scan`; graph spine's `while decision == retry_scan` has no independent step cap. A test-injected bad decide could loop forever. Apply the **same** outer watchdog to all candidates during benchmark and record the limitation as a baseline defect; don't silently change just one engine's retry logic.

Other source nuances the graph must preserve:
- `decision_node` removes `decision_detail` at entry with `state.pop`; a state update framework without deletes will diverge.
- EXIT intents (and specific Monitor BUY intents) have dedicated decision behavior; do not replace with generic score threshold.
- `portfolio_guard_node` can filter `intents` and clear `selected`; don't skip it to reach “7 nodes” marketing diagram.
- `hydrate` behavior checks truthiness of `use_skill_hydration` **or** `skill_runner`; retain both.
- Returning `approve` at this layer never bypasses real Supervisor/Executor; graph has only a pending stub.

Proposed pure routing:
```python
def should_hydrate(s):
    return bool(s.get("use_skill_hydration")) or bool(s.get("skill_runner"))

def route_after_decide(s):
    d = str(s.get("decision") or "noop").lower()
    if d == "retry_scan":
        return "retry_hydrate" if should_hydrate(s) else "retry_scan"
    if d == "approve":
        return "mark_pending"
    return "end"
```

## 3. LangGraph candidate — exact implementation sketch

```python
# PROPOSED graphs/orchestration/engines/langgraph_engine.py
# Validate state update/deletion with frozen fixtures before implementing this.
from langgraph.graph import StateGraph, START, END

g = StateGraph(CompatibleState)
g.add_node("strategist", bind("strategist"))
g.add_node("hydrate", bind("hydrate"))
g.add_node("scanner", bind("scanner"))
g.add_node("monitor", bind("monitor"))
g.add_node("portfolio_guard", bind("portfolio_guard"))
g.add_node("decision", bind("decide"))
g.add_node("mark_pending", bind("mark_execution_pending"))
g.add_edge(START, "strategist")
g.add_conditional_edges("strategist", should_hydrate,
                        {True: "hydrate", False: "scanner"})
g.add_edge("hydrate", "scanner")
g.add_edge("scanner", "monitor")
g.add_edge("monitor", "portfolio_guard")
g.add_edge("portfolio_guard", "decision")
g.add_conditional_edges("decision", route_after_decide,
                        {"retry_hydrate": "hydrate",
                         "retry_scan": "scanner",
                         "mark_pending": "mark_pending",
                         "end": END})
g.add_edge("mark_pending", END)
candidate = g.compile() # OFFLINE, no durable live order checkpoint
result = candidate.invoke(frozen_state)
```

**Not yet tested:** LangGraph's state-channel/reducer semantics must be proven to handle mutation, SET/DELETE, absent keys and exact old output. A naive `TypedDict` that drops extra keys fails. If faithful compatibility requires unreasonable scaffolding, score negatively or DEFER; no silent compatibility rewriting.

## 4. Pydantic Graph candidate — concrete API and trade-offs

At benchmark time pin and verify `pydantic_graph.beta`:
- `GraphBuilder(state_type=..., output_type=...)`
- `@g.step` and `StepContext` for steps
- `g.edge_from(...).to(...)`, `g.decision().branch(g.match(...).to(...))` for routing
- `g.build()`, `graph.run(state=...)` inside one controlled async runner.

Construct steps for strategist/hydrate/scanner/monitor/portfolio_guard/decision/pending using **the same injected binding and state bridge** as LangGraph, not a separate Scanner/Supervisor rewrite. Decisions returning Literal "retry_hydrate" / "retry_scan" / "mark_pending" / "end" must follow branch priority and exact retry timing. Bridge to sync caller *outside* M13/Commander. If the beta API changes, update this proposal after pinning — do not silently call deprecated methods.

Official evaluation references:
- https://docs.langchain.com/oss/python/learn (LangGraph StateGraph concepts; API pin at implementation)
- https://ai.pydantic.dev/graph/beta/decisions/ (GraphBuilder/decision matching; API pin at implementation)

## 5. Mode coverage: what P1.6 may and may not reroute

| Mode or phase | Actual path / scope | P1.6 handling |
|---|---|---|
| `graph_spine` | `graphs/trading_graph.py` | Full 3-engine offline functional parity candidate. |
| `integrated_chain` | `graphs/commander_runtime.py::_run_integrated_chain_impl` | **No replacement** in P1.6 initial phases; capture read-only precomputed stage traces for coverage. |
| `decision_packet` | Commander → `decide_trade` → `execute_from_packet` | **Hard exclusion** from candidate execution; observe recorded decision/outcome only. |
| `preopen`, `closeout` | Commander phase-specific/fast-path routes | Existing runtime only, negative tests prevent interception. |
| M13 daily loop | `run_live_loop` + `run_m13_once` + `run_m13_tick` | Existing ownership, market clock, load/store, EOD/report and shutdown untouched. |
| Reporter | Real reporting, LLM optional | Compare captured final artifacts/lineage offline, never rerun real Reporter in candidate. |
| Supervisor/Executor | Real authority + Step5C/UNKNOWN | Remain outside all candidate checkpoint/resume/retry mechanisms. |

## 6. Checkpoint/resume/failure isolation

Checkpoint data is scoped by `fixture_id + freeze_SHA + engine/version + run_id + invocation_id + step`. Persist only pure fixture decision data and frozen outputs. `thread_id`, if used, is trace identity only, never a new broker `intent_id` or SQLite order journal.

A crash before/after a **pure** node may resume from the prior checkpoint; assert same output, stage order and no duplicate evidence. For Strategist, use recorded LLM outputs (no new paid/live call); for Reporter, recorded read-only artifact views. Resume/retry of Supervisor persisted approvals, Executor, Step5C/5D, broker UNKNOWN or live ownership **must always be denied**. Fail closed on invalid/unserializable state; do not resume a live order.

Shadow mode is a separate future user decision: it may replay captured **canonical output packets**, not rerun a second live Strategist model or market scanner. Default engine selection remains existing custom; missing/unknown flags cannot enable another execution path.

## 7. Rollback and state correctness criteria

- Keep old `run_trading_graph` signature/import stable. Stage new engines under optional modules only.
- Choose framework only when output hash/decision/rank/guard reasons, patch SET/DELETE, run/intent lineage, retry sequence and failure policy are identical under explicit normalization.
- Failure to reproduce a key, post-restart state, cancellation or safety property is FAIL/DEFER, even if latency/LOC improves.
- If ADOPT accepted later, integrate through Commander `graph_runner` DI behind default-OFF flag. *Never* replace `execute_from_packet` with a graph node that directly orders.
