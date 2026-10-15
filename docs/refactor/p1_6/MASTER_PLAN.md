# Agentra P1.6 Master Plan — Orchestration Modernization

Status: DESIGN ONLY / PRE-FREEZE PLANNING | 2026-10-12  
Pinned code reviewed: `refactor/p1.5@62cdebf63e295765ca546a0e6ffb569f7aba0bdb`  
Program authority: `docs/refactor/p1_5_p1_6_master_plan.md` + `P15_FAST_TRACK_FIRST_PASS_2026_10_12.md`

## 1. Goal and decision to make
Evaluate whether **current custom runtime**, **LangGraph 1.x**, or **pydantic-graph** better orchestrates the *same* Agentra components. Prefer existing code unless a replacement shows meaningful maintainability/recoverability benefit with full safety, contract, artifact and behavioral parity. P1.6 is not a strategy/alpha/LLM expansion and must not create a new execution path.

**Fixed seven roles:** Commander, Strategist, Scanner, Monitor, Reporter, Supervisor, Executor. Existing operational topology/mode routing takes precedence over any attractive framework diagram. Initial **read/decision-only** shadow comparison covers Strategist → Scanner → Monitor → Supervisor conceptually; Reporter is an observation sink; Executor and Broker are **out of scope for first benchmark**.

## 2. Non-negotiable invariants
- Agents propose; **Monitor never orders**. Supervisor/approval and Executor/Execution Layer remain distinct. Approval is not broker authority; final guards can always block.
- `intent_id` and Step5C CAS/idempotency stay authoritative. No checkpoint/replay/retry may duplicate an order, issue fresh implicit approval or bypass UNKNOWN quarantine, R6.2, Step5D, or protected Supervisor/Executor mutation chain.
- Runtime ownership lease, Host-vs-Docker gating, cancellation/SIGTERM drain, safe shutdown, state transitions and existing `graph_spine` / `decision_packet` / `integrated_chain` routing remain behaviorally identical.
- Stable public façade/IO/DTO/state-key contracts, selection rank, hard timing, policy order, LLM model/prompts/calls/timeouts, reporter/provenance artifact formats, `run_id` and trace identity. No new LLM decision role or strategy.
- Safe default: fail closed. Only isolated mock/replay; zero real orders, zero live cloud LLM, zero production file/SQLite/report writes. Tests create bounded temporary artifacts only.

## 3. Work packages — large-grain roadmap

### P1.6-A — Freeze handoff and framework-neutral baseline
**Before executable work:** P1.5.11 accepted/frozen; pin exact commit, versions, normalized input/output contracts, single Owner per agent, caller/monkeypatch compatibility matrix, runtime paths and policy state. Repair only proven handoff gaps via separately authorized P1.5 work. Re-read only the current frozen deltas, not the entire project history.

### P1.6-B — Three-way offline orchestration benchmark
At the accepted freeze SHA, run the **same immutable input fixtures** and injected agent stubs on: (1) custom runtime, (2) LangGraph 1.x, (3) pydantic-graph. Only explicit state patches and pure decisions; no broker, online data or actual LLM. Compare deterministic output equivalence, transitions, event lineage, failure behavior, dependencies, complexity, startup/step overhead and operability. Do not mix P1.5 business refactor into framework changes.

### P1.6-C — Lifecycle and operability stress comparison
Exercise no-candidate/noop, retry boundedness, partial failure, restart/resume, stop/cancel, parallelism **only for independent reads**, replay, checkpoint serialization, cross-day state isolation and operator traceability. A framework's built-in checkpoint is **not** an order journal and never replaces Step5C/ownership lease. Default comparison remains side-effect free; test Executor safety only via non-mutating contract checks and separate existing offline guard suites.

### P1.6-D — ADR, optional shadow and rollout design
Publish a scored decision record (retain custom runtime is valid). Only if a contender materially improves the required dimensions with all hard gates green: propose an explicitly authorized **shadow-only** graph behind a disabled flag. Compare against existing runtime; no duplicated Strategist live LLM calls and **never** run two broker mutation-capable runtimes. Production cutover/rollback requires a separate risk review, Docker/UEF/ownership replay validation and user approval. No implied go-live.

## 4. Outputs to decide upon
- Source-to-agent/transition map and immutable fixture manifest.
- Three-way benchmark table with version pins, code/config hashes, exact metric definitions and measured numbers (**none exist yet**).
- Parity/guard/write-isolation matrix with PASS/FAIL/NOT RUN and independently reproduced evidence.
- ADR: KEEP_CUSTOM / ADOPT_LANGGRAPH / ADOPT_PYDANTIC_GRAPH / DEFER. No winner designated today.
- If ADOPT: migration plan, rollback plan and explicit separately approved execution boundary.

## 5. Boundaries to neighboring programs
P1.5 finishes modular structure; P1.6 is **orchestration only**; P2/2.E6 integrates Q10/Q12/US/SOX/BTC/JPY regime and strategy inputs after structural freeze. Safety 5D→5E→6, Q100/Reporter v2, research and evidence memory retain their own stage authority. Avoid accidental scope absorption.

## 6. Immediate decision
**PREPARED, NOT STARTED.** P1.5 Fast Track Wave A remains active and P1.5.2 final parity is open. P1.6 documentation can coexist without touching active code; implementation, benchmark runtime and dependency changes are BLOCKED pending formal P1.5.11 freeze.

## 7. Concrete future implementation authority (2026-10-12 supplement)

The prior A–D roadmap is the **program-level structure**, not sufficient for a handoff on its own. The following detailed approved-for-design-only artifacts specify actual future files, functions, state handling and tests:

- [Implementation Blueprint](IMPLEMENTATION_BLUEPRINT.md): proposed new `graphs/orchestration/` modules and tests, exact change/no-touch table, optional future `graphs/commander_runtime.py` graph_runner seam.
- [State, Routing & Engines](STATE_ROUTING_AND_ENGINE_DESIGN.md): real graph-spine sequence including hydration, portfolio_guard, decision vs Supervisor, deletion semantics, example LangGraph wiring and Pydantic Graph matching, checkpoint safety.
- [Build Packets & Tests](BUILD_PACKETS_AND_TEST_MATRIX.md): handoff tasks WO-16.0–16.6 with files, acceptance, failure and rollback.

No P1.6 Python file, test, requirement or production config is changed by this update. The plan must be reviewed against the formally accepted P1.5.11 SHA before coding.
