> **HISTORICAL WORK ORDER — NOT CURRENT AUTHORIZATION.** ACTIVE/READY/pending statuses, role assignments, branch/worktree cleanup commands, and next steps below describe the original pinned historical task only. Do **not** restart implementation or audit, create/delete branches/worktrees, or run operational checks from this page. Current authority: [D00](../../ENGINEERING_DELIVERY_POLICY.md) + [CURRENT](CURRENT.md) + [GitHub Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20). Original safety restrictions and recorded SHA/PASS/FAIL/SKIP evidence remain intact.

# P15 FAST TRACK WAVE A 013 — Reporting first-pass handoff + Operator UI first-pass

**Status:** ACTIVE, preauthorized first-pass implementation on `refactor/p1.5`.
**Read order:** `CLAUDE.md` → `docs/refactor/work_orders/CURRENT.md` → this order → [Fast Track policy](../P15_FAST_TRACK_FIRST_PASS_2026_10_12.md) → `COMMON_RULES.md`. Only inspect stage-specific packets if a real code boundary requires it; do not reread historical work orders.
**Start repository SHA:** `9b36b638d812b71152b764dbcdd56c427bcc27f7`. Audited LOC 010 code SHA `b0cfc2b5646ff81ec5ce7b738f485a9d22365826`. Isolated clone only; never operate in `C:\Agentra` / Q12 worktrees.

## A1 — Reporting quick first pass (no repeated 50-line rounds)
1. Accept LOC010 as **PASS_WITH_FINDINGS** for the 20 narrative functions (Codex-reported 812 selected PASS/1 SKIP, 460 core PASS, 436 ABI/86 moved ledger, 0 clone writes; differential 99,689/99,690 remained Claude-only).
2. In one contiguous low-risk implementation window, group **compatible deterministic** dependency-map candidates (AI 2, Story 3; estimated −69/−64 façade LOC). Optionally add a truly cohesive Markdown pure-format group if it fits the same bounded integration work and can be proven behavior-preserving. Prefer reuse of existing Owners; any new Owner ≤350 physical LOC. **Never touch real LLM fallback/router/truth-precedence/authority to chase LOC**.
3. One full focused Reporting ABI (436)/moved-body (86+new)/use-time monkeypatch/import DAG/golden/mock-LLM and 0-production-write gate at the end of A1. Do not individually create/close further tasks per helper. Keep oversized Reporting façade + numbered Owner cohesion as **SECOND_PASS_DEBT**, not FINAL PASS. Actual frozen report/LLM parity BLOCKED/NOT RUN.
4. If the candidate set is low benefit or tests fail, STOP that extraction, record reason and still proceed to A2 only if A2 does **not depend on the failed or unknown Reporting behavior**.

## A2 — Operator UI / Brief P1.5.3 first pass (same wave)
1. Load `docs/refactor/p1_5_operator_ui_brief_implementation_packet_v1_0.md` and **actual** source imports/callers; inventory core `apps/operator_ui/data_access_core.py`, `libs/reporting/operator_period_summary.py`, `libs/reporting/operator_visibility.py`, existing Owners and state/API consumers.
2. Extract several **cohesive pure/read-only** read-model, view formatting, briefing presentation/section and state adaptation concerns in a **single integrated patch set**; only create owners when required, each ≤350 physical LOC. No new framework or duplicated canonical truth.
3. Keep UI API/routes, report artifact read priority, Brief prompt/LLM invocation/call count, persistence and runtime behavior EXACTLY. Run affected offline UI/Brief/Reporting tests, import DAG, API contract/golden fixtures, patch seams and 0 operational writes. If real data snapshots absent, report BLOCKED, do not invent them.
4. Mark Operator UI **FIRST_PASS_WITH_DEBT** only when focused safety and contract gates pass; otherwise BLOCKED with exact reason and no false completion.

## Wave A closeout
- One concise stage matrix for P1.5.2 and P1.5.3: files before/after LOC, canonical Owner map, moved API/module identities, exact commands/counts, 0 production writes, tests intentionally NOT RUN and high-risk debts.
- Commit/push same `refactor/p1.5` branch (can use intermediate same-branch commits for safety), compare origin HEAD before push; no new branches, no unsafe reset/clean or live work.
- Update both canonical UI patch-note sources and daily patch. No ZIP/download artifact: Git commit/push is the only deliverable; preserve evidence within bounded retention.
- STOP at wave boundary and hand one pinned SHA plus cumulative diff to Codex for an independent A-wave audit, not per-small-function audits. Codex must report PASS / PASS_WITH_FINDINGS / FAIL / BLOCKED.
- If independent wave A findings are nonblocking, proceed to preauthorized Wave B in sequence after evidence is recorded. Critical, unknown or authority-sensitive findings block transition; P1.5.11 and actual deployment always require explicit final acceptance.
