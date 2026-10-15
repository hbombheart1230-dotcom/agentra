# P1.6 — Orchestration Modernization (DESIGN ONLY)

**Status:** DESIGN/PREPARED, NOT IMPLEMENTED, NOT ACCEPTED (2026-10-12)  
**Branch:** `design/p1.6-orchestration`  
**Source snapshot:** `refactor/p1.5@62cdebf63e295765ca546a0e6ffb569f7aba0bdb` (P1.5 WIP, **not** P1.5 freeze)  
**Canonical repository:** `hbombheart1230-dotcom/agentra` (former `Trading_Agent_System` name redirects)

P1.6 evaluates the orchestration *of the existing seven agents*, not the trading algorithms. A new graph engine is an option, not a predetermined decision.

## Read in this order
**Implementation-grade blueprint added 2026-10-12 (still PRE-DESIGN, not implemented):**
- [IMPLEMENTATION_BLUEPRINT.md](IMPLEMENTATION_BLUEPRINT.md): concrete future ADD/MODIFY/KEEP file paths, functions, interfaces and locked boundaries.
- [STATE_ROUTING_AND_ENGINE_DESIGN.md](STATE_ROUTING_AND_ENGINE_DESIGN.md): state patch/delete semantics, exact graph routing, LangGraph/Pydantic candidate code sketches and checkpoint policy.
- [BUILD_PACKETS_AND_TEST_MATRIX.md](BUILD_PACKETS_AND_TEST_MATRIX.md): WO-16.0–16.6, per-file tests, acceptance/rollback and agent handoff.
These are proposed changes, not code commits. Additional code inspection: `refactor/p1.5@fb8de628eb56b0941007e90ad2e98b4f684983ba` (WIP). Reconcile with accepted P1.5.11 freeze SHA before development.

1. [MASTER_PLAN.md](MASTER_PLAN.md) — program boundary, major phases and go/no-go.
2. [CODE_AUDIT.md](CODE_AUDIT.md) — source-backed entrypoints, mode split, authority boundaries and gaps.
3. [BENCHMARK_AND_GATES.md](BENCHMARK_AND_GATES.md) — comparable experiments, freeze gates and acceptance.

## Authority and isolation
- This design branch **does not supersede** `docs/refactor/work_orders/CURRENT.md` or alter Claude's P1.5 implementation scope. Existing P1.5 single-implementation-branch rule remains for code work; this **user-requested, documentation-only P1.6 exception** may not be used as a new implementation/worktree branch.
- `main` and `refactor/p1.5` are unchanged by P1.6 planning. Do **not** merge this branch, run a shadow engine, install dependencies, touch broker/LLM/live Docker/host, or modify production state.
- Before any P1.6 executable proof, P1.5.11 must formally freeze with full regression, actual provenance/LLM parity as applicable, UEF/Docker/authority/write isolation, and GPT+user acceptance. Reconcile this snapshot against the eventual freeze SHA **by explicit review**, not blind rebase or merge.
- Agentra workflow: GPT architecture → Claude implementation → Codex independent audit → GPT/user acceptance. Keep Agentco separate.

**DELIVERABLE NOW:** code audit + overall plan **and implementation-grade file/function-level blueprint**. Zero runtime/test/config/dependency changes; P1.6 implementation and benchmark are NOT RUN.