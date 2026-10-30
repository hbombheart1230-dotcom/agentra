# P1.6 — Validation, Handoff and Continuity Gates

**Status: DESIGN ONLY / NOT RUN (2026-10-30).** This is the single active validation plan. The prior five file/function and graph-only packets are preserved in archive, not active work orders.

## 1. Do not interrupt P1.5

Current P1.5 controls and owners (refresh the linked sources every session, not historical P1.6 snapshots):

| Flow | Live authority/source | Evidence |
|---|---|---|
| Developer B / independent peer | [C01](../work_orders/C01_CODEX_CURRENT.md) | Issue #12 |
| Developer A / independent peer | [C02](../work_orders/C02_CLAUDE_CURRENT.md) | Issue #11 |
| Assignment | [C03](../work_orders/C03_LEAD_TRIAGE_CURRENT.md) | latest A/B/RunLab delta |
| Integration, tests, CI | [C04](../work_orders/C04_LEAD_INTEGRATION_CURRENT.md) | Issue #36 |
| Accept RF / DONE | [C05](../work_orders/C05_LEAD_CLOSEOUT_CURRENT.md) | canonical RF/STATUS |
| Read-only external audit | [C06](../work_orders/C06_AUDIT_CURRENT.md) | Issue #37 |
| Runtime/RunLab independent validation | [RunLab CURRENT](../../runtime/validation/CURRENT.md) | Issue #32 |

The active D00 §2 FAST-3 gates and actual CURRENT/RF documents govern **P1.5**; old P1.6 WO-16.*, deprecated old branch assignments and historic seven-column gates do not. **Never modify C01–C06, D00, RF, existing automation, current CI, or RunLab to “prepare” P1.6.** If the scheduled P1.5 task is active, it remains active. Real A/B source SHA, integration SHA, targeted tests, hosted CI and RunLab source identity must be evaluated separately; mock/unit PASS is not runtime PASS.

## 2. Entry gate — accept real P1.5 completion first

Do not assume DONE counts equal P1.5 freeze. Gate A requires:
- Formal P1.5 completion decision, exact immutable source SHA, branch and freeze/tag evidence.
- Exact live entrypoints, seven role public contracts, state owners, nested consumer paths and operation mode mapping; compare against the old P1.6 source snapshots and declare PATH_DRIFT / ABI_DRIFT / SEMANTIC_DRIFT.
- Actual baseline tests, relevant safety/UEF integrity, Docker/runtime and RunLab validation receipts, classified BLOCKED/NOT_RUN where evidence is missing. No false assertion of a clean full suite or safe production readiness.
- Clear owner approval to start P1.6 code changes. Design permission alone does not authorize execution.

## 3. Architecture/Identity evidence gate

Identify one truth owner for market context, strategy policy, candidate rank, entry/exit state, order-intent ownership, approval, broker effect, execution outcome, UEF evaluation, knowledge memory and reporter presentation. A role may suggest changes but may not silently take another role's authority.

Verify at least:
- Three-holding short-horizon identity, scalp/intraday/2–3-day swing policy targets, multi-candidate/watchlist vs held-position boundary.
- Commander can initiate, query, challenge, request more research and decide without directly submitting orders.
- Strategist theme → Scanner selection → Monitor timing has explicit backward collaboration; no fake “every role can order” shortcut.
- Per-task model and memory selection are advisory/bounded; deterministic order guards preserve supremacy.
- Distinguish existing behavior, desired target, prototype and deferred P2–P8 function explicitly.

## 4. Pruning gate

For every KEEP / CONSOLIDATE / REBUILD / ARCHIVE / DELETE disposition:
1. Verify runtime callers, dynamic consumers, CLI/scheduler, UI/report, tests, configuration flags, frozen API and research dependency on the accepted freeze SHA.
2. Record deletion's expected behavior, evidence/data impact, rollback reference and affected tests. No untested wholesale removal.
3. Run focused tests on changed source plus normal and optimized Python mode where applicable; separately run protected guard/UEF and meaningful end-to-end mock/RunLab probes.
4. Demonstrate source integration SHA, actual deployment/source identity and runtime outcome independently. Never claim RunLab validated a SHA it did not identify.
5. Protect operational SQLite, identity/intent journal, evidence ledger, frozen Q/UEF and historic reports. Archive presentation-only historical materials without contaminating authoritative evaluation or deleting raw proof.

No code reductions are accepted solely on LOC, test count or files deleted.

## 5. Framework benchmark — conditional, after scope freeze

**Candidates:** custom runtime (control), LangGraph and pydantic-graph; optional variants only by ADR. Do not install packages or select a winner from popularity alone.

Use exactly pinned Python/framework versions and same offline, immutable fixtures. Isolate network, LLM, broker, production writes, runtime ownership and live Reporter. Compare:
- State SET/DELETE, absent-vs-None, aliases, rank/intent/guard reasons, event lineage and existing mode/phase parity.
- Retry/cancel/restart, pure-node checkpoint, determinism, isolated failures, duplicate effect prevention and dependency/import safety.
- Maintenance complexity, type safety, operability, cold/warm latency, p50/p95, memory, cost and ownership burden.

An engine checkpoint is not Step5C execution truth; no checkpoint may replay broker mutation or implicit approval. Benchmarks of historical graph-spine parity do **not** certify real integrated-chain behavior or new autonomous decision quality.

Output a measured ADR: KEEP_CUSTOM / ADOPT_LANGGRAPH / ADOPT_PYDANTIC_GRAPH / DEFER. Exact counters, source hashes, tool versions and failure results required; no nominal PASS when NOT_RUN. Any shadow adoption is default-off and separately approved; any production cutover is yet another safety review.

## 6. Adaptive policy, model and learning evaluation

Evaluate bounded policy/weight changes against frozen baseline and comparable UEF-evaluated samples. Log proposal, validation cohort, model/prompt, effective policy version, rejected alternatives, decision timestamps and future/observed outcome. Avoid look-ahead, duplicated samples and random backfills. In-session proposals must never bypass trade-budget/stop rules, and existing holdings must not have stop policy changed implicitly.

Test model routes with the same Agentra market-reasoning and structured-contract fixtures. Measure correct abstentions, hallucinated facts, schema validity, p95 latency, cost and fallback failure states. Price/subscription offers are subject to verification; no agent auto-switches models or adds credentials as a byproduct of this document.

UEF is immutable measurement authority; Q100/Experience retrieval is a future read-only consumer. Reporter human summaries may be consolidated only when operational audit and knowledge consumers remain intact. Engineering Lab may suggest patch/test/rollout after market close, but must remain out of band until later roadmap gates; no same-session live source self-modification.

## 7. P1.6 closeout report (future)

At implementation end, one concise closeout must contain: accepted P1.5 base SHA, exact P1.6 source SHA, owner-approved identity/ADR, Feature Disposition Ledger counts and deletion proof, per-mode test results (PASS/FAIL/BLOCKED/NOT_RUN), broker/LLM/production-write isolation, CI SHA, RunLab runtime SHA and health, framework decision, rollback, unresolved debt and next-stage P2/P3/P4 handoff. Only accepted evidence may claim P1.6 DONE.
