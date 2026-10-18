# Agentra shared execution rules — current

> **Canonical:** [ENGINEERING_DELIVERY_POLICY.md](../../ENGINEERING_DELIVERY_POLICY.md) + [Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20). Previous 2026-10-12/15/16/17 `OVERRIDE` blocks, `refactor/p1.5` one-branch, old Reporter/Monitor activation, Claude-only implementer and no-user-ZIP text are **superseded historical material**, preserved at Git SHA `c5fe8a9a`.

## Single authority and bounded context
- Operator's latest explicit authorization and frozen fail-closed trading safety → standing policy → Issue #20 current checkpoint → [CURRENT.md](CURRENT.md) pointer → explicitly active owner issue. GitHub HEAD/CI wins over stale written status.
- Codex and Claude each have developer **and** independent auditor roles depending on exact assigned issue; the auditor must not edit code being audited. GPT is architect + sole integrator; user authorizes dangerous/live/main changes.
- Read only relevant paths, contracts and frozen fixtures. Old `archive/`, `evidence/`, `P15-*.md`, [Reporter/Monitor ACTIVATE](../work_projects/ACTIVATION.md) and `STATUS.json` are evidence, NOT a command to restart an old phase. No extra task document or analyzer needed for every function.

## Safe branch, tests, source ownership
- Keep protected `main`, ONE integration branch `integration/p15-monitor-shared-20261018`, and minimum existing developer branches; detached isolated clones for read-only audit. No force push/reset, bulk remote deletion or local worktree prune on dirty/unknown operational paths. Never edit operational `C:\Agentra`, Q12 worktrees, production DB/reports or live broker.
- Developer commits exact, meaningful responsibility slice to assigned branch; targeted normal/`-O` mock/offline regression, ABI, identity/monkeypatch, State, DTO, prompt/IO/LLM equivalence. Auditor checks only changed risk plus adversarial fail-closed cases, reuses SHA-matched hosted CI instead of repeating 3k tests. Conclude PASS/REWORK/BLOCKED and STOP.
- GPT cherry-picks/composes approved exact paths, resolves both UI patchnotes, runs required CI on NEW composed integration SHA; then marks `INTEGRATED`. Full repository, genuine data and visual UI stage gates determine `RELEASE_ACCEPTED`; neither dev CI nor audited source means final release.
- **Whole root** is in scope (`.github/apps/config/data/deploy/docs/graphs/libs/scripts/tests` and root files). Move true pure responsibility, never cosmetic interfaces or source just to cut LOC; preserve module-level public imports, dynamic consumers, call-time patching and original facades where necessary.
- No redundant rank/approval/order/UEF authorities, eager Broker reexport, production-write changes, Supervisor/Executor/Step5C mutation or unsafe LLM/real-order test. Separately authorize and prove all SAFETY_LOCK changes.
- Session-isolated ignored scratch, successful scratch cleanup, bounded failed evidence retention. Do not waive frozen expectations or add skip/xfail/unknown-success to pass tests.
- Any authorized Git-tracked change updates both UI patchnote JSON and MD; user-facing ZIP contains **only actually changed files** and never secrets/live data; no CI ZIP.

## Compact developer or audit handoff
```text
TASK / OWNER / BASE_SHA / NEW_SHA / EXACT_CHANGED_PATHS
FUNCTIONAL_DELTA / TESTS_SELF_RUN / CI_REUSED_WITH_SHA
INDEPENDENT_VERDICT / INTEGRATION_SHA_OR_PENDING
BLOCKERS / NOT_RUN / NEXT_SINGLE_ACTION
```
Ask before any further tool, audit, branch or matrix run: **Does this eliminate a real current integration blocker?** If not, stop.
