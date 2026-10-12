# Agentra Git-hosted work orders

- **Start:** [CURRENT.md](CURRENT.md) → [COMMON_RULES.md](COMMON_RULES.md) → ONE task linked by CURRENT. Don't reread archives or completed prior history on normal startup.
- **Agentra:** Claude IMPLEMENTS, Codex independently AUDITS pinned SHA, GPT/user approves. **Agentco roles are reversed**; do not mix projects.
- Original preserved protocol: [../P15_EXECUTION_PROTOCOL.md](../P15_EXECUTION_PROTOCOL.md) (R3 single-feature exception noted). Current R3 task: [P15_R3_FACADE_DECOMPOSITION_001.md](P15_R3_FACADE_DECOMPOSITION_001.md).
- Immutable old CURRENT records: `archive/`. Scope-specific reports, exact SHA, tests, blockers: `evidence/`.
- For R3 only, use one isolated feature worktree, no live operational-root testing, no Q12 cleanup, no real orders/LLM/production writes; feature merges ONLY after independent audit and GPT/user approval.
- All meaningful changes update UI-linked `docs/trading_agent_patch_notes_detailed_update/patch_notes.json` **and** `patch_notes.md`. Deliver changed-files-only ZIP.
