# Strategist P1.5 — GPT Architecture Decision: S1/S2 only

**Date:** 2026-10-17 KST  
**Author:** GPT (ordinary ChatGPT, architect on demand).  
**Status:** S1/S2 TEST_AND_EVIDENCE_ONLY_APPROVED; S3-S6 SOURCE_CHANGES_NOT_AUTHORIZED.  
**Read-only evidence SHA:** `d8b34e669e1c43342eadd80b13ea43aac4bc255b` on `evidence/p15-strategist-readonly-20261017`.  
**Source snapshot used by inventory:** `d773709ba2f70471fad9badba4f92400f7818319`, asserted to have no libs/graphs/apps/scripts/tests diff vs historical integration `d269c906`. Recheck against **actual current assembly SHA** before implementation.  
**Claude lane:** independent Reviewer of Codex shared integration is P1; Strategist S1/S2 can run only on a separated test/evidence branch and within an explicit budget.  
**Active architecture:** `11_P15_TWO_WORKER_ARCHITECT_ON_DEMAND_20261017.md`.

## A. GPT assessment of Claude's draft

The inventory has 156 top-level defs in `graphs/nodes/strategist_node.py`, of which 104 are R3 style dynamic facade wrappers. Of the 52 residual non-wrappers, 23 were heuristically flagged effect/authority (2,290 LOC) and 29 were flagged potential pure/helpers (393 LOC). The **29 count is NOT 29 independently proved pure/movable definitions**: `_resolve_strategist_frame_llm_strict_enabled` may consult env through `_env_bool`; `_condition_search_source_enabled` may cross network/data policy. Output labels such as `_trade_aggressiveness` also affect strategy interpretation; a pure function can still be policy-sensitive. Do not infer source-transfer authorization from token heuristics.

Existing ownership includes 39 implementation modules in `libs/runtime/strategist` (13 context, 9 output plus LLM/policy groups) and five S1-057 canonical Agent owner modules with strict identity shims; do not repeat these older migrations. `StrategistOutput` in `libs/strategies/contracts.py` is a consumer/schema contract, not automatically a Strategist-owned source move.

The `strategist_node(state)` LangGraph input/output state identity, all current state keys and insertion order, error/timeout/retry behavior, named output DTO, event/file-write order, provider interactions, LLM prompt/token budget bytes, use-time monkeypatch points, policy wording/thresholds and no brokerage authority are structural invariants. T4-C pinned replay at `tests/test_p164_strategist_contract_freeze.py` remains authoritative; do not regenerate goldens to make a refactor pass.

## B. Authorized S1 — exact ownership and dependency proofs

**Work type:** read existing Git objects and generate evidence files only on `evidence/p15-strategist-readonly-20261017` or a new explicitly isolated `evidence/p15-strategist-s1-s2-20261017` branch. NEVER commit Strategist runtime source changes to either.

- Compare the inventory generator outputs with actual current integration-source tree before relying on old d773709; record paths/commits that differ. Do not assume main, integration, Reporter or Monitor HEADs have the same Strategist source.
- For each 52 residual definition, use AST callgraph + caller/source tracing to classify (1) demonstrably pure display/format utility, (2) policy-consumed pure transform (protected), (3) runtime/LLM/network/env/clock/writer authority, (4) imported definition or name/identity collision. Distinguish import-time capture, lazy-global monkeypatch, mutable aliases, exception control flow.
- Reconcile the 39 implementation modules and five previously moved S1-057 owner modules with exact module paths, imports and test consumers. No accidental duplicate relocation.
- Mark `SAFE_MOVE_CANDIDATE` only as a candidate with a *specific* reproducible expected proof, not approved to move. Classify the two uncertain functions named above as `NEEDS_EVIDENCE` until their entire transitive caller/effect chain is demonstrated safe.
- Record effects and decisions for each State field written/read, the call sites of `StrategistOutput`, the exact action/order in writers, deterministic extraction inputs, dependency version and pass/fail evidence. Preserve no-live execution.
- Produce concise S1 ledger, not another huge source dump. Use changed-SHA diff instead of rereading all completed records.

**S1 pass:** 156 defs accounted for uniquely; all 52 residual defs have exact observable responsibility and disposition; historic 104 wrappers and 5 moved agent modules identified without duplicate ownership; known T4-C and authority boundaries cited. May finish even with OPEN protected or NEEDS_EVIDENCE entries.

## C. Authorized S2 — offline CONTRACT TESTS only, not production edits

- Begin with 3–5 high-value *safe-to-exercise, non-network* components selected from existing `libs/runtime/strategist/{context,output}` ownership. Do not execute LLM/news/market/exchange, production file-write, feedback truth or brokerage code. Read-only/static fixtures suffice for effectful areas.
- Freeze deterministic clock and locale, use nonrepo temporary cwd with inherited OS environment, dummy fixtures only, no real accounts or persisted production artifacts. Compare pinned BASE and current role environment in **same interpreter**; use separate child process for module identity/import-order cases.
- Check dict/State key **order and values**, exceptions including interpreter-version cases, use-time facade patching (before- and mid-call), mutable aliases, file read/write order (mocked), and negative mutations that reliably fail.
- Do not rewrite historical T4-C golden, stage pins, policy thresholds or tests to make a new fixture pass. `python -O` check is required; Linux 3.12 where available and Windows 3.13/3.14 where supported. Report NOT_RUN explicitly.
- Tests/fixtures/evidence may be committed in an isolated evidence/test branch **only**; don't alter shared T3/T4/CI, live runtime, other implementation branches or main.
- If the isolated tests reveal an actual existing risk, post reproducible issue finding rather than bypass it. Broader S2 expansion requires a concrete plan/size estimate and GPT checkpoint, not unbounded expensive replay of all 39 owners.

**S2 pass:** initial bounded suite executes and detects planted semantic mutation, clearly identifies input/expected outputs and no write/trade side effects; logs exact interpreter/deps/baselines. A suite that merely compares two failing exception cases without populated success evidence is NOT sufficient.

## D. Still blocked until separate GPT source charter

- **S3 package destination:** Do NOT decide to mass move 39 current `libs/runtime/strategist` modules under `libs/agents/strategist` yet. Existing canonical owner path may remain correct. Compare import costs, legacy shim ABI and shared gates after Reporter+Monitor combined integration is verified; GPT decides target then.
- **S4 relocations and S5 body moves:** NONE authorized now, even for 29 heuristic pure candidates. Future charter must name exact accepted file/function and target owner, source SHA, closed allowlist and focused negative regression, especially POLICY and LLM transforms.
- **S6 whole-role acceptance:** needs integrated Reporter+Monitor contract gate green and role-specific independent verification. Current S1/S2 evidence is not role completion.
- **Other roles:** Scanner remains Codex's next read-only architecture lane; no overlap or new source work assignment.

## E. Actual handoff sequence / credit policy

(1) Claude responds to Codex Issue #14 shared integration candidate immediately when real SHA appears — independent audit has priority. (2) Otherwise S1 progresses with bounded doc work. (3) S2 3–5 pure offline targets only. (4) Stop when those packets are genuinely done: do not manufacture endless code changes or poll GitHub aggressively. (5) GPT architect decides the next source package and S3–S6 work charter when user asks for next milestone.

**No recurring Work automation is active or requested. No main merge. No source policy/trading/LLM edits.**
