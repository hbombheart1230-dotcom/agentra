# Codex shared candidate — independent Claude audit required

Status: IMPLEMENTED / NOT ACCEPTED. Selected full matrix currently FAIL; do not merge.

## Inputs and assembly

- Design reference initially read at b90d1a9; subsequently observed
  `faa6b76c61e59dd9f68f04078a43b5c9bd6ba888` adds workspace policy 15, read and applied.
- Monitor: `4bc4250844093050438d8a9c29f5842991ad1c3a`; runtime `800841f229606c419dae67b0d6f794b9238676e9`.
- Reporter: `443f90362ad5970a4731685311a45e8e0f6b55e4`.
- Shared runtime BASE: `d773709ba2f70471fad9badba4f92400f7818319`.
- Common activation ancestor: `eeb742a33b16f6271ff364a904e187b470561c7e`.
- Monitor local retained-boundary checkpoint: `9f94f78`; 359 explicit exclusions,
  bounded syntactic calls/writes/control flow, no further runtime move or purity claim.
- Merge commit `726d0e05a9b2f761ce633a35465ebdaffb7b72da` assembled both exact inputs.
  Zero overlapping changed paths since activation; no conflict or silent side selection.
- Candidate only: `integration/p15-monitor-shared-20261018` at
  `C:/Agentra/.worktrees/p15-monitor-shared-20261018`. Role refs, live root and Q12 untouched.

## Implementation

Reporter guard reconstructs all 23 original facade ASTs covering 313 moved bodies,
including unmoved definitions, module statements/order, exact imports and forwarding
headers/arguments. R10-to-R11 runtime and move-ledger diff is empty. Existing moved
body/global/patch tests remain required. Exact immutable role-input source comparison
additionally protects all 105 Reporter and 41 Monitor runtime changed paths.

Monitor resolves only 14 immutable ledger pairs after exact three-statement shim
verification and full BASE canonical equality. Eight mixed facades/20 named moves
must reconstruct their entire BASE modules and exact owner ASTs. T3/T4 current-head
resolution now uses these proofs. Historical stage checks remain unchanged; the T3
path prohibition is preserved through frozen BASE, then exact pinned proofs apply.
Monitor-only protected-path checks remain checked on the Monitor SHA, with combined
runtime proof added for this integration. No runtime implementations changed here.

Negative tests cover Reporter same-path unmoved body, imports/redirects, wrappers,
module execution/order; all 14 Monitor shims, all eight mixed facades' selected and
unselected bodies/module statements; canonical corruption, extra numbered owner and
Broker path. Agent package sets remain exact equality. No new skip/xfail/deselect.

F1 appends clearly historical markers to CURRENT while preserving activation and
the original source inventory checker. Removing either marker in a temporary
candidate view fails the original checker. F2 enumerates verified included-router
metadata and mounts, checks actual OpenAPI paths, rejects POST/PUT and unknown/cyclic
route shapes. Generated OpenAPI metadata's standard GET/HEAD route is explicitly
validated; production API routes/auth/security/dependencies are unchanged.

CI requires Reporter R8/R10/R11, Monitor M9/native, T1/T2/T3/T4, scanner, UEF,
package, UI, API and mutations. Linux 3.12/Windows 3.13 normal/-O matrix plus
FastAPI 0.142.2/0.143.0 API matrix on the exact candidate branch. Failures stay red.
Run `python scripts/refactor/shared_candidate_tests.py --suite all [--optimized]`.
Final runner uses verified ignored `.agentra-worktmp/<run>` TEMP/TMP/TMPDIR,
no runtime report writes. Earlier externally isolated runs predate policy-15 uptake.

## Executed Windows Python 3.14.2 evidence before final code commit

- Monitor local: 24 PASS, 6.29s. Initial sandbox 24 setup ERROR (WinError 5),
  then external TEMP retry; intermediate retained-count correction recorded.
- Combined original T3/T4-B before repair: 18 PASS / 6 FAIL (not merely five).
- Repaired full T3/T4-B: 24 PASS, 56.71s.
- Shared + F1/F2 + UI/package: 45 PASS normal, 24.84s; 45 PASS optimized, 23.24s.
- Separate FastAPI 0.143.0 / Starlette 1.8.0 venv API: 9 PASS, 0.75s.
- Whole selected matrix: 2865 PASS / 1 FAIL / 24 SKIP, 687.22s, 2890 collected.
  M9 full native replay included and PASS. Existing UEF1 real-artifact skips remain
  NOT_RUN for those data-dependent gates; no real inputs copied/fabricated.
- UEF9 failure: test_a_valid_current_authority expects CONDITIONAL=7 and
  NOT_COMPARABLE=84; clean checkout yields 0 and 91. Same interpreter, unchanged
  frozen BASE archive independently reproduces EXACTLY 19 PASS / 1 FAIL in 1.41s.
  No UEF policy/test changes, waiver, expected-count update or synthetic real-data claim.
- Intermediate shared probe: 39 PASS / 1 harness FAIL / 2 API fixture ERROR;
  probe overlapped test authoring. Stable shared rerun above passed all 45. A redirect
  mutation that did not change event shims was corrected. Added direct AST cases
  distinguish the all-moved annotation facade's remaining module statements.
- Expanded direct-negative/full optimized runs and exact committed-SHA results
  are recorded in the subsequent evidence checkpoint, not assumed green here.
- Expanded shared direct-negative tests: 75 PASS under -O, 29.73s. First full -O
  attempt was interrupted during Reporter tests after the newly observed scratch
  policy; one new test-harness StopIteration was corrected by mutating module
  statements for the annotation facade which has no unmoved function. No gate bypass.

## Sandbox acknowledgment after policy-15 uptake

SANDBOX_ROOT: C:/Agentra/.worktrees/p15-monitor-shared-20261018
GIT_COMMON_DIR: C:/Agentra/.git
WORKTREES_ALLOWED_FOR_WRITES: only the candidate registered above; live/Q12 read only.
SCRATCH_ROOT: candidate/.agentra-worktmp (git-ignored, checked before creation).
BRANCH/HEAD: candidate / 726d0e05a9b2f761ce633a35465ebdaffb7b72da before code commit.
DIRTY_STATUS: only task shared source/tests/docs/workflow; no unknown material staged.
PERMISSION_MODE_EFFECTIVE: workspace-write; protected Git/network operations tool-approved.
OUTSIDE_ROOT_WRITES: earlier explicitly approved OS-TEMP tests/dependency installer;
new runs use verified candidate scratch. No broad filesystem approval/config change.

## Unrun / acceptance and rollback

Hosted Linux 3.12/Windows 3.13 and whole repository pytest NOT_RUN at authoring.
Genuine historical persisted-report/LLM parity NOT_RUN: frozen real inputs absent.
Independent Claude audit NOT_RUN until SHA-specific response on Issue #14.
Source changes must not be self-approved; request AUDIT_PASS/AUDIT_REWORK/NOT_RUN.
Full selected gate remains FAIL because the reproduced UEF9 failure is not waived.
No main merge, deployment, policy/guard/authority change, live LLM/broker, Docker or automation.

Rollback: candidate is isolated and unmerged. Keep role refs and live checkout
unchanged; discard candidate adoption. No reset/clean/worktree deletion is required.
Deliver only task-modified paths since shared BASE; exclude venv/caches/untracked
operational data and deleted historical binary caches. Artifact packaging is local,
never performed in CI.

Exact code SHA 95c11cacb9c73ae3d97d89e2061372762efff12b: Windows normal and -O each 2895 PASS / 1 FAIL / 24 SKIP (2920 tests, zero setup ERROR). FastAPI 0.143 normal/-O each 9 PASS. No full PASS; baseline-reproduced UEF9 failure and missing real-artifact skips retained. Hosted CI and independent Claude audit NOT_RUN.

Final UI full-manifest probe: two patch-note schema/freshness tests completed,
then no API test completion for over 120s; interrupted. Remaining subset and
full-tier audit NOT_RUN. The same API tests PASS in both completed exact-code-SHA
matrices using the default fast audit. No full-audit claim.
