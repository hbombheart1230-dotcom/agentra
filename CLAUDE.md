# Agentra — Claude local implementation entrypoint

For any P1.5 task, do not implement from copied chat messages.

1. Work in the local C:\Agentra checkout; read docs/refactor/P15_EXECUTION_PROTOCOL.md.
2. Read the ONE active docs/refactor/work_orders/CURRENT.md and its exact design docs.
3. Follow the CLAUDE / PRIMARY ENGINEER procedure from the protocol; do only the current work order.
4. Verify local branch, SHA, dirty state, ancestry, and the two existing dirty Q12 worktrees. No force reset, clean, worktree pruning or operating on unknown data.
5. Never issue real orders, restart production or bypass safety to meet LOC targets. Newly extracted implementation Owner files <=350 physical LOC.
6. After an authorized implementation or audit, produce a bounded evidence report and commit/push on refactor/p1.5 only. For code patches, update UI patch notes JSON+Markdown and the daily patch. No tranche/artifact branches.
7. Let Codex independently audit the pinned code/evidence SHA. Claude never marks its own work GPT_ACCEPTED.

If CURRENT.md is AUDIT-ONLY, do not edit Python runtime files.
