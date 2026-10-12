# P15-R3-SEAM-RESTORATION-003 — compatibility-first seam repair

**Owner:** Claude implementation and tests → Codex independent audit → GPT/user integration decision.
**Single Git branch:** `refactor/p1.5`, no new branch ever. Use isolated **separate clone** from latest `origin/refactor/p1.5`, not the live checkout. Preserve Q12 worktrees; do not reset/force-clean unknown files.
**Source of truth:** [Claude evidence 002](docs/refactor/work_orders/evidence/P15-R3-CLAUDE-ACCEPTANCE-EVIDENCE-002.md) and pinned R3 baseline `ba6618d483e6d617f4ee56b2cb5647392c777071`. Inspect only affected façade/Owner/test files.

## Architectural decision
- **REJECT** treating call-entry global capture as acceptable compatibility drift. In 36/57 moved functions, callback-triggered within-call façade-global monkeypatching behaves differently from original module-level late lookup.
- **RESTORE original use-time façade global resolution**, not merely pre-call monkeypatch reachability. Keep 436 original façade callable names/signatures/decorators, 57 moved-body responsibility, original imports/dynamic consumers and no Owner → façade imports/cycles.
- Do **not** use `__getattr__`, `exec`, dynamic module reflection hacks, fabricated goldens or cosmetic LOC tricks. Explicit `facade` dependency is allowed; safe, typed/explicit access at the original use sites is preferred. Preserve semantics for callable and noncallable globals, nested callbacks, scopes, recursion, default-arg evaluation, and strict order of resolution.
- R3 AST gate must validate correct baseline equivalence **including global-resolution timing**, not force an AST-identical body despite necessary qualification changes. **Never delete/disable tests or silently relax 436 ABI, truth precedence or LLM safety**. Add targeted reproducing tests for each class of the 36 differences and the unchanged 21, including mid-call, pre-call and nested callback seams.
- Each newly affected Owner <=350 physical LOC; façade size remains **SIZE_DEFERRED** unless genuinely reduced without API drift. Provider/router/prompt/retry/timeout/fallback/merge paths remain safety locked. Domain regrouping of `bodies_01..05` is **not authorized in this tranche**; retain as named acceptance debt.

## Execution and acceptance
1. **One-time branch hygiene first.** Verify old feature tip `1c6e603` is an ancestor of current `refactor/p1.5` using Git; inspect the old R3 feature worktree for both tracked and untracked changes. If clean, safely remove only that feature worktree/local branch and delete old remote `feature/p152-facades-r3`; never force. If dirty, stop cleanup and preserve files (do not block isolated evidence activity).
2. Claude implements **only** bounded Reporting seam repairs on `refactor/p1.5`. Commit/push after SHA check, and provide precise changed-file inventory; no parallel work by Codex.
3. Reproduce baseline-vs-fix **57/57 pre-call and 57/57 within-call seam equivalence** on the same deterministic inputs; target 0 semantic differences. Add focused regression tests protecting lazy use-time lookup and AST/provenance at 436-ABI level. Run targeted mock/offline Reporting pytest, static import DAG, consumer/monkeypatch checks and a zero-write focused audit in isolated clone. If a seam cannot be preserved without unsafe broad rewrites, STOP with concrete counterexample, never label PASS.
4. Recheck existing 47,092 synthetic call comparisons (ignore only proven wall-clock nondeterminism), report mock LLM prompt/retry/fallback/call count, truth precedence, format/Unicode unchanged; no real LLM/broker calls, production writes or Docker restarts.
5. Do **not** rerun full native pytest blindly: prior one-shot suite + baseline failure inventory already exists. The unrelated controlled-mock-lane CWD write isolation remains a separate OPEN safety/test-quality item; identify culprit in a later scoped task. Never claim full-suite 0-write PASS.
6. Record exact commands, SHA, PASS/FAIL/NOT RUN and residual gates, update UI-linked patch-notes JSON+MD and daily patch, and package **only changed files** in ZIP. Codex independently audits pinned committed code/evidence after Claude finishes; no automatic merge.
7. If real historical frozen snapshots/LLM traces are absent, keep genuine real-data parity **BLOCKED / NOT RUN**. P1.5.2 OPEN / P1.5.3 NOT AUTHORIZED.

**Stop conditions:** any ABI break, unproven dynamic patch seam, new import cycle, production-path write, changed LLM/trading authority or >350-LOC new Owner. Do not touch main or live `C:\Agentra`.
