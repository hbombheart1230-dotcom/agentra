# P1.5 Monitor Implementation Packet v1.0

Status: DESIGN COMPLETE / IMPLEMENTATION GATED
Date: 2026-10-07
Design branch: design/p1.5-p1.6-modernization
Scope: P1.5.6 Monitor orchestration decomposition

## 1. Purpose

P1.5.6 restores an explicit Monitor component boundary without changing entry/exit semantics, policy interpretation, scoring behavior, candidate-cascade behavior, position sizing, exit guards, intent semantics, execution authority, or runtime topology.

Canonical current Monitor runtime:
- graphs/nodes/monitor_node.py
- approximately 3,633 LOC
- 14 top-level functions
- monitor_node() approximately 2,635 LOC
- _evaluate_monitor_entry_candidate() approximately 660 LOC

Major adjacent signal engine:
- libs/runtime/intraday_monitor_signals.py
- approximately 3,608 LOC
- large deterministic entry-policy / chart / scoring engine

The current Monitor already reuses many focused entry/exit modules. P1.5.6 therefore completes the existing decomposition rather than rewriting Monitor.

## 2. Monitor Authority Boundary — Frozen

The current runtime authority model remains:

Strategist
- owns strategy frame and policy intent

Scanner
- ranks/selects candidate attention
- chart-fit remains soft ranking context

Monitor
- owns actionable entry/exit timing decision
- emits at most one intent per cycle
- does not execute an order

Supervisor
- remains approval / safety authority

Executor
- remains side-effect / broker execution authority

Therefore:

Monitor hard decision owner != trading execution authority.

P1.5.6 must preserve:
- Monitor may emit BUY/SELL intent or NOOP
- Monitor cannot bypass Supervisor
- Monitor cannot call broker execution directly
- no new LLM decision role
- no direct production trading authority is introduced

## 3. Existing Ownership — Reuse, Do Not Duplicate

Existing focused Monitor entry owners include:

- libs/runtime/monitor_candidate_cascade.py
  runner-up cascade plan

- libs/runtime/monitor_directional_edge.py
  horizon directional edge estimation

- libs/runtime/monitor_entry_blockers.py
  entry guard evaluation

- libs/runtime/monitor_entry_controls.py
  max positions, pending orders, open-position and closeout guards

- libs/runtime/monitor_entry_cost_filter.py
  cost-drag / cost-adjusted edge filtering

- libs/runtime/monitor_entry_policy_context.py
  Commander entry-control, effective policy trace, scoring config, memory-bias payload

- libs/runtime/monitor_entry_quality.py
  entry quality gate and chart-fit candidate classification

- libs/runtime/monitor_entry_sizing.py
  cash/position context and sizing inputs

- libs/runtime/monitor_entry_state.py
  posture and entry transition state

- libs/runtime/monitor_memory_bias.py
  entry/hold/exit memory-bias application

- libs/runtime/monitor_minute_ohlcv.py
  minute-data fetch/cache/freshness recovery

- libs/runtime/monitor_policy.py
  MonitorEntryPolicy and contract normalization

- libs/runtime/monitor_runner_up_quality.py
  runner-up quality evaluation

- libs/runtime/monitor_strategy_frame.py
  Strategist/Commander frame projection and entry/exit policy framing

- libs/runtime/intraday_monitor_signals.py
  deterministic entry-policy interpretation, chart evidence, scoring and signal evaluation

Existing focused Monitor exit owners include the libs/runtime/monitor_exit package:

- selection.py
- preview.py
- price_resolution.py
- policy_config.py
- hold_controls.py
- observability.py
- overnight_carry.py
- order_lifecycle.py
- position_tracking.py
- reasons.py
- post_exit_shadow.py
- position_risk.py
- position_state_enrichment.py
- selected_snapshot.py
- market_enrichment.py
- session_vwap.py
- additional focused exit adapters/helpers

P1.5.6 must promote these owners and remove orchestration duplication from monitor_node. It must not create parallel versions.

## 4. Legacy Compatibility Surface

### graphs/nodes/monitor_node.py

Canonical integrated-chain Monitor runtime today.

Classification:
- KEEP AS GRAPH FACADE / WRAPPER during staged migration

### libs/agent/monitor.py

The source explicitly describes this as a legacy placeholder interface.

Current update(...) method is a no-op compatibility surface.

Classification:
- WRAPPER / LEGACY COMPATIBILITY
- do not silently repurpose this class as the new canonical Monitor implementation
- retain until consumers are explicitly migrated

## 5. Current Responsibility Map

monitor_node.py currently mixes:

1. strategy / policy context assembly
2. portfolio/open-position resolution
3. entry-policy contract selection
4. memory-bias application
5. minute OHLCV freshness / recovery IO
6. top-pick entry evaluation
7. runner-up candidate cascade
8. position sizing
9. cost-aware entry filter
10. entry quality gate
11. deterministic signal/scoring/policy interpretation
12. opening Rank-1 controlled-probe integration
13. directional-edge and quant evidence integration
14. selected-candidate mutation/enrichment
15. exit-symbol selection
16. exit-policy construction
17. exit-price/freshness handling
18. hold/min-hold/sell-cooldown/confirmation guards
19. overnight carry / closeout handling
20. exit intent construction
21. final entry-vs-exit intent arbitration
22. monitor_output construction
23. compatibility state mutation
24. transition/posture state persistence
25. operator/evaluation surfaces
26. event/evidence/decision-trace writes
27. quant shadow evidence
28. canonical Monitor artifact write

The target is explicit PURE / ORCHESTRATION / IO / AUTHORITY / EVIDENCE separation.

## 6. Main Hotspots

Current top-level hotspots:

- monitor_node: ~2,635 LOC
- _evaluate_monitor_entry_candidate: ~660 LOC
- _entry_forced_block_reason_for_open_carry: ~45 LOC
- event/log helpers: small

The low top-level function count is misleading: most orchestration is embedded directly in monitor_node.

Adjacent giant module:
- intraday_monitor_signals.py: ~3,608 LOC

This module already has many internal responsibilities:
- scoring configuration
- human chart detail
- human chart buy guard
- human chart entry setup
- policy interpretation
- policy interpreter trace
- policy alignment
- policy-aware gating
- chart-structure decision hint
- scoring fields
- candle normalization/compression/session analysis
- MonitorEntryPolicy resolution
- evaluate_intraday_entry_signal

It requires a later staged decomposition, not a same-commit rewrite with monitor_node.

## 7. Existing Entry Semantics — Freeze

P1.5.6 is structural only.

Preserve exactly:
- MonitorEntryPolicy normalization
- policy-source precedence
- Commander entry-control meaning
- Strategist monitor-policy meaning
- memory-bias behavior including observation-only mode
- minute OHLCV freshness/retry/cache behavior
- hard-filter semantics
- scoring mode and score calculation
- policy interpreter semantics
- required/preferred/relaxable checks
- chart-structure evidence
- human chart detail / buy guard / entry setup behavior
- cost filter
- directional edge
- entry quality gate
- position sizing
- same-symbol loss re-entry logic
- opening Rank-1 controlled-probe behavior
- entry cooldown
- post-exit cooldown
- closeout-window guard
- max-position / pending-buy guards
- candidate cascade eligibility and order
- runner-up selection semantics

No threshold or tuning change is part of P1.5.6.

## 8. Shadow / Experimental Monitor Scoring — Freeze

Historical Monitor scoring work remains structurally present.

Current design history states:
- scoring experiment was introduced to reduce excessive no-trade
- production promotion was deferred
- local/shadow evidence was retained
- policy-driven Monitor interpretation became the higher-level owner

P1.5.6 must not:
- promote shadow scoring
- disable it
- change its thresholds
- redefine its authority
- tune reclaim/volume/breakout/confidence logic

Scoring remains whatever current runtime semantics already implement.

Structural refactor must preserve legacy/scoring/shadow fields and decisions exactly.

## 9. Policy-Driven Monitor Boundary — Freeze

Current architecture already contains Strategist/Commander policy projection into Monitor.

The intended ownership remains:

Strategist policy
-> Monitor policy interpretation
-> deterministic evidence/scoring helpers
-> Monitor final entry decision
-> intent
-> Supervisor approval
-> Executor side effect

Scoring/evidence is not an independent agent or authority.

P1.5.6 must not add an LLM to Monitor.

## 10. Existing Exit Semantics — Freeze

The monitor_exit package is already strongly decomposed.

Preserve:
- exit-symbol selection
- position snapshot enrichment
- price-source precedence
- quote freshness semantics
- technical vs account price meaning
- min hold
- sell cooldown
- exit confirmation ticks
- hard/emergency exit reason priority
- stop-loss / take-profit / trailing / peak-drawdown behavior
- cost-aware profit floor
- expected-exit pricing
- protective exit behavior
- overnight carry
- EOD closeout behavior
- position peak tracking
- post-exit shadow
- exit-vs-strategy-intent evidence
- partial exit semantics
- exit quantity/fraction
- all current guard-adjustment semantics

P1.5.6 does not reorder sell-side safety decisions.

## 11. Intent Contract — Freeze

monitor_node currently documents and implements:
- at most one intent per cycle
- intent generation only
- no direct execution

Preserve:
- state["intents"]
- BUY/SELL side meaning
- quantity meaning
- selected/final symbol meaning
- NOOP represented through no intent plus Monitor decision surfaces
- entry-vs-exit arbitration
- exit priority where current runtime gives exit precedence
- downstream Supervisor/Decision/Executor expectations

No multi-intent behavior is introduced.

## 12. Compatibility State-Write Surface

Direct assignments observed in monitor_node contain 27 compatibility keys:

- _monitor_entry_cooldown_until
- _monitor_exit_confirm
- _monitor_pending_exit_lock
- _monitor_prev_position_qty
- _monitor_sell_cooldown_until
- intents
- monitor
- monitor_action_decision
- monitor_entry
- monitor_entry_blocker_surface
- monitor_entry_cascade
- monitor_entry_decision_detail
- monitor_evaluation
- monitor_exit
- monitor_exit_decision_detail
- monitor_focus_context
- monitor_no_trade_surface
- monitor_output
- monitor_posture
- monitor_sizing
- monitor_state_transition
- monitor_threshold_snapshot
- opening_rank1_controlled_probe
- quant_shadow_candidates
- scanner_monitor_handoff
- scanner_selected_snapshot
- selected

This list is a compatibility surface, not necessarily the pure AgentResult shape.

P1.5.6 must preserve all observable state meanings until consumers migrate.

## 13. monitor_output Compatibility

monitor_output is a large operator/runtime compatibility payload.

It currently exposes categories including:

- selected symbol and intent side/qty
- entry/exit reason
- cascade result
- cost/quality/directional-edge evidence
- quant entry/exit evidence
- received/effective policy
- policy source/provenance
- memory-bias application
- scoring/shadow fields
- hard-filter / score breakdown
- policy interpreter/alignment/gating
- chart-structure evidence
- transition state
- position sizing
- exit prices/freshness
- exit thresholds and active axis
- cost-aware exit fields
- peak drawdown / trailing / profit ladder fields
- carry / EOD state
- position and capacity guards
- no-trade surface
- scanner-monitor handoff

Do not prune monitor_output merely because fields appear redundant.

Field cleanup belongs only after consumer proof.

## 14. New Agent-Level Boundary

Frozen names:

- MonitorAgentInput
- MonitorAgentResult

Standalone callable:

run_monitor(input: MonitorAgentInput) -> MonitorAgentResult

Graph adapter:

state
-> MonitorAgentInput
-> run_monitor(...)
-> MonitorAgentResult
-> compatibility state patch

monitor_node(state) remains the graph entrypoint during migration.

The pure component must not require arbitrary hidden graph mutation after the state adapter is mature.

## 15. MonitorAgentInput Groups

### Runtime identity / clock
- run_id
- canonical/current time inputs
- test/runtime clock overrides

### Policy
- policy
- state monitor policy
- Strategist output and strategy policy
- Commander applied policy / Commander context
- Monitor entry policy
- entry-control fields

### Scanner handoff
- selected
- ranked_candidates
- scanner_output
- top_stock and compatible Scanner metadata

### Market / feature inputs
- skill results
- market quotes
- minute OHLCV
- feature maps
- selected feature context
- freshness/cache context

### Portfolio / account
- positions
- cash
- account orders
- order status
- persisted position state
- peak state

### Memory / history
- persisted_state
- Monitor memory bias
- recent trade/loss re-entry context
- post-exit cooldown state
- post-exit shadow context

### Adapter / test hooks
- event logger
- mock/test clock
- injected runners where currently supported

The Agent contract groups existing inputs; it does not reinterpret them.

## 16. MonitorAgentResult Groups

Recommended result groups:

- intent / NOOP result
- final monitored symbol
- entry decision
- exit decision
- sizing result
- cascade result
- posture / transition result
- Monitor output projection
- no-trade/blocker surfaces
- scanner-monitor handoff
- evaluation/decision detail payloads
- cooldown/confirmation state updates
- selected-candidate enrichment update
- quant shadow evidence request/result
- evidence/event payload bundle
- compatibility_state_patch

The result does not gain broker execution authority.

## 17. IO / Purity Boundary

Explicit IO/adapters:
- minute OHLCV runner / cache
- market quote / order status skill reads
- canonical artifact writes
- evidence ledger writes
- event logger
- decision trace
- Rank-1 probe persistence
- overnight-carry persistence
- quant shadow persistence
- any canonical report/file access

Deterministic / policy logic:
- policy contract normalization
- strategy-frame projection
- hard filters
- policy interpretation
- scoring evidence
- chart evidence
- entry quality/cost logic
- candidate cascade planning
- sizing calculations
- exit preview/calculation
- hold/cooldown/confirmation logic
- reason classification
- state-transition calculation

Do not bury new filesystem/network access in deterministic modules.

## 18. Target Ownership Model

Reuse current modules first.

Recommended additions:

libs/runtime/monitor/
- contracts.py
- service.py
- state_adapter.py
- entry_orchestrator.py
- exit_orchestrator.py
- intent_arbitration.py
- evidence.py

Optional later signal decomposition:

libs/runtime/monitor_entry_signals/
- policy_resolution.py
- chart_context.py
- policy_interpreter.py
- scoring.py
- candle_series.py
- evaluation.py

Compatibility facade:
- libs/runtime/intraday_monitor_signals.py remains import-compatible while implementation moves behind it

Do not move the existing monitor_exit package just to make the tree visually uniform.

## 19. Function Ownership Guidance

### MOVE -> entry_orchestrator.py
Current _evaluate_monitor_entry_candidate orchestration.

It should coordinate existing owners, not reimplement them.

Responsibilities:
- entry input preparation
- minute-source request
- policy/effective-policy setup
- memory-bias application
- signal evaluation call
- sizing/cost/quality integration
- guard result
- intent-eligible result

### MOVE -> exit_orchestrator.py
The large exit orchestration embedded in monitor_node:
- exit-symbol selection
- preview/policy integration
- memory bias
- carry / closeout
- hold/cooldown/confirm guards
- exit intent candidate construction

Keep monitor_exit helpers authoritative.

### MOVE -> intent_arbitration.py
Pure final choice among:
- SELL intent
- BUY intent
- NOOP

Preserve existing priority and reason semantics exactly.

### MOVE -> state_adapter.py
All 27-key compatibility state writes plus nested Monitor output compatibility.

### MOVE -> evidence.py
Build:
- raw-input evidence
- cycle-summary payload
- monitor summary payload
- decision-trace payload
- decision bridge
- threshold/state transition evidence
- evaluation/operator surfaces

Actual persistence remains explicit IO.

### KEEP / WRAPPER -> monitor_node.py
- graph entrypoint
- compatibility imports/private aliases
- Agent input adaptation
- run_monitor call
- state-patch application
- explicit IO bridges until migrated

Target final monitor_node size:
- approximately 150-350 LOC plus temporary compatibility wrappers

## 20. intraday_monitor_signals Decomposition Guidance

Do not decompose this giant module in the same first commit as monitor_node.

Later staged split should preserve public imports:
- resolve_intraday_entry_policy
- evaluate_intraday_entry_signal

Possible owners:
- candle/session normalization
- chart detail/context
- policy interpretation
- policy-aware gating
- scoring evidence
- final deterministic entry evaluation

All public/private test seams remain wrappers until migrated.

No semantic cleanup while extracting.

## 21. Private Test / Monkeypatch Seams

Known direct Monitor-node compatibility imports include:
- _evaluate_entry_cost_filter
- _extract_monitor_strategy_frame
- _classify_vwap_reclaim_pullback_candidate
- _resolve_price_with_source
- monitor_node

Known monkeypatch seams include:
- graphs.nodes.monitor_node._monitor_selected_snapshot_for_symbol
- graphs.nodes.monitor_node._ensure_monitor_minute_ohlcv_for_symbol
- graphs.nodes.monitor_node.evaluate_intraday_entry_signal
- graphs.nodes.monitor_node._resolve_entry_closeout_window_guard

Additional tests patch Monitor-node aliases and helper functions.

These wrappers/re-exports remain until tests/consumers migrate.

## 22. Existing Test Coverage

The core Monitor-specific/adjacent files inspected for this design contain at least 294 tests, including:

- tests/test_intraday_monitor_signals.py — 76
- tests/test_monitor_exit_guard.py — 114
- tests/test_m29_3_monitor_exit_policy.py — 17
- tests/test_monitor_feedback_adaptive_policy.py — 10
- tests/test_monitor_candidate_cascade.py — 14
- tests/test_monitor_memory_bias.py — 8
- tests/test_monitor_directional_edge.py — 8
- tests/test_monitor_fallback_quality_gate.py — 5
- tests/test_m29_4_monitor_position_sizing.py — 5
- tests/test_m29_5_monitor_metrics_report.py — 2
- tests/test_m22_skill_native_scanner_monitor.py — 11
- tests/test_m17_monitor_emits_intent_only.py — 2
- tests/test_monitor_exit_price_freshness.py — 9
- tests/test_monitor_minute_ohlcv_resilience.py — 1
- tests/test_monitor_price_source_resolution.py — 1
- tests/test_scanner_monitor_compatibility.py — 11

This excludes additional Commander/execution/reporting integration tests.

These are migration assets, not cleanup noise.

## 23. P1.5.6 Implementation Batches

Do not refactor monitor_node and intraday_monitor_signals in one commit.

### MO1 — Contracts + state-adapter characterization

Add:
- MonitorAgentInput
- MonitorAgentResult
- result/state compatibility fixtures

Initially allow the service to delegate to legacy behavior.

Freeze:
- 27-key compatibility surface
- intent semantics
- monitor_output semantics

### MO2 — Existing-owner completion

Promote current focused entry/exit helpers.

Remove only proven local orchestration duplication.

No policy/signal/exit semantic change.

### MO3 — Entry orchestration extraction

Move _evaluate_monitor_entry_candidate behind entry_orchestrator.

Keep monitor_node wrappers for current private test seams.

Golden comparison:
- same entry_info
- same guard reason
- same quantity
- same BUY/WAIT outcome
- same policy/evidence fields

### MO4 — Exit orchestration extraction

Move embedded exit flow behind exit_orchestrator.

Mandatory golden comparison:
- same selected exit symbol
- same reason
- same thresholds
- same confirmation/cooldown/min-hold behavior
- same SELL/HOLD outcome
- same price-source/freshness fields

### MO5 — Intent arbitration + state adapter

Extract final BUY/SELL/NOOP arbitration and compatibility mutation.

Assert at-most-one-intent invariant.

### MO6 — Evidence / IO orchestration

Move evidence payload construction and explicit IO bridges:
- event logs
- decision trace
- evidence ledger
- canonical Monitor artifact
- quant shadow
- probe/carry persistence where appropriate

Preserve failure tolerance and paths.

### MO7 — intraday signal-engine decomposition

Only after MO1-MO6 are green.

Split intraday_monitor_signals by responsibility behind compatibility facade.

No formula, threshold, interpretation or scoring changes.

### MO8 — monitor_node façade + staged test migration

Reduce graph node to:
- state -> input
- run_monitor
- apply state patch
- explicit IO/evidence bridge
- compatibility wrappers

Then gradually migrate tests into unit/integration/regression layout.

## 24. Target Test Architecture

Migrate gradually toward:

tests/unit/monitor/
- test_contracts.py
- test_policy_context.py
- test_entry_orchestrator.py
- test_candidate_cascade.py
- test_entry_quality.py
- test_entry_cost.py
- test_entry_sizing.py
- test_memory_bias.py
- test_intent_arbitration.py
- test_state_adapter.py

tests/unit/monitor/signals/
- test_policy_resolution.py
- test_policy_interpreter.py
- test_chart_context.py
- test_scoring.py
- test_entry_evaluation.py

tests/unit/monitor/exit/
- preserve current focused exit tests by responsibility

tests/integration/monitor/
- test_monitor_service.py
- test_scanner_handoff.py
- test_minute_ohlcv.py
- test_portfolio_entry_guards.py
- test_entry_exit_cycle.py
- test_commander_policy.py

tests/regression/monitor/
- test_exit_guard.py
- test_price_freshness.py
- test_shadow_scoring_compatibility.py
- test_intent_only_authority.py
- historical incident regressions

Do not bulk-move tests.

## 25. Behavior Locks

All remain SAME:

- Monitor emits at most one intent
- no broker execution in Monitor
- entry policy source precedence
- Strategist/Commander policy meaning
- Monitor memory bias
- scoring mode / shadow behavior
- hard filters
- score formulas and threshold
- policy interpreter
- chart logic
- candidate cascade
- runner-up selection
- Rank-1 controlled probe
- position sizing
- cost filter
- directional edge
- entry quality
- same-symbol re-entry rules
- max-position guard
- pending-order guard
- closeout guard
- post-exit cooldown
- entry cooldown
- exit symbol selection
- exit reason priority
- price-source/freshness policy
- min hold
- sell cooldown
- confirmation ticks
- hard/emergency exits
- stop/take-profit/trailing/peak-drawdown logic
- cost-aware exit floor
- overnight carry
- EOD behavior
- partial exit semantics
- final BUY/SELL/NOOP arbitration
- monitor_output schema/meaning
- all 27 compatibility state keys
- evidence/artifact paths
- Scanner soft authority
- Monitor hard timing authority
- Supervisor approval authority
- Executor side-effect authority
- UEF semantics

## 26. Explicit Non-Goals / Deferred Tuning

Do NOT use P1.5.6 to:
- enable/promote Monitor shadow scoring
- tune scoring threshold
- tune reclaim/volume/breakout logic
- change hard vs soft checks
- add new chart features
- change candidate cascade breadth
- change runner-up policy
- change opening Rank-1 probe policy
- alter stop/take-profit/trailing values
- change overnight carry policy
- change position sizing
- change strategy alpha
- add an LLM call
- change Supervisor/Executor behavior

## 27. Forbidden Changes

Stop/report instead of improvising if extraction requires:
- semantic field reinterpretation
- intent priority change
- BUY/SELL threshold change
- exit guard weakening
- direct broker call
- Supervisor bypass
- multi-intent behavior
- state-key rename without compatibility
- artifact/evidence semantic change
- new dependency
- new LLM decision point
- UEF change
- Step5C/Step5D change

## 28. Required Validation

Focused minimum:
- tests/test_intraday_monitor_signals.py
- tests/test_monitor_exit_guard.py
- tests/test_m29_3_monitor_exit_policy.py
- tests/test_monitor_feedback_adaptive_policy.py
- tests/test_monitor_candidate_cascade.py
- tests/test_monitor_memory_bias.py
- tests/test_monitor_directional_edge.py
- tests/test_monitor_fallback_quality_gate.py
- tests/test_m29_4_monitor_position_sizing.py
- tests/test_m29_5_monitor_metrics_report.py
- tests/test_m22_skill_native_scanner_monitor.py
- tests/test_m17_monitor_emits_intent_only.py
- tests/test_monitor_exit_price_freshness.py
- tests/test_monitor_minute_ohlcv_resilience.py
- tests/test_monitor_price_source_resolution.py
- tests/test_scanner_monitor_compatibility.py

Then affected Commander/Supervisor/Executor/reporting integration and full pytest.

Acceptance:
- deterministic replay unchanged
- at-most-one-intent invariant PASS
- Monitor direct broker execution NONE
- execution without Supervisor approval NONE
- production-write leakage NONE
- trading-authority leakage NONE
- new LLM decision roles 0
- UEF semantics SAME
- Step5C/Step5D semantics SAME

## 29. Documentation

During implementation:
- update canonical Monitor architecture docs
- preserve historical scoring/shadow/policy documents
- preserve historical incident and M17/M22/M29 records
- add daily technical patch for each major tranche
- append UI/API patch-note entry
- verify every patch-note source path exists

## 30. Implementation Gate

P1.5.6 runtime implementation starts only from the frozen P1.5 implementation baseline required by the master plan.

This design branch remains design/documentation only.

## 31. Design Verdict

Monitor node inventory: COMPLETE
Canonical runtime identified: YES
Legacy adapter identified: YES
Existing entry owners mapped: YES
Existing exit owners mapped: YES
2,635-line monitor_node hotspot identified: YES
660-line entry evaluator hotspot identified: YES
3,608-line signal engine identified: YES
27-key state-write compatibility surface mapped: YES
294+ focused/adjacent tests inventoried: YES
private/monkeypatch seams mapped: YES
Monitor intent-only authority frozen: YES
Scanner/Monitor/Supervisor/Executor boundary frozen: YES
MonitorAgentInput/MonitorAgentResult boundary frozen: YES
MO1-MO8 implementation order frozen: YES
Runtime implementation: NOT STARTED
