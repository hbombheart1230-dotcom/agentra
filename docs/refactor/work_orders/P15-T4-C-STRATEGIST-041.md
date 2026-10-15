# P1.5 THIRD PASS — T4-C Strategist coherent structural extraction (Claude)

**Status:** READY / AUTHORIZED STRUCTURAL DEVELOPMENT ONLY — NOT IMPLEMENTED. **Base SHA:** `4e242e5b1fc609b0ec012e0c6faed37b202e4aa0` (T4-B Codex ACCEPT, final CI `38664980307` SUCCESS). When this documentation commit advances the HEAD, Claude must fetch and pin the actual newest `origin/refactor/p1.5` SHA as its BASE; do NOT use the historic task SHA blindly.

**Roles:** Claude implementer → Codex independent audit → GPT/user acceptance. Branch `refactor/p1.5` only, isolated clone, no new feature branch, no touching live `C:\Agentra` / dirty Q12 worktrees / main.

## Context minimization

Read `docs/refactor/work_orders/CURRENT.md` -> this one task -> `docs/refactor/work_orders/COMMON_RULES.md`; only `docs/refactor/P15_THIRD_PASS_GPT_REPORTER_INCLUSIVE_DESIGN_2026_10_13.md` phase T4 and direct Strategist source/consumers/tests. Do not reread T0–T4-B archives, T4-A/B fixtures or earlier audit logs unless a failure forces an exact dependency lookup.

## Scope

Primary target: `graphs/nodes/strategist_node.py::strategist_node` (at T4-B HEAD approx **1,216 body LOC**, begins around line 3461; physical source file ~4,676 lines). Partition **coherent deterministic responsibilities**, not arbitrary 100-LOC chunks:

- Candidate/universe selection and fallback **plans/values** (do not move generator IO, change fallback precedence or State writes).
- Market/global sentiment, theme/memory/news **input/read-model projections**, preserving clock, fallback exceptions, news provider invocation order and event-trace order in the node.
- Deterministic strategy/frame policy normalizations, selected/scanner guidance and monitor entry/exit policy projections, keeping **Scanner canonical ranking/Rank-1 authority** unchanged.
- Pure Strategist output/evidence and event-payload builders, preserving dictionary key insertion order, output schema, downstream Commander/Scanner/Monitor consumers and exact state patch order.
- Prefer existing `libs/runtime/strategist/{context,policy,output}/` owners. Create new semantic owners (<=350 LOC) only for genuine single responsibility; do not duplicate logic already extracted or create circular imports. Do NOT create `service.py` or rename files purely to mimic target tree; post-T4 architecture visual review controls that work.

**SAFETY_LOCK — leave at original call boundary:** Frame LLM `_run_strategist_frame_llm` and all LLM prompts/messages, selected model/provider, timeout/retry/fallback, call counts, and result insertion order. Real LLM not used. Do not move environment/clock/UUID calls, news/network IO, persistence, event emission or State mutation out of the node unless explicit separately approved immutable evidence proves parity. No new model/agent decision role.

## BEFORE touching implementation

1. Inspect remote HEAD and working-tree cleanliness; record BASE_SHA, source/function LOC and existing owner matrix.
2. Freeze real BASE-derived **Mock/offline** Strategist contracts in a dedicated immutable fixture commit, **before** code changes. Include cases: empty and fallback universe, global/news exceptions, risk-on/off, missing/stale memory, theme/news, policy overrides, mock LLM success/error/timeout/fallback with zero external calls, empty/duplicate candidates, output contract and event order.
3. Oracle must verify deterministic full State (including key order), exact output/return identity, ordered effects with argument digests, exceptions, and selected symbol/rank authority non-interference. Platform-bound cases use same-host pinned BASE, **no normalization that masks a differential**. Variant inventory must be conserved bidirectionally, missing/malformed golden/BASE/FEATURE fail closed.

## Implementation and gates

- Perform sizeable verbatim AST reconstructable extraction with use-time facade lookups for existing monkeypatch seams; ensure native mutation, exception and LLM order remain the same. Ledger each extracted chunk and prove inlining recovers BASE AST; untouched defs remain AST-identical.
- Explicitly test **mock LLM call count, request payload ordering and fallback** with injected fake providers, not actual LLM/network. If true frozen request/response is unavailable, report `REAL_LLM_PARITY_NOT_RUN`, never PASS. REAL_REPORT_PARITY_BLOCKED stays OPEN.
- Preserve Scanner rank-selection, handoff to Monitor, Commander policy precedence, cross-agent contract and event log order. No new trading policy, BUY/SELL effects, broker calls, Docker restart, production data/reports writes, Supervisor/Executor/Step5C changes or shadow authority.
- Run focused Strategist tests, offline Strategist→Scanner/Commander/Monitor consumers, historical/current P1.5 gates, new structural/behavior replay, on Windows native + Linux same-host BASE portable gates. Strict JUnit accounting for required tests. Full-corpus replay is not replaced by a sample-only claim; keep counts distinct.
- Session-isolated pytest outputs, no unbounded repo artifacts; successful temporary results cleaned and failed evidence bounded.
- Required GitHub CI on final **CODE SHA** Linux and Windows SUCCESS; audit the final docs-only CI separately (if still pending, label pending, never claim verified).

## Delivery and stop condition

Commit/push only `refactor/p1.5` after remote-head check. Update `CURRENT.md`, T4-C evidence, daily patch and both UI-linked patch notes JSON/MD. Record BASE/FREEZE/CODE/FINAL SHA, changes and owner matrix, LOC, full variant counts, AST results, LLM call parity, State/event parity, tests and CI including skipped/unrun, deferred SAFETY_LOCK. **Stop before T4-D, T5, P1.5.10, Wave D or layout reorganization**; Codex must independently audit this T4-C SHA.

Mandatory future convergence gate remains `docs/refactor/P15_POST_T4_ARCHITECTURE_VISUALIZATION_GATE_2026_10_15.md`. Do not produce or implement target diagrams while T4 structural extraction is underway.
