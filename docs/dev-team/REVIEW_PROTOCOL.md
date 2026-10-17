> **ROLE CORRECTION (2026-10-17):** Claude owns Reporter, Codex owns Monitor, Work independently reviews both and coordinates shared T3/T4 and final integration. The authoritative current work orders are docs/dev-team/assignments/00–06. Any older Codex-as-Reporter-auditor/Runner text below is superseded.

# Continuous review, feedback, acceptance, and integration protocol

## 1. GitHub shared review inbox

Use one permanent GitHub issue per role as the cross-branch channel. Design docs may live on a separate branch; issue comments are immediately visible independent of code branch. Each issue body links its scoped program, implementation branch, pinned baseline and acceptance criteria. Every worker checks the issue at its checkpoint boundary. Do not direct-push reviewer opinions into a worker's working tree.

**Reviewer publication format** (in one issue comment; multiple findings allowed):

~~~yaml
review_id: P15-RPT-RV-001
role: reporter
reviewer: <actual actor and reviewer role>
head_sha: <40-char reviewed commit>
previous_reviewed_sha: <sha or FIRST_REVIEW>
scope_paths: [<file paths>]
findings:
  - id: F-001
    severity: P0 | P1 | P2 | NOTE
    file: <path>
    symbol_or_lines: <locator>
    claim: <specific failure or regression>
    evidence: <reproducer, changed lines, failing test>
    requested_fix: <narrow bounded repair / new test>
    acceptance: <exact objective proof>
suggested_next_review_sha: <optional>
~~~

Reviewer MUST differentiate **observed**, **not run**, and **inferred**. If there is no blocker, publish REVIEWED_NO_BLOCKER with exact SHA and tests examined—not a fabricated complete-program PASS.

Priorities:
- **P0** = live-trading authority/leak, secret disclosure, irreversible data loss, severe test bypass. Stop unsafe implementation path immediately; rollback/quarantine; operator notified.
- **P1** = ABI/monkeypatch/output regression, clear design violation, missing essential test. Owner repairs next unless another independent P0-safe work packet has higher critical value.
- **P2** = maintainability, performance, weak test quality without demonstrated contract break. Schedule within role.
- **NOTE** = observation/idea, not binding new scope.

An owner response must cite finding ID + fix SHA + targeted proof, or REJECTED_WITH_REASON and a verifiable counterexample. A reviewer later marks VERIFIED or REOPENED. Do not close findings just because a commit was pushed.

## 2. Work reviewer procedure

At each explicitly launched/scheduled review window:

1. Read this protocol and last review marker, not all historical chats.
2. Inspect role issue, most recent checkpoint comment, its **actual remote HEAD**, and diff from last reviewed SHA.
3. Examine changed code plus imports, facade ABI, exported APIs, relevant tests and forbidden authority paths. Focus on semantic risks and gaps; do not just count moved files.
4. Compare claims against test command/results; independently reproduce when an environment exists; otherwise label NOT_RUN.
5. Publish evidence-bound findings to the **role issue**, and optionally detailed annotations to the draft role PR. Record reviewed SHA.
6. Update design/change-request docs only on a separate coordination branch if architecture needs adjustment; link that PR/commit on the issue and require explicit acceptance for scope changes.
7. Do not require reviewer sign-off for each internal commit. If a worker has already advanced past the inspected SHA, require re-check before claiming a newer SHA passes.

ChatGPT Work is not a permanently running GitHub bot by default. Scheduled review requires an explicitly configured runtime/automation that can actually invoke a reviewer with GitHub access.

## 3. Developer feedback poll

At the end of each checkpoint:
- Fetch current design ref; determine if a revision has been **approved**, not merely proposed.
- Fetch role issue comments newer than the last acknowledged comment ID.
- De-duplicate finding IDs; reject irrelevant/mismatched repo/branch/contract instructions.
- Map actionable comments to backlog: P0 immediate halt only for affected path; P1 next repair; P2 queue; NOTE no scope expansion.
- Reply once with linked SHA, tests, or documented disagreement.
- Continue the next approved READY task—**no user handoff**.
- If an issue thread disagrees with signed-off safety requirements, safe defaults win; only operator may authorize risk envelope changes.

## 4. Audits and shared-contract integration

**Independent Work audit** of both Claude Reporter and Codex Monitor is required at substantial milestones and ROLE_READY. Work compares code, fixtures, negative-path coverage and authority boundaries against scoped design at exact SHA; additional independent reviewer may be separately allocated, but Codex is not a Reporter auditor under the active assignment.

Shared-tests/CI that touch multiple role branches go into a **separate integration change queue**, not arbitrary edits on the active other branch. Role owners may modify only tests explicitly authorized for their scope while preserving pinned historical rules. Integration maintainer cherry-picks only verified, dependency-safe changes and resolves overlap after all roles are ready.

Final integration gate:
1. Verify each P1.5 role's ROLE_READY SHA and complete owner ledger.
2. Rebase/merge only into dedicated integration branch; record all source SHAs.
3. Run contract/negative/trading-authority leak tests and representative full regression in mock conditions.
4. Inspect UI patch notes, temporary artifact hygiene, changed-path manifest, rollback.
5. Independent Work audit of both role branches + operator authorization.
6. Only then merge integration result into main. Never auto-enable live trading.

## 5. Daily operator digest (single update)

~~~text
Agentra P1.5 — YYYY-MM-DD
Reporter: ACTIVE/ROLE_READY | HEAD <SHA> | RP waves <done>/<total> | facade before/after LOC
Monitor: ACTIVE/ROLE_READY | HEAD <SHA> | completed + remaining
Additional roles: <state / not activated>
Validation: <PASS/FAIL/NOT_RUN by contract group>
P0/P1 open: <counts and links>
Merge: NOT_YET / READY_FOR_APPROVAL
Credits/runner: <observed remaining if available; do not invent>
Only decisions needed: <none or exact approval request>
Next autonomous batches: <one line per active role>
~~~

If automatic daily delivery is needed, configure an actual scheduler/notification recipient separately. GitHub branch updates alone do not send this digest to the user.
