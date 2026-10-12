# Agentra — CLAUDE PRIMARY IMPLEMENTER (not Agentco)

Agentra roles: **CLAUDE IMPLEMENTS → CODEX INDEPENDENTLY AUDITS → GPT/USER DECIDES**. Agentco uses the inverse implementation/audit roles.

1. Inspect actual `git status --short`, branch/HEAD, `git worktree list`, and fetched `origin/refactor/p1.5`. Preserve operational `C:\Agentra` and two dirty Q12 worktrees; no reset, clean, automatic checkout or data cleanup.
2. Read `docs/refactor/work_orders/CURRENT.md` → its ONE linked task → `docs/refactor/work_orders/COMMON_RULES.md`. Read only needed code/tests; no historical work-order rereading or lengthy chat prompts.
3. For active P1.5.2 R3, IMPLEMENT in ONE isolated feature worktree at `feature/p152-facades-r3` from current origin, not inside the live `C:\Agentra` checkout. Do A/B/C only when the previous stage passes. Keep 436 ABI/monkeypatch semantics, all new Owners <=350 physical LOC.
4. Run mock/offline targeted tests in isolated environment; record exact tests, code SHA, write audit, remaining NOT RUN. Preserve source truth/LLM prompt/retry/timeout/authority and do not touch live systems.
5. Commit/push only on the task-authorized feature branch, update both UI patch notes and a short daily patch; supply changed-files-only ZIP and concise evidence for Codex. **No direct merge to refactor/p1.5 or main; Codex then reviews fixed SHA.**
6. Don't authorize P1.5.3 or label unfinished native full pytest / genuine snapshot parity PASS.
