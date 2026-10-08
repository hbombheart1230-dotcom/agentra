# P1.5 Scanner Implementation Packet v1.0

Status: DESIGN COMPLETE / IMPLEMENTATION GATED
Date: 2026-10-07
Design branch: design/p1.5-p1.6-modernization
Scope: P1.5.5 Scanner orchestration decomposition

## 1. Purpose

P1.5.5 restores an explicit Scanner component boundary without changing Scanner selection semantics, candidate-source behavior, score weights, Monitor authority, runtime topology, or execution behavior.

Canonical current Scanner runtime:
- graphs/nodes/scanner_node.py
- approximately 4,179 LOC
- 61 top-level functions/classes
- scanner_node() itself approximately 1,945 LOC

The current node already reuses many focused runtime modules, so P1.5.5 is not a rewrite. It is a staged completion of the existing decomposition.

## 2. Existing Ownership — Reuse, Do Not Duplicate

Existing focused Scanner owners include:

- libs/runtime/scanner/candidate_selection.py
  candidate source, source policy, Kiwoom pool, fallback resolution

- libs/runtime/scanner/theme_filter.py
  selected/avoid theme extraction and filtering

- libs/runtime/scanner/practical_filters.py
  quote metrics, practical pool reduction, restricted mock-broker filtering

- libs/runtime/scanner/market_representative_guard.py
  market representative policy and overlay

- libs/runtime/scanner/candidate_risk.py
  candidate base-risk calculation

- libs/runtime/scanner/output_snapshots.py
  compact candidate/feature/ranking snapshots

- libs/runtime/scanner/output_payloads.py
  ranking-table and selection-reason evidence payloads

- libs/runtime/scanner/control_eligibility.py
  full Strategist-control eligibility metadata

- libs/runtime/scanner_feature_hydration.py
  feature hydration and seed data resolution

- libs/runtime/scanner_policy.py
  runtime Scanner source-policy resolution

- libs/runtime/scanner_bias.py
  normalized structured Scanner-bias contract

- libs/runtime/scanner_memory_bias.py
  memory-bias calculation and summary

- libs/runtime/quant/suitability.py
  candidate tactic suitability

- libs/runtime/intraday_monitor_signals.py
  Monitor-side entry-policy evaluation reused only for Scanner soft compatibility estimation

- graphs/nodes/skill_contracts.py
  normalized quote/order/minute-OHLCV skill contracts

P1.5.5 must promote these owners instead of creating parallel implementations.

## 3. Legacy Compatibility Surfaces

### graphs/nodes/scanner_node.py

This is the canonical integrated-chain Scanner runtime today.

It must remain a compatibility façade during staged migration.

### libs/agent/scanner.py

This is explicitly documented in code as a legacy Scanner adapter.

Its current scan(plan, context) contract is not the canonical integrated-chain Scanner contract.

Classification:
- WRAPPER / LEGACY COMPATIBILITY
- do not make it the new authority by silently moving scanner_node behavior into the existing class contract
- retain until consumers are explicitly migrated

### graphs/nodes/scan_candidates.py

Explicit compatibility candidate-stage helper. Canonical ranking remains scanner_node.py.

Classification:
- WRAPPER / LEGACY STAGE CONTRACT
- keep state["candidates"] compatibility

### graphs/nodes/select_candidate.py

Historical minimal M11 selection helper, separate from canonical integrated Scanner ranking.

Classification:
- LEGACY COMPATIBILITY / later naming-cleanup candidate
- do not fold its cheap-first placeholder semantics into the canonical Scanner component

## 4. Current Scanner Node Responsibility Map

The node currently mixes the following responsibilities:

1. candidate-source orchestration
2. live-equity / asset / practical filtering
3. Strategist/Commander guidance projection
4. Scanner runtime-policy projection
5. repeat-selection and repeat-blocker memory
6. symbol historical priors
7. quote/order skill hydration
8. feature hydration
9. candidate quantitative scoring
10. structured Scanner bias
11. memory bias
12. Monitor-readiness soft compatibility scoring
13. macro chart-fit soft scoring
14. market-representative guard
15. blocker-family concentration overlay / optional selection veto
16. ranking and selected-candidate output construction
17. compatibility state mutation
18. evidence/event logging
19. Q9 snapshot generation
20. canonical Scanner artifact write

The target is to separate calculation, IO, evidence, orchestration and compatibility-state adaptation.

## 5. Size / Hotspot Inventory

Largest current functions:

- scanner_node: ~1,945 LOC
- _compute_entry_compatibility_signal: ~193 LOC
- _extract_scanner_guidance: ~153 LOC
- _build_scanner_policy_trace: ~152 LOC
- _compute_scanner_macro_chart_fit: ~127 LOC
- _compute_symbol_prior_adjustment: ~106 LOC
- _apply_blocker_family_concentration_overlay: ~94 LOC
- _apply_scanner_guidance_weights: ~76 LOC
- _compute_structured_scanner_bias: ~62 LOC
- _resolve_compatibility_bias_context: ~62 LOC
- _scanner_macro_focus: ~61 LOC
- _extract_feature_engine_map: ~60 LOC
- repeat guard penalty helpers: ~55-59 LOC each

The 1,945-line scanner_node body is the main P1.5.5 decomposition target.

## 6. Authority Boundary — Frozen

The existing architectural rule is authoritative:

Strategist:
- defines strategy frame and tactical preference

Scanner:
- builds/ranks candidate set
- selects the candidate worth Monitor attention
- may apply soft chart-fit / Monitor-readiness bias

Monitor:
- remains the actionable entry and exit hard-gate authority

Commander:
- controls runtime sequencing, policy and execution flow

Supervisor / Executor:
- retain safety/execution authority

Scanner must not become a second entry gate during P1.5.5.

Existing fields and meanings remain unchanged:
- entry_compatibility_score
- compatibility_bias
- scanner_chart_fit_score
- scanner_chart_fit_authority = soft_rank_bias_only where currently applicable
- scanner_macro_chart_fit_score
- scanner_macro_chart_fit_authority = soft_rank_bias_only
- expected_monitor_block_reason

No P1.5.5 extraction may turn soft rank context into a BUY/SELL approval.

## 7. Hard Scanner-Level Exclusions / Policy Semantics

Current Scanner-level exclusions/overlays remain behaviorally identical.

Examples include:
- invalid or disallowed asset class
- live-equity symbol filtering where enabled
- halted / practical liquidity filtering where current policy applies
- mock-broker restricted symbol filtering
- current market-representative guard behavior
- current blocker-family concentration behavior
- current policy-controlled selection veto behavior

P1.5.5 does not tune or broaden any of these.

## 8. New Agent-Level Boundary

The new standalone Scanner component should use explicit Agent-level contracts.

Frozen design names:

- ScannerAgentInput
- ScannerAgentResult

Standalone surface:

run_scanner(input: ScannerAgentInput) -> ScannerAgentResult

scanner_node(state) remains the graph compatibility adapter and performs:

state -> ScannerAgentInput
run_scanner(...)
ScannerAgentResult -> compatibility state patch

The existing libs.agent.Scanner remains a separate legacy wrapper until consumer migration.

## 9. ScannerAgentInput Groups

The Agent input should group existing runtime inputs without semantic reinterpretation.

### Runtime identity / policy
- run_id
- policy
- applied_policy / Commander context where currently consumed
- canonical day/time inputs
- runtime/test clock overrides

### Strategist frame
- strategist_output
- scanner_guidance compatibility override
- themes / avoid themes / playbook
- scanner_priority
- scanner_source_policy
- scanner_bias_context
- scanner_memory_bias
- trade_aggressiveness
- risk_tone
- monitor_guidance
- strategy policy / monitor entry policy references

### Candidate / universe inputs
- injected candidates
- candidate-source metadata
- market/universe data already available to the Scanner source resolver

### Market / skill inputs
- skill_results
- quote data
- account orders
- minute OHLCV
- feature-engine / scanner-feature seed data
- OHLCV seed data

### Portfolio / memory context
- persisted_state
- portfolio/account context currently read by Scanner
- symbol prior/report-root context
- previous Monitor block context

### Test / adapter-only hooks
- mock_scan_results
- injected event logger
- controlled hydration overrides

The pure Scanner service should not require the whole arbitrary graph state once the adapter is complete.

## 10. ScannerAgentResult / Compatibility Output

The new result must preserve the current output meaning.

Current direct/compatibility state-write surface in scanner_node.py contains 21 keys:

- auto_skill_runner
- candidates
- persisted_state
- q9_scanner_snapshot_result
- ranked_candidates
- risk
- scan_results
- scanner_candidate_pool
- scanner_candidate_ranking_table
- scanner_candidate_selection_reason
- scanner_feature
- scanner_margin_vs_second
- scanner_output
- scanner_quote_diagnostic
- scanner_ranking_table
- scanner_runner_up_reasons
- scanner_selection_reason
- scanner_skill
- scanner_source_universe_before_strategy_weighting
- selected
- top_stock

Not every key belongs in the pure result contract. The state adapter must nevertheless preserve every currently observable compatibility write.

Recommended ScannerAgentResult groups:

- selected candidate
- ranked candidates
- full scan results
- risk summary
- scanner output summary
- candidate pool metadata
- quote/feature/skill diagnostics
- ranking and selection evidence payloads
- evaluation/control snapshots
- memory update request
- evidence payload bundle
- compatibility_state_patch

Do not silently rename existing state keys during P1.5.5.

## 11. Downstream Compatibility Seams

Known downstream consumers rely on:
- state["selected"]
- state["top_stock"]
- state["ranked_candidates"]
- state["scanner_output"]
- state["risk"]

Monitor directly consumes selected/ranked_candidates/scanner_output.

Decision consumes selected and risk.

Commander consumes selected and post-Scanner candidate snapshots.

These compatibility surfaces remain frozen until later explicit migration.

## 12. Private Test / Monkeypatch Seams

Tests directly import or monkeypatch Scanner internals.

Known imported private functions:
- _apply_scanner_guidance_weights
- _candidate_quote_metrics
- _compute_symbol_prior_adjustment
- _extract_scanner_guidance
- _compute_structured_scanner_bias

Known monkeypatch seams include:
- graphs.nodes.scanner_node._maybe_hydrate_scanner_skill_results
- graphs.nodes.scanner_node.hydrate_scanner_feature_map
- graphs.nodes.scanner_node.build_symbol_read_model
- graphs.nodes.scanner_node._resolve_scanner_candidates
- graphs.nodes.scanner_node._scanner_bias_total_cap
- graphs.nodes.scanner_node._compute_entry_compatibility_signal
- graphs.nodes.scanner_node._load_symbol_priors
- graphs.nodes.scanner_node.evaluate_intraday_entry_signal

These must remain wrapper/re-export seams during staged extraction.

Do not break tests and call that cleanup.

## 13. Existing Test Coverage

The current Scanner-specific/adjacent test set inspected for this design contains at least 113 tests across files including:

- tests/test_scanner_strategy_frame_integration.py
- tests/test_scanner_monitor_compatibility.py
- tests/test_scanner_policy_overlay.py
- tests/test_scanner_rank_plumbing_fix.py
- tests/test_scanner_fallback_policy.py
- tests/test_scanner_practical_selection_engine.py
- tests/test_scanner_feature_hydration.py
- tests/test_scanner_memory_bias.py
- tests/test_scanner_bias_integration.py
- tests/test_scanner_candidate_risk.py
- tests/test_scanner_quote_hydration_runtime.py
- tests/test_scanner_live_symbol_filter.py
- tests/test_scanner_universe_candidate_metadata.py
- tests/test_m22_skill_native_scanner_monitor.py
- tests/test_m29_2_scanner_feature_integration.py
- tests/test_commander_post_scanner_context.py
- additional evaluation/reporting Scanner tests

Historical M11 compatibility tests remain historical assets.

## 14. Target Ownership Model

Reuse existing libs/runtime/scanner modules first.

Add only residual owners that do not already exist.

Recommended target:

libs/runtime/scanner/
- candidate_selection.py                existing
- theme_filter.py                       existing
- practical_filters.py                  existing
- market_representative_guard.py        existing
- candidate_risk.py                     existing
- output_snapshots.py                   existing
- output_payloads.py                    existing
- control_eligibility.py                existing
- guidance.py                           new residual owner
- repeat_guard.py                       new residual owner
- symbol_prior.py                       new residual owner
- compatibility.py                      new residual owner
- macro_chart_fit.py                    optional separate residual owner
- scoring.py                            new main deterministic scoring owner
- evidence.py                           new evidence/event payload owner
- contracts.py                          new ScannerAgentInput/Result
- service.py                            new run_scanner orchestration
- state_adapter.py                      new graph-state compatibility adapter

Existing external owners remain external:
- scanner_feature_hydration.py
- scanner_policy.py
- scanner_bias.py
- scanner_memory_bias.py
- intraday_monitor_signals.py
- quant/suitability.py
- skill_contracts.py

Do not move files merely for directory purity.

## 15. Function Ownership Guidance

### MOVE -> guidance.py
- _extract_scanner_guidance
- _build_scanner_policy_trace
- _normalize_priority_list
- _apply_scanner_guidance_weights
- related score-weight normalization that is Scanner-guidance-specific

### MOVE -> repeat_guard.py
- _resolve_scanner_repeat_guard_policy
- _scanner_recent_selection_history
- _scanner_recent_block_history
- _resolve_now_epoch
- _repeat_symbol_penalty
- _repeat_blocker_cooldown_penalty
- selected-symbol memory-update calculation

The actual mutation of persisted graph state should be applied through state_adapter, not hidden inside pure scoring.

### MOVE -> symbol_prior.py
- report-root / symbol-prior read adapter boundary
- _compute_symbol_prior_adjustment

Prefer separating the file-read adapter from the pure prior adjustment function.

### MOVE -> compatibility.py
- Scanner/Monitor policy input/frame construction
- _compute_entry_compatibility_signal
- blocker-family normalization
- compatibility-bias context projection
- mock compatibility override
- blocker-family concentration overlay

Preserve soft-ranking authority exactly.

### MOVE -> macro_chart_fit.py
- _scanner_macro_focus
- _compute_scanner_macro_chart_fit
- related macro chart-fit helpers

This may remain inside compatibility.py if the resulting module stays coherent and below review thresholds.

### MOVE -> scoring.py
The per-candidate deterministic score assembly now embedded in scanner_node.

It should consume explicit candidate context and return scored rows without writing graph state.

### MOVE -> evidence.py
- Scanner event payload construction
- raw-input evidence preparation
- decision-bridge payload construction
- ranking/selection evidence orchestration
- Q9 snapshot request preparation where practical

Actual file/event writes remain explicit IO operations.

### MOVE -> state_adapter.py
- current 21-key compatibility state patch
- scanner_output construction
- selected/risk/top_stock compatibility
- persisted recent-selection update
- legacy alias fields

### KEEP / WRAPPER -> scanner_node.py
- graph entrypoint
- compatibility imports/private wrappers
- build Agent input
- call run_scanner
- apply state patch
- call explicit evidence/artifact adapters until migrated

Target final node size: approximately 150-350 LOC after staged migration, allowing temporary wrappers.

## 16. IO / Purity Boundary

P1.5.5 should make these dependencies explicit:

IO / adapter responsibilities:
- Kiwoom candidate source access through existing providers
- skill hydration
- feature hydration
- symbol prior report reads
- event logger
- evidence ledger writes
- Q9 snapshot generation
- canonical Scanner artifact writes

Pure/deterministic responsibilities:
- guidance normalization
- score-weight application
- candidate risk/score calculations
- structured bias
- soft chart compatibility
- macro chart fit
- ranking transforms
- selection metadata construction

Do not introduce hidden filesystem or network access into pure scoring modules.

## 17. Implementation Batches

Do not refactor the 4,179-line node in one commit.

### SC1 — Contracts + state adapter shell

Add:
- ScannerAgentInput
- ScannerAgentResult
- state-to-input adapter
- result-to-state compatibility adapter

Initially the adapter may wrap the existing implementation.

Goal:
- freeze boundary without moving scoring

Tests:
- compatibility state-patch fixture
- selected/ranked/risk/scanner_output equivalence

### SC2 — Existing-owner completion

Promote/reuse existing:
- candidate selection
- theme filtering
- practical filters
- output snapshots/payloads
- policy helpers

Replace local duplication with wrappers where behavior is proven identical.

No score changes.

### SC3 — Guidance + repeat/prior extraction

Move:
- Strategist/Commander guidance projection
- Scanner policy trace
- repeat guard/memory
- symbol prior adjustment

Keep private wrappers in scanner_node for current tests.

### SC4 — Compatibility/chart-fit extraction

Move:
- entry compatibility
- Scanner chart fit
- macro chart fit
- compatibility bias context
- blocker-family overlay

Authority regression test is mandatory:
Scanner remains soft ranker; Monitor remains hard entry gate.

### SC5 — Deterministic scoring service

Extract the large per-candidate scoring/ranking loop into a state-independent service using explicit inputs.

No weight, threshold, sort-key or tie-break changes.

Golden fixture comparison should assert candidate order and score components are identical.

### SC6 — Evidence / IO orchestration

Move:
- event/evidence payload preparation
- canonical artifact write orchestration
- Q9 snapshot handling
- symbol-prior/skill/feature IO adapters where not already owned

Keep write behavior and failure tolerance identical.

### SC7 — scanner_node façade + tests

Reduce scanner_node to:
- input adaptation
- run_scanner call
- state patch
- explicit IO/evidence bridge
- compatibility wrappers

Then gradually split tests into unit/integration/regression layout.

## 18. Test Architecture Target

Migrate gradually toward:

tests/unit/scanner/
- test_candidate_selection.py
- test_guidance.py
- test_scoring.py
- test_bias.py
- test_repeat_guard.py
- test_symbol_prior.py
- test_compatibility.py
- test_macro_chart_fit.py
- test_output_contract.py
- test_state_adapter.py

tests/integration/scanner/
- test_scanner_service.py
- test_feature_hydration.py
- test_skill_hydration.py
- test_strategist_frame.py
- test_monitor_compatibility.py
- test_commander_post_scanner.py

tests/regression/scanner/
- test_rank_plumbing.py
- test_fallback_policy.py
- test_live_symbol_filter.py
- test_policy_overlay.py
- test_authority_separation.py

Historical M11 tests remain preserved.

Do not bulk-move tests in one commit.

## 19. Behavior Locks

All remain SAME:

- candidate source precedence
- Kiwoom/static/Strategist fallback behavior
- live-equity filtering behavior
- asset-universe filtering
- practical filter behavior
- score weights
- Strategist guidance multipliers
- repeat-guard penalties
- symbol-prior penalties/bonuses
- structured Scanner bias
- memory bias
- entry compatibility formula
- Scanner chart-fit formula and soft authority
- macro chart-fit formula and soft authority
- market-representative guard
- blocker-family concentration overlay
- policy-controlled selection veto semantics
- rank sort/tie-break behavior
- selected candidate
- ranked candidate field schema
- scanner_output field schema
- risk summary
- evidence payload meaning
- Q9 snapshot meaning
- artifact paths
- state compatibility keys
- Monitor hard-entry authority
- Commander/Supervisor/Executor authority
- UEF semantics

## 20. Explicit Non-Goals / Deferred Tuning

P1.5.5 must NOT implement known Scanner tuning ideas.

Deferred examples:
- trading_value vs volume_surge weight tuning
- defensive-playbook liquidity rebalance
- new candidate sources
- new chart-reading features
- new Strategist Scanner schema fields
- broader selection veto
- Monitor threshold changes
- strategy alpha changes

Those require separate strategy/tuning approval after structural freeze.

## 21. Forbidden Changes

Stop/report rather than improvise if decomposition appears to require:
- score-weight change
- ranking-order semantic change
- candidate-source policy change
- soft Scanner chart fit becoming a hard entry gate
- Monitor authority change
- new LLM role/call
- new dependency
- breaking scanner_output/state key rename
- artifact/evidence semantic change
- UEF change
- Step5C/Step5D change
- broker/execution path change

## 22. Required Validation

Focused Scanner suites must include at least:
- tests/test_scanner_strategy_frame_integration.py
- tests/test_scanner_monitor_compatibility.py
- tests/test_scanner_policy_overlay.py
- tests/test_scanner_rank_plumbing_fix.py
- tests/test_scanner_fallback_policy.py
- tests/test_scanner_practical_selection_engine.py
- tests/test_scanner_feature_hydration.py
- tests/test_scanner_memory_bias.py
- tests/test_scanner_bias_integration.py
- tests/test_scanner_candidate_risk.py
- tests/test_scanner_quote_hydration_runtime.py
- tests/test_scanner_live_symbol_filter.py
- tests/test_scanner_universe_candidate_metadata.py
- tests/test_m22_skill_native_scanner_monitor.py
- tests/test_m29_2_scanner_feature_integration.py
- tests/test_commander_post_scanner_context.py

Then affected Monitor/Commander/Decision/reporting regressions and full pytest.

Additional acceptance:
- deterministic ranking replay unchanged
- production-write leakage NONE
- trading-authority leakage NONE
- new LLM decision roles 0
- Monitor hard-gate authority unchanged
- UEF semantics SAME
- Step5C/Step5D semantics SAME

## 23. Documentation

During implementation:
- update canonical Scanner architecture documentation
- preserve historical role-boundary/tuning documents
- do not rewrite historical M11/M18/M22 records as current architecture
- add daily technical patch for each major tranche
- append matching UI/API patch-note entry
- verify all patch-note source paths exist

## 24. Implementation Gate

P1.5.5 runtime implementation starts only from the frozen P1.5 implementation baseline required by the master plan.

This design branch remains design/documentation only.

## 25. Design Verdict

Scanner runtime inventory: COMPLETE
Canonical node identified: YES
Legacy adapters identified: YES
Existing focused owners mapped: YES
61 top-level functions inventoried: YES
1,945-line orchestration hotspot identified: YES
21-key compatibility state-write surface mapped: YES
Private/monkeypatch test seams mapped: YES
Scanner/Monitor authority boundary frozen: YES
Scanner Agent boundary frozen: YES
SC1-SC7 implementation order frozen: YES
Runtime implementation: NOT STARTED
