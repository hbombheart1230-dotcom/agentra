# P1.5.2 R3 — Git-first task setup / definitive Agentra roles (2026-10-12)

- User clarified that **Agentra = Claude implements / Codex independent audits**. Agentco alone is inverse. No user-facing long prompts; use `CLAUDE.md` / `AGENTS.md` and `docs/refactor/work_orders/CURRENT.md`.
- Archive the 214-line old CURRENT unchanged to `docs/refactor/work_orders/archive/CURRENT_R2_THROUGH_341CEDC_2026-10-12.md`. The new 26-line active pointer plus `COMMON_RULES.md` + `P15_R3_FACADE_DECOMPOSITION_001.md` contain phase R3 scope and all safety/evidence/reporting rules.
- Permit ONE isolated task feature branch `feature/p152-facades-r3` for Claude implementation only; Codex independently audits pinned code SHA. Only GPT/user authorizes integration back into `refactor/p1.5`. No unrelated extra branches.
- R3: 636 / 2658 / 2761 physical lines -> <=350 each if and only if original 45+209+182=436 callable contracts and monkeypatch/LLM/Reporting parity hold.
- Baseline `341cedcd95b37b2f30e8dc6b821a25c20fd3fa7b`. Prior isolated clone 295 PASS/1 SKIP and write-audit zero, but whole repository pytest incomplete and real report/LLM parity NOT RUN. P1.5.2 still OPEN; P1.5.3 unauthorized.
- Update UI-linked canonical patch notes (JSON + Markdown) and dynamic changed-only CI ZIP comparison, replacing stale prior-tranche baseline.
- Changes are **documentation, entrypoint and CI packaging only**; no Reporting runtime code changes and no R3 implementation/test PASS claims.

- Follow-up CI guard correction: obsolete R2 read-only task marker assertions replaced by R3 active pointer/roles/archive assertions.
