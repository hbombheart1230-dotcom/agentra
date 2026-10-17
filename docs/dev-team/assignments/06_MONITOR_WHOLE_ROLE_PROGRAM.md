# Monitor P1.5 — Codex-owned whole-role continuous program

**Owner:** Codex sole writer on work/monitor-role-20261017
**Observed HEAD:** a33c28780592917481eb610a3d69c3948e4a4ead, re-fetch actual SHA before running.
**Status:** 11 moved full BASE implementation blobs already documented; local proof reports 1,213 PASS and five shared-gate mapping failures. These counts are developer-reported and must not be mislabeled as hosted CI PASS. Role completeness not independently decided.
**Base:** d773709ba2f70471fad9badba4f92400f7818319.
**Shared issue:** https://github.com/hbombheart1230-dotcom/agentra/issues/12.
**No main or integration branch merge until all P1.5 roles finish.**

## Verified GitHub artifacts to begin with, without repeating work

- docs/refactor/work_projects/evidence/monitor/path_ledger.json
- docs/refactor/work_projects/evidence/monitor/HANDOFF.md
- docs/refactor/work_projects/evidence/monitor/test_results.json
- docs/refactor/work_projects/evidence/monitor/proposed_patch_note.md
- tests/test_work_monitor_role_contracts.py
- scripts/refactor/work_monitor_contracts.py
- tests/test_p163_t4b_extraction_gates.py, tests/test_p159_current_owner_contract_gates.py
- Test fixtures under tests/fixtures/work_monitor/

The existing Monitor seed moved 11 canonical owner modules under libs/agents/monitor/events and libs/agents/monitor/projections behind strict identity shims in libs/runtime/monitor. The role evidence describes 1,598 implementation LOC and <=285 LOC per owner, 108 BASE-frozen synthetic cases, 1,213 unique PASS and five shared-contract mapping failures; verify numbers at current SHA. A later Monitor commit contains an independent audit of an older Reporter SHA 81f6a691. That bounded historical audit is not a substitute for any Reporter R7 final audit and does not require Codex to stop Monitor implementation.

## Internal continuous batches

### M0 — Rebaseline and classify ownership
- Check remote branch HEAD and working tree, preserve dirty code and existing evidence; do not reset or re-run completed migrations blindly.
- Revalidate path_ledger exact source/destination mapping and BASE blobs, module identity, import order, functions/signatures, use-time monkeypatch, behavior parity, owner LOC and forbidden runtime effects.
- Enumerate all Monitor-owned functions across graphs/nodes/monitor_node.py, libs/runtime/monitor, entry/exit policy/runtime helpers, projections, events and dependent tests. Classify canonical implementation, compatibility shim, true policy authority, shared contracts, ops and blocked items. Do not assume all monitor-related files must move.
- Record meaningful no-op/retained decisions and a next-ready list.

### M1 — Proven pure-body and projection extraction
- Continue only with safe structural changes in projections, event payloads, decision traces, read-only state views, and deterministic builders after caller/patch contract analysis.
- Keep old module path exports, import identity, signatures, exception and alias behavior and exact AST/byte proofs. New owners <=350 LOC; no mutation of policy/trade authority.
- A function named evaluate_exit_policy or central monitor_node orchestrator is not to be mechanically moved under this structural mandate merely to reduce LOC.
- Preserve the canonical rank-1, candidate fallback, entry/exit policy, cooldown, sizing, hold/position and session behavior exactly. This is NOT a strategy change assignment.
- If an owner cannot be moved without semantics or contract change, mark exact blocker and continue another safe group. No forced migration.

### M2 — Negative safety contract and consumer parity
- Compare BASE and CURRENT with real synthetic replay: dictionary insertion order, float/int conversions, exception classes and messages, alias/container identity, mutable input behavior, callback order, facade lookup at use time, import in both orders, module sys.modules identity.
- Validate Monitor emits OrderIntent only; no direct Broker or Executor call added, no Supervisor/guard bypass, no real trading authority.
- Validate no changed entry/exit thresholds, cooldown semantics, position sizing, Q10/Q12 decision policy, UEF/Step5C truth or persistence.
- Add focused path-negative, shim mutation, forbidden-import and policy-authority leak regression tests. Preserve historical T3/T4 tests; no skip/xfail or silent allowance broadening.
- Test under existing Python local and CI 3.12 when available; NOT_RUN is distinct from PASS. Keep successful pytest artifacts isolated and cleaned, failed evidence bounded.

### M3 — Shared-contract handoff (proposal only)
- The reported five mapping failures concern shared T3/T4/agent-tree gates and integration with Reporter. Do not independently relax them on Monitor branch.
- Record exact legacy→owner pair list and tight shared patch proposal. Work owns acceptance and the final shared-integration candidate after role readiness. A proposed exception must preserve old BASE checks, negative tests and exact package allowlists.
- Do not import Reporter code changes to force standalone green status. Do not edit Reporter branch or main.
- Update actual UI-linked patch-note source only if proven connected and safely within role; otherwise supply proposed JSON and Markdown entries for Work integration.

### M4 — Complete Monitor responsibility audit and role freeze
- For every Monitor-origin file/function, account for ownership, moved bodies, intentional compatibility wrappers and actual blocked scope with reasons. Evaluate remaining substantial safe groups, including other deterministic helper modules.
- Run representative focused consumers and broader role gates, native Windows and required Linux CI matrix if available; use mock-only run, never real order action.
- Record git diff changed paths, high-risk policy files unchanged, results PASS/FAIL/NOT_RUN with exit, negative evidence and rollback.
- Declare ROLE_READY only after complete owner inventory, safe moves done, equivalence proven, no unaddressed role P1 and integration-only blockers enumerated. Otherwise PARTIAL_WITH_BLOCKERS and continue another ready group if one exists.
- Codex may assemble a concise Monitor-specific audit package but Work or another independent reviewer is required to verify Codex's own implementation. Self-certification not accepted.

## Continual team workflow

One whole role is assigned, not a single set of eleven files. Repeated cycle:
1. Read only changed diff since checkpoint, Issue #12 latest and actual branch SHA.
2. Select next highest-value READY Monitor group.
3. Implement in a bounded reversible batch, run focused positive and negative tests.
4. Commit and push on Monitor branch only.
5. Write append-only checkpoint with scope, actual SHA posted after push, test commands, before/after LOC, open blockers, next safe batch. Read new Work findings on Issue #12 and repair valid P0/P1.
6. Continue without another user prompt; a commit is NOT a stop condition.

If GitHub issue writes are unavailable, do NOT scrape credentials. Push role evidence and an Issue-ready message on Monitor branch, keep coding. If a batch's safety approval is blocked, leave exact proposed patch and continue other safe Monitor tasks.

## Completion and scope protection

Monitor is intent generation, never execution. Trading authority remains Supervisor and Execution/guard layers. Any changes to live Broker, Executor, Supervisor, order/cancel API, real execution toggles, entry/exit/sizing/cooldown policies, Q10/Q12 logic, Step5C, UEF, truth precedence or LLM policies require a new explicit user authorization. Do not mix this refactor with performance or strategy work.

At final role checkpoint include:
- Actual sha and all changed paths
- Total audited source files/functions; moved vs retained and why
- Test pass/fail/not-run by command and exact platform; negative guard outcomes
- Five known historical shared mapping failures status and isolated integration request
- Work findings addressed with proof
- UI patch-note provenance and changed-files-only ZIP + SHA-256 manifest
- Residual blockers, precise next SAFE steps, independent acceptance request
- No early main merge or destructive branch cleanup

## Full-time reality check

CLI sessions do not survive unlimitedly based on a prompt. A verified persistent runner/host with daily cost caps, stop and resume is required for truly unattended multi-session operation. Building that runner is **NOT** Codex's Monitor assignment; it remains future infrastructure work. Within every active Codex session, keep processing Monitor batches instead of final-answering after each internal checkpoint.
