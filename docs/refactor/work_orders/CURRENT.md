# ACTIVE WORK ORDER — P1.5.2 R3 façade decomposition

**State:** READY_FOR_CLAUDE_IMPLEMENTATION. R3 NOT STARTED, P1.5.2 OPEN, P1.5.3 NOT AUTHORIZED.
**Baseline:** `341cedcd95b37b2f30e8dc6b821a25c20fd3fa7b` on `origin/refactor/p1.5` (plus this docs-only task activation commit).
**One task:** [P15_R3_FACADE_DECOMPOSITION_001.md](P15_R3_FACADE_DECOMPOSITION_001.md).
**Shared rules:** [COMMON_RULES.md](COMMON_RULES.md).
**Agentra roles:** CLAUDE implementation → CODEX independent audit → GPT/user integration decision. NOT Agentco roles.
**Workspace:** live `C:\Agentra` must be protected; implementation on isolated feature worktree as task requires. Two dirty Q12 worktrees must remain intact.
**History:** [archived previous CURRENT](archive/CURRENT_R2_THROUGH_341CEDC_2026-10-12.md) (NOT an ordinary task prerequisite).

## Verified baseline and unresolved gates
- Story `trade_story_pipeline.py` **636** physical LOC; Markdown `trade_report_markdown_clean.py` **2658**; AI `trade_report_ai.py` **2761**. Combined original **436** callable public contracts (45 + 209 + 182). Target <=350 LOC per façade only with full import/patch/behavior compatibility.
- Isolated Windows acceptance at `341cedc`: P1.5.2 selected **295 PASS / 1 SKIP**, production-path write audit **0**, correct venv Python/FastAPI. Evidence [clone acceptance](evidence/P15-R2-CODEX-CLONE-ACCEPTANCE-2026-10-12.md); not whole suite.
- Whole native pytest **INCOMPLETE/NOT PASS** (API GET-only failure; another run terminated ~50% without summary). Historical Linux full safe sweep **4919 PASS / 41 FAIL / 2 ERROR**. Do not conflate out-of-scope known failures with Reporting regression.
- Historical real Markdown/JSON/JSONL and captured LLM before/after evidence **missing**, so real-data and LLM output parity **NOT RUN/BLOCKED**. Do not invent snapshots.
- **Next action:** Claude implements R3-A→R3-B→R3-C in isolated task branch, publishes exact code SHA and test reports; Codex audits that exact SHA before any integration. STOP if safety/compatibility cannot be proved.

## R3 status update (2026-10-12, compatibility-first resume)
- Claude implemented R3-A/B/C on `feature/p152-facades-r3` with SIZE_DEFERRED façade LOC; **awaiting Codex independent audit of the pinned SHA in `evidence/P15-R3-CLAUDE-IMPLEMENTATION-001.md`**. Not merged; P1.5.2 OPEN; P1.5.3 NOT AUTHORIZED. Real snapshot/LLM parity NOT RUN; whole native pytest incomplete.
