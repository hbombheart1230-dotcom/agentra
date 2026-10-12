# ACTIVE — P1.5.2 R3 use-time façade seam restoration

**Status:** R3_SEAM_REGRESSION_CONFIRMED; REWORK_APPROVED_IN_SCOPE; P1.5.2 OPEN; P1.5.3 NOT AUTHORIZED.
**One active task:** [P15_R3_SEAM_RESTORATION_003.md](P15_R3_SEAM_RESTORATION_003.md).
**Common rules:** [COMMON_RULES.md](COMMON_RULES.md).
**Agentra roles:** Claude implements → Codex audits pinned SHA → GPT/user decides.
**Sole refactor branch:** `refactor/p1.5`. **NO additional feature/task/ZIP branches.**
**HEAD at decision:** `bd8053bcf21d256337a97863700bdf442683ba11`, already contains prior R3 code and concurrent Claude acceptance evidence through `1c6e603`; `main` unchanged.
**Safety:** work from isolated clone tracking `origin/refactor/p1.5` only; do NOT modify live `C:\Agentra` or either dirty Q12 worktree.

## Verified evidence, not completion
- Claude [acceptance evidence 002](docs/refactor/work_orders/evidence/P15-R3-CLAUDE-ACCEPTANCE-EVIDENCE-002.md): 47,091/47,092 synthetic moved-function calls identical (one nondeterministic latency), plus 357 direct test cases; 57/57 pre-call patch seams identical.
- **FAIL:** 36/57 moved functions differ from baseline when façade globals change *during* one call: Owner currently captures globals at function entry. **GPT decision: do not waive; restore original use-time lookup semantics before acceptance.**
- Baseline-matched full pytest: 5,115 PASS / 35 FAIL / 27 SKIP / 2 ERROR / 9 deselected; 37 failure/error nodes outside Reporting, same as baseline. One **test-originated** `data/logs/controlled_mock_lanes` write-isolation finding must remain OPEN; no false 0-write full-suite PASS.
- 11 R3 Owners <=350 LOC, façade LOC 562/1,891/1,958 (**SIZE_DEFERRED**). Story Owner actually 102 LOC. Source-order `bodies_01..05` naming/cohesion is unresolved debt; no cosmetic rename within this seam fix.
- Real frozen Markdown/JSON/JSONL and LLM prompt/retry/timeout/call-count parity: **BLOCKED/NOT RUN**; no fabrication.
- Codex's older independent verdict PASS_WITH_FINDINGS covers pre-evidence R3, **not** the 36 mid-call seam failures nor the next fix.

## Immediate next action
1. First safely retire obsolete `feature/p152-facades-r3` only if fully ancestor of `refactor/p1.5` and local feature worktree clean; **no forced cleanup or lost untracked files**. If unsafe, keep it and report BLOCKED, but never push further to it.
2. Claude performs **one bounded seam restoration** per linked task on `refactor/p1.5`; Codex independently audits changed runtime and regression tests at pinned SHA.
3. No `main` merge, live rollout, operational trade/LLM calls, P1.5.2 final PASS or P1.5.3.

## Seam restoration 003 implemented (2026-10-12, Claude) — awaiting Codex audit
- Moved bodies now qualify every former façade global at its use site as `facade.NAME` (no entry-time prelude). Evidence: [P15-R3-CLAUDE-SEAM-RESTORATION-003.md](docs/refactor/work_orders/evidence/P15-R3-CLAUDE-SEAM-RESTORATION-003.md). Within-call seams 57/57 identical to baseline (was 21/57); pre-call 57/57; 47,091/47,092 synthetic calls identical (1 = latency). Focused 925 passed / 1 skipped, 0 writes.
- Still OPEN: real snapshot/LLM parity (BLOCKED), full-suite zero-write (controlled_mock_lanes finding), façade SIZE_DEFERRED, bodies_01..05 cohesion debt. P1.5.2 OPEN; P1.5.3 NOT AUTHORIZED; no main merge.
