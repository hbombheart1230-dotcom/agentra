# Agentra P1.5 — Three-Role Continuous Development Charter (Corrected)

**Updated 2026-10-17 KST:** Codex = MONITOR IMPLEMENTER. Claude = REPORTER IMPLEMENTER. Work = ARCHITECT / TECHNICAL LEAD / CROSS-ROLE REVIEW & FINAL INTEGRATION. Earlier Codex-as-Reporter-auditor/runner wording is superseded and must NOT be followed.
Repository: hbombheart1230-dotcom/agentra
Design ref: origin/design/agentra-dev-team-loop-20261017
No implementation branches or main merged until **all P1.5 roles** pass final integration with operator authorization.

## Hard single-writer ownership

| Role | Responsibility | Mutable area | Cross-role inbox |
|---|---|---|---|
| Claude | Reporter whole-role P1.5 continuous implementation, remaining safe-body triage, fidelity/consumer proofs | work/reporter-role-20261017 ONLY | Issue #11 |
| Codex | Monitor whole-role P1.5 continuous implementation, source/consumer ownership, replay/strict tests | work/monitor-role-20261017 ONLY | Issue #12 |
| Work | architecture, independent reviews of both workers, scope decisions, shared T1/T3/T4 contract proposals, CI/integration planning, daily digest | design coordination branch/docs/issues; isolated integration candidate only under approved gate | Issues #11, #12, #14 |
| Operator | priorities, safety/budget decisions, final authorization to merge full P1.5 | none automatically | daily digest |
| Future infrastructure owner (NOT Codex's current job) | persistent process runner design/implementation after approval | separate isolated branch | future issue |

**Work does not wait for workers to finish before reviewing**; Claude and Codex do not wait for Work's approval per batch. They progress independently on their owned role and poll GitHub findings at checkpoints. Work does not overwrite active role branches. Developer-written tests are evidence, not independent proof until Work actually reproduces or reviews.

## Verified starting state, refresh before work

- Reporter work/reporter-role-20261017 HEAD 8ce327ecc71c4c92074c1fa5fb6f00428ba9279b; 264 moved function bodies / 21 modules, remaining blockers, Reporter PARTIAL_WITH_BLOCKERS. Reporter Issue #11 includes checkpoint and review findings.
- Monitor work/monitor-role-20261017 HEAD a33c28780592917481eb610a3d69c3948e4a4ead. 11 moved full-blob owners under libs/agents/monitor/events and projections; five shared T3/T4/package-mapping failures reported, not a blanket role-wide PASS.
- Existing integration branch d269c906ebadad75a0b833778ebc6a632a388e7c is NOT assumed to contain either latest worker HEAD.
- Issue #14 is shared Work review/contract queue (earlier Codex Reporter audit assignment superseded).
- Design draft PR #13 is documentation only and MUST NOT be confused with completion or runtime activation.

## Engineering loops

### Claude — Reporter
Read exact HEAD + latest role checkpoint + Issue #11; select whole Reporter role's next safe subproject; implement, targeted tests, negative proof, commit/push, issue checkpoint, poll Work findings, move to next READY subproject. Never stop after a single file/batch unless no safe work exists or process/budget stops. Owner transfers maintain facade semantics, signatures, dynamic monkeypatch and report bytes. Existing 264 moves are baseline, not redo.

### Codex — Monitor
Read exact HEAD + latest role checkpoint + Issue #12; continue whole Monitor role after eleven existing owners. Inspect other safe projections/event/read-model bodies and consumers, preserve Monitor intent-only, entry/exit/rank/sizing/cooldown and guard authority unchanged; test, commit/push, checkpoint, poll Work findings, continue another ready Monitor batch. Five shared contract mapping failures are reported to Work but do not stop independent Monitor code work.

### Work — Team architecture and two-sided reviewer
Review actual Reporter and Monitor HEAD diffs and consumer/test evidence; assign objective P0/P1/P2 findings with exact SHA and acceptance tests to corresponding Issues. Own solution design for T3 historical test conflict, including untouched-function AST same-path mutation protection, and separate shared CI mapping queue. Does NOT write active Claude/Codex branches. Independently review both branches, evaluate role completeness, provide one daily digest and reserve final integration after whole P1.5 closure.

## Shared contract / CI

Historical BASE pins must remain honest; no test skips, no widening of forbidden production paths, no blanket exemptions. Reporter R7 T3 v4 change as proposed exempts whole facade paths; Work must ensure **unmoved function bodies and module-level statements** remain protected and include negative same-path mutation. Work coordinates safe integration on a dedicated candidate after exact role SHAs; no unilateral T3 edits in worker branches. CI must include Reporter seed and body tests, Monitor strict owner tests, required Linux/Windows safety and authority coverage, and UI-connected patch notes. Earlier tests reported by workers are not hosted CI results.

## Continuous checkpoints and review cadence

At every meaningful reversible batch each worker leaves:
- exact previous and pushed HEAD SHA; source paths/symbols moved/retained and why;
- changed LOC, AST/ABI/monkeypatch/alias/byte fidelity proof;
- tests with precise commands, exit code and PASS/FAIL/NOT_RUN;
- negative scope/authority tests;
- open review finding ACKs + fix SHA, blocked symbols/permission;
- NEXT_READY >=2 safe packets where feasible;
- real UI patch-note source or proposed-only;
- current runtime/credit status as OBSERVED or UNKNOWN.

Share role findings through GitHub Issue comments: #11 Reporter, #12 Monitor. Cross-role/shared-contract issue #14 is coordinated by Work. If CLI lacks Issue write access, worker commits versioned issue-ready handoff rather than scraping credentials; Work can relay. A git commit alone is NOT a stop signal. Avoid rereading completed history and repeated expensive full tests. Tests and scratch artifacts use session-isolated ignored directories, success cleanup and capped failure retention.

## Safety and scope

P1.5 is behavior-preserving only. Neither worker may place trades or change Broker/Executor/Supervisor/guard approval, Step5C, UEF truth contracts, Q10/Q12 policy, Monitor exit/entry/sizing/rank/cooldown, live execution config, persisted production data, truth precedence, LLM execution/retry/routing/cost or output policy. No import-time callable capture, unchecked facade relocation, test bypass, blind reset/clean or force-push. All changes to these behaviors need separate explicit operator authorization. Work must not secretly approve them by a GitHub comment.

## Full-time operations truth

These docs **do not launch or restart** Claude, Codex or Work. Within a live CLI session the owner should process as many safe batches as supported. After an exit, truly unattended work requires an installed authenticated process supervisor, always-on host, explicit daily credit limits, branch leases, crash recovery, a kill switch and Work review scheduling through supported product controls. Runner architecture is recorded in 04_PERSISTENT_RUNNER_SPEC.md as a **future separate infrastructure project**, not Codex Monitor's work. Without that infrastructure, resume is manual and checkpoint-driven. No background work may be promised as already active.

## Start order

1. Launch Claude with 02_CLAUDE_FULLTIME_ORDER.md and Reporter #11.
2. Launch Codex with 03_CODEX_FULLTIME_ORDER.md and 06_MONITOR_WHOLE_ROLE_PROGRAM.md plus Monitor #12.
3. Launch Work with 01_WORK_FULLTIME_ORDER.md, both Issues and shared review #14. It reviews and coordinates continuously within its active/supported scheduled windows.
4. Main merge only after entire P1.5 is ready, Work shared-contract/CI review passes and operator explicitly approves.

Paste-ready condensed prompts: 05_LAUNCH_PROMPTS.md.
