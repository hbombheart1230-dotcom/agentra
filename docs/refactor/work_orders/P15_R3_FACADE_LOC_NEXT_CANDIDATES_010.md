# P15-R3-FACADE-LOC-NEXT-CANDIDATES-010 — ACTIVE: maximum safe reduction

**Scope:** Claude implements **ONE bounded, coherent** façade reduction slice then STOPS for Codex independent audit. No further prompt needed to choose among the candidates. Start at `119c68f58cfcd44b64c48ce8383edbc1311b2d5e` on `refactor/p1.5` only. Work in separate isolated clone; DO NOT modify live `C:\Agentra` or Q12 worktrees. No new branches, main merge, trading runtime or real LLM/broker.
**Minimal context:** `CLAUDE.md → CURRENT.md → this document`. Existing [LOC 008 Claude evidence](evidence/P15-R3-CLAUDE-LOC-008.md) and [Codex 009 result](evidence/P15-R3-CODEX-LOC-008-AUDIT-009.md); do not reread unrelated history.

## Starting measured façade sizes
| Public façade | Current physical LOC | Original P1.5 design LOC | Preserved top-level declarations |
|---|---:|---:|---:|
| `libs/reporting/trade_report_ai.py` | **1958** | 8354 | 182 |
| `libs/reporting/trade_report_markdown_clean.py` | **1678** | 5862 | 209 |
| `libs/reporting/trade_story_pipeline.py` | **562** | 4527 | 45 |
| **Total** | **4198** | 18743 | **436** |

All 436 current callable names/signatures/defaults/decorators and their dynamic use-time monkeypatch seams remain intact. Existing 66 moved-body ledger gate (57+9) must not be weakened.

## Ranked candidate set (Claude's LOC 008 dry-run ESTIMATES, remeasure first)
1. Markdown narrative/translation builders — **~93 net façade LOC**, estimated Owner ~159 LOC.
2. Story or AI call-time dependency-map factories — **~75 net LOC each**, evaluate individually and select by true net savings and semantic risk.
3. Markdown memory/policy phase — **~65 net LOC**, high truth/precedence risk.
4. Markdown numeric/format primitives — **~55 net LOC**, hot code, many consumers.
5. Time/duration helpers — **~38 net LOC**.
Only ONE cohesive group can be implemented in this tranche; no number is a promise. Prefer the largest safe positive-net slice on inspection, not merely the largest nominal candidate.

## Work and acceptance
1. Inventory proposed group members, true implementation LOC vs wrapper LOC, existing canonical Owner, static/dynamic consumers, global lookup timing and import-cycle exposure. For rejected better-looking candidates, record concrete reason.
2. Move only genuine pure/formatting/dependency composition responsibility to one cohesive named Owner ≤350 physical LOC (reuse existing correct Owner if practical). Preserve façade 436 ABI/import/module identity. Lazy `facade.NAME` binding at every actual lookup site, including callbacks and patched globals; no entry-time captures. Avoid `__getattr__`, dynamic magic/proxies, artificial line packing, duplicate active business logic or `bodies_06`.
3. Safety-lock LLM prompt/router/retry/timeout/fallback/call-count, report truth-source priority, orders and UEF/Step5 authorities. No real LLM or broker calls. Require mock LLM and output/Unicode/ordering regression if touching nearby helpers.
4. Re-run isolated focused Reporting tests (including 436 ABI, all moved-body ledger gates, selected consumer seams, Guard006 relevant tool tests) plus independent-style pre/post synthetic comparisons; report exact PASS/FAIL/SKIP, new vs baseline failures, import DAG, 0 production writes. Historical real Markdown/JSON/JSONL and LLM trace parity stays BLOCKED/NOT RUN if immutable snapshots absent. Do NOT run full pytest or any test from live root.
5. Publish **real BEFORE/AFTER LOC for every changed façade/Owner** and net façade savings. No forced 350-line façade compliance by deleting unproven contracts; `SIZE_DEFERRED` remains OPEN until genuinely reduced or supported by consumer proof.
6. Commit/push only `refactor/p1.5` after comparing remote HEAD. Update both UI-linked `patch_notes.json` / `patch_notes.md`, daily patch, compact evidence and changed-files-only ZIP; tests temporary paths session-isolated, success cleaned and failure evidence bounded. Stop at CODEX_AUDIT_PENDING with pinned SHA.

## Unchanged separate debts
Frozen actual report/LLM parity BLOCKED, `controlled_mock_lanes` test-isolation OPEN, numbered Owner cohesion OPEN, compatibility retirement P1.5.10 only. P1.5.2 OPEN; P1.5.3, main merge and deployment forbidden.
