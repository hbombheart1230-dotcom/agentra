# P1.5 Git-hosted work orders

- CURRENT.md is the ONE current task; agents must not silently assume a subsequent task from a previous chat.
- ../P15_EXECUTION_PROTOCOL.md is the role, state machine and approval protocol.
- Each task specifies ID, baseline/reference SHA, phase, allowed files, no-go actions, source design and objective acceptance.
- Claude submits one bounded commit and a task-specific report; Codex separately verifies the exact code SHA and writes an independent report. GPT makes the acceptance decision and updates CURRENT.md.
- Existing work-order evidence must be preserved, never overwritten. Do not create extra Git branches for tranches, CI or ZIP artifacts.
- Patch notes must update the UI-linked canonical JSON and Markdown for meaningful changes. Deliver ZIP with ONLY the paths changed in the particular commit.
- No unknown worktree cleanup. Two Q12 dirty worktrees remain outside P1.5 scope.
