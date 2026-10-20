> **HISTORICAL WORKFLOW — NOT CURRENT (2026-10-20).** The original Codex → Gemini sequence below describes a former development convention and must **not** direct P1.5–P8 sessions. Current **D00** [delivery policy](../ENGINEERING_DELIVERY_POLICY.md) with **D01** [Codex](../../AGENTS.md), **D02** [Claude](../../CLAUDE.md), and live [Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20) supersedes it. No CLI/worktree launch before DOC_FREEZE operator acceptance; retain the text below as history.

# Dev Workflow

## Flow
1. Codex implements
2. Gemini reviews
3. Codex finalizes
4. Zip (changed files only)

## Principle
- Single source of truth
- Additive change only
- Safety first
- Follow `docs/dev/code_structure_policy_2026-04-20.md` for script/module boundary rules
