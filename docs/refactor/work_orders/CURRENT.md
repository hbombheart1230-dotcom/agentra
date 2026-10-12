# ACTIVE — Agentra P1.5 FAST TRACK Wave A (Reporting → Operator UI) — CLOSED FIRST_PASS_WITH_DEBT

**State:** WAVE_A_CLOSED_FIRST_PASS_WITH_DEBT (Codex PASS_WITH_FINDINGS, scope guard + CI fixed); P1.5.2 OPEN (final acceptance); P1.5.3 FIRST_PASS_WITH_DEBT (not final accepted); MAIN_FROZEN.
**Work order:** [P15_FAST_TRACK_WAVE_A_013.md](P15_FAST_TRACK_WAVE_A_013.md). **Workflow authority:** [Fast Track plan](../P15_FAST_TRACK_FIRST_PASS_2026_10_12.md) → [COMMON_RULES.md](COMMON_RULES.md).
**Roles:** Claude implements a wave → Codex audits the pinned aggregated diff → GPT/user final release decisions.
**Only `refactor/p1.5` development branch**; `main` frozen; no feature/task branches. **No ZIP/download artifacts — Git commit/push is the only deliverable** (user decision 2026-10-12).
**Wave A start:** `fb8de628eb56b0941007e90ad2e98b4f684983ba` (LOC010 code `b0cfc2b5646ff81ec5ce7b738f485a9d22365826`). Pinned wave SHA: see the evidence file / final commit.
**Protected:** live `C:\Agentra`, dirty Q12 worktrees, broker, real LLM, production data/reports, Docker/scheduler.

## Wave A result (evidence: [P15-FAST-TRACK-WAVE-A-CLAUDE-014.md](evidence/P15-FAST-TRACK-WAVE-A-CLAUDE-014.md))
- **A1 Reporting:** 55 more bodies (dependency maps + deterministic domain helpers) moved to 10 responsibility-named Owners; façades 4,047 -> 3,479 LOC (AI 1,656 / Markdown 1,325 / Story 498); 436 ABI intact; moved-body ledger 141.
- **A2 P1.5.3 Operator UI/Brief:** 136 IO-free bodies moved to 22 responsibility-named Owners; `data_access_core.py` 6,871 -> 4,594, `operator_period_summary.py` 3,210 -> 1,195, `operator_visibility.py` 1,879 -> 1,520 (-4,651); every public def/signature retained; use-time `facade.NAME` seams.
- Persistence/IO/clock/LLM-calling functions and any single function > 350 LOC (`_build_operator_brief_sections` 846, `_render_operator_brief_markdown` 652, `_load_operator_brief` 442, `_build_operator_brief_input` 426, ...) were intentionally NOT moved — SECOND_PASS_DEBT.

## Still open (not FINAL)
- Real frozen report Markdown/JSON/JSONL and LLM before/after parity **BLOCKED / NOT RUN**; full native pytest and `controlled_mock_lanes` write isolation **OPEN**; façade size and numbered Owner cohesion **SECOND_PASS_DEBT**.
- Codex Wave A verdict **PASS_WITH_FINDINGS** recorded in [P15-FAST-TRACK-WAVE-A-CODEX-AUDIT-015.md](evidence/P15-FAST-TRACK-WAVE-A-CODEX-AUDIT-015.md); the one policy failure (R2-era scope guard) is fixed by a stage-pinned guard and the CI workflow now validates the Fast Track active contract with all ZIP packaging removed.
- Next: Wave B (P1.5.4-P1.5.6) under its own scope/authority gate. No main merge, deployment or final P1.5.2/P1.5.3 acceptance.
