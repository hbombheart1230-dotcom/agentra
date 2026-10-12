# P15-R3 — CODEX Independent Audit (active)

**Role:** Codex independently audits; Claude implemented; GPT/user accepts. **READ ONLY** on code/tests/feature history. Do not merge, push code fixes, restart runtime, use live broker/LLM, or touch live `C:\Agentra` / dirty Q12 worktrees.

**Pinned task baseline:** `ba6618d483e6d617f4ee56b2cb5647392c777071`
**Pinned Claude review SHA:** `e41d42d754dba9d538fba0fa2dda969d6ea83f02`
**Pinned runtime source SHA:** `321eabb5b83a6aa4eb912cadaf6436a82214a848`
**Branch:** `feature/p152-facades-r3`. Audit the pinned code, not later documentation commits.

## Mandatory checks
1. Diff and 436 façade ABI/contracts, 57 moved bodies, monkeypatch seams, import DAG, LLM/trading authority boundaries and untouched production paths.
2. Inspect call-entry `facade` global captures vs original use-time lookup, including callbacks/nested functions/recursion and mutation during a single call. Mark actual semantic risks, not blanket parity.
3. Assess cohesion and domain naming: `bodies_01..05.py` is a temporary numbered grouping, not proven single-responsibility architecture. Recommend narrowly scoped fixes only if needed.
4. Reconcile Story Owner reported 271 LOC versus pinned `trade_story_facade_r3_parts/bodies_01.py` observed 102 physical LOC; verify file SHA, provenance and ledger.
5. Run independent isolated mock/offline ABI, focused tests and *before-vs-after same synthetic fixture differential* for representative Story/Markdown/AI outputs and mock LLM call/retry/fallback traces. Never call real LLM/broker, write real reports or invent historical snapshots.
6. Verify new Owners <=350 physical LOC, source scope, 0 production-path writes, unchanged test strength, patch notes parity and stale `CURRENT` state removed.

## Evidence and verdict
Record exact SHA, commands, PASS/FAIL/SKIP, LOC, real-data/LLM parity **NOT RUN** if frozen pre/post unavailable, full pytest **NOT PASS/INCOMPLETE** until proven otherwise. Return **PASS / PASS_WITH_FINDINGS / FAIL / BLOCKED** and minimal actionable deltas for Claude. Report externally/read-only unless separate evidence-only commit is explicitly authorized.

**Do not integrate to `refactor/p1.5` or main. P1.5.2 OPEN; P1.5.3 NOT AUTHORIZED.**
