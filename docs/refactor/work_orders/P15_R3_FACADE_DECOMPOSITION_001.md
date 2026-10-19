> **HISTORICAL WORK ORDER — NOT CURRENT AUTHORIZATION.** ACTIVE/READY/pending statuses, role assignments, branch/worktree cleanup commands, and next steps below describe the original pinned historical task only. Do **not** restart implementation or audit, create/delete branches/worktrees, or run operational checks from this page. Current authority: [D00](../../ENGINEERING_DELIVERY_POLICY.md) + [CURRENT](CURRENT.md) + [GitHub Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20). Original safety restrictions and recorded SHA/PASS/FAIL/SKIP evidence remain intact.

# P15-R3-FACADE-DECOMPOSITION-001 — P1.5.2 residual large façade work

**Status:** READY_FOR_CLAUDE_IMPLEMENTATION, no implementation performed in this task activation.
**Pinned existing source baseline:** `341cedcd95b37b2f30e8dc6b821a25c20fd3fa7b`; start from latest `origin/refactor/p1.5` containing this task docs commit.
**Agentra roles:** **CLAUDE IMPLEMENTS → CODEX AUDITS → GPT/USER APPROVES**. Agentco is reversed. Never swap.
**Branch/workspace:** Create ONE isolated worktree `C:\AgentraWorktrees\p152-facades-r3`, branch `feature/p152-facades-r3`; preserve live root `C:\Agentra` and both dirty Q12 worktrees. This feature is the only authorized exception to old no-extra-branch rule.
**Allowed runtime files:** Three target `libs/reporting/trade_story_pipeline.py`, `libs/reporting/trade_report_markdown_clean.py`, `libs/reporting/trade_report_ai.py` and directly related Reporting helpers/Owners only. Additional focused P1.5.2 Reporting tests, task evidence, daily patch, UI patch notes. NO unrelated execution/LLM routing/Scanner/UEF/Step5C/D/Q12/Docker API changes.
**Rules:** `COMMON_RULES.md` (already linked by CURRENT); read source and precise tests only, no historical task traversal.

## Preflight (Claude)
- Observe branch/HEAD/status/worktrees without changing live workspaces, fetch `origin/refactor/p1.5`. If conflicting/dirty feature tree, STOP; do not reset.
- Record original 636/2658/2761 physical LOC and public callable 45/209/182 (436 total), signature and module-level patch/dynamic consumer ledger; cache relevant offline fixed fixture output and current baseline test counts in safe isolated temp locations.
- Avoid changes to real LLM calls, prompt/retry/model/timeout/call count. Genuine historical report and LLM snapshot inputs are absent: don't try to read live operational data as comparison baseline.

## Work sequentially (Claude implementation)
- **R3-A STORY (636 → <=350):** move coherent assembly/dependency/formatting pieces to existing `trade_story_*` Owners or new <=350 LOC small Owners. Preserve 45 callable names, signatures, patch hooks and exact render outputs.
- **R3-B MARKDOWN (2658 → <=350):** coherent blocks e.g. render/monitor/strategy/provenance; reuse already extracted `markdown_*_parts` and avoid 1-function micro-owner churn. Preserve all 209 callables, byte-exact Markdown/Unicode/line order and monkeypatch seams.
- **R3-C AI (2761 → <=350):** coherent deterministic/normalization/fallback/dependency grouping. **Safety lock** provider call, router.chat, prompt, retry, hard timeout, count, exception routing, truth precedence, model selection and service state. Preserve all 182 callables; no real provider call.
- No huge replacement helpers, hidden dynamic API hacks, deleting apparently unused symbols, or circular owner→façade imports. If <=350 is impossible without changing behavior/patch semantics, STOP with exact blocker, don't game LOC.

## Per-stage acceptance before continuing
- Exact baseline and new file LOC, changed path list, executable focused mock/offline Reporting tests in isolated clone and project venv; zero production-path write audit; record skips and full commands.
- All 436 callable original public names and signatures retained across all façades; inspect patch targets and runtime resolution, module import order/DAG; test captured synthetic output equality, no semantic/canonical/LLM drift.
- A stage failing ABI/output/monkeypatch safety blocks the next stage. Run full repository pytest diagnosis **once only if safe**, preserve exit code and last test, separate known out-of-scope API/Scanner/UEF/Step5B failures. Real frozen report and LLM provenance remain NOT RUN until actual existing snapshots are supplied.

## Deliverables and handoff
- Claude commits **coherent passing A, B, C batches** (same feature branch), updates both canonical UI patch notes JSON/MD and brief daily patch, writes `docs/refactor/work_orders/evidence/P15-R3-CLAUDE-IMPLEMENTATION-001.md`: pinned code SHA per batch, LOC and ABI before/after, commands, test counts, write audit, deviations/missing gates. Push single task feature branch; ZIP exactly changed files since task baseline, no live files or secrets.
- **STOP and hand to Codex**; no feature merge to `refactor/p1.5`, no main change or P1.5.3.
- Codex independent read-only audit: pinned Claude SHA, source diff, all 436 ABI, seams and import DAG, LOC <=350, output/LLM safety, isolated tests and blocked gates. Report to `docs/refactor/work_orders/evidence/P15-R3-CODEX-INDEPENDENT-001.md` only if safe evidence-write authorized; otherwise deliver report externally. PASS/PASS_WITH_FINDINGS/FAIL/BLOCKED with honest NOT RUN.
- GPT/user alone authorize integration and eventual P1.5.2 acceptance. Small façades and passing focused tests alone do NOT close missing real-data parity or whole-suite blockers.

## GPT architecture decision — compatibility-first resume (2026-10-12)
- R3 resumed on the same `feature/p152-facades-r3`. **Façade <=350 LOC is SIZE_DEFERRED when unmet** (ABI guard sets a per-façade floor: Story 417, Markdown 1024, AI 1100 at original formatting); every new implementation Owner stays <=350.
- Preserve 436 callables, signatures, decorators, import names and patch call-time semantics. Forbidden: `__getattr__`, exec, indiscriminate re-export, formatting compaction.
- Verify the pinned contract (façade ABI test) separately from current implementation location (ledger `r3_owner` + `tests/test_p152_r3_moved_bodies.py`). AI provider/router/prompt/retry/timeout/fallback/merge paths are not moved without proof.
- Real frozen-snapshot and LLM parity stay NOT RUN; whole native pytest stays incomplete. No P1.5.3, no merge into `refactor/p1.5` or `main` before Codex audit.
- Evidence: `evidence/P15-R3-CLAUDE-IMPLEMENTATION-001.md` (supersedes the BLOCKER section there).
