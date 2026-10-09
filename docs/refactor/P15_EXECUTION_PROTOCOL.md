# P1.5 Git-Driven Claude/Codex Execution Protocol v1.0

Date: 2026-10-09
Repository: https://github.com/hbombheart1230-dotcom/Trading_Agent_System (may redirect to /agentra)
Canonical branches: main (frozen) + refactor/p1.5 (only implementation)
Primary runtime/artifact environment: C:\Agentra (Windows, Docker, SQLite, data/reports, scheduler)
This is HOW to work. CURRENT.md is WHAT to work on.

## Authority documents (read in order)

1. docs/refactor/P15_EXECUTION_PROTOCOL.md
2. docs/refactor/work_orders/CURRENT.md (one active task and exact phase)
3. docs/refactor/p1_5_small_owner_policy_and_rollback_decision_v1_2.md
4. The versioned stage packet linked from CURRENT.md, e.g. docs/refactor/p1_5_reporting_implementation_packet_v1_2.md
5. docs/refactor/p1_5_refactor_constitution.md and docs/refactor/p1_5_1_to_11_responsibility_alignment_v1_1.md
6. Executor tasks additionally need p1_5_executor_safe_decomposition_packet_v1_1.md and the original v1.0 precise guard order; full freeze needs p1_5_full_regression_docker_uef_freeze_implementation_packet_v1_0.md.

Original detailed designs and historical old branch names are preserved evidence, not current checkout instructions.

## One-work-order state machine

READY_FOR_LOCAL_BASELINE -> CLAUDE_IMPLEMENTING -> CLAUDE_SUBMITTED
-> CODEX_VERIFYING -> CODEX_PASS / CODEX_PASS_WITH_FINDINGS / CODEX_FAIL / BLOCKED
-> GPT_ACCEPTED / GPT_FIX_REQUIRED / HUMAN_REVIEW_REQUIRED -> NEXT_WORK_ORDER

CURRENT.md status transitions are documented by GPT only after reviewing the appropriate evidence. Passing CI alone does not mark a work order accepted. An AUDIT-ONLY order does not authorize source edits.

## Claude — primary local engineer

- Read CURRENT.md completely before any action. In C:\Agentra check git branch --show-current, git rev-parse HEAD, git status --porcelain, git merge-base --is-ancestor main refactor/p1.5, git worktree list --porcelain. Fetch as needed but never hard-reset or discard either existing dirty Q12 worktree.
- Check the work order's observed remote SHA and the actual local SHA; a docs-only update may advance HEAD. If unexplained local changes or mismatch exist, report BLOCKED rather than inventing a reconciliation.
- BEFORE: capture explicit unchanged outputs, direct callers, private monkeypatch references, test baseline and truth/LLM/fallback/authority requirements. Use captured read-only local reports; redact secrets.
- Only if CURRENT authorizes CODE CHANGES: move one coherent responsibility to one canonical Owner; every NEW/moved/expanded Python implementation Owner <=350 physical LOC (150–300 preferred), no new 1,000-line helper dumping ground; retain existing patch/import seams and canonical source precedence.
- Execute targeted pytest, real-data equivalence when safe and available, import/cycle and no-production-write checks in isolated temp directories. Record commands, SHA, count and PASS/FAIL/NOT RUN; do not fake operational acceptance.
- For meaningful code changes: append to BOTH docs/trading_agent_patch_notes_detailed_update/patch_notes.json and patch_notes.md; add a daily patch note; document actual changed paths and local rollback/failure evidence. Test PASS temp artifacts cleaned; FAIL evidence bounded.
- Commit/push only on refactor/p1.5; changed-files-only ZIP can be provided by the repo Actions workflow or created from a deterministic commit diff. Do not create ci/* or artifacts/* branches.
- Publish a Claude evidence report at the CURRENT-specified path, pin the commit SHA; stop for Codex. Claude does not self-certify final PASS.

## Codex — independent local verifier

- Read the same canonical Git files and Claude's submitted SHA. Recompute actual git diff, caller/import/monkeypatch graph, physical file LOC, canonical single Owner and semantic equivalence; independently run targeted and broader tests as permitted.
- Check no weakened tests/fixtures, owner->façade cycles, hidden graph mutations/IO, changed LLM call/prompt, changed report truth/serialization, and frozen seven-agent, UEF/Step5C/D/R6.2, Supervisor/Executor mutation boundary as affected by the actual change.
- Verify evidence and failures rather than trusting Claude's report. Do not implement fixes and do not touch Python code. Commit ONLY a separate work-order verification report after Claude completes, when asked; record the CODE SHA separately from verification-report SHA.
- Give PASS, PASS_WITH_FINDINGS, FAIL or BLOCKED with tests actually run and NOT RUN gates. CODEX_PASS is not production/freeze approval.

## GPT — design gate / next order

- Inspect the work-order report(s), pinned implementation SHA, changed files, CI and unresolved evidence.
- Decide GPT_ACCEPTED, GPT_FIX_REQUIRED or HUMAN_REVIEW_REQUIRED. Record the decision in versioned CURRENT.md; only then publish the next work order. All stages end in the P1.5.11 full pytest/mock Docker/UEF/Codex + human freeze gate.

## Frozen rules

P1.2 CLOSED; P1.3 FULL_DOCKER_FROZEN with 2 GiB production memory, per 2026-10-09 operator handoff. Ordinary refactor never reopens those baselines.
Do not change seven-agent topology, Scanner rank/formulas, Strategist prompts, entry/exit, cost_edge, stops, BTC/Q, UEF COMPLETE/current/latest/registry identity, R6.2 immutable readiness/current owner/generation, Step5C CAS/Step5D, Supervisor approval, broker mutation/UNKNOWN or Docker production authority.
No live brokerage orders, production restarts, destructive SQL, production-volume crash tests, test-generated production writes or dirty Q12 worktree cleanup. No new LLM decision owner. Safety overrides LOC.

## User's one-sentence commands

Claude: "Read CLAUDE.md and docs/refactor/work_orders/CURRENT.md on refactor/p1.5, execute only its Claude task and commit the report."
Codex: "Read AGENTS.md and docs/refactor/work_orders/CURRENT.md on refactor/p1.5, independently verify Claude's pinned commit and publish only the audit report."

No large prompt copy-paste. Everything needed for actual scope, stop rules and reporting paths belongs in GitHub.
