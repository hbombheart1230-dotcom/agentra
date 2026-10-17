# Agentra Work operating rules

## Ownership and authority
- User owns priorities and activation. User approval is required for main merge, real-trading deployment and safety-authority changes.
- Work owns architecture, project scope, accountable assignments, evidence evaluation, technical verdict and serial integration management. GitHub write capability is not authority to release.
- User-authorized assignment (2026-10-17): Claude implements Reporter and audits Monitor; Codex implements Monitor and audits Reporter. A reviewer never certifies its own implementation. Work integrates shared changes and records the final technical decision; an implementation defect found during audit returns to the implementer.
- Work cannot silently launch/control external Claude/Codex sessions. Handoffs are written instructions; status is based on observed commits and submitted evidence, not assumed background activity.

## Project size and continuous development
One agent's entire responsibility is one project. Its internal batches are implementation details, not five-file approval checkpoints. The implementer proceeds through approved independent batches without user interruption. A whole-role responsibility register records every identified owner/facade, consumer and effect as MOVE / KEEP_WITH_REASON / SHARED / BLOCKED / OUT_OF_ROLE. Reuse existing inventories; investigate only relevant changed edges. Unknown is not proof of safety or absence of consumers.

For paths outside the seed ledger, the implementer may continuously extend its own role ledger BEFORE editing, recording an exact source-to-destination pair, runtime BASE blob, actual consumers, purity/effects and test plan. This is preauthorized only within the own-role pure scope in ACTIVATION.md, preserving V3 and all protected boundaries. Work and the independent reviewer validate the aggregate ledger at handoff; no per-file Work/user acknowledgment is needed. Ambiguous/shared/effect paths stay BLOCKED and independent work continues. Safety boundary expansion and behavioral changes require separate scope decisions. Do not fill folders with placeholders or rename the frozen V3 architecture.

Physical relocations preserve complete implementation blobs, ABI, module identity, late-bound patch seams, order/alias/exception behavior and output bytes. Internal decomposition is a separate named batch with appropriate semantic parity evidence; do not claim blob equality for rewritten bodies. New implementation owners follow the existing 350 physical LOC policy; facade/oversize debt is explicit, never formatting compression.

## Parallel ownership and integration
Use isolated role branches from the same user-approved integration BASE; no operational workspace edits. Reporter and Monitor must have disjoint source/test/fixture/evidence writes. TMP/TEMP and pytest basetemp are unique per run and process; no deletion of active paths. Clean successful temporary artifacts; retain failure evidence with a recorded bounded retention policy.

Work exclusively owns shared AST allowlists, versioned exact package sets, workflows, root instructions, CURRENT and official UI patch notes during integration. Workers submit unique proposed note entries with their evidence; Work appends BOTH patch_notes.json and patch_notes.md before integration acceptance. This narrow serialization rule avoids branch overwrites. No simultaneous shared-file edits or blind branch merges.

After independent pinned-SHA role review, integrate one role then the other using exact approved paths/commits; reconcile shared contracts without weakened assertions. Keep a checkpoint after each role. On combination failure isolate the role delta in the non-operational integration workspace; never force-reset/push the operational branch. Re-audit changed patches; require complete hosted required CI on the final combined SHA before technical acceptance. main and deployment remain separate approvals.

## Tests and performance
Local: scope/protected paths, BASE blob or named decomposition parity, strict shim AST plus mutation/-O negatives, fresh-process import order and monkeypatch, relevant consumers, BASE-frozen outputs/exceptions/order/alias/effects, and impacted legacy gates. Frozen BASE producers are separate from FINAL; fake LLM/Broker only. Fixtures stay deduplicated; target <=256 KiB, justify larger fixtures to Work before adding. Never manufacture missing persisted/live parity.

Role integration: existing mandatory Linux/Windows T4, Reporting/Web/native LF and Scripts gates, plus explicit new role test wiring and no missing/skip substitution. Confirm the actual required job matrix at activation; do not invent or silently remove requirements. Missing provenance/parity = BLOCKED/NOT RUN. Record PASS/FAIL/SKIP/NOT RUN separately. Do not relabel old failures as proven pre-existing without evidence.

Reuse proof by (source SHA/blob, dependency/test/fixture hashes, runtime, OS, relevant environment, scope). Code, environment or integration changes invalidate affected proof. Do not repeat unrelated full local suites before CI or rerun identical successful CI reflexively. Measure capture/move/focused tests/legacy gates/queue/CI/rework separately. No live LLM, broker, production writes or restarts. Cached immutable metadata must retain safety checks.

## Completion and truthful progress
Weights fixed at activation: responsibility coverage 15%, approved structural work 40%, compatibility/effect proof 20%, independent audit 15%, combined integration/CI 10%. Each point is earned by a named acceptance item and SHA evidence; use 0% or NOT_STARTED before execution. Within a phase use predefined items, not files/LOC/time spent. A seed-only migration is PARTIAL, not whole-agent completion. Deferred in-scope work remains open unless explicitly accepted as a reduced scope; protected responsibilities can be complete dispositions without being moved, with justification. P2 debt is visible, never erased by a green migration.

P0/P1 or safety-boundary violations: immediately report, pause affected execution/integration, preserve evidence and continue only independent safe work. P2: log owner, impact and closure condition; continue when acceptance permits.

## Reporting in this conversation
Use the existing six-hour Agentra report, Asia/Seoul 00:00 / 06:00 / 12:00 / 18:00. Do not create or modify schedules, notifications, dashboards or servers. Report: actual owner changes and SHA; tests/CI; blockers; next six hours; user decision or none. Reporting never pauses normal authorized development. On inactive local sessions, report NOT_STARTED/IDLE/UNKNOWN from evidence; GitHub inactivity alone is not proof of a running or stopped process. No claim of background Work control.

Workers write uniquely named role evidence/status on their own branch. Work reads GitHub evidence at review/report time and updates shared STATUS.json; workers never wait for a six-hour report to proceed. If local execution evidence has not been handed off, say UNKNOWN rather than invent activity.

## Codex Auto-review (permission review only)
Recommend Auto-review when supported; preserve sandbox, filesystem/network boundaries and managed requirements. It routes eligible escalation requests to a separate safety reviewer, not a correctness audit or GitHub PR review. No automatic main merge/deployment/safety authority changes. No credential probing, risky broad deletion or policy-denial bypass. If denied, choose a materially safer permitted route or report the blocked action; do not switch to Full Access to force it through.

Local state is UNVERIFIED until the actual worker checks it. Desktop: make Auto-review available under Settings > General > Permissions when supported, then select Approve for me for the current chat. CLI example: workspace-write sandbox, approval_policy="on-request", approvals_reviewer="auto_review"; do not overwrite managed policy. UI availability depends on version/account/organization. Do not rewrite a complete security policy merely to add this setting.

Official guidance checked 2026-10-17: https://learn.chatgpt.com/docs/sandboxing/auto-review and https://learn.chatgpt.com/docs/permission-modes . Free/unmetered safety-review pricing was user-provided; the fetched Auto-review page did not establish pricing, so do not promise zero usage for the overall coding task. Auto-review is recommended, not a blocker when unavailable; default human approvals remain.

## Release artifacts
Role handoff includes BASE/FINAL SHA, exact changed paths, disposition ledger, proof manifest, independent verdict and bounded changed-files-only ZIP outside CI. Exclude secrets/live data/logs/caches. Keep official UI JSON/MD synchronized through the integration owner. Planning-only edits need documentation validation, not runtime CI.
