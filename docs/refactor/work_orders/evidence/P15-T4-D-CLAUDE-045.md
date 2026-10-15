# P15 T4-D — Commander behavior policy and Operator brief structural decomposition (Claude)

BASE `97934d2509cee2593a5978a8f46b48860f293907` (CURRENT.md stage-marker repair on `ac4642d` code; required CI 38692860394 SUCCESS) → FREEZE `dcca2be1b6dd0a01c8ed3deceb0fa1621e82eca6` (golden v2; v1 `0a80646` covered two targets) → CODE `0c9936e7cb96f51ab1fc16ce75bc2c35f63db62a`. Scope: `graphs/commander_runtime.py::{_resolve_commander_behavior_policy, _attach_commander_applied_policy, _assess_open_position_commander_override}` and `apps/operator_ui/data_access_core.py::{_render_operator_brief_markdown, _build_operator_brief_sections, _build_operator_brief_input}`. No LLM, Broker, Supervisor, Executor, Step5C, State or execution authority change; `_load_operator_brief` (LLM-bound loader), `_save_operator_brief_artifact`, caching and every env/clock helper are untouched (SAFETY_LOCK). The T4-C Reporter-feedback fallback coverage P2 is kept separate and NOT part of T4-D.

## 0. Entry gate

Latest HEAD `5071480` required CI **failed** at "P1.5.2 final-acceptance inventory contracts" (`stage_frozen` marker `P1.5.2 OPEN`/`P1.5.3` absent from CURRENT.md after the preceding docs edits; no code differed from `ac4642d`). Implementation did not start on a red HEAD: the markers were restored in a docs-only commit `97934d2` and its required Linux + Windows CI was confirmed SUCCESS first.

## 1. Freeze before implementation

Captured from the existing offline suite (no production env/credentials/LLM/Broker), frozen from the unmodified BASE tree (`git archive`): 189 records, 6,456 deterministic variants/scenarios, 856 recorded seam calls. Targets: commander_policy 47, commander_attach 50, commander_override 22, operator_markdown 41, brief_sections 15, brief_input 14. Scenarios: route×phase grid (24), nine environment toggles plus all-toggles, empty applied_policy/override/market_context, loss-near-close with failed session recovery, brief `status` ∈ {blank, ok, partial, salvaged, repaired, fallback, unexpected}, Unicode/Markdown suffix on every string, status-only and empty brief, plus per-key drop/none/empty perturbations. Frozen per record: returned value (Markdown compared as the exact string), mutated inputs, ordered seam calls, exception, returned-object identity. Replay: scrubbed environment (toggles are scenario inputs), frozen clock, network blocked, disposable cwd. Native Windows exact golden; portable mode compares against the same-host pinned BASE (`git archive` of `libs graphs apps`); 99 records are platform bound (Windows separators inside brief/ids) and are compared FEATURE == same-host BASE. Strict variant conservation and fail-closed oracle validation. **REAL_BRIEF_PARITY_NOT_RUN** — synthetic offline renderer parity only, NOT real Operator Brief artifact parity (REAL_REPORT_PARITY_BLOCKED stays OPEN).

## 2. LOC

| Function | BASE | CODE |
|---|---:|---:|
| `_resolve_commander_behavior_policy` | 528 | 135 |
| `_attach_commander_applied_policy` | 297 | 175 |
| `_assess_open_position_commander_override` | 155 | 129 |
| `_render_operator_brief_markdown` | 351 | 22 |
| `_build_operator_brief_sections` | 341 | 249 |
| `_build_operator_brief_input` | 314 | 105 |
| `graphs/commander_runtime.py` (file) | 3,494 | 2,974 |
| `apps/operator_ui/data_access_core.py` (file) | 3,706 | 3,102 |

## 3. OWNER_MATRIX (11 new Owners, all ≤ 243 LOC; 25 ledger segments, `docs/refactor/p1_5_third_pass_t4d_moved_segments_ledger.json`)

| Owner | LOC | Responsibility |
|---|---:|---|
| `libs/runtime/commander/behavior_policy_llm_profiles.py` | 123 | LLM execution profiles and strategist runtime/memory/feedback fields of the behavior policy |
| `libs/runtime/commander/behavior_policy_monitor_scanner.py` | 107 | scanner and monitor policy surfaces |
| `libs/runtime/commander/behavior_policy_applied_summary.py` | 165 | commander_applied_policy_summary surface |
| `libs/runtime/commander/behavior_policy_carry_overrides.py` | 71 | carry-risk exit policy overrides and adjustment trace |
| `libs/runtime/commander/applied_policy_context_projection.py` | 141 | commander_context update and context_ref surfaces |
| `libs/runtime/commander/open_position_override_result.py` | 40 | open-position override result surface |
| `apps/operator_ui/data_access_brief_render_helpers.py` | 193 | pure text/label/metric helper closures of the renderer |
| `apps/operator_ui/data_access_brief_render_narrative_helpers.py` | 33 | narrative/summary/compaction closures |
| `apps/operator_ui/data_access_brief_render_summary_derivation.py` | 148 | early fallback Markdown and derived Korean summaries |
| `apps/operator_ui/data_access_brief_sections_projection.py` | 136 | brief section builders |
| `apps/operator_ui/data_access_brief_input_sections.py` | 243 | brief input blocks (commander, strategist, scanner, monitor, trade_report) |

Existing `libs/runtime/commander` and `apps/operator_ui` owners (including `data_access_brief_render_sections.py` / `_render_fallback.py`) were reused untouched; the new Owners hold the remaining inline runs, so no second policy or render authority exists. Moves are verbatim; locals enter as explicit parameters; module globals resolve at use time as `facade.NAME` (monkeypatch seams intact). Returned dict key insertion order is preserved because each moved sub-dict stays at its original key position.

## 4. Parity

* Full frozen replay (`verify <fixture> 1`): 189 records / 6,456 variants, **0 mismatches** on the CODE tree (native), and portable mode against the pinned BASE passes.
* AST gate (`tests/test_p165_t4d_extraction_gates.py`, 10 tests): inlining every Owner call reproduces the BASE AST of all six functions exactly; all other definitions AST-identical; only ledger Owner names are new imports; Owners ≤ 350 LOC without env/I-O/clock tokens or LLM/effect names; changed paths stay in Commander/Operator UI scope.
* Markdown: the exact string of every frozen renderer call (41 records + variants incl. Unicode, status and empty cases) is part of the frozen digests — byte equality, not normalized text.

## 5. REVIEW / SAFETY_LOCK (deliberately not moved)

* `_load_operator_brief` (442 LOC, LLM/provider/prompt/retry/cache/env), `_save_operator_brief_artifact`, `load_overview`, `load_run_detail`, `_trade_report_index` (filesystem/Path/read-model IO).
* `_resolve_commander_behavior_policy` keeps the env-reading `_env_bool`/`_commander_default_bool` and `os.getenv` sizing lines in place.
* `_run_integrated_chain_impl`, `_run_commander_runtime_impl`, `_run_pre_entry_exit_sweep`, `_build_commander_decision`: route transitions, persistence, Supervisor/Executor sequencing — authority code, not extracted.
* BASE×2/FEATURE×2 independent-session differential NOT RUN (P2 carried).

## 6. Verification

| Item | Result |
|---|---|
| T4-D structural gates (10) | passed |
| T4-D frozen contract tests (5) incl. forced portable + full-corpus replay | passed / 0 mismatches |
| Stage gates T3.5/T4-A/T4-B/T4-C and historical scope gates (93) | passed; T4-C scope gate stage-pinned to `ac4642d` |
| Existing Commander/Operator-UI related tests (135 files) | FEATURE and pristine BASE fail the identical 16 tests (time/environment-dependent `monitor_exit_guard`, `uef*` etc.), nothing newly failing |
| `test_p15*`/`test_p16*` (historical P1.5 gates) | 3,123 passed, 1 skipped (conditional) on the CODE tree |
| Production-write leakage | none (disposable roots, network blocked) |

## 7. Remaining

T4-D IMPLEMENTED / PENDING independent Codex audit. T5, Wave D, P1.5.10, main merge NOT STARTED. REAL_REPORT_PARITY_BLOCKED / REAL_BRIEF_PARITY_NOT_RUN. T4-C Reporter-feedback fallback coverage P2 (separate). NTFS mtime P2. Cross-seed telemetry-order P2.

## 8. CI

Required CI run 38699806358 on CODE `0c9936e`: **regression SUCCESS, Windows harness isolation smoke SUCCESS** (T4-D Linux gate with pinned-BASE portable oracle and Windows native replay accounting included). The earlier red HEAD `5071480` (run 38690582622, stage-marker guard) and its repair `97934d2` (run 38692860394 SUCCESS) are described in section 0. Final documentation commit CI recorded in the report.
