# D00 — Agentra engineering constitution: DELIVERY FIRST / NO RECURSIVE AUDIT

**Stable alias:** D00 = `docs/ENGINEERING_DELIVERY_POLICY.md`; D01 = root `AGENTS.md` (Codex), D02 = root `CLAUDE.md` (Claude). Trading safety source: `docs/ground_rules/AGENT_RULES.md`. No alternate D00/D01/D02 filenames.

**Adopted by operator / GPT Tech Lead: 2026-10-18. Standing policy for all future P1.5–P8 work.**
**Purpose:** finish verified trading-system improvements in a single integrated codebase, rather than endlessly generating tools, inventories, evidence documents, and branch-specific PASS labels.

> **CURRENT SAFETY / BRANCH TRUTH (2026-10-19):** `main` is **policy-protected / user-approval-only**, but GitHub branch-protection enforcement was **reported absent (`protected:false`, no active ruleset) in the 2026-10-19 read**, and has **not been independently reverified** in this docs-only change. References below to "protected main" describe a **must-not-edit policy**, NOT confirmed GitHub enforcement. Do not merge/push to `main`; request explicit operator-admin setup and verified rules before release promotion. Only `integration/p1.5` is active for document convergence. Closed #16–#19 are historic only. No code task is authorized until DOC_FREEZE plus user acceptance.

## 0. Authority order and handoff
1. Trading safety/fail-closed invariants and explicit latest operator authorization always take precedence. Never weaken broker gates, Step5C CAS/UNKNOWN quarantine, UEF oracle, production-write isolation, credentials, or approval control for speed.
2. This standing delivery policy governs HOW all four workers operate. The CURRENT task issue supplies the *specific exact SHA, paths, scope and reviewer*. Historical work orders, dated overrides, stale branch pointers and old NOT_STARTED checklists are **evidence, not active instructions** when they conflict.
3. One live master issue (#20) and `docs/refactor/work_orders/CURRENT.md` identify the single currently approved integration milestone. A GitHub issue/comment **does not launch a CLI session**. The user/operator launches local sessions.
4. GPT acts as **architect + integrator + finish-owner**, not just prompt writer. GPT must directly inspect actual tree/code/imports when possible, settle one owner per responsibility, decide approval and merge scope, and report what was actually committed vs planned. The user retains control of high-risk/live deployment, destructive removal, and protected-main decisions.

## 1. Define DONE properly
- `IMPLEMENTED`: developer committed/pushed exact source SHA and target test evidence.
- `AUDITED`: independent reviewer checked changed boundary and recorded PASS/REWORK with test/CI facts and NOT_RUN, NOT_VERIFIED clearly labeled.
- `INTEGRATED`: **the approved changed code is on the integration branch**, there is no missing cherry-pick, branch fork contamination, or patchnote chronology conflict, and appropriate checks ran on the **newly composed integration SHA**.
- `RELEASE_ACCEPTED`: whole-repository/safety/UI/real-evidence gates required for the *stage* completed; only then user-authorized protected `main` promotion. Never call developer-branch PASS a completed integration or final release.
- A refactor is progress only when **owner clarity, original-file responsibility/complexity reduction, duplicate/compatibility-debt reduction, reliable imports and accepted integrated code** improve. File count, PR count, documents, inventory lines, test invocations and SAFE-count are not delivery metrics.

## 2. Stop endless loops
1. Do **not** create new analyzer, analyzer-of-analyzer, AST inventory, counterexample factory, scope checker, harness or extra document merely to certify another checker. Reuse existing targeted runtime/contract/differential proof. A previously **REWORK/FROZEN** analyzer stays untrusted and is never a source-migration SAFE certificate.
2. Audit **only exact changed paths/callable contracts** since a pinned, previously accepted base. Reuse prior independent PASS for unchanged code. A new negative result in the changed boundary must be addressed; known unchanged historical debt is documented as HOLD, not silently accepted or recursively reaudited.
3. The reviewer must return a bounded `PASS / PASS_WITH_FINDINGS / REWORK / BLOCKED` decision plus evidence/NOT_RUN and STOP. No autonomous expansion into additional full scans, old worktree surveys, extra test generation or other roles without a real code-change/safety trigger and operator scope approval.
4. If work is blocked, present the **specific blocking evidence and the smallest executable remediation**, rather than producing more analysis artefacts. If work passes, hand it to integration promptly instead of starting a new wave on an old developer base.
5. An engineer proposing new infrastructure must demonstrate direct functional need, expected time/cost, alternatives, and specific owner approval. **No perfect-testing-system project nested inside a source refactor.**

## 3. Test strategy (avoid duplicate 3,000-test loops)
- **Developer:** touched-module regression, positive and negative tests, import/State/IO/monkeypatch/LLM/broker boundary checks as applicable, normal and `-O` for relevant focused suites.
- **Independent reviewer:** static diff plus self-run *risk-targeted* tests, fixture/golden and fail-closed adversarial checks; may rely on real, SHA-matched GitHub CI for existing entire matrix. Do not independently rerun ~3,100 tests in two modes on every developer SHA without a demonstrated uncovered cross-cutting risk.
- **Integrator:** compare selected developer commits, resolve conflicting notes, run required matrix on **new integration SHA** and perform contract/replay/write-safety checks. Full-repository pytest/UI visual/real-data parity belong at the stage/freeze gate (or earlier when a real high-risk change warrants it).
- Maintain distinguishable counts: selected CI collection != whole repository; 24 genuine-real-data SKIPs remain SKIP/NOT_RUN, never hidden as PASS. Never fix a failing test by relaxing oracle, skip/xfail/waiver, invented fixture labels, suppressed error, or shortened safety path.
- Resource contention can cause false failures: report hardware/OS/Python and rerun isolated *failing case* first. Parallel or serial full matrices should be a reasoned exceptional choice, not a default reviewer ritual.
- CI success is **not** independent source review, and independent review is **not** a second copy of the entire CI.

## 4. Branches, scope, and integration
- Keep only user-approved active branch lanes: protected `main`, **one integration branch**, and the minimum needed developer branches; read-only auditors use isolated detached SHAs. No new branches for incremental tasks/ZIPs/re-audits without authorization.
- **Selective audited change promotion only.** Never merge a whole diverged developer branch just to pick a document or tiny source slice. Check actual integration HEAD and ensure notes/paths stay coherent.
- Historical refs with unique commits, open PRs, unknown local worktrees, dirty state or upstream differences are preserved. Delete only after owner/scheduler/restore/unique-commit review; no force-reset, force-move, prune, worktree delete or production directory clean as a shortcut.
- Close and record each accepted slice on integration as soon as its exact required gates pass; do not accumulate weeks of audited-but-unintegrated code.
- The **entire repository root** is in scope: `.github/apps/config/data/deploy/docs/graphs/libs/scripts/tests` and root config files. Role folders alone are not the P1.5 definition of done.
- HYBRID-7 V3: seven roles are public responsibility boundaries, not permission to copy broker, ranking, approval, or UEF authority. `graphs/trading_graph.py` is a graph-shaped test baseline; real operational order path through Commander and `execute_from_packet.py` is separately SAFETY_LOCK.
- No cosmetic `__init__.py`, facade, service, duplicate owner or package just to look complete. Preserve dynamic consumers and late monkeypatch/cold-import semantics.

## 5. Reporting and artifact discipline
Every task report must fit the following compact record; link detailed evidence once, do not duplicate historical results:
```text
TASK / OWNER / BASE_SHA / NEW_SHA / EXACT_CHANGED_PATHS
FUNCTIONAL_DELTA / TESTS_SELF_RUN / CI_REUSED_WITH_SHA
INDEPENDENT_VERDICT / INTEGRATION_SHA_OR_PENDING
RISK_BLOCKERS / NOT_RUN / NEXT_SINGLE_ACTION
```
- The GPT Tech Lead owns a clear **integrated-code progress board**: DONE on integration, AUDITED waiting for pick, REWORK with blocker, BLOCKED/NOT_RUN. No misleading blanket green board.
- When a meaningful tracked change is authorized, update both UI-linked `docs/trading_agent_patch_notes_detailed_update/patch_notes.json` **and** `patch_notes.md` on the actual integration commit, recording honest scope (including docs-only). Don't overwrite older entries or claim an unperformed run.
- When handing user a file bundle, ZIP **only actually changed files** with their relative repository paths; never include secrets, production data, caches, untracked evidence piles or unchanged files. No ZIP generation in CI.
- Test scratch must be session-isolated; successful scratch auto-cleaned, failed evidence bounded retention. Do not grow files/dirs every full test rerun.

## 6. Required integration-first sequence
```text
GPT fixes owner/target + exact change scope
  → Developer implements and commits
  → Independent reviewer checks DELTA and decides
  → GPT selectively integrates accepted changes
  → Integration-SHA required CI and compatibility
  → Mark INTEGRATED; close old task and move to next root-wide slice
  → Stage/FREEZE whole-repo + real-data + UI checks
  → User approves protected-main promotion
```
**2026-10-19 user override — DOC FIRST:** 339-file `docs/refactor` classification, canonical authority consolidation, historical instruction quarantine, full link/reference verification, independent audit and user DOC_FREEZE acceptance precede **all further P1.5 code tasks and new Codex/Claude development branches**. Prior S5/UEF9/Strategist/Operator UI work at `a50d6e47` is completed scoped evidence, not a new task. GitHub Issue comments do NOT launch terminated CLI sessions. Do not mistake previous SHA CI PASS for full release acceptance.

## 7. Anti-loop exit question
Before asking for another audit, plan, tool, branch, inventory or test run, answer:
> **Will this action eliminate a real remaining delivery blocker on the current integration SHA?**
If NO, **stop**, state the fact and return to actual integration or approved source work. The user can override this rule explicitly; trading safety locks cannot be overridden merely by convenience.
