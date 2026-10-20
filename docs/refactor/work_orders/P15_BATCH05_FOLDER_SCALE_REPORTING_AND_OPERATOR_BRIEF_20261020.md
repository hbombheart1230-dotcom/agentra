# Agentra P1.5 — BATCH05 FOLDER-SCALE delivery: Reporter operational observability × Operator Brief

**Authorization:** Product Owner 2026-10-20, expressly requests 2–3× larger source packets, **3–4 real deliverable groups per primary developer**, folder-level ownership, CLAUDE-style identical final reports from both developers, and actionable local CI/reviewer execution diagnostics. **This approves only the two disjoint source packets below plus bounded local diagnostics.** It does not authorize a previous refused GitHub CI workflow edit, loosening tests/pins, new source/trading authority, or `main`.

**Branch check / immutable starting baselines (fetch and recheck before using):**
- `CLAUDE_DEV_A: work/p15-a-reporter-analysis-projection-20261020@4dbbfa34c2f89a407bcc3b79b11d88b945ba7f42` (BATCH04-A two Strategist summary Owners; developer normal/-O 344/344, six hostile mutations; child Codex exit0 PASS, reviewer pytest NOT_RUN; 545/524 LOC `SIZE_DEFERRED`, `SOURCE_ADMISSION_PENDING_GPT`).
- `CODEX_DEV_B: work/p15-b-operator-live-overview-20261020@57e588d6b1281e69fa6d00ef4cc23246fca12501` (BATCH04-B Decision Context + Skill projections; developer normal/-O 113/113; fresh child Claude exit0 source PASS, independent normal/-O 79/79; 1 denied supplementary JSON-check command; **full review completion BLOCKED**, paired notes not independently inspected by child).
- `integration/p1.5@2def329e2e146af9c141a91d91c6b02b6a972ee7` is the *prior docs-only* instruction commit and will advance to this docs commit. No BATCH03/04 new source yet selected into integration. Git `main@2f95bba429636ee15ae9a399cc4ff7c4e6dcd5cb` must remain unchanged.
- Prior hosted selected B `2f159b6447f5c3f07a82a254eee4f2eeee3dcf02` reporting regression T3 step 42 PASS/1 FAIL, `fatal: bad object 54bebe5ece0ac34c4f45df55c44889c9ce323e95` on Linux despite workflow's historical hydration step succeeding; six workflow results 5 success / 1 failure. Previous direct workflow modification request **denied by tool safety**, `CI_REPAIR_BLOCKED_PENDING_PERMITTED_APPROVAL`. Not a semantic source PASS, not permission to edit workflow via another path.

## 1. Scale contract — 4 substantial deliverable groups per developer

**Target is 4 meaningful connected source improvements per primary lane as ONE development batch**, substantially bigger than BATCH04, not 4 tiny prompts, arbitrary LOC goals, or artificial 60-minute minimum. Initial original surface estimates: A `1521+1362+1196+546 ≈ 4625` physical lines over 4 Reporter operational/reporting modules; B 8 existing Operator Brief modules grouped into 4 functional pairs, with relevant tests. Work by folder/unit, but **writable allowlist is exact**: no carte-blanche folder permission. Preserve existing P1.5.3 old frozen moved-body/Owner/shim evidence. Size-only debt marked `SIZE_DEFERRED` when genuinely necessary, not grounds to spin endless wrappers or delay next *approved* deliverable.

### DEV-A — four Reporter operational observability groups (primary Claude)

**Owned functional area:** `libs/reporting/` reporting/observation, non-execution surfaces only. Inspect current BASE sources and existing extracted Owners before editing.

**A1 — Operator daily visibility composition**: `libs/reporting/operator_visibility.py` (~1,521 lines), corresponding existing `libs/reporting/operator_visibility_parts/reason_text_and_time.py` and `summary_snapshot_and_bundle.py` **READ-ONLY**, not authorized to rewrite the old Owners. Extract a **substantive currently retained PURE** daily-summary/readout/context projection (not file I/O/LLM scheduling, event traversal, save or production write). Preserve `build_operator_daily_summary_payload`, `generate_operator_daily_summary`, `generate_decision_story_report`, `generate_run_card_report` public ABI/effects; use-time facade patching, stream ordering, timestamps, exact Markdown and no memory blowup.

**A2 — Phase runtime-health pure aggregate/render**: `libs/reporting/phase_runtime_health.py` (~1,362 lines). Separate meaningful pure `_build_policy_aware_gating_deadness`, `_build_policy_source_summary`, suspect flags / compact views and deterministic text/Markdown projection, while keeping JSON/JSONL reads, `_iter_run_dirs`, event selection, runtime `main`, clocks and external `normalize_monitor_entry_policy_schema` at actual original call-time. Do not alter policy or guard decisions; reporting is observational only.

**A3 — Operator period summary/reconciliation presentation**: `libs/reporting/operator_period_summary.py` (~1,196 lines). It already has **10** `operator_period_summary_parts/*` Owners, which are **READ-ONLY existing pinned implementations**. Carve only currently retained pure grouping/compact summary output with verified exact late dependency resolution; keep memory synchronization, account snapshots/broker day receipts, market/news, filesystem and JSON/MD writes in the facade. Existing R3 `test_p153_operator_ui_moved_bodies.py` validates unchanged public declaration inventory/pinned moved-body proofs: **do not modify pinned declarations/body and do not weaken or edit that test/ledger**. If a new forwarder changes this frozen gate, record that group `STAGE_CONTRACT_BLOCKED`, leave baseline unchanged; continue other approved A groups.

**A4 — Metrics report aggregation/Markdown**: `libs/reporting/metrics_report_generator.py` (~546 lines) and existing `libs/reporting/metrics_report/*` modules **READ-ONLY**. Isolate one coherent pure metrics/format/reason-code projection from long generator; preserve event reader order, UTC day, `resolve_runtime_write_path` and output file paths; never run production writes. Convert only non-effectful body; if the existing owners already cover all meaningful pure logic, record exact proof rather than create useless wrappers.

**Allowed changes DEV-A (no other files):**
- `libs/reporting/operator_visibility.py`, `libs/reporting/phase_runtime_health.py`, `libs/reporting/operator_period_summary.py`, `libs/reporting/metrics_report_generator.py`;
- at most FOUR new owner modules under `libs/reporting/`: `operator_visibility_projection_p15.py`, `phase_runtime_health_projection_p15.py`, `operator_period_projection_p15.py`, `metrics_generator_projection_p15.py` — create only if genuinely substantial pure code moves, no per-function microfiles;
- `tests/test_operator_visibility_reports.py`, `tests/test_operator_summary_reports.py`, `tests/test_operator_summary_mining.py`, `tests/test_check_phase_5_2_5_3_runtime_health.py`, `tests/test_generate_metrics_report.py`, `tests/test_p153_operator_ui_moved_bodies.py` **READ-ONLY gate**;
- new `tests/test_p15_reporting_operational_projections.py` and `tests/test_p15_reporting_operational_parity.py`;
- paired branch-local JSON+MD UI patchnotes (paths below).

**Acceptance:** baseline first normal/`-O` under immutable A `4dbbfa34`; legacy old R3 structural gate must be green on an actual valid composed baseline (otherwise `BLOCKED_BASELINE`, not fake mutant PASS). Exact synthetic events/day/status/newline/Korean/JSON/Markdown/mtime/read and write order, patch-at-call-time, error branches, production write denial; meaningful adversarial mutants (gating threshold, status, quote/number, line order, report ID, schedule, effect injection) must be caught after valid green. Avoid editing older Reporter A `e92950d`, quant/feedback/Strategist BATCH04, shared contract/UEF/Step5C source.

### DEV-B — four Operator Brief UI data-projection groups (primary Codex)

**Owned functional area:** `apps/operator_ui/data_access_brief_*.py` **exact names only**, read-only input/summary/report formatting. Do NOT change `data_access_core.py`, `data_access_overview_projection.py` or `data_access_trade_index_projection.py`, which have prior B strict immutable source pins. Historical first-pass R3 Owner AST/ordering is also protected.

**B1 — canonical-trade and briefing input composition:** existing `data_access_brief_canonical_input.py` + `data_access_brief_input_projection.py` + `data_access_brief_input_sections.py`; remove retained duplication only where true deterministic projection. Preserve actual canonical input and event-source provenance, null/empty semantics, run_id/symbol/ordering. Keep I/O in original approved boundary; no account/broker reads added.

**B2 — monitor/news/market human presentation:** existing `data_access_brief_monitor_sections.py` + `data_access_brief_market_sections.py`; preserve all guard status labels, unknown/NOOP, source+confidence, no invented order approval or false execution status, as well as exact Korean text and timeline order.

**B3 — seven-section operator brief assembly and deterministic rendering:** existing `data_access_brief_sections_projection.py` + `data_access_brief_render_sections.py`; improve cohesive assembly/render ownership and eliminate real duplicate derivation if BASE parity proves safe. Keep exact keys, section ordering, ID linkages, confidence/missing cases and byte-for-byte existing Markdown/JSON presentation.

**B4 — compaction/sanitization and bounds:** existing `data_access_brief_compaction.py` + `data_access_brief_sanitation.py`; preserve prompt/brief budgets, top-N ordering, truncation, escape, malformed scalar cases and Unicode. No LLM prompt content/routing changes beyond BASE-identical bytes; no new live API calls.

**Allowed changes DEV-B (no other files):**
- Exact 9 existing Python paths under `apps/operator_ui/`: `data_access_brief_canonical_input.py`, `data_access_brief_input_projection.py`, `data_access_brief_input_sections.py`, `data_access_brief_monitor_sections.py`, `data_access_brief_market_sections.py`, `data_access_brief_sections_projection.py`, `data_access_brief_render_sections.py`, `data_access_brief_compaction.py`, `data_access_brief_sanitation.py`.
- At most TWO meaningful pure helper Owners if strictly needed: `apps/operator_ui/data_access_brief_evidence_projection_p15.py`, `apps/operator_ui/data_access_brief_presentation_projection_p15.py`. Prefer strengthening existing folder owner seams instead of new thin wrappers.
- Existing `tests/test_operator_ui.py`, `tests/test_operator_ui_data_access_phase2.py`, `tests/test_p153_operator_ui_moved_bodies.py` **READ-ONLY frozen gate**, `tests/test_p165_commander_ui_contract_freeze.py` **READ-ONLY gate**, new `tests/test_p15_operator_brief_folder_parity.py` and `tests/test_p15_operator_brief_folder_mutations.py` writable.
- Paired branch-local JSON+MD UI patchnotes only.

**Critical baseline gate:** `data_access_brief_compaction.py` / `data_access_brief_canonical_input.py` contain existing `_r3_impl` owners and the old R3 proof may pin their bodies. Before editing, run the real frozen positive check; if an existing exact-body/alias check rejects a modification, **stop that sub-boundary as STAGE_CONTRACT_BLOCKED; do not patch old ledger, tests, contract allowlist or owner pins**. Continue other approved B groups safely; report per-group outcome. Do not turn a baseline red into permissive tests. Preserve lookups, UI-only observation status; no strategy/decision/risk/trade/execution modification.

**Acceptance:** frozen B `57e588d6` original outputs/state/Unicode/Markdown/JSON/errors and Python -O. Use synthetic reports and controlled mock contexts. Test empty/unknown, repeated symbols/trades, linked run ids, stale/missing canonical, truncated prompt, guard denial, late monkeypatch, ordering and negative fixture; baseline green then hostile mutants; no real broker or production writes. Existing stage validators remain unmodified, even if they require a later GPT-versioned stage for admission. Achieve material folder-level rationalization, not a 3-line wrapper and stop.

## 2. BATCH05 shared local-CI/reviewer environment troubleshooting — **diagnose, do not bypass**

**Two distinct failures MUST have separate statuses and evidence, without consuming whole development batch on audit plumbing:**

**LOCAL-REVIEW-AUTHORIZATION issue:** Claude child of previous BATCH04 source passed 79 normal + 79 optimized but was denied ONE extra JSON check (denial count1), hence reviewer source PASS ≠ all-source+notes reviewed. Codex child of A static PASS but Python pytest was denied by native read-only sandbox, hence reviewer tests NOT_RUN. For each new candidate:
1. Primary author executes exact approved normal and -O tests in **the primary own allowed writable workspace with isolated pytest scratch**, `python -B -m pytest -q -p no:cacheprovider <exact listed tests>`, then `python -B -O -m pytest -q -p no:cacheprovider <same list>` where available; record actual process exits, pytest summary, test base and actual environment. Do not run live orders or generation.
2. Fresh independent child CLI inspects exact Git diff, **including both patchnote files**, and uses a preapproved *plain executable+argument* allowlist (no `2>&1 | tail`, `echo`, pipeline, inline JSON Python, bash trick, implicit shell wrappers). A reviewer with actual OS-imposed read-only/no-production/credential-free isolation may use specifically approved full CLI permission flags per D00 §3A; otherwise strict native no-prompt read-only. **No permission-denial circumvention**: if pytest/python not permitted, `REVIEWER_TESTS_NOT_RUN` and report distinct reviewer `SOURCE_STATIC_PASS` vs `REVIEW_COMPLETION_BLOCKED`. The author may separately perform the doc consistency check in their normal authorized workspace; do not attribute it to peer.
3. Perform patchnote JSON/MD sanity in ordinary author test via already listed test (`python -m pytest ... tests/test_patch_notes_sync.py` if that existing test is discoverable and approved), not an unapproved `python -c` in child. At any denial report the exact command, classifier reason and exit; **no repeated bypass or forced alternate shell**. For the current developer SHA, note review may be completed by GPT read-only comparing both note files; track which actor reviewed it.
4. Verify ignored temp output is session-isolated, `PYTHONDONTWRITEBYTECODE=1`, pytest no cache provider, documented per-session temp base using authorized normal shell configuration only; clean only authorized scratch after green, retain bounded failed evidence. Do not disable guard, change test outcome, forge reviewer stdout, or write credentials into logs.

**HOSTED-T3-SHA issue is SEPARATE:** `2f159b6` Linux test owner-surface gate reported `fatal: bad object 54bebe5...`; prior workflow-edit request was policy-denied and **stays denied**. Developer may **read-only diagnose** local immutable object presence and reproduce allowed pure T3 predicate on an authentic full baseline (e.g. `git cat-file -t 54bebe5ece0ac34c4f45df55c44889c9ce323e95` returns commit vs error; `git rev-parse HEAD`; inspect run logs and existing hydration steps), and record exact commands, exits and object availability. Do **not** edit or request a surrogate CI YAML/script/test/allowlist/pin, `git replace`, synthetic object SHA, skip/xfail or workflow reroute; do not mask the genuine missing-object failure by relying on a different local ref. For a permitted fix, tech lead needs a **separate lawful approval path for the previously denied workflow mutation**; until then `CI_REPAIR_BLOCKED_PENDING_PERMITTED_APPROVAL`, and no source `INTEGRATED` label. A local green is not hosted CI green and cannot waive exact composed SHA required checks. Developer may work other independent source groups rather than waiting on T3.

**Do not create a new CI framework, nested child loop, or independent workaround scripts as replacement for forbidden workflow edit.** Report object diagnosis in `LOCAL_CI_REPRO` with `RAN/FAIL/NOT_RUN/BLOCKED` status and evidence in handoff; keep actual CI conclusion separate.

## 3. Standardized mandatory developer reply — **Claude BATCH04-A format for BOTH**

**Both Claude and Codex replies must use this structure in Korean, equal detail, final heading exactly `### 티키타카 실행 리스트`; no freeform one-paragraph Codex reply anymore.** A one-line checkpoint is allowed while actively coding, not as the final handoff.

```markdown
## BATCH05-[A|B] 결과: SOURCE_PASS | REWORK | BLOCKED / 통합 대기

- BASE_SHA: <full 40 hex>
- CANDIDATE_SHA: <full 40 hex> (branch, push, remote match, dirty clean/dirty)
- STATUS: IMPLEMENTED | PEER_PASS | PEER_PARTIAL | REWORK | BLOCKED / SOURCE_ADMISSION_PENDING_GPT / INTEGRATION_PENDING
- 변경 경로: 파일별 변경/신규/삭제, 담당 폴더 범위 준수와 UI patchnotes JSON+MD 동시 갱신
### 산출물
- [A1–A4 or B1–B4] 각 그룹: 실제 변경 기능/증거, 전/후 LOC, 스코프/계약/환경 의존성, 원본 효과/ABI 보존, SIZE_DEFERRED 또는 BLOCKED 이유 (필요 시)
### 동등성 및 적대적 검증
- Immutable BASE: 정상 조건·입출력 byte/JSON/Markdown·예외·호출/시간/상태 alias·failed case
- normal N PASS / -O M PASS (동일 final candidate, 실제 명령/exit; 중복 집계 금지)
- mutation baseline 먼저 PASS, M-k 탐지/미탐지와 실제 수정
### 로컬 CI 및 차단
- LOCAL_REVIEW_AUTHORIZATION: ...
- LOCAL_CI_REPRO / HOSTED_T3: ...
- reviewer child tests RAN/N vs NOT_RUN, note diff reviewed by WHO, denials N
- NOT_RUN: Linux/full pytest/hosted composed CI/실데이터/UI build 등 실제 미실행만
- 소스 승인·통합·실거래 승인 명확히 분리
### 티키타카 실행 리스트
| # | 대상 | BASE → CANDIDATE | 실제 CLI 명령/권한/격리 | exit | PASS/REWORK/BLOCKED | 독립 reviewer tests RAN/NOT_RUN | 수정/새 SHA |
| ...모든 실제 호출(거부 포함)을 시간순으로... |
```

**No fictitious CLI invocations, pytest, elapsed wall time, review success or commit SHAs.** Exact explicit reviewer verdict AND real process exit mandatory; a denied supplementary check is exposed, not hidden under headline PASS. Reviewer test NOT_RUN never replaced with author's pytest count. Actual REWORK→source author makes new commit/SHA→fresh review; no actual defect means do not invent extra cross-check. Stop if owner/stage safety fails; do not modify scope to make prior tests pass.

## 4. Integrator lane (GPT) and next work

Tech Lead will inspect both newest exact source SHAs, reconcile UI notes independently, acknowledge earlier A review (Codex source-static PASS, no reviewer pytest) and B partial review (Claude 79/79 source PASS with one supplementary permission denial). Shared contract `8fd49dd` accepts immutable A-P2 `e92950d` only; it does NOT automatically admit A Quant `41ca719a`, Feedback `ead33ca`, Strategist Summary `4dbbfa34`, new B Decision/Skill `57e588d6`, or BATCH05 sources. All new Owners need exact stage/versioned source admission by GPT, with no historic test/oracle weakening.

Selectively integrate source, never indiscriminately merge the two developer branches; read-only reporting and Operator UI patches are independently ordered by contract. If T3 repair forbidden remains unresolved, state `INTEGRATION_BLOCKED_T3` and continue authorized isolated folders; do not claim full `INTEGRATED`/release. Next queue work beyond these 4 groups/lane still requires explicit separate owner approval. `main`, broker orders, credentials, production deploy, UEF, Step5C safety and DTO authority stay locked.
