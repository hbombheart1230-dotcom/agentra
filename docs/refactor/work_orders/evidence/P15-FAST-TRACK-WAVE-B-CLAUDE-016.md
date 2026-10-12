# P15 Fast Track Wave B — Claude implementation evidence (P1.5.4 Strategist / P1.5.5 Scanner / P1.5.6 Monitor)

Branch `refactor/p1.5` only; isolated clone `C:\AgentraEvidence\r3_seam_clone`. Start SHA `877455db439e9e6f72af413216acc9758b91a2a9` (after Wave A closeout; CI green at `2504d70`). Wave SHA = commit carrying this file. Scrubbed env, no credentials, `PYTHONDONTWRITEBYTECODE=1`; live `C:\Agentra`/Q12/broker/real LLM/Docker untouched; no ZIP.

## Phase 1 (Wave A closeout) — done before Wave B
- Stage-pinned scope guard (`tests/test_p152_facade_abi_and_authority_boundary.py`, pin `318015a0`, `apps/operator_ui/` allowed, `apps/api`, `graphs`, `conftest.py`, execution paths forbidden) and the stage-pinned P1.5.2 inventory (`INVENTORY_END_REF`).
- `.github/workflows/p152-r2c-residual-regression.yml`: R3-era CURRENT checks replaced by a Fast Track active-contract guard; **all ZIP packaging/upload steps deleted**; JSON inventory, JUnit, ABI, Owner size, patch-note sync, offline regression kept; gates split per file; one Linux-only deselect of a documented Windows-path assertion (`test_operator_brief_input_paths_fallback_to_trade_root_not_reports_dir`, pre-existing, still run in the Windows diagnostic job).
- CI run for `2504d70`: **Success**; artifacts = JSON inventories + JUnit only. (Two real defects were found by CI on the way and fixed: the harness guard validated the Windows live-root string with the POSIX path module; the inventory/scope guards needed stage pinning.)
- Codex Wave A PASS_WITH_FINDINGS recorded: [P15-FAST-TRACK-WAVE-A-CODEX-AUDIT-015.md](P15-FAST-TRACK-WAVE-A-CODEX-AUDIT-015.md). Wave A = FIRST_PASS_WITH_DEBT.

## Wave B changes
| Module | Before | After | Delta | Moved symbols | New Owners |
|---|---:|---:|---:|---:|---:|
| `graphs/nodes/strategist_node.py` | 8,878 | **5,144** | -3,734 | 104 | 22 (`libs/runtime/strategist/{context,policy,llm,output}/`) |
| `graphs/nodes/scanner_node.py` | 4,178 | **2,652** | -1,526 | 40 | 11 (`libs/runtime/scanner/`) |
| `graphs/nodes/monitor_node.py` | 3,632 | **3,594** | -38 | 2 | 1 (`libs/runtime/monitor/entry_carry_guard.py`, 60 LOC) |
| **Total** | 16,688 | 11,390 | **-5,298** | **146** | **34** (6,792 LOC, max 312) |

Owners (Strategist): context — `memory`, `common_values`, `market_inputs`, `market_key_events`, `commander_refresh_context`, `symbol_read_models`, `news_compaction`, `news_context`, `theme_compaction`, `theme_packet`, `theme_strength`; llm — `stage_reviews`, `override_normalization`, `adjustment_directives`, `candidate_watch_overrides` (post-processing of already received LLM output only); policy — `monitor_entry_policy`, `monitor_entry_policy_seed`, `exit_and_defaults`, `scanner_policy`; output — `strategy_scores_and_summary`, `commander_context_and_plan`, `strategic_answers`.
Owners (Scanner): `scoring_inputs`, `repeat_guard`, `blocker_family_overlay`, `symbol_prior`, `evidence`, `feature_coverage`, `sentiment_inputs`, `guidance`, `macro_focus`, `compatibility`, `macro_chart_fit`.

**Not moved (isolated, by design):** every Strategist LLM call path (`_run_strategist_frame_llm`, message/repair builders, token budget, call-kind/trace labels, parse-failure classification, JSON/prose contract extraction, stage-specific requirement text), file/memory loaders (`_load_*`, refresh memory excerpt), event/log emitters, `strategist_node` itself; Scanner event/log emitters, skill-hydration (`_maybe_hydrate_scanner_skill_results`), symbol-prior file loader, selected-symbol state write (`_remember_selected_symbol`), `scanner_node`; Monitor: `monitor_node` (2,634 LOC), `_evaluate_monitor_entry_candidate` (658 LOC) and the remaining small helpers.

## B3 Monitor
`monitor_node.py` = `monitor_node` (2,634 LOC) + `_evaluate_monitor_entry_candidate` (658 LOC) + helpers. Only two policy helpers (`_entry_forced_block_reason_for_open_carry`, `_memory_bias_observation_only`) were moved. Mechanical verbatim moves cannot satisfy the <=350 Owner rule for the two large functions; decomposing them is real refactoring of entry/exit ordering and is **SECOND_PASS_DEBT (B3_BLOCKED_BY_GIANT_FUNCTION)**. Intent-only role and order/risk logic were not touched.

## Gates
| Gate | Result |
|---|---|
| Moved-body gate (144 symbols x 3 arg shapes): baseline AST equality after unqualification, exact qualified names, no unresolved globals, wrapper injection, use-time oracle vs pinned baseline function, declarations retained, Owners <=350 + scope/authority test | **759 passed** (144 symbols; +2 Monitor helpers verified in the final 1,156-test run: p154 gates + all `monitor_node` consumer files) |
| 60 Strategist/Scanner/Monitor consumer test files (620 tests; mock LLM, rank/selection, state output) | **620 passed** in both baseline and feature trees, per-test outcomes identical |
| Call differential vs the same-commit baseline (`877455d`), baseline and feature run **concurrently** (isolated TEMP): 17,464 recorded calls of 141/144 moved symbols | **0 differing records among the 16,792 baseline-stable records**; 672 records differ run-to-run even baseline-vs-baseline (live public market-data fetch inside existing tests: yfinance `ma*` values, wall-clock IDs/epochs) |
| Authority: scope diff limited to the three node modules, `libs/runtime/{strategist,scanner,monitor}/`, tests/docs/scripts; no execution/broker/supervisor/LLM-routing imports in Owners | pass |
| Production-path writes in isolated runs | 0 |
Not run here (Wave D): full native pytest, Docker, UEF replay.

## Findings / debt
- Existing offline tests call live yfinance market data (non-deterministic, network read); pre-existing, outside Wave B; makes sequential differentials noisy (use concurrent runs).
- The recorder normalises wall-clock epochs/timestamps/hex digests; an earlier sequential comparison produced false positives for that reason (documented, not a code difference).
- Real frozen report/LLM parity BLOCKED; `controlled_mock_lanes` isolation OPEN; large node functions (`strategist_node` 1,705, `_run_strategist_frame_llm` 349, `monitor_node` 2,634, `_evaluate_monitor_entry_candidate` 658, scanner `scanner_node`) and façade/wrapper size are SECOND_PASS_DEBT. Wave B is FIRST_PASS_WITH_DEBT (B1, B2; B3 only two small helpers), not FINAL.
