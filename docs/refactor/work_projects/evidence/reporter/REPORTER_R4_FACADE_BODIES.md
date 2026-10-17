# Reporter R-4 — facade-body batch (Issue #11, Option 1)

BASE d773709. Pattern: P1.5.2 R3 facade injection (`facade.NAME` use-site qualification, wrapper passes `facade=_r3_sys.modules[__name__]`, owner never imports a facade). Tool: `scripts/refactor/work_reporter_r4_extract.py`; ledger `r4_facade_ledger.json` (14 moves); current-head facade ledger `facade_symbol_ledger_v2.json` (`scripts/refactor/work_reporter_facade_ledger_v2.py`).

| Facade | Moved bodies | LOC before -> after | Owner |
|---|---|---|---|
| trade_report_markdown_clean.py | 10 (`_first_report_path, _listify, _has_payload, _merge_preferred, _num_opt, _fmt_signed_pct, _summary_money, _resolve_strategy_refresh_trace, _looks_corrupted, _dedupe`) | 1325 -> 1284 | libs/agents/reporter/narrative/markdown_clean_bodies_01.py (100) |
| trade_report_ai.py | 4 (`_sanitize_report_language_fields, _first_dict_from, _trade_report_parse_meta, _trade_report_language_meta`) | 1656 -> 1597 | libs/agents/reporter/narrative/report_ai_bodies_01.py |
Excluded on purpose: `_resolve_intraday_report_model` (LLM routing), `build_separated_ai_trade_report` (runs reporter agent), `render_trade_summary_markdown_with_evaluation` (imports another facade); all functions with effect/authority tokens; `trade_story_pipeline` has no non-delegating body left (44/45 thin).

## Approved closed path set (scope test)
`libs/reporting/trade_report_markdown_clean.py`, `libs/reporting/trade_report_ai.py`, `libs/agents/reporter/narrative/markdown_clean_bodies_01.py`, `libs/agents/reporter/narrative/report_ai_bodies_01.py`, `tests/test_p152_facade_symbol_ledger.py`. (Issue text wrote `libs/reporting/narrative/...`; the actual owner paths are under `libs/agents/reporter/narrative/` per V3.) R-4 script/ledgers/proof test fall under the pre-existing Reporter-owned prefixes. The set is hard-coded, independent of the ledger; `test_r4_ledger_cannot_grant_paths_outside_the_closed_r4_set` pins ledger schema/base/14 moves/exact facade-owner pairs; `test_scope_checker_still_rejects_unexpected_and_forbidden_paths` feeds 11 forbidden/unexpected paths (all rejected).
Reproduction (isolated clone): committing `libs/reporting/stray_r4_probe.py` -> NEW scope test FAIL with exactly that path; OLD (d17d33c) scope test also FAIL.

## Proofs
- `tests/test_work_reporter_r4_facade_bodies.py` (R3 test logic, BASE d773709): unqualify == BASE body, qualified names == former facade globals, no unresolved globals/bare facade, arg names, wrapper contract + injection, before-call and within-call patch event sequences == BASE function on live globals (3 shapes), owners <=350 and facade-import-free, lazy lookup actually exercised. Vacuous dependency-map skip removed.
- `tests/test_p152_facade_symbol_ledger.py`: v1 historical assertions unchanged but evaluated on the BASE blobs; new v2 current-head test (same strictness + no name/kind/disposition change + exact r4_owner records).

## Shared-gate effect
`tests/test_p159_current_owner_contract_gates.py::test_t3_changed_paths_contain_no_authority_surface` diffs ede47324..HEAD and forbids any change to the two facades and any `bodies_0N.py` -> FAIL on this branch (not authorised to edit). Proposed patch `shared_contract_patch_R4_T3.diff`: pin that historical window to BASE d773709 (unchanged rules) + new current-head test allowing only the closed R-4 set after BASE. Verified in an isolated clone: 15/15 PASS with R-4; an unapproved edit to `trade_story_pipeline.py` -> FAIL.

## R-5 — T1-pinned read models / deterministic helpers (56 more bodies, same proof)
| Module | Bodies | LOC before -> after | Owner(s) |
|---|---|---|---|
| trade_report_ai_deterministic.py | 9 | 749 -> see wc in final report | read_models/report_deterministic_bodies_01.py |
| trade_report_ai_compact_input.py | 2 | 418 -> | read_models/compact_input_bodies_01.py |
| trade_read_model.py | 21 | 1356 -> | read_models/read_model_bodies_01.py, _02.py |
| trade_memory_surface.py | 15 | 393 -> | read_models/memory_surface_bodies_01.py |
| trade_memory_application_surface.py | 9 | 392 -> | read_models/memory_application_bodies_01.py |
T1 gates evaluate historical T1_END snapshots, so they are unaffected (PASS). Extractor now also skips module-identity dependent bodies (`__name__` / `_r3_sys` would bind to the owner): a first attempt without that rule broke 70+ consumer tests (memory parts received the owner module as facade) and was reverted before commit.
Focused run after fix: R-4/R-5 proof 360+ PASS; 1722 PASS / 11 FAIL = scope-negative example + v2 ledger (both test maintenance, fixed: 74 PASS) + T3 window (shared, patch v2 verified 15/15 in isolated clone) + 8 `test_uef2a_forward_policy_contract` failures that are identical on d17d33c/aaeb8a0 (pre-existing, unrelated).
Closed scope set extended explicitly by R5_FACADE_FILES/R5_OWNER_FILES; ledger test pins 70 moves and the exact 8 facade-owner pairs; negative example now `single_trade_report.py`.

## R-6 — pure bodies of I/O-mixed Reporter modules (66 bodies; effect/identity-dependent bodies stay)
| Module | Bodies | LOC before -> after | Owner |
|---|---|---|---|
| trade_explain.py | 8 | 904 -> 556 | narrative/trade_explain_bodies_01.py |
| trade_bundle_assembly.py | 13 | 1890 -> 1451 | read_models/bundle_assembly_bodies_01.py |
| trade_bundle_state.py | 13 | 826 -> 590 | read_models/bundle_state_bodies_01.py |
| trade_lifecycle_builder.py | 12 | 973 -> 801 | read_models/lifecycle_builder_bodies_01.py |
| single_trade_report.py | 8 | 920 -> 857 | narrative/single_trade_report_bodies_01.py |
| trade_story_pipeline_provenance.py | 12 | 227 -> 83 | narrative/story_provenance_bodies_01.py |
R-5 final LOC: deterministic 749->440, compact_input 418->95, read_model 1356->741, memory_surface 393->249, memory_application 392->108.
Proof: R-4..R-6 proof suite 696 PASS (136 moves). Focused consumers + facade/T1/T2 gates: 1845 PASS / 0 FAIL. T3 patch v3 (adds R-6 owners) verified 15/15 in isolated clone.
