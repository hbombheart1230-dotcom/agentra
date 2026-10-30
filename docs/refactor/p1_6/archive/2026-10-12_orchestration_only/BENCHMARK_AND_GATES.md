# P1.6 — Offline Benchmark, Acceptance and Safe Handoff

Status: TEST PLAN ONLY. **0 P1.6 benchmarks run; 0 P1.6 runtime/test dependencies modified.** All metrics/results below are *definitions*, not evidence.

## 1. Controlled comparison
Compare (A) current Agentra custom graph, (B) LangGraph 1.x, (C) pydantic-graph using the same **frozen P1.5 SHA**, Python/OS versions, fixture manifest and agent contracts. Pin actual framework versions at experiment start; do not claim current dependency APIs as installed. Separate warmup from measured runs, warm/cold starts, deterministic fixed seeds and repeated identical batches. Disclose unsupported capabilities as NOT SUPPORTED/NOT RUN rather than replacing them with different business logic.

**Phase-1 graph:** read/decision-only Strategist → Scanner → Monitor → Supervisor-decision projection. `Reporter` is observer, `Commander` controls routing; **Executor/Broker excluded**. Use recorded Strategist results/fake model rather than real LLM. In all engines, forbid network, real broker, production DB and real artifact writes.

## 2. Required fixture families
1. Normal Strategist → Scanner rank → Monitor intent → Supervisor decision.
2. No candidate, no intent, policy veto and protected hard-guard rejection.
3. Scanner low-confidence bounded retry, fallback and zero/one/multiple candidate handling.
4. Missing/stale/invalid market data; deterministic error paths and observation completeness.
5. Fast-path and `graph_spine`/`decision_packet`/`integrated_chain` routing snapshots (**compare only where behavior is defined and safely stubbed**).
6. State alias, missing/default key, tuple/list/date/DTO serialization and compatibility test cases.
7. Failure injection before/after each pure node, cancel, shutdown, crash/restart and checkpoint/resume.
8. Duplicate `intent_id` / replay / partial-complete outcome; **assert zero mutation authority and no repeated LLM or reporter write**, then separately run existing offline Step5C/guard tests without a new Executor implementation.
9. Reporter read-model/event lineage equivalence (`run_id`, `intent_id`, stage/reason, ordering, artifact references).
10. Concurrency only for independent READS, with identity/state conservation, cancellation and merge-order determinism.

Every fixture: manifest ID, input source hash, P1.5 SHA, mode, expected contracts/event sequence, forbidden side effects, output hash, result PASS/FAIL/BLOCKED. Genuine frozen production artifacts are used only if safely immutable/anonymized and independently verified; synthetic fixtures do not prove real-output parity.

## 3. Hard acceptance gates (must all pass, no weighted exception)
- **G0 Baseline:** accepted P1.5.11 freeze + recorded SHA/tag; no outstanding prohibited parity, authority or production-write blocker.
- **G1 Isolation:** all three candidates offline/disabled; 0 broker mutation, 0 cloud LLM, 0 production writes; isolated temporary roots, bounded retained failure evidence.
- **G2 Contracts:** public ABI, state key/DTO, candidate ordering, decision/guard reason, observable run lineage and relevant replay outputs exactly equivalent under documented normalization; no silent semantic improvements.
- **G3 Lifecycle:** configured retry/stop/cancel/failure recovery and cross-day reset equal; checkpoint/resume never implicitly repeats an unsafe side effect.
- **G4 Safety:** independent suites for Supervisor, Executor/Step5C/D, ownership, R6.2, UEF; hard guard precedence unchanged. Framework must not become new approval/broker authority.
- **G5 Operability:** Docker/mock source parity, scheduler/lease ownership, SIGTERM drain, incident tracing, rollback; do not infer green from an in-process toy graph.
- **G6 Independent verdict:** Claude implementation and Codex independent audit at pinned SHA; GPT+user explicit KEEP/ADOPT/DEFER decision. Failed/unrun gates are FAIL/BLOCKED, never nominal PASS.

## 4. Evaluation scorecard (only after hard gates)
| Dimension | Measurement / evidence |
|---|---|
| Behavior | exact output and transition parity rate, divergence ledger by fixture |
| Correctness & typing | contract coverage, static type/schema diagnostics, invalid state behavior |
| Recovery | checkpoint/resume correctness, recoverable read-only failures, retry bounds |
| Maintainability | orchestration/adapters LOC and file count, public API surface, duplicate glue, reviewer effort |
| Observability | stage/intent/run lineage completeness and divergence diagnostics |
| Runtime footprint | cold/warm startup, p50/p95 stage overhead, peak RSS/serialized state footprint |
| Compatibility | Windows/host/Docker, Python dependency conflicts, deployment/rollback delta |
| Cost & risk | maintenance burden, test speed, integration risk, version churn/upgrade policy |

Do not choose a library from feature marketing or synthetic throughput alone. A framework may bring better checkpoint tooling but require larger adapters; **retain custom runtime** if gains are small, ambiguous or safety becomes harder to verify.

## 5. Decision record and execution order
1. **Now:** only this design branch and documents. No test runs or dependency installation.
2. **After freeze:** reconcile P1.5 component interfaces/mode path/owner map; lock code SHA and fixture manifests.
3. **Offline:** build comparable sandbox proof, collect source-based benchmark and independent audit.
4. **Decision:** ADR `KEEP_CUSTOM` / `ADOPT_LANGGRAPH` / `ADOPT_PYDANTIC_GRAPH` / `DEFER`, with exact evidence, open debt and rollback conditions.
5. **Only with separate approval:** shadow observation behind default-OFF feature gate, non-mutating, no duplicate real LLM call/Executor.
6. **Any real integration is another change window:** new safety approval, full regression/Docker/UEF/ownership acceptance, restore-to-custom switch and user sign-off.

## 6. Reference material (evaluation topics, not framework lock)
- LangGraph Python guide: https://docs.langchain.com/oss/python/learn
- Pydantic Graph decisions: https://ai.pydantic.dev/graph/beta/decisions/
- Agentra historical graph spec: `docs/architecture/m20_langgraph_orchestration.md`
- Agentra formal acceptance spec: `docs/refactor/p1_5_full_regression_docker_uef_freeze_implementation_packet_v1_0.md`
