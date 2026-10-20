# Agentra P1.5 — BATCH04, two substantive multi-boundary development packages

**Approved by Product Owner, 2026-10-20:** "응 진행하고 작업을 더 크게 계속 몇분 몇십분이면 끝나자나 지팀장." **AUTHORITY: TWO DEVELOPMENT LANES ONLY.** This explicit approval activates precisely the two developer-specific source+test bundles below, not unlimited future work. D00/D01/D02, CURRENT and Issue #20 remain binding; immutable trading safety always prevails. Starting the task requires the operator to send one short start instruction into **each existing primary coding CLI**; the Git commit and Issue comment do not start local processes.

## 0. Verified refs before dispatch (must fetch and recheck, not hard-coded forever)

- Integration reference at work-order authoring: `integration/p1.5@0801be0cfd7da67fbc844c439bf5ed0a45990335` (docs-only latest; superseded by this work-order docs commit).
- DEV-A exact starting branch: `work/p15-a-reporter-analysis-projection-20261020@ead33ca78e7ee8eb17123fbd25bc129dbc042902`. Existing A-P3 quant `41ca719a` and Feedback `ead33ca` self+local peer PASS are **not integrated**, no re-audit on unchanged source.
- DEV-B exact starting branch: `work/p15-b-operator-live-overview-20261020@8fd49ddf958574f0f505249c3370314ffc06aeac`. BATCH03-B **real direct child Claude PASS** reported at Issue #20 comment 6289817411; exact reviewer normal23/-O23 PASS, exit0 and denials0; Tech Lead source admission accepted in comment 6289917784. No new SHA or redundant re-review.
- `main@2f95bba429636ee15ae9a399cc4ff7c4e6dcd5cb` stays operator-policy protected.
- **Existing selected-B integration CI NOT GREEN:** `2f159b6` six hosted workflows 5 success / 1 Reporting T3 failure `fatal: bad object 54bebe5` in Linux checkout. Prior direct workflow edit request was denied by tool safety policy. No alternative edit surface or indirect developer command may circumvent that denial. `CI_REPAIR_BLOCKED_PENDING_PERMITTED_APPROVAL`. Neither BATCH04 developer owns YAML/CI repair; GPT owns lawful resolution. Do not modify tests, pin hashes or allowlists to green a blocked workflow.

## 1. Parallel ownership, aggregate work scale

Two substantive bounded packages, each composed of **2 related runtime responsibilities plus targeted parity/adversarial suites and peer review**. Plan for connected outcomes rather than micro-commit per function, auditing analyzers or time padding. Make real progress even when one lane/CI is blocked. Commits may be checkpoints but finish the full approved packet before handing off unless actual safety/contract blocker. Never silently enlarge the exact allowlists or open a new branch/worktree.

### CLAUDE_DEV_A — Strategist LLM Summary quality/readout + deterministic Markdown

**Baseline owner:** `libs/reporting/strategist_llm_summary.py` ~1,700 physical lines at `ead33ca`. Actual `build_strategist_llm_summary_payload`, quality audit and both legacy/current `render_strategist_llm_summary_markdown` declarations were inspected. It contains effectful response/canonical file reads and `_utc_now_iso`; multiple render definitions are part of the **actual last-binding semantics**. Do not accidentally make a formerly shadowed definition public or silently normalize inconsistent historical output.

**Exact writable tracked paths (only):**
1. Existing `libs/reporting/strategist_llm_summary.py`.
2. New `libs/reporting/strategist_llm_summary_quality_projection.py` — ONE deterministic audit/readout/strategy-detail owner if a nontrivial proven pure boundary exists.
3. New `libs/reporting/strategist_llm_summary_markdown_projection.py` — ONE deterministic Markdown body/stage-specific formatting owner if safe.
4. Existing `tests/test_strategist_llm_summary.py`.
5. Existing `tests/test_strategist_frame_llm_integration.py`, only where a changed contract is exercised.
6. New `tests/test_p15_strategist_summary_projection.py`.
7. Paired UI notes `docs/trading_agent_patch_notes_detailed_update/patch_notes.json` and `.md`.

**Connected, meaningful deliverables** (complete as one bounded batch):
- **A1:** Audit pure-vs-effectful call boundaries and runtime consumers at the actual A SHA; implement a substantial deterministic quality/news/memory/stage decision and operator-readout projection while preserving lazy facade lookup, monkeypatching, original function names and signatures, exception types, dict insertion order and Korean strings. External `classify_market_regime_rail` / `build_risk_off_exception_policy` behavior remains in original boundaries unless proven effect-free; no strategy decision policy changes.
- **A2:** Extract coherent deterministic Markdown presentation (normal and stage-specific, current effective renderer), preserving exact whitespace/newlines and old render entrypoint, including fallback, missing news/memory, empty themes, negative quality and stage-specific examples. Preserve duplicate-name binding semantics; do not reorganize the original function selection in a behavior-changing way. If one new Owner would exceed the bounded structural target, use meaningful partition **within the listed two new files** and up to 3 true reduction attempts; otherwise mark `SIZE_DEFERRED` rather than changing contract to win LOC.
- **A3:** Exact `BASE_SHA=ead33ca` differential tests on synthetic fixtures (not production files): JSON order/bytes, Markdown Unicode/newline bytes, response/meta/canonical path and timestamp substitution, policy fallback and malformed/missing input, late monkeypatch, normal vs `python -O`. Seed baseline must PASS before meaningful hostile body/line/threshold mutations are counted. Capture output/signal/call/exception order; no live LLM calls or file writes outside isolated test temp.
- **A4:** Self tests, commit/push, then **the existing primary Claude CLI directly launches NEW `codex exec` read-only review** over exact BASE/NEW SHA; real REWORK→repair exact allowed files/new SHA/new child. Report child process exit **AND** PASS/REWORK/BLOCKED; existing CLI `-s read-only` or D00 §3A safe permissions. Review cannot write/commit/push, invoke another CLI, or touch main. Reconcile candidate branch JSON/MD notes locally; GPT preserves integration's newer entries on selection.

**Must NOT change:** `libs/reporting/reporter_feedback*`, quant/Reporter A-P2 source/guard/seed, `graphs/nodes/strategist_node.py`, policy/market/LLM runtime, trading authorities, UEF, Step5C, shared contracts, CI workflows, any production evidence or currently accepted source pins. If a strict full-tree gate rejects a new Owner before exact source-stage pin, report `SOURCE_ADMISSION_PENDING_GPT` instead of weakening the gate. Source self PASS is not integration admission.

### CODEX_DEV_B — Commander decision context + skill hydration read-only projection

**Inspected baseline owners:** `graphs/nodes/build_decision_context.py` 545 lines and `graphs/nodes/hydrate_skill_results_node.py` 323 lines at `8fd49dd`. They share state-oriented context/evidence normalization but still own **effectful** clock/env/yfinance/feature/news/skill-runner calls which must stay in the old nodes and occur in the exact order. Two connected modules supply enough substantive work without touching `decision_node.py`, `execute_from_packet.py` or permission guards.

**Exact writable tracked paths (only):**
1. Existing `graphs/nodes/build_decision_context.py`.
2. New `graphs/nodes/decision_context_projection.py` — one *pure* cache-hit/refresh metadata and signal/state-view projection Owner.
3. Existing `graphs/nodes/hydrate_skill_results_node.py`.
4. New `graphs/nodes/skill_result_projection.py` — one *pure* skill output normalization/summary Owner.
5. Existing `tests/test_m10_6_decision_context_hydration.py`.
6. Existing `tests/test_m22_skill_hydration_node.py`.
7. Existing `tests/test_m22_skill_contracts.py` or `tests/test_m22_graph_hydration_wiring.py` only for touched observable boundary.
8. New `tests/test_p15_decision_context_skill_projection.py`.
9. Paired UI notes JSON and MD at `docs/trading_agent_patch_notes_detailed_update/`.

**Connected meaningful deliverables:**
- **B1:** Pure deterministic cache-hit/reuse/fallback signal and `decision_context_meta` materialization. Keep clock lookup `time.time`, all env reads, `_fetch_yfinance_seed`, `_update_feature_context`, `build_feature_map`, news collection and scoring, global sentiment computation **in original module at original use-time**. No new market fetches. Preserve in-place state identity, dict aliases, per-symbol cache writes, signal status/source/reason, miss/hit/expiry and early no-symbol return.
- **B2:** Pure `_skill_output_to_record`, `_error_reason`, quote-symbol dedupe and canonical skill fetch summary projection where demonstrably effect-free. Keep `runner.run` invocation count/order, market.quote/account.orders/order.status I/O, UTC clock/event logger and error exception timing in existing `hydrate_skill_results_node`. Do not reclassify skill `ready` as approved trading or bypass guard. Preserve `run_id`, errors_total, attempt/ready counts, original record ordering.
- **B3:** Frozen `BASE_SHA=8fd49dd` differential tests normal/`-O`: cache valid/stale/clock edge, absent row, news failure, missing symbol, partial signal, missing trade/order response, stale order_reference, duplicate candidates/selected symbol and late monkeypatch. Assert byte/state/alias/call timing, error reason and effect count, no broker order or unintended production write; **unmodified baseline first**, then changed-cache/status/order/effect mutants are genuinely rejected. Focused M10/T4D/M22/Monitor/execution authority negatives only as needed; avoid rerunning whole repository each candidate.
- **B4:** Self tests, commit/push then primary Codex directly invokes **fresh local read-only `claude -p`**, captures real exit + explicit verdict, REWORK→new SHA→fresh child; do not use main Claude developer chat as reviewer. Follow D00 §3A; strict `dontAsk` with plain allowlisted commands where no external OS read-only isolation exists. Candidate branch notes are **not** to replace the integration's 335+ historic patchnotes.

**Must NOT change:** `scripts/refactor/shared_role_contracts.py`, `shared_strategist_contracts.py`, Reporter A/quant source, runtime Broker/Executor/Supervisor/Monitor guards, live market/network skill implementation, DTOs, CI YAML, golden contracts, UEF/Step5C, `main`. New Owner current-stage admission is a separate GPT integration gate, NOT a reason to edit old historical validators on developer branch. If the pure boundary is too small or tests reveal real effects, keep original owner/effects, prove unchanged and record narrow debt; do not force thin wrappers purely for LOC.

## 2. Tiki-taka, reporting and final handoff (both lanes)

- Existing operator PC, existing primary Claude/Codex sessions and separate already approved isolated writable developer workspaces; verify `git fetch`, branch/HEAD/dirty state and patchnotes consistency before changes. User does **not** paste a reviewer prompt in other developer's long-running session. No unsanctioned new branch or worktree.
- Independent reviewer uses `REVIEW_ONLY_NO_NESTED_CLI`. Approval-free full-access CLI flags only with demonstrably **external OS-enforced read-only isolation and no credentials**, otherwise strict native read-only/no-prompt controls; never circumvent a denial by changing tool surfaces. Run meaningful normal/`-O` target suites and truly discriminating hostile tests; do not equate subprocess exit0 with peer PASS.
- Every final developer response **ENDS with `티키타카 실행 리스트`**, including every real attempt, exact BASE/CANDIDATE SHA, command and relevant flags/isolation, actual child exit, explicit PASS/REWORK/BLOCKED, independently executed tests vs NOT_RUN, real findings/fixes/new SHA. Before this final section give compact implemented paths, self-test counts, source/peer/integration statuses, CI/NOT_RUN and next authorized action. No fabricated work duration, reviews or completed CI.
- If batch completes early, do **not** stop after a single helper while authorized linked deliverables remain. If finished, next work may start only when specifically authorized by CURRENT/Issue; otherwise report `NO_MORE_AUTHORIZED_READY_SCOPE`. Neither developer may self-authorize further source modules simply because this batch finished quickly.

## 3. GPT integration lane — independent of the developer batches

**Already peer-PASS accepted from BATCH03:** `8fd49dd` exact Reporter A current-stage contract accepts A-P2 `e92950d` three blobs (facade/Owner/guard), **not** later A quant/feedback or BATCH04 modules. Patchnotes from B (323), A and integration (335+) require unique, serial reconciliation by GPT; neither developer merges full branches. `integration/p1.5` source CI is still blocked by hosted T3 immutable missing object. Do not mark `INTEGRATED` or proceed to main/live without exact newly composed SHA and required passing CI.

**CI remediation policy:** a previous direct GitHub workflow mutation was denied. The user authorizes continued engineering progress, **not** bypassing that tool/safety denial. If a legitimately allowed future approval route exists, separate explicit object hydration and exact-sha verification can be considered without weakening original test predicate, with independent change review and 5/6→all-required CI. Until then `CI_REPAIR_BLOCKED_PENDING_PERMITTED_APPROVAL`, and GPT focuses on bounded source acceptance and next READY delivery. BATCH04 developer source scope does not include CI files or workaround instructions.

**Release:** production, Docker operations, real broker, protected `main`, full 24 real-data skipped cases, UEF/Step5C and final freeze all remain independently gated and NOT approved.
