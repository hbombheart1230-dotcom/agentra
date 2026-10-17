# P1.5 Continuous Engineering Loop — operating contract

> **2026-10-17 authority update:** Active [two-worker + GPT architect on-demand policy](assignments/11_P15_TWO_WORKER_ARCHITECT_ON_DEMAND_20261017.md). Claude Reporter -> independent shared-integrator reviewer; Codex Monitor -> isolated shared T3/T4/CI integrator; GPT architecture decisions on demand. `AUDIT_PASS` is by the OTHER worker, never self-certified by Codex's own integration tests. Recurring Work monitor is disabled. Older three-role/Work approval passages below are historical only.


## 1. Two independent loops

**Implementation loop (developer-owned):** pick next ready batch -> implement -> targeted test -> repair -> commit/push -> append checkpoint -> poll review inbox -> incorporate valid findings -> pick next ready batch. **Never stop merely because a commit completed or a reviewer has not responded.**

**Review loop (reviewer-owned):** inspect latest role HEAD and previous reviewed SHA -> compare changed code and test evidence -> run/reason about focused safeguards -> publish findings with severity and reproducible instructions -> later confirm owner resolution. Review should not seize the worker's branch or silently relax tests.

Both loops communicate through a **per-role GitHub issue** plus SHA-linked commits. Each worker retains a role-local journal for crash recovery. Design revisions are distributed through the design branch / approved PR, not by direct editing of working branches.

## 2. State machine

- PLANNED: scoped issue, owners, input baseline, acceptance criteria.
- READY: dependencies cleared, guardrails fixed.
- ACTIVE: owner implementing continuously; several internal batches may complete.
- REVIEW_PENDING: independent review requested at meaningful milestone; implementation **continues** on independent ready batches.
- REWORK: finding accepted; owner queues repair (priority P0 before unrelated work).
- ROLE_READY: all movable implementation owned, scoped tests verified, explicit exceptions logged.
- AUDIT_PASS / AUDIT_REWORK: independent Codex audit, SHA-bound.
- INTEGRATION_READY: **all** relevant P1.5 roles pass, conflict and shared contracts verified.
- MERGED: authorized final P1.5 merge with traceable CI and rollback.
- BLOCKED_DEPENDENCY: particular batch blocked; do not escalate to whole role while another safe batch exists.

Never declare a role COMPLETE from a single subset such as 12 moved files. Progress is verified against the role's **full inventory**.

## 3. Batch-selection and interruption policy

Assign **one whole role**, not a handful of files, as a continuous assignment. Internally choose batches by dependency and verification cost (typically one facade subsystem or cohesive feature group). Each batch should be substantial but independently reversible and testable. A stuck facade must not block separate ready formatting/read-model tasks.

When a batch is blocked, record symbol/file, attempted design, exact failure or missing authority, and suggested next action; then select another READY task. Escalate only when (a) scope/authority changes are necessary, (b) no ready safe work remains, (c) hard safety regression is found, or (d) credits/runners actually stop. An ordinary commit or progress report is never a stop signal.

Polling: at the end of each checkpoint, poll the role issue for reviewer findings newer than the last acknowledged comment ID; validate they apply to the current branch SHA before acting. Keep an acknowledgement table per finding so replies are not duplicated. A reviewer does **not** need to approve every batch.

## 4. Durable checkpoint format

Create a file for each milestone on the worker's branch: docs/dev-team/checkpoints/<role>/CP-<NNN>-<short-name>.md. Avoid concurrent edits to one global status file. Each file must contain:

~~~yaml
checkpoint_id: reporter-CP-003
role: reporter
base_sha: <verified parent sha>
head_sha: <pushed commit sha>
state: ACTIVE
scope: <bounded subsystem / exact path list>
implemented: <functions / files with disposition>
tests:
  - name: <focused command>
    result: PASS | FAIL | NOT_RUN
    evidence: <artifact pointer or log excerpt>
abi_monkeypatch: PASS | FAIL | NOT_RUN
authority_boundary: PASS | FAIL | NOT_RUN
contract_delta: <none or precise approved change>
findings_ack: <issue comment IDs + resolution>
blocks: <exact blocked items, not generic BLOCKED>
next_ready: <next safe batch in priority order>
remaining_scope: <estimated inventory remaining>
ui_patchnotes: <source path + entry, or NOT_APPLICABLE with reason>
~~~

**Self-consistency:** a checkpoint committed in the same commit cannot know its own commit SHA in advance. Put the immutable SHA in the GitHub issue checkpoint comment *after* push, and refer to the previous verified commit and this comment from the next checkpoint file. Do not use invented or self-referential SHAs.

For a role issue checkpoint comment, use:

~~~text
CHECKPOINT reporter-CP-003
SHA: <actual pushed SHA>
Scope: <short>
Tests: <PASS / FAIL / NOT_RUN with commands>
Findings: <acknowledged IDs>
Next: <ready batch>
Blocked: <exact issue or none>
~~~

## 5. Evidence and test cost policy

- Focused tests on every functional batch; ABI, monkeypatch-before-call/mid-call, negative authority, output byte parity, exceptions, side-effect behavior where applicable.
- Run broader regression per facade milestone and at role freeze, not the entire suite after each small move.
- Run independent Codex audit only at substantial milestones or ROLE_READY (can review spot samples earlier).
- Historical pinned BASE assertions are not replaced, weakened, skipped or re-anchored to new HEAD. Add a separate current-head ownership/equivalence ledger.
- Treat NOT_RUN as NOT_RUN, not PASS. Preserve exact commands, exit status, relevant logs, environment limitations.
- Temporary pytest/artifacts live outside repo or in session-isolated ignored paths. Automatically purge successful temp artifacts; keep bounded failure evidence (size/time/count); do not commit huge caches or sensitive artifacts.

## 6. Review cadence and human-facing cadence

**Developer:** checkpoint after each meaningful batch; review inbox read after checkpoint.  
**Reviewer:** review approximately every 4–6 hours *if independently invoked/scheduled* and at major semantic risk; leave SHA-bound notes without blocking every batch.  
**Operator:** one concise **daily** digest of ownership inventory, changed LOC, completed vs remaining batches, safety/contract status, links, blockers, credits/budget. Immediate escalation only for real-order authority changes, destructive data risks, unrecoverable stop, or scope expansion.

These cadences are a desired operating policy, not proof that a process is running. Timers/agents require a persistent runner, scheduler or deliberate Work session with appropriate permissions; GitHub does not supply a long-running Claude or Work session by itself.

## 7. Single-writer and branch rules

- One worker owns one implementation branch. Never force-push or move another worker's refs.
- Work/architect writes design PR and issue feedback, **not** implementation files on active role branches.
- Cross-role shared contract edits require a separately scoped integration queue. An owner may modify only the specifically delegated tests inside its own branch, with pinned historical guarantees intact.
- Keep PRs unmerged until P1.5 all-role freeze; final conflicts are resolved on the integration branch with explicit owners and CI.
- Use SHA + expected-head checks when coordinating automated writes. Re-read remote head on mismatch; no blind overwrite.
- Branch count: keep currently active owner branches plus at most one integration/design branch; archive/remove *only after* evidence and merge verification, never automatically delete an active branch.

## 8. Safety boundary

P1.5 is structure-preserving only. No production mode toggles, order placing, broker/execution/guard semantic change, trade authority transfer, Q10/Q12 strategy change, UEF mutation, Step5C, secrets, or report-LLM execution policy change. Monitor remains intent-only; approval plus guards remain mandatory; DTO schemas do not break; observation must not affect control flow. If crossing this boundary is necessary, record a named blocked dependency and request a separate authorization.

## 9. Unattended implementation: prerequisite checklist

An actual 24-hour loop requires a durable runner outside this document:

1. Persistent compute (Windows/WSL/container/CI runner), an authenticated CLI for each worker, permissions scoped to its repo branch and issue, and configured budget limits.
2. Supervisor process that detects worker process exit/credit exhaustion, resumes from most recent remote checkpoint, and avoids duplicate batch execution.
3. A poller for approved design updates and issue review comments, with allowlisted authors, throttling, retry/backoff, and idempotent acknowledgements.
4. CI targeted-test jobs, artefact retention, and a kill switch; branch protection prevents accidental main writes.
5. Daily digest delivery configured explicitly, not implied by this design.

**Minimum viable adoption without any runner:** give each worker the single long-horizon prompt from ROLE_RUNBOOK.md, use role issues as shared review inboxes, and let a reviewer inspect SHA deltas whenever launched. This provides durable collaboration but **not guaranteed autonomous operation after an AI session exits**.
