# Reporter R10-R12 — Continuous Non-Authority Work After 313 Moves

**Effective:** 2026-10-17 KST. **Status:** approved OFFLINE reporter verification/characterization, not approval to move I/O- or authority-bearing functions.
**Owner:** Claude only. **Source branch:** work/reporter-role-20261017. **Observed resume SHA:** 3b549d753f3cebbb2f7d843318e38e494bb698a8 (re-fetch before work).
**Issue:** https://github.com/hbombheart1230-dotcom/agentra/issues/11
**Work oversight:** Work owns shared T3/CI/integration and final scope decisions. Codex remains MONITOR implementer and is never reassigned to Reporter.

## Why the R8-007 'stop' must not recur prematurely

'Safe structural extraction exhausted' is a legitimate movement milestone, not equivalent to 'all safe Reporter work exhausted'. The 47 RETAIN_FACADE and 21 NEEDS_AUTHORITY dispositions do NOT authorize arbitrary moves. They DO leave useful baseline-only characterization, fixture, API consumer and CI readiness work. When all independent work in this packet is genuinely complete, a checkpoint and role park are correct; never invent pointless changes or claim the CLI will outlive its process.

R7 through R9 moved 313 bodies from 23 facade paths into 41 bounded owners. R8-000..007 checkpoints already cover: 91 triaged rows, 22 R8 callback/read proof, 53 renderer classes (54 tested cases), 500-file inventory, producer/consumer map, API file-by-path consumers, Windows UEF baseline explanations. Do NOT regenerate or rerun those artifacts without a new hypothesis. Continue with exact NEW gaps only.

## Strictly authorized work queue (execute as a sequence of SUBSYSTEM-SIZED batches)

### R10-A — Retained I/O contracts, not blind relocation
Read the committed r8_function_triage.json rows with disposition RETAIN_FACADE (47). Split into:
- read-only deterministic filesystem consumers;
- writers/side-effect or environment/clock/log consumers;
- module-identity-dependent (4);
- redefinitions (2);
- mixed or unknown.

For the genuinely **read-only** subset, implement targeted BASE-vs-HEAD offline temp-directory characterization, preserving read path AND ORDER, encoding, CRLF/missing/malformed/permissions, exception types and messages, callbacks and patch-at-use, no unexpected writes. Prefer parameterized tests over 47 near-identical files. Maintain an exact per-function coverage map (COVERED, NOT_APPLICABLE with reason, NEEDS_FIXTURE). Negative mutation of read order or exception must fail. Do not move these functions on the basis of a passing fixture without Work's explicit narrowly scoped relocation decision.

For writes, time/log and module identity, add offline **observation** and current behavior characterization only when side effects can be isolated without changing production output or permission. If not safely testable, record why and continue other groups. Avoid real persisted reports, broker/network, wall-clock-dependent flaky assertions. Only BASE/current temp inputs.

### R10-B — Cross-boundary report artifact parity
Extend the existing producer -> DTO/read model -> renderer -> path-based API consumer map with verifiable fixtures for the actual report artifacts (read only, copied synthetic/pinned fixtures). Use canonical file names and call traces from REPORTER_ROLE_FREEZE_PACK_R8.md. Test deterministic JSON/Markdown byte equality, Korean/unicode, newlines, missing/partial/stale artifacts, duplicate-run ambiguity, empty or malformed JSON, same effective precedence. API FastAPI tests should run only when dependencies are installed in isolated test venv, otherwise give exact NOT_RUN reason and dependency checklist. No actual LLM, live portfolio, production artifact write, schema/routing precedence change.

For runtime persisted-report behavior that cannot be reproduced offline: supply READ_ONLY evidence path and an executable non-production replay plan; do not guess PASS or fabricate representative output.

### R10-C — CI and matrix readiness without editing Work-owned shared files
Prepare role-local tests that import and execute deterministically on Linux Python 3.12 and Windows Python 3.13 where installed. Tests must not assume Windows-only filesystem state, git archive availability without fetch-depth history, timestamps, locale or unstable ordering.

Use current R8 suite plus negative guards. Report targeted evidence with executable command, interpreter, environment and PASS/FAIL/NOT_RUN. Local UEF2A missing operational data and UEF5_1 hash/CRLF mismatch have documented BASE reproductions; do not mask them by weakening test assertions. Improve only Reporter-specific fixture portability on your branch. The shared T3 guard and agent-tree allowlist/CI workflow are **Work-owned** and MUST stay unchanged on the Reporter branch.

Prepare CI inclusion list of seed, moved-body, read-contracts, callback-parity and renderer-bytes tests plus any R10 additions. Provide an exact integration proposal, not branch changes to shared workflows. Work independently tests the assembled candidate.

### R10-D — Coverage and residual ownership proof
For 47 RETAIN_FACADE rows, publish machine-readable classification with BASE/current test evidence or explicit reason not testable. For 21 NEEDS_AUTHORITY rows, do **read-only** callgraph + ownership/side-effect/authorization-boundary mapping; no test invocation that causes external effects, no production or LLM calls, no movement or semantic change. Include why each retained def is intentionally left in its facade and the exact Work/user decision required for any proposed movement.

Confirm controlled_mock_lane_report remains at existing legacy path as Reporter PRESENTATION/READ ADAPTER per Work decision; no Q10/Q12 lane/truth changes.

### R10-E — UI patch-note provenance and role acceptance packet
Verify the actual operator UI / API patch-note source and publish a role-local proposed entry with exact version, final move counts, tests and explicit NOT_PUBLISHED marker unless the connected source can be changed solely inside authorized Reporter scope. Work owns shared/UI runtime integration. Keep JSON/Markdown proposals consistent, correct links and source commit.

Freeze packet must cite: current pushed SHA, total moved/retained functions, 47 function coverage outcomes, 21 authority exclusions, registered API path consumers, actual test matrix PASS/FAIL/NOT_RUN, negative mutations, outstanding Work-shared P1 and integration-only blockers, required CI list, recovery steps, mock test artifact retention policy, and next action by owner. ROLE_READY only after Work independent acceptance and defined gates; otherwise PARTIAL_WITH_BLOCKERS is the honest status.

### R11 — Work findings and integration feedback loop
Before each new coherent batch and after each push:
1. Fetch fresh Reporter Issue #11 (or latest versioned issue-ready handoff if no write access).
2. Filter SHA-bound Work findings not already ACKed, prioritize P0/P1 and reproduce.
3. Patch Reporter-owned code/tests only, never Work shared guard/CI or Codex Monitor branch.
4. Publish actual pushed SHA and test status, then automatically choose next R10 ready group.

If shared Work integration raises a new Reporter-local defect, reproduce in a sandbox and fix it immediately. If no new review message, continue R10 work independently.

### R12 — Honest role park, NOT endless artificial work
Only after R10-A through R10-E are **completed or explicitly blocked with specific evidence** AND the latest Issue feedback contains no safe Reporter-local tasks may the worker mark REPORTER_LOCAL_READY_FOR_INTEGRATION / WAITING_ON_WORK. That means the local role work is complete, NOT P1.5 done. Do not keep a CLI session alive by repeated tests/commits or rewrite historical proof. Work next takes shared CI/T3/integration actions while Codex continues Monitor. A sleeping/offline CLI or exhausted credits cannot be made persistent by this prompt; a separately authorized supervisor is required.

## Mandatory checkpoints

After a cohesive set of fixtures/contract changes, commit/push on Reporter branch only with an R10-XXX checkpoint (issue comment if GitHub write access; otherwise versioned issue-ready evidence in branch). State START_SHA, PUSHED_SHA (comment after push), examined function IDs, actual test command/exits, negative mutation outcomes, existing failures vs BASE, covered/uncovered rows, Work finding ACK, next 2 READY groups, budget/session status (UNKNOWN if unavailable), and patch notes state. Do not ask for approval for a normal offline fixture batch.

## Prohibited

No forced movement or semantic edits of 47 retained I/O functions or 21 authority functions; no broker, live order, supervisor/guard, Q10/Q12, Step5C, truth precedence, LLM policy, persisted production report or secrets access. Do not rewrite historical pinned tests, weaken negative scopes, broad allowlists, or use unauthorized GitHub tokens. Preserve dirty trees. No main merge or Monitor branch modifications.

## Immediate Claude bootstrap (paste only this paragraph if the full doc is already on GitHub)

Resume Reporter at the actual HEAD of work/reporter-role-20261017 (was 3b549d753f3cebbb2f7d843318e38e494bb698a8). Read docs/dev-team/assignments/07_CLAUDE_REPORTER_R10_CONTINUATION.md from origin/design/agentra-dev-team-loop-20261017 WITHOUT merging the design branch, then Issue #11 and R8_CHECKPOINTS.md. R8-007 was a structural move milestone, NOT authorization to end the full role while R10 offline parity, consumer, coverage and acceptance work remain. Execute R10-A/B/C/D/E with cohesive verified batches, push checkpoints, poll review findings and continue. Do not move retained I/O or authority functions without separate scoped authorization. Work owns T3/CI, Codex owns Monitor, no main merge. Park only after every authorized Reporter-local work item is completed or explicitly blocked with evidence; leave exact SHA/resume point.
