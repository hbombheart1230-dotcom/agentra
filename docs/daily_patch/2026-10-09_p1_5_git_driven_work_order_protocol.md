# 2026-10-09 — P1.5 Git-driven Claude and Codex work orders

## Purpose
Stop relying on manually copied long conversations to hand tasks to local agents. GitHub is the authoritative work scope/role document system.

## Files
- CLAUDE.md — root discovery for local Claude, points to the one current order and protocol.
- AGENTS.md — root discovery for Codex, independent verifier role.
- docs/refactor/P15_EXECUTION_PROTOCOL.md — fixed read order, state transitions, test/documentation/branch and safety rules.
- docs/refactor/work_orders/README.md — immutable evidence and current task policy.
- docs/refactor/work_orders/CURRENT.md — active P15-R2-R0R1-001 audit-only task.
- docs/refactor/README.md — navigation.
- canonical UI-linked JSON and Markdown patch notes synchronized.
- .github/workflows/p152-r2c-residual-regression.yml — validates current task and role links, runs existing reporting tests and creates only-changed-files ZIP.

## Workflow contract
GPT writes or advances CURRENT.md after verified evidence. Claude works local C:\Agentra, commits bounded work on refactor/p1.5; Codex independently verifies an exact submitted code SHA, writes only its separate verification report; GPT decides PASS/FIX/NEEDS_HUMAN before next order. Claude and Codex must not edit the same implementation files concurrently.

## Current first work order
P15-R2-R0R1-001 (AUDIT-ONLY): verify local branch and two dirty Q12 worktrees, establish read-only Reporting BEFORE baseline, build actual sections.py caller/Owner/monkeypatch map, propose one safe <=350 LOC extraction for the NEXT work order. NO Python code change authorized.

## Preserved
P1.2 CLOSED, P1.3 FULL_DOCKER_FROZEN with 2 GiB production constraint per user handoff. R2-A/B/C lineage not rolled back, Step5C/D, R6.2, UEF, seven-agent topology, strategy/LLM and broker authority unchanged. Only main/refactor/p1.5 remote branches. No production operations.
