# Agentra — CLAUDE PRIMARY IMPLEMENTER (not Agentco)

Agentra roles: **CLAUDE IMPLEMENTS → CODEX INDEPENDENTLY AUDITS → GPT/USER DECIDES**. Agentco uses the inverse implementation/audit roles.

1. Inspect actual `git status --short`, branch/HEAD, `git worktree list`, and fetched `origin/refactor/p1.5`. Preserve operational `C:\Agentra` and two dirty Q12 worktrees; no reset, clean, automatic checkout or data cleanup.
2. Read `docs/refactor/work_orders/CURRENT.md` → its ONE linked task → `docs/refactor/work_orders/COMMON_RULES.md`. Read only needed code/tests; no historical work-order rereading or lengthy chat prompts.
3. Implement **ONLY on `refactor/p1.5`** using a separate isolated clone (not live `C:\Agentra`; same branch must not be simultaneously checked out in linked worktrees). Never create any additional remote or local development branch. Existing R3-A/B/C are already on `origin/refactor/p1.5` as unaccepted WIP.
4. Run mock/offline targeted tests in isolated environment; record exact tests, code SHA, write audit, remaining NOT RUN. Preserve source truth/LLM prompt/retry/timeout/authority and do not touch live systems.
5. Commit/push authorized work **only to `origin/refactor/p1.5`**, after checking latest remote SHA and ensuring fast-forward; update both UI patch notes and a short daily patch; supply changed-files-only ZIP and concise evidence for Codex. No main merge, live deployment or P1.5.3 without GPT/user approval.
6. One-time branch cleanup per CURRENT: after verifying `origin/feature/p152-facades-r3` is fully ancestor of `origin/refactor/p1.5` and checking the old R3 feature worktree is clean, safely remove only that worktree/local branch and delete the old remote feature branch (`git push origin --delete feature/p152-facades-r3`). If dirty or unsure, STOP and preserve files; never force-remove. Do not authorize P1.5.3 or label unfinished full pytest / real snapshot parity PASS.
