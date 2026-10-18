# Agentra P1.5 — Three active branches, auditor housekeeping, development/verification relay

**Effective:** 2026-10-18 KST. **Operator objective:** exactly THREE ACTIVE P1.5 branches plus separately protected `main`. This file establishes the canonical active set; it does **not** certify that older remote branches have been physically deleted. GitHub and the live local worktree registry must be independently confirmed before actual deletion. **No automatic main merge or trading execution.**

## 1. Exactly three ACTIVE development refs

| Slot | Authoritative branch | Observed 2026-10-18 SHA | Sole writer | Purpose |
| --- | --- | --- | --- | --- |
| INTEGRATION | `integration/p15-monitor-shared-20261018` | `5fcd5e1d9c175e64dfa54ecb2e61f9eef2430dda` before this docs-only policy commit | Integration gate by cross-review | Reporter+Monitor assembled contracts, accepted verified deltas, paired UI patch-note evidence; no unreviewed developer direct changes |
| CODEX_DEVELOPER | `work/codex-p15-20261018` | Create once from this integration policy HEAD | Codex developer | Fix P1.5 shared candidate / CI / test-evidence blockers; produce reviewed PR or SHA for integration |
| CLAUDE_DEVELOPER | `work/strategist-role-20261018` | `21ec7fe438f48dfb7d98b5d7bded15aadd89ad8b` | Claude developer | Strategist S5-D and S5-E next; S5-A/B/C source already moved; no replay of completed implementation |

**Important:** `main` stays separate and frozen pending explicit operator merge authorization. The integration **code** SHA was `95c11cacb9c73ae3d97d89e2061372762efff12b`; its later `5fcd5e1d` evidence HEAD differed only by docs/UI evidence. This new **docs-only** policy commit changes the branch HEAD once more; do not conflate head with the independently audited code SHA.

Codex's old Monitor branch `work/monitor-role-20261017` and Claude's old Reporter branch `work/reporter-role-20261017` are **already ancestors of the integrated branch**; they are NOT active work lanes. Both retain immutable historical pin SHAs in the existing integration checks and must be safe to reference after Git branch retirement.

## 2. Other existing branches = INACTIVE / RETENTION PENDING, not deleted by documentation

Review these exact seven old branches separately, do not count them as active developer lanes:
- `work/monitor-role-20261017`: ancestor of INTEGRATION; historical immutable Monitor reference `4bc4250844093050438d8a9c29f5842991ad1c3a`.
- `work/reporter-role-20261017`: ancestor of INTEGRATION; historical immutable Reporter reference `443f90362ad5970a4731685311a45e8e0f6b55e4`.
- `evidence/p15-strategist-readonly-20261017`: unique inventory, ancestor of the next evidence branch; do not drop its proof objects without archive.
- `evidence/p15-strategist-s1-s2-20261017`: unique S1/S2 ledger+evidence, NOT merged into Claude's S5 source branch; preserve/copy in an audit-safe migration.
- `infra/p15-continuity-runner-20261017`: unique spec/prototype evidence, **not an active or deployed process supervisor**.
- `integration/p15-t4-pr5-convergence-20261015`: one unique post-divergence retired-branch backup/bundle commit. S5 Claude source **descends from this ref**, so preserve its objects.
- `design/agentra-dev-team-loop-20261017`: unique GPT architecture orders; **open PR #13**. Do not delete while the PR references it or without migrating its current authoritative charters.

### Remote-branch deletion gate (auditor only; never by a developer)

Before retiring a remote branch: record exact HEAD+SHA and compare, verify no open PR and no active local registered worktree, verify all unique commits, embedded historical refs/fixtures and relevant documents remain reachable through retained refs, approved tags or a verified archive; ensure no developer is using it. Use a tested dry-run delete plan and attach an auditable manifest including a restoration ref and commands. **Branches with unique unmerged commits or open PR are NOT eligible for automated deletion**. Users' existing dirty/untracked files and production runtime are never removed. Request operator confirmation before deleting any remote branch that cannot be proven lossless. GitHub lacking a delete-ref action is `NOT_EXECUTED`, never `DONE`.

## 3. Consolidate local worker workspaces under C:\AgentraEvidence (on the user's Windows PC)

Desired workers:
- `C:\AgentraEvidence\dev-codex`: registered checkout/worktree for CODEX_DEVELOPER.
- `C:\AgentraEvidence\dev-claude`: registered checkout/worktree for CLAUDE_DEVELOPER.
- `C:\AgentraEvidence\audit-claude`: isolated **detached or read-only checkout**, no new remote auditor branch.
- `C:\AgentraEvidence\audit-codex`: isolated **detached or read-only checkout**, no new remote auditor branch.
- `C:\AgentraEvidence\_control`: scoped checkpoints, exact-SHA audit packets, retention manifest; **no installed unattended runner assumed**.

Those are TARGET paths, not a claim that folders already exist. Inspect `C:\Agentra`, `C:\AgentraEvidence`, `C:\AgentraWork`, `C:\AgentraWorktrees` (and any relevant `C:\Agent Workspace`) before moving/removing anything. `C:\Agentra` may have operational data/services. `C:\Agentco` is **strictly separate and untouched**. A Windows directory cannot be safely relocated merely by moving the `.git` pointer in Explorer: create/register new `git worktree` paths from verified source clones and retire only *stale* correctly unregistered worktrees after proving equivalence. Don't kill active processes.

**Write boundary:** Only exact verified registered Agentra worktree path(s) for the actor, not an entire `C:\AgentraEvidence` blanket. Auditor may delete **only its own proven ignored, successful-run scratch/cache** within verified auditor roots. Do not delete another session's scratch until its PID/session is confirmed ended and the evidence retention gate is met. No `git clean -fdx`, `git reset --hard`, brute-force `rmdir`, OS profile/Temp or production DB cleaning.

Retention: auto-clean scratch for SUCCESS after run; for FAIL keep bounded newest THREE executions or SEVEN days in the verified Agentra-only scratch root. Keep hashed/brief failure manifest first. No source, reports, historical evidence, unmerged worktree, local human content, `.env`, cache containing personal info, or Git object removal on automated policy. First dry-run inventory, then bounded deletion with log, size reclaimed and item path. Do not create new global Git config/hooks/credentials.

## 4. Four long-running roles, exactly THREE active remote branches

| Session | Works on | Checkpoint / release trigger | May edit source? |
| --- | --- | --- | --- |
| Codex developer | CODEX_DEVELOPER | Pushed scoped commit/test evidence, ready for Claude audit | YES, only Codex branch |
| Claude auditor | detached exact Codex commit from verified isolated worktree | `AUDIT_PASS / REWORK / NOT_RUN` with exact test reproduction | NO; cleanup own scratch only |
| Claude developer | CLAUDE_DEVELOPER | Pushed S5 bounded commit/test evidence, ready for Codex audit | YES, only Claude branch |
| Codex auditor | detached exact Claude commit from verified isolated worktree | `AUDIT_PASS / REWORK / NOT_RUN` with exact test reproduction | NO; cleanup own scratch only |

Relay: **developer commit SHA → opposite-model auditor on that exact SHA → PASS/REWORK → same developer fixes deltas → verified integrator promotes only an approved patch to INTEGRATION**. No editing shared integration code from reviewer worktrees; no simultaneous writer on any worktree. Auditor reports findings once per *changed* SHA and verifies only the delta and affected regression suites; never re-run prior completed audit merely to remain active. Actual session process auto-restart requires separately deployed runner and explicit opt-in; a GitHub doc/prompt alone **cannot** auto-relaunch a dead CLI. If no runner exists, preserve `NEXT_READY` and leave a copyable resume command in checkpoint; do not represent the pipeline as continuously running.

**Developer continuation:** after each approved subtask, proceed to next approved task without manual approval. If only high-risk or unapproved work remains, post exact SHA+next request and wait; do not invent permission to rewrite policies/trades. Never activate hourly ChatGPT Work polling.

## 5. Immediate next steps, NOT previously done

1. Claude developer: resume `work/strategist-role-20261018` at `21ec7fe4`; S5-A/B/C DONE, execute S5-D parity/frozen T4-C and S5-E handoff. Separate Codex audit of its SHA, no same-worktree interference. P2 Reporter error-message filter / Strategist S2 case count remain scoped maintenance follow-ups on their respective branches, not unauthorized S5 migrations.
2. Codex developer: use `work/codex-p15-20261018` based on integration baseline, no redo M9. Integrate/triage existing Claude-auditor findings and baseline-reproduced UEF9 1 FAIL **without accepting a failing overall gate**, and complete Linux hosted CI/real-artifact claims only when actually observed. No bypass, expectation rebaseline, silent waiver or synthetic real data.
3. Auditors: first run **inventory-only** on local/worktrees (retired branch refs, dirs and running processes). Their next trusted duties include bounded scratch cleanup and exact SHA audits; no deletion of remote historical branches or other projects until archive/restore gate is verified.
4. Integration branch is not a live production branch. Its former shared code SHA `95c11cac` had Windows normal and -O each 2895 PASS, 1 FAIL (UEF9 reproducible on immutable BASE), 24 SKIP (real data unavailable). CI Linux, full repo sweep, final independent integrated acceptance NOT_RUN. It is **NOT overall PASS**, hence NO main merge.

## 6. Mandatory checkpoint schema

```
ROLE: CODEX_DEV | CLAUDE_DEV | CLAUDE_AUDITOR | CODEX_AUDITOR
BRANCH / CODE_SHA / EVIDENCE_SHA: ...
TASK_COMPLETED / NEXT_READY: ...
TESTS: command, PASS, FAIL, SKIP, NOT_RUN and environment
REVIEWED_INPUT_SHA / INDEPENDENT_VERDICT: ...
SANDBOX_ROOT / WORKTREE_GIT_COMMON_DIR / SCRATCH_ROOT: ...
SCRATCH_REMOVED / FAILURE_EVIDENCE_RETAINED / RETENTION_MISMATCH: ...
REMOTE_BRANCH_RETIREMENT: NO / OPERATOR_APPROVED_AND_VERIFIED
RUNNER_ACTUALLY_DEPLOYED: NO (unless proven)
PRODUCTION_OR_MAIN_CHANGED: NO
```

**Safety:** Follow existing [Agentra sandbox charter](https://github.com/hbombheart1230-dotcom/agentra/blob/design/agentra-dev-team-loop-20261017/docs/dev-team/assignments/15_P15_WORKSPACE_SANDBOX_POLICY_20261018.md), but prefer this exact three-branch operational target for any conflicting older "Monitor/Reporter still active" wording. User's Agentco repository, local secrets, real brokerage and production systems are strictly out of scope.
