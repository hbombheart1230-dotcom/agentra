# P15-R3-FACADE-LOC-MAX-REDUCTION-008 — ACTIVE: measure and extract maximum safely cohesive slice

**Authorized:** Claude first analyzes then IMPLEMENTS **one** high-value bounded Reporting façade reduction slice without another prompt; STOP after commit/push/evidence for Codex independent audit.
**Branch:** `refactor/p1.5` only. Detached/isolated separate clone allowed for evidence; DO NOT create feature/task remote branches or disturb live `C:\Agentra`/Q12.
**Start SHA:** `ac12d2d570c0fed436eca0c129b2923f166499f0`. Read `CLAUDE.md → docs/refactor/work_orders/CURRENT.md → this task`; do not revisit archives.
**Scope:** `libs/reporting` (only the three public façades and genuinely existing/cohesive Owners or a necessary bounded domain Owner), directly relevant tests, documentation and UI patch notes. No `apps/`, `graphs/`, `conftest.py`, trading logic, live data, broker or real LLM.

## Why big — measured at Guard 006 SHA
| Façade | Initial LOC | Current LOC | Top-level defs | Before-first-def LOC | Functions ≤5 LOC |
|---|---:|---:|---:|---:|---:|
| `trade_report_ai.py` | 8354 | **1958** | 182 | 217 | 93 |
| `trade_report_markdown_clean.py` | 5862 | **1891** | 209 | 187 | 107 |
| `trade_story_pipeline.py` | 4527 | **562** | 45 | 150 | 25 |
| **TOTAL** | **18743** | **4411** | **436** | **554** | **225** |

The 436 top-level declarations are compatibility/patch surfaces (and many already thin); 182 AI and 209 Markdown declarations alone cannot fit into 350 LOC under current ABI. **Do not stop at SIZE_DEFERRED:** reduce real residual body and dependency wiring as far as semantic proof permits. Do not minify, suppress symbols or add `__getattr__`/wildcard proxy hacks.

## Authorized ordered work
1. **Read-only measurement first (within this task):** inventory every remaining façade function's body/LOC and reason: pure implementation, domain glue, dependency-map, necessary dynamic patch wrapper or LLM safety-locked entrypoint. For meaningful candidates record canonical Owner, static and dynamic consumer hazards, monkeypatch timing and expected LOC savings. Produce a compact inventory in the evidence, not a 436-row chat dump.
2. **Choose ONE biggest high-confidence cohesive candidate group** and IMPLEMENT transfer to the existing correct Owner or new responsibility-named Owner only when necessary, bounded <=350 physical LOC. Prioritize pure Markdown formatting, Story assembly glue or deterministic AI helpers and dependency-map consolidation; evaluate the real size savings rather than merely moving a function to another filename. Avoid fragile LLM timeout/repair/fallback and truth precedence until strong deterministic mock evidence; no new numbered `bodies_06` or responsibility duplication.
3. **Compatibility invariants:** preserve the public façade’s 436 name/signature/default/decorator/module identities, `facade.NAME` **use-time** global resolution (including mid-call mutation), import DAG, return/schema/order/truth provenance/Unicode, mock LLM prompt/routing/retry/timeout/call count, and no new execution/approval authority.
4. **Gates:** before/after line counts for changed façade and Owners, 436 ABI, 57 moved-body seam, deterministic synthetic Markdown/JSON fixtures (mock LLM where applicable), import cycle, all affected Reporting focused pytest, guard 006 offline tools if used; **zero production writes** in separate isolated clone. Record exact commands/counts/SKIP; no full native pytest rerun, no real operational reports, orders or LLM calls. Do not weaken tests to match implementation.
5. **Stop if blocked:** if no safe positive-value reduction survives the real caller/seam review, **do not make runtime changes**; publish measured reasons and next best candidates. Do not substitute source packing, fragile aliases, blanket export deletion, or code relocated into an oversized Owner. Public symbol retirement only with full consumer proof and later P1.5.10 authorization.
6. **Delivery:** one coherent commit/push to `origin/refactor/p1.5` after head check, update BOTH UI-linked patch notes JSON/MD and daily patch, save bounded evidence under `docs/refactor/work_orders/evidence/`, generate ZIP of **only modified/new paths**, and STOP for Codex independent audit at pinned SHA. No main merge/production rollout/P1.5.3.

**Separate unresolved gates:** historic real report/LLM parity BLOCKED, pre-existing `controlled_mock_lanes` write-isolation OPEN, façade size exceptions and numbered Owner cohesion debt until explicitly resolved. **P1.5.2 OPEN.**
