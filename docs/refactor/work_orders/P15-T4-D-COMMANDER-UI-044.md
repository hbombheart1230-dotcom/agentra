> **HISTORICAL WORK ORDER — NOT CURRENT AUTHORIZATION.** ACTIVE/READY/pending statuses, role assignments, branch/worktree cleanup commands, and next steps below describe the original pinned historical task only. Do **not** restart implementation or audit, create/delete branches/worktrees, or run operational checks from this page. Current authority: [D00](../../ENGINEERING_DELIVERY_POLICY.md) + [CURRENT](CURRENT.md) + [GitHub Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20). Original safety restrictions and recorded SHA/PASS/FAIL/SKIP evidence remain intact.

# Agentra P1.5 Third Pass — T4-D Commander & Operator UI structural closure

**Status:** READY / AUTHORIZED LOW-RISK STRUCTURAL DEVELOPMENT ONLY. **Approval:** T4-C Codex ACCEPT; FINAL CI `38679851004` SUCCESS on `ac4642dc265811bf7ff56e32adbadf8203fed771`.
**Branch:** `refactor/p1.5` only; fetch latest remote HEAD first, isolate a clean clone (never live `C:\Agentra` or dirty Q12 worktrees). Current-HEAD required Linux/Windows CI must be SUCCESS before implementation. Pin actual head as BASE; don't use a historical SHA if branch advanced.

**Workflow:** GPT/user scope → Claude implements → Codex independent audit → GPT/user acceptance. Stop before unrelated tasks.

## Read minimal context

1. `docs/refactor/work_orders/CURRENT.md`
2. THIS single work order
3. `docs/refactor/work_orders/COMMON_RULES.md`
4. Only T4-D section of `docs/refactor/P15_THIRD_PASS_GPT_REPORTER_INCLUSIVE_DESIGN_2026_10_13.md` and exact impacted source/tests.

Do not reread archived T0–T4-C history or reproduce earlier full reports unless needed for a failure.

## Source-verified T4-D targets

**Commander** `graphs/commander_runtime.py::_resolve_commander_behavior_policy` (begins around line 554, ~530 LOC). Pure policy precedence, normalization and output projection; preserve exact legacy-vs-applied policy, explicit overrides, risk/position sizing, memory flags, route/phase/fast-path settings and LLM profile defaults. Check already-existing `libs/runtime/commander/` Owners and reuse canonical implementations; no second precedence source. Leave `_env_bool`, `_commander_default_bool`, clock, State writes, route transitions, Broker/Supervisor approvals, fast path execution order **in place**. Do not move effects into pure Owners.

**Operator UI** `apps/operator_ui/data_access_core.py::_render_operator_brief_markdown` (begins ~2786, ~351 LOC): extract cohesive pure text formatting/read-view projections only; maintain **exact byte-level Markdown/Unicode/newline/escape/order** output, fallback semantics and canonical factual inputs. Existing `apps/operator_ui/data_access_brief_render_sections.py`, `data_access_brief_render_fallback.py` already own parts; prefer reuse. `_load_operator_brief` (begins ~2204; LLM-bound ~444 LOC) and caching, persistence and artifact paths are **SAFETY_LOCK**; only inspect its pure auxiliary calculations if safely frozen, do NOT split provider/prompt/retry/timeout/cache/write/LLM call order. No real LLM.

Also source-review any still-oversized *pure* Commander/UI functions in these packages, but keep scope coherent and exclude unsafe ownership changes; record `REVIEW/SAFETY_LOCK` rather than force extraction. No filesystem relocation or wrapper deletion until post-T4 architecture approval.

## Pre-implementation BASE freeze (MANDATORY)

Record BASE_SHA and source/Owner LOC; capture immutable real pre-change **mock/offline** input/results *before implementation*, with separate fixtures/effect recorders covering:

- Commander: applied policy vs legacy defaults, override priority, route/phase, live-position vs flat, memory on/off, risk-off, positional limit, sizing, phase precedence, env/default toggles. No production env/credentials.
- Operator renderer: valid brief, empty/partial/fallback, BUY/SELL/HOLD/WAIT, mismatched selected symbol, missing/duplicate headlines, Korean/English input, Unicode/newlines, escaping and source-truth precedence. Compare **exact Markdown bytes**, not normalized text.
- Stable call/State keys, key insertion order, exceptions, monkeypatch seams, returned-object identity, event/trace and *nonoccurrence* of IO/LLM/Broker effects.
- Pin original real BASE implementation, record full variant inventory and fail-closed sample counts; missing/extra/invalid oracle evidence must FAIL. Portable comparison must use isolated pinned BASE **same host**; Windows native compares frozen exact golden. Platform-bound records must be flagged with evidence, not broad-waived.
- Freeze must not access live market/news, real Broker/LLM or production reports. Redirect all temporary files into isolated roots with bounded cleanup.

**Important:** Historical REAL_REPORT_PARITY_BLOCKED and real Operator Brief artifact byte parity cannot be declared PASS using synthetic renderers. If authentic frozen artifacts are unavailable, record `REAL_BRIEF_PARITY_NOT_RUN/BLOCKED` while still enforcing offline exact renderer parity.

## Implementation constraints

- Extract substantial cohesive **pure** statement runs/builder responsibilities, not 10-line convenience wrappers. Prefer existing `libs/runtime/commander` and `apps/operator_ui` Owners. New Owners ordinarily <=350 physical LOC, with semantic names.
- AST ledger must reconstruct unchanged BASE for each chosen target. Nonmoved defs and public ABI signatures stay identical. Original consumers, monkeypatchable `facade.NAME` use-time semantics, import DAG and dynamic aliases are protected.
- Preserve Commander policy precedence, risk-off, phase/route/fast-path order, State/event effects, Supervisor/Executor/Step5C authority. UI exact Unicode/Markdown and LLM prompt/retry/output semantics unchanged; no extra LLM calls or UI fabrication.
- Before code change verify current canonical owners; do not duplicate Commander policy truth or render output authority. Keep explicit pure vs effectful boundary.
- NO Broker, real LLM, production data/writes, Docker/scheduler restart, main merge, P1.5.10, Wave D, P1.6 or full-target folder reorganization.

## Verification & exit

1. Test AST exact reconstruction, def/signature/monkeypatch parity, dependency DAG, and Owner capabilities; negative mutation gates if possible.
2. Full frozen BASE-vs-FEATURE replay: all captured records and variations (not just sampled), State/effect ordering, byte-identical Korean/UI Markdown. Explicit counts.
3. Focused Commander policy/phase/route/read-model regressions; Operator UI render/brief tests and cross-Agent offline contracts, with no real LLM.
4. Strict CI Linux same-host pinned BASE oracle and Windows native replay; JUnit gate ensures each named contract test actually PASSES with no skipped/deselected/missing cases.
5. Preserve previously accepted T3.5/T4-A/B/C frozen fixtures/gates and justify any stage-end pin. No broad test weakening, no source changes in execution/broker/supervisor/LLM areas.
6. Evidence includes exact BASE/FREEZE/CODE/FINAL SHAs, LOC before/after, owners/segments, coverage corpus and sample counts, local/hosted CI, trace/Markdown parity, explicit NOT RUN safety gaps; no premature ACCEPT.
7. Update `docs/refactor/work_orders/CURRENT.md`, new T4-D evidence, daily patch and **both UI patch_notes.json and patch_notes.md**; commit/push only on `refactor/p1.5`, after fast-forward check. Successful temp files cleaned; failed artifacts bounded.

**STOP after T4-D.** Codex must independently audit, including whether this finishes structural T4. **Reporter residual structural closure and post-T4 architecture visualization** still require user/GPT sequencing. The [visual architecture approval gate](../P15_POST_T4_ARCHITECTURE_VISUALIZATION_GATE_2026_10_15.md) is not bypassed. The independent [T4-C v1→v3 Reporter-feedback coverage gap](evidence/P15-T4-C-GOLDEN-SCENARIO-GAP-044.md) must be closed before final P1.5 acceptance but is *not* a T4-D entry blocker. No T5 or Wave D authorization.
