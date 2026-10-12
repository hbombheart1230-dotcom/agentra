# ACTIVE — P1.5.2 Reporting façade maximum safe LOC reduction 008

**State:** GUARD_007_CODEX_PASS_WITH_FINDINGS; LOC_008_ACTIVE; P1.5.2 OPEN; P1.5.3 NOT AUTHORIZED.
**ONE task:** [P15_R3_FACADE_LOC_MAX_REDUCTION_008.md](P15_R3_FACADE_LOC_MAX_REDUCTION_008.md).
**Rules:** [COMMON_RULES.md](COMMON_RULES.md).
**Roles:** Claude implements one bounded slice → Codex independently audits pinned SHA → GPT/user decides.
**Only refactor branch:** `refactor/p1.5`. No additional feature/task/ZIP branches; `main` remains frozen.
**Baseline for next work:** `ac12d2d570c0fed436eca0c129b2923f166499f0`; Guard 006 audited code `f6cc71b25d9f3aadd356ee6509b629778861ce32`.
**Operational protection:** do not execute tests or modify files under live `C:\Agentra` or dirty Q12 worktrees. Work in separate isolated clone only.

## Guard 007 — accepted independent audit
- User-supplied Codex audit **PASS_WITH_FINDINGS** on `f6cc71b`: guard tests **61 PASS / 0 SKIP**, guarded seam smoke **357 direct cases / 57 functions**, clone write audit **0**, detached clone clean; `libs/`, `apps/`, `graphs/`, `conftest.py` unchanged; no live/Q12 access.
- Nonblocking finding: pytest `cache_dir` unknown-config warning (1). **No mandatory Guard 007 fix**.
- Evidence: [P15-R3-CODEX-GUARD-AUDIT-007.md](evidence/P15-R3-CODEX-GUARD-AUDIT-007.md). Counts are reported by Codex via user, not rerun by GPT.

## LOC 008 — why further shrinking is justified
- Three current Reporting public façades: AI **1,958** LOC (182 defs), Markdown **1,891** (209 defs), Story **562** (45 defs), sum **4,411**. Original sum **18,743**; remaining is partly 436 preserved callable seams plus dependency maps and actual residual implementation.
- **SIZE_DEFERRED = unmet size target, NOT indefinite waiver.** Claude must measure all remaining nontrivial functions and dependency factories, identify existing canonical Owners and migrate the highest-value **safe cohesive** slice now; no arbitrary code formatting tricks or unproven ABI removal.
- Keep 436 callable signatures/decorators and lazy use-time façade-global lookup. New/moved Owners <=350 physical LOC and domain responsibility clear; no numbered catch-all.
- LLM prompt/retry/timeout/call-count, report truth precedence, order, Unicode, output schema and trading authorities are frozen. No real LLM/broker or production writes.

## Still OPEN
Actual frozen report Markdown/JSON/JSONL and LLM before/after traces **BLOCKED / NOT RUN**; full native pytest previous baseline-matched 35F+2E and `controlled_mock_lanes` test write-isolation **OPEN**; numbered Owner cohesion debt OPEN. **P1.5.2 final PASS, `main` merge, live rollout, P1.5.3 all unapproved.**
