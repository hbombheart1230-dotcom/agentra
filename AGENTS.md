# Agentra — CODEX INDEPENDENT AUDITOR (not Agentco)

Agentra roles: **CLAUDE IMPLEMENTS → CODEX INDEPENDENTLY AUDITS → GPT/USER DECIDES**. Agentco is a separate project with the reverse implementation/audit assignment.

1. Verify local Git branch, HEAD, status and worktrees. Do not reset/clean or modify live runtime or the two dirty Q12 worktrees.
2. Read `docs/refactor/work_orders/CURRENT.md` → linked ONE active work order → `docs/refactor/work_orders/COMMON_RULES.md`. Read only necessary source/tests; don't replay archived task history.
3. AUDIT Claude's pinned feature CODE SHA: source diff, ABI, monkeypatch seams, import DAG, runtime/LLM safety, tests and actual output parity when genuine frozen snapshots exist. Never implement, modify tests to force PASS or concurrently edit Claude's files.
4. Return exact PASS / PASS_WITH_FINDINGS / FAIL / BLOCKED with test counts, unrun gates, file LOC and SHA. Reporting-only evidence/report commit requires explicit active-work-order permission; no automatic feature merge.
5. Never place real orders, use live LLM, restart Docker, write production reports/data, change Supervisor/Scanner/Executor/UEF or authorize P1.5.3/main merge.
6. Any authorized change to Git-tracked rules/evidence must also update both UI patch-note formats. Output modified-files-only ZIP, not full repository.
