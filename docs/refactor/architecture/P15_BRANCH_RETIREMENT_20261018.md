# P1.5 — GitHub BRANCH RETIREMENT AND ARCHIVE DECISION (2026-10-18)

**Latest remote fetch 2026-10-18 KST.** Exact refs (fetched at inspection time):

| Branch | HEAD prefix | Versus integration `5cb90b39` | Decision | Destructive deletion now? |
|---|---|---|---|---|
| `main` | `2f95bba4` | protected baseline | KEEP protected | NO |
| `integration/p15-monitor-shared-20261018` | `5cb90b39` (prior to this docs-only commit) | canonical integration | KEEP single integrator | NO |
| `work/codex-p15-20261018` | `f8232e10` | active UEF9 synthetic fixture, 2 new commits vs `0c6d72d8` | ACTIVE | NO |
| `work/strategist-role-20261018` | `3a44bed2` | active developer, 6 commits vs `185509f6` | ACTIVE (docs/role) | NO |
| `design/agentra-dev-team-loop-20261017` | `9477a93c` | DIVERGED ahead73 behind466 | HISTORICAL FREEZE; DRAFT PR #13, unique commit history | NO |
| `evidence/p15-strategist-readonly-20261017` | `d8b34e66` | DIVERGED ahead2 behind48 | HISTORICAL FREEZE, unique evidence | NO |
| `evidence/p15-strategist-s1-s2-20261017` | `fcf79594` | DIVERGED ahead5 behind48 | HISTORICAL FREEZE, unique evidence | NO |
| `infra/p15-continuity-runner-20261017` | `2233cae7` | DIVERGED ahead1 behind466 | HISTORICAL FREEZE; Runner not deployed | NO |
| `integration/p15-t4-pr5-convergence-20261015` | `d269c906` | DIVERGED ahead1 behind48 | HISTORICAL FREEZE, one unmerged commit | NO |
| `work/monitor-role-20261017` | `4bc42508` | BEHIND by35; ahead0 | REMOTE_DELETE_CANDIDATE after local worktree check | **NOT YET** |
| `work/reporter-role-20261017` | `443f9036` | BEHIND by18; ahead0 | REMOTE_DELETE_CANDIDATE after local worktree check | **NOT YET** |

Only **2 of 7** historical branches are provably ancestor branches of current integration. **Five diverged** branches preserve unique unreconciled commits; deleting now can make rollback and provenance inaccessible. Prior team estimate of historical 78 union-unique commits is a historical claim, not newly reproduced by this table. The DRAFT PR #13 contains documented development-loop protocol and says DO NOT MERGE; closing that workflow PR (reversible) may be a separate cleanup decision, **not** branch retention proof.

### Completed in this architecture intervention
- Logical branch cleanup: only integration + two active developers + main are ACTIVE; 7 historical refs marked frozen/read-only. Integrator branch is source baseline for the full 3,908 file tree and all new docs.
- Exact ancestor/divergence evidence recorded for all 7 historical refs; no force/reset/merge.

### Not performed / blocked
- Physical GitHub remote branch deletion: current connected GitHub actions expose no delete-ref operation. Do **not** fake deletion by force-moving refs; that would destroy useful old head pointers without reducing branch count.
- Cannot inspect local `git worktree list`, dirty/unpushed jobs or external scheduled scripts from connected remote. **Therefore even the 2 ancestor branches are NOT YET cleared**. Owner must prove no checked-out branch/worktree, no CI/PR/restore references and preserve a rollback SHA/tag/bundle before remote retirement. No `git branch -D`, no `git push --delete` now.
- Any future remote delete requires exact branch allowlist, approved archive/restore proof and write capability. Retain 11 remote refs physically until then (this docs-only commit does not change that count).
