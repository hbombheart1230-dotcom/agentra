# P1.5 Commander / Runtime Implementation Packet v1.0

Status: DESIGN COMPLETE / IMPLEMENTATION GATED
Date: 2026-10-07
Design branch: design/p1.5-p1.6-modernization
Scope: P1.5.7 Commander/runtime decomposition

## 1. Purpose

P1.5.7 decomposes the canonical Commander/runtime orchestration while preserving all runtime routing, policy composition, fast-path behavior, execution safety, lifecycle, resilience, ownership, and evidence semantics.

Canonical current Commander runtime:
- graphs/commander_runtime.py
- approximately 6,298 LOC
- 105 top-level functions
- 46 directly assigned compatibility state keys

Largest current hotspots:
- _build_commander_decision: ~859 LOC
- _resolve_commander_behavior_policy: ~742 LOC
- _assess_open_position_commander_override: ~439 LOC
- _attach_commander_applied_policy: ~398 LOC
- _run_commander_runtime_impl: ~300 LOC
- _build_commander_entry_control: ~280 LOC
- _run_integrated_chain_impl: ~232 LOC
- _should_use_monitor_only_fast_path: ~167 LOC
- _resolve_commander_applied_policy: ~156 LOC
- _run_pre_entry_exit_sweep: ~137 LOC
- _should_use_session_closeout_fast_path: ~108 LOC

The current runtime already has substantial focused extraction under libs/runtime/commander/. P1.5.7 must complete that ownership migration rather than introduce a second Commander framework.

## 2. Commander Role — Frozen

The P1.5 master plan defines Commander as:

- deterministic orchestration
- deterministic policy/routing
- no new LLM decision point

LLM roles remain exactly:
- Strategist: allowed
- Reporter: allowed

Commander must not become an LLM agent.

Commander coordinates when components run. It does not become the semantic owner of Strategist, Scanner, Monitor, Supervisor, Executor, or Reporter internals.

## 3. Runtime Authority Model — Frozen

The existing authority chain remains:

Runtime ownership / live-loop gate
-> Commander routing/orchestration
-> Strategist / Scanner / Monitor
-> Decision / Supervisor safety
-> Executor mutation owner
-> Reporter / evidence

Important distinction:

Commander may invoke execution paths after a decision is marked approved, but Commander itself is not broker mutation authority.

The canonical execute_from_packet path retains:
- Supervisor checks
- execution readiness
- symbol/order guards
- duplicate guards
- unknown-outcome quarantine
- mutation ownership/ordering
- broker-side effect ownership

P1.5.7 must not move these checks into Commander and must not reorder them.

## 4. External SAFETY-LOCK Dependencies

The following are not refactoring targets for P1.5.7.

### Runtime ownership

libs/runtime/runtime_ownership.py and live-loop ownership wiring remain safety-locked.

Existing ownership invariants include:
- single runtime owner through SQLite/CAS lease semantics
- no PID-based authority
- no foreign lease deletion
- no silent stale takeover
- explicit recovery required after stale takeover
- no new tick after ownership loss
- clean release on shutdown

P1.5.7 may consume ownership state but must not change ownership semantics.

### Live-loop lifecycle

libs/runtime/live_loop_runner.py, runtime_lifecycle.py and entrypoint lifecycle/heartbeat behavior remain external runtime-envelope owners.

P1.5.7 must not move ownership heartbeat or shutdown/drain semantics into Commander.

### Execution safety

graphs/nodes/execute_from_packet.py and execution safety modules remain safety-locked until the later Executor phase.

Supervisor/CAS/idempotency/broker-mutation semantics are explicitly protected by the master plan.

### UEF / Step5C / Step5D

No UEF, Step5C, Step5D or broker mutation ordering change is permitted.

## 5. Existing Commander Owners — Reuse, Do Not Duplicate

Existing focused owners under libs/runtime/commander/:

### env_overrides.py
- temporary Commander runtime defaults
- env restoration
- Commander route/memory feature switches

### runtime_modes.py
- RuntimeMode normalization
- RuntimePhase normalization
- agent-chain annotation
- mode/phase resolution

### route_surface.py
- selected-route derivation
- reporter integration configuration
- reporter feedback policy

### policy_readers.py
- nested policy helpers
- route toggles
- cooldown policy readers
- trade-report policy reader

### policy_surface.py
- Commander-owned policy-field declarations
- route/scanner/monitor constants
- entry-control blocker sets
- temporary runtime defaults
- pre-entry sweep transient-key contract

### output_frames.py
- Commander decision-frame projection

### nodes.py
- IntegratedChainNodes dependency bundle
- lazy node loading

### shadow_runtime.py
- Strategist executed/skipped shadow markers
- pre-buy/post-scanner shadow reset and status

### session_context.py
- prior shadow seeding
- integrated-chain session context

### strategist_cache_decision.py
- Strategist cache reuse preference and cache-age context

### strategist_cache_store.py
- Strategist output contract/cache persistence

### strategist_fingerprint.py
- Strategist input fingerprint
- post-Scanner candidate compaction/context
- drift assessment

### strategist_refresh_decision.py
- pre-buy and selected-symbol refresh decision

### strategist_cycle.py
- pre-Scanner Strategist cycle
- post-Scanner refresh cycle

### execution.py
- approved Monitor decision orchestration into execute_from_packet
- trade-report/update-state post execution
- controlled mock lane orchestration

### fast_paths.py
- monitor-only path
- closeout-guard path
- pre-entry exit sweep wrapper
- forced closeout handling

### integrated_chain_support.py
- transitional compatibility re-export surface

P1.5.7 must finish migration toward these owners.

## 6. Existing Graph / Compatibility Surfaces

### graphs/commander_runtime.py

Canonical Commander runtime API today.

Classification:
- KEEP AS COMPATIBILITY FACADE
- progressively reduce implementation
- preserve run_commander_runtime public signature during P1.5.7

### graphs/nodes/commander_node.py

Thin wrapper over run_commander_runtime.

Classification:
- KEEP
- no orchestration logic should migrate into this node

### graphs/trading_graph.py

Legacy/custom graph-spine execution surface.

Current flow:
Strategist -> optional hydration -> Scanner -> Monitor -> portfolio guard -> Decision -> optional retry -> Executor stub

Classification:
- KEEP AS CURRENT FRAMEWORK SURFACE
- P1.5 does not migrate to LangGraph
- framework comparison belongs to P1.6

### decision_packet mode

Compatibility/runtime mode remains behaviorally unchanged.

Do not use P1.5.7 to retire it unless later P1.5.10 compatibility cleanup proves it unused and safe.

## 7. Runtime Modes and Phases — Frozen

Current RuntimeMode:
- graph_spine
- decision_packet
- integrated_chain

Current RuntimePhase:
- preopen
- session
- closeout

Mode resolution precedence and decision_packet opt-in behavior remain unchanged.

Current agent-chain annotations remain compatibility-visible.

P1.5.7 must not:
- add a runtime mode
- remove a runtime mode
- rename a mode
- alter default mode
- change phase mapping
- change runtime agent ordering

Naming cleanup belongs to P1.5.8.

## 8. Current Commander Responsibility Map

graphs/commander_runtime.py currently mixes:

1. runtime clock helpers
2. runtime phase/mode orchestration
3. runtime transition handling
4. resilience cooldown/incident handling
5. operator resume intervention
6. market-context clock normalization
7. Commander policy assembly
8. Strategist/Monitor/Scanner policy projection
9. LLM profile policy projection
10. memory packet and memory-bias policy
11. Commander horizon policy
12. entry-control construction
13. candidate-watch policy
14. Commander decision projection
15. Commander decision frame
16. open-position carry/recovery assessment
17. open-position Strategist refresh
18. Strategist cache / refresh orchestration
19. monitor-only fast-path selection
20. session closeout fast-path selection
21. pre-entry exit sweep
22. Stage-4 carry review
23. graph-spine dispatch
24. integrated-chain dispatch
25. preopen dispatch
26. closeout dispatch
27. decision-packet dispatch
28. controlled mock lane integration
29. execution orchestration bridge
30. reporter hook dispatch
31. portfolio preflight routing
32. state compatibility writes
33. Commander event logging
34. canonical Commander artifact writes
35. shadow Commander artifact writes
36. absent-stage LLM evidence
37. post-exit shadow recap runtime

This is the decomposition target.

## 9. Compatibility State-Write Surface

Direct assignments observed in graphs/commander_runtime.py contain 46 compatibility keys:

- applied_policy
- auto_skill_runner
- candidates
- commander_applied_policy
- commander_applied_policy_meta
- commander_applied_policy_summary
- commander_behavior_policy
- commander_decision
- commander_decision_frame
- commander_horizon_policy
- commander_open_position_override
- commander_open_position_refresh_context
- commander_pre_entry_exit_sweep
- commander_reporter_feedback_policy
- commander_route_observability
- commander_shadow_runtime
- decision
- decision_packet
- decision_reason
- execution
- force_refresh_strategist
- intents
- market_context
- monitor_entry_policy
- monitor_feature_hydration
- monitor_memory_bias
- path
- persisted_state
- portfolio_preflight
- portfolio_preflight_closeout_fallback
- post_exit_shadow_recap_runtime
- reporter_hook_results
- reporter_hook_summary
- resilience
- run_id
- runtime_fast_path
- runtime_phase
- runtime_retry_count
- runtime_status
- runtime_transition
- scanner_bias_context
- scanner_memory_bias
- selected
- snapshots
- strategist_output
- strategy_policy

This is a compatibility surface, not a recommendation that a single pure result DTO contain all 46 as first-class fields.

All observable meanings must remain compatible until consumers migrate.

## 10. Commander Decision Surface

_build_commander_decision currently aggregates a very broad control/evidence surface including:

- mode / runtime path / phase
- command intent
- Strategist invocation and cache choice
- Scanner mission and policy
- Monitor mission and policy
- entry control
- candidate watch/cascade control
- max positions / capacity
- market regime rail
- open-position carry/recovery state
- memory policy and memory-bias summaries
- horizon policy
- reporter feedback policy
- LLM invocation/execution profile policy
- intraday performance circuit
- adaptive policy observations
- source references and policy provenance

P1.5.7 must not prune this output opportunistically.

The first task is to move construction behind a dedicated owner while preserving payload shape.

## 11. Commander Policy Ownership — Frozen

policy_surface.py already explicitly declares Commander-owned fields.

P1.5.7 must preserve this ownership map.

The refactor must not transfer policy authority between:
- Commander
- Strategist
- Scanner
- Monitor
- Supervisor
- Executor
- Reporter

Examples that remain Commander-owned include current route toggles, memory usage switches, selected scanner source controls, monitor-entry runtime controls, execution cooldown projections, selected LLM profile routing and related runtime-level policy surfaces.

Semantic tuning is out of scope.

## 12. New Runtime-Level Boundary

Commander is orchestration, not a new semantic agent.

Therefore P1.5.7 does not add a new LLM/agent decision contract analogous to StrategistAgentInput.

Frozen design names for the deterministic runtime core:

- CommanderRuntimeInput
- CommanderRuntimeResult
- CommanderRoutePlan
- CommanderDecision

Target internal surface:

run_commander_cycle(input: CommanderRuntimeInput) -> CommanderRuntimeResult

Compatibility public surface remains:

run_commander_runtime(state, ...) -> state

Target adapter flow:

graph/state
-> CommanderRuntimeInput
-> deterministic route/phase service
-> component invocations through injected dependencies
-> CommanderRuntimeResult
-> compatibility state patch + explicit evidence IO

This separates orchestration state from arbitrary graph mutation without introducing a new decision authority.

## 13. CommanderRuntimeInput Groups

### Runtime envelope
- current state snapshot
- runtime mode override
- runtime phase override
- runtime transition
- runtime status
- runtime resilience state
- operator intervention state

### Policy/configuration
- policy / applied_policy
- Commander behavior policy inputs
- environment-derived compatibility defaults
- model/execution profile routing
- risk max positions

### Market/session
- market context
- market clock fields
- portfolio snapshot/preflight state
- account/open-order/readiness snapshots

### Component context
- Strategist output/cache/fingerprint
- Scanner output/ranked candidates
- Monitor output/intents
- Decision state
- execution state
- Reporter integration state

### Memory/history
- persisted_state
- Commander memory packets
- Scanner/Monitor memory bias
- position/carry history
- incident/cooldown context

### Injected dependencies
- graph runner
- integrated-chain runner
- preopen runner
- closeout runner
- decision function
- execution function
- Agent/component node bundle
- logger/artifact adapters where currently injectable

## 14. CommanderRuntimeResult Groups

Recommended deterministic result groups:

- selected mode
- selected phase
- selected route/path
- runtime status
- runtime transition result
- CommanderDecision
- CommanderDecisionFrame
- runtime plan
- applied policy projection
- behavior policy projection
- entry-control projection
- open-position override projection
- fast-path result
- downstream component outcome summaries
- resilience/incident update request
- reporter hook request/result
- evidence/artifact payload bundle
- compatibility_state_patch

Actual broker mutation stays inside the execution dependency, not in the pure Commander result.

## 15. Target Ownership Model

Reuse current libs/runtime/commander modules first.

Recommended new residual owners:

libs/runtime/commander/
- contracts.py
- service.py
- state_adapter.py
- policy_composition.py
- decision_builder.py
- entry_control.py
- open_position_control.py
- phase_router.py
- lifecycle.py
- evidence.py
- reporter_hooks.py

Existing modules remain:
- env_overrides.py
- execution.py
- fast_paths.py
- integrated_chain_support.py
- nodes.py
- output_frames.py
- policy_readers.py
- policy_surface.py
- route_surface.py
- runtime_modes.py
- session_context.py
- shadow_runtime.py
- strategist_cache_decision.py
- strategist_cache_store.py
- strategist_cycle.py
- strategist_fingerprint.py
- strategist_refresh_decision.py

Exact filenames are secondary. Responsibility boundaries are authoritative.

## 16. Function Ownership Guidance

### MOVE -> policy_composition.py

- _resolve_commander_applied_policy
- _resolve_commander_behavior_policy
- _attach_commander_behavior_policy
- _attach_commander_reporter_feedback_policy
- _attach_commander_applied_policy
- related policy summary/provenance helpers

This module composes runtime policy; it must not execute Agents.

### MOVE -> entry_control.py

- _extract_strategist_candidate_watch_policy
- _normalize_candidate_watch_proposal_for_commander
- _candidate_watch_rank_cap
- _apply_candidate_watch_proposal_to_entry_control
- _build_commander_entry_control
- related blocker/cascade control projections

No tuning of blocker sets or ranks.

### MOVE -> decision_builder.py

- _build_commander_decision
- decision event metadata / compact summaries that are pure projections
- use existing output_frames.py for decision-frame output

Target: decision construction, not routing.

### MOVE -> open_position_control.py

- carry state helpers
- session-open recovery assessment
- _assess_position_carry_control
- _build_open_position_strategist_refresh_context
- open-position selection/focus helpers
- _assess_open_position_commander_override
- closeout unresolved symbol helpers
- position profit/recovery helpers

No exit policy or Monitor semantic change.

### MOVE -> phase_router.py

- preopen orchestration
- closeout orchestration
- integrated-chain high-level route
- graph-spine routing
- decision-packet route

This module chooses paths but does not own Agent semantics.

### MOVE -> lifecycle.py

- runtime clock projection
- runtime transition application
- Commander cooldown guard
- operator resume intervention
- incident registration
- runtime status progression

Do not absorb live-loop ownership/heartbeat semantics.

### MOVE -> reporter_hooks.py

- reporter-agent resolution
- hook invocation
- hook enablement/orchestration
- reporter hook summary

Reporter content generation remains Reporter-owned.

### MOVE -> evidence.py

- Commander event payloads
- route/start/end/error evidence
- Commander artifact payloads
- shadow assessment payload
- absent later-stage LLM review evidence
- post-exit recap runtime evidence coordination

Actual file/log writes remain explicit IO adapters.

### MOVE -> state_adapter.py

- current compatibility state patch
- 46-key compatibility semantics
- state alias writes
- runtime-plan projection

### KEEP / WRAPPER -> graphs/commander_runtime.py

Final responsibilities:
- compatibility public API
- temporary env default scope
- adapt state -> CommanderRuntimeInput
- call Commander service
- apply compatibility result/state patch
- preserve private compatibility wrappers used by tests
- explicit top-level error boundary if needed

Target final size:
- approximately 200-500 LOC plus temporary compatibility wrappers

## 17. Existing-Owner Completion

Several parts of Commander are already extracted.

P1.5.7 should remove duplicated/stranded logic from commander_runtime only when equivalent ownership is proven.

In particular:
- integrated_chain_support.py is explicitly transitional
- new code should increasingly import execution.py, fast_paths.py, nodes.py and shadow_runtime.py directly
- strategist cycle/cache/fingerprint ownership is already clear
- runtime mode resolution is already clear

Do not re-inline these helpers during refactor.

## 18. Integrated Chain — Frozen Order

Current integrated-chain semantics and ordering must remain stable.

The current path includes combinations of:
- portfolio/open-order/readiness snapshots
- risk context
- Strategist cycle/cache reuse
- Scanner
- possible post-Scanner Strategist refresh
- Monitor
- Decision
- execute_from_packet path when approved
- Reporter/update-state hooks
- optional controlled mock lane
- fast-path variants

P1.5.7 must not dynamically reorder Agents.

No planner is introduced.

## 19. Graph Spine — Frozen

graphs/trading_graph.py remains the current custom graph-shaped runtime surface.

P1.5.7 does not:
- adopt LangGraph
- adopt pydantic-graph
- change retry semantics
- change graph-spine topology
- merge graph_spine and integrated_chain behavior

P1.6 will compare frameworks after P1.5 freeze.

## 20. Fast Paths — SAFETY-LOCK Behavior

Existing Commander fast paths include:
- monitor-only holding path
- session closeout guard
- pre-entry exit sweep
- forced closeout sell
- pending BUY cancellation
- controlled mock lanes

These paths may synthesize selected/intents/decision state before calling the execution chain.

They are high-risk structural surfaces.

P1.5.7 may move orchestration code but must preserve:
- activation conditions
- path names
- selected-symbol focus
- cancel/sell intent construction
- decision reasons
- execution call sequence
- reporting/update-state sequence
- shadow runtime fields
- return/short-circuit behavior

No “cleanup” of forced closeout/cancel flow without dedicated safety proof.

## 21. Execution Boundary — SAFETY-LOCK

Commander execution orchestration currently delegates to execute_from_packet.

The refactor must preserve:

decision eligible/approved
-> decision packet
-> execute_from_packet
-> Supervisor/guards/readiness
-> execution mutation owner
-> trade report/update state

P1.5.7 must not:
- call broker APIs directly
- instantiate broker executors inside new Commander modules
- reproduce Supervisor rules
- bypass execution readiness
- reorder mutation guards
- interpret ACCEPTED/UNKNOWN outcomes itself

Executor low-risk extraction belongs to P1.5.9.

## 22. Runtime Ownership Boundary — SAFETY-LOCK

The live-loop ownership store is above Commander cycle execution.

Target boundary:

live-loop/ownership gate
-> run_commander_runtime cycle
-> return
-> ownership heartbeat/next-tick gate

Commander must never:
- acquire/release another runtime lease
- decide stale takeover
- weaken recovery_required
- dispatch a second cycle after lost ownership

P1.5.7 tests must keep runtime ownership integration green even if no ownership code is modified.

## 23. Resilience Boundary — Frozen

Current Commander resilience behavior includes:
- ensure runtime resilience state
- retry/pause/cancel/resume transition semantics
- cooldown guard
- incident registration
- operator resume intervention
- degrade/runtime status evidence

P1.5.7 may extract these into lifecycle ownership.

It must not change:
- incident thresholds
- cooldown meaning
- fail-closed behavior
- transition names
- retry count semantics
- operator resume semantics

## 24. Private / Compatibility Test Seams

tests/test_m21_commander_runtime_entry.py directly imports private Commander internals including:

- _attach_commander_applied_policy
- _assess_open_position_commander_override
- _build_commander_decision
- _build_intraday_performance_circuit
- _ensure_market_context_clock_fields
- _intent_from_monitor_state
- _normalize_candidate_watch_proposal_for_commander
- _post_scanner_candidate_snapshot
- _resolve_commander_behavior_policy
- _run_integrated_chain
- _should_use_cached_strategist_from_commander_skip
- _should_use_session_closeout_fast_path
- _hydrate_strategist_output_cache
- resolve_runtime_mode
- resolve_runtime_phase
- _run_preopen_phase
- run_commander_runtime

Known monkeypatch targets include:
- graphs.commander_runtime._hydrate_monitor_symbol_features
- graphs.commander_runtime._build_commander_decision
- graphs.commander_runtime.run_controlled_mock_lane_path

Other tests import:
- _run_integrated_chain
- _compact_post_scanner_candidate_row
- run_commander_runtime

These seams must remain wrappers/re-exports until tests and consumers migrate.

Do not break them in an early tranche.

## 25. Focused Test Inventory

The Commander/runtime-focused and adjacent tests inspected for this design include at least 170 tests across suites such as:

- tests/test_m21_commander_runtime_entry.py — 84
- tests/test_p0d_runtime_ownership.py — 11
- tests/test_m21_graph_spine_parity.py — 2
- tests/test_runtime_mode_gate.py — 12
- tests/test_commander_contract.py — 4
- tests/test_commander_env_migration_phase1.py — 5
- tests/test_commander_env_migration_phase2.py — 5
- tests/test_commander_memory_policy.py — 8
- tests/test_commander_post_scanner_context.py — 1
- tests/test_reporter_commander_hooks.py — 3
- tests/test_m23_4_commander_incident_cooldown_routing.py — 3
- tests/test_m27_4_runtime_portfolio_guard_integration.py — 5
- tests/test_runtime_entrypoint_import_boundaries.py — 2
- tests/test_runtime_entrypoint_common.py — 5
- tests/test_m28_1_runtime_profile_scaffold.py — 7
- tests/test_m28_2_runtime_lifecycle_hooks.py — 5
- tests/test_m23_1_runtime_resilience_state_contract.py — 3
- tests/test_m23_2_runtime_circuit_breaker_core.py — 4
- tests/test_m21_runtime_once_script.py — 4

This excludes many execution, Step5, UEF, Docker, Monitor, Scanner and Reporter integration tests that are also affected by runtime routing.

These tests are migration assets.

## 26. Implementation Batches

Do not refactor 6,298 LOC in one commit.

### C1 — Contracts + characterization / state adapter shell

Add:
- CommanderRuntimeInput
- CommanderRuntimeResult
- CommanderRoutePlan
- compatibility state-patch characterization

Keep run_commander_runtime API unchanged.

Create golden fixtures for:
- runtime mode/phase
- path
- status
- CommanderDecision
- 46-key compatibility surface where present

No route movement yet.

### C2 — Policy composition extraction

Move:
- applied policy resolution
- behavior policy
- policy attachment/provenance
- reporter feedback policy composition

Keep private wrappers in graphs/commander_runtime.py.

Required parity:
- policy values
- source chain
- validation/fallback metadata
- env fallback behavior
- LLM profile routing

### C3 — Entry control + Commander decision builder

Move:
- candidate-watch control
- entry-control construction
- _build_commander_decision

Use output_frames.py for frame projection.

Required parity:
- CommanderDecision payload
- entry-control mode/reason/ranks
- memory/horizon/route policy fields

### C4 — Open-position control extraction

Move:
- carry state/recovery assessment
- open-position focus selection
- refresh context
- Commander open-position override

No Monitor/exit semantics change.

### C5 — Runtime lifecycle + reporter hooks

Move:
- clock projection
- runtime transitions
- cooldown/incident/operator-resume
- reporter hook dispatch
- Commander event payload preparation

Live-loop ownership remains outside this module.

### C6 — Phase routing

Extract:
- preopen
- closeout
- graph-spine
- decision-packet
- integrated-chain high-level dispatch

Use existing fast_paths.py and strategist_cycle.py.

Preserve exact path names and short-circuit returns.

### C7 — Fast-path / execution seam hardening

Do not rewrite fast-path behavior.

Make dependency seams explicit and characterize:
- monitor-only
- closeout guard
- pending BUY cancel
- forced closeout SELL
- pre-entry exit sweep
- controlled mock lane
- execute_from_packet call ordering

This is primarily boundary cleanup + regression protection.

### C8 — Evidence / artifact orchestration

Move:
- route/end/error event construction
- Commander artifact write coordination
- shadow artifact coordination
- absent-stage review evidence
- post-exit recap runtime evidence

No path/schema/failure-tolerance change.

### C9 — commander_runtime compatibility façade

Reduce graphs/commander_runtime.py to:
- public signature
- env-scope wrapper
- service invocation
- state adapter
- explicit compatibility aliases/private wrappers

Target no giant policy or decision implementation.

### C10 — staged test migration

Only after runtime parity.

Migrate tests gradually by owner:
- policy
- decision
- open-position
- lifecycle
- route
- fast path
- integration
- safety regressions

Do not bulk-move.

## 27. Target Test Architecture

Suggested eventual structure:

tests/unit/commander/
- test_contracts.py
- test_policy_composition.py
- test_entry_control.py
- test_decision_builder.py
- test_open_position_control.py
- test_lifecycle.py
- test_reporter_hooks.py
- test_state_adapter.py

tests/integration/commander/
- test_runtime_service.py
- test_integrated_chain.py
- test_graph_spine.py
- test_preopen.py
- test_closeout.py
- test_strategist_cache_cycle.py
- test_monitor_execution_seam.py
- test_portfolio_preflight.py

tests/regression/commander/
- test_monitor_only_fast_path.py
- test_closeout_guard_fast_path.py
- test_pending_buy_cancel.py
- test_forced_closeout_sell.py
- test_runtime_mode_gate.py
- test_resilience_routing.py
- historical incident regressions

tests/safety/runtime/
- ownership lease
- lost ownership
- Supervisor/execution boundary
- Step5/UEF mutation safety regressions

Historical milestone tests remain preserved until P1.5.8/P1.5.10 explicitly addresses naming/wrappers.

## 28. Behavior Locks

All remain SAME:

- runtime mode resolution
- runtime phase resolution
- runtime plan order
- graph-spine topology
- integrated-chain topology
- preopen behavior
- closeout behavior
- decision-packet behavior
- runtime transition semantics
- resilience/cooldown semantics
- operator resume semantics
- portfolio preflight behavior
- closeout fallback
- Strategist cache reuse
- Strategist refresh triggers
- post-Scanner refresh
- monitor-only routing
- session closeout routing
- pre-entry exit sweep
- Stage-4 carry review
- candidate-watch control
- entry-control behavior
- open-position override
- memory policy/bias
- horizon policy
- reporter integration
- model/execution profile routing
- controlled mock lane
- pending BUY cancellation
- forced closeout SELL
- decision packet construction
- execute_from_packet call ordering
- Supervisor/guard authority
- execution mutation ownership
- unknown outcome quarantine
- state compatibility keys
- Commander artifacts and shadow artifacts
- runtime ownership/CAS
- UEF semantics
- Step5C/Step5D semantics

## 29. Explicit Non-Goals

P1.5.7 must NOT:
- adopt LangGraph
- adopt pydantic-graph
- add planner/replanner
- dynamically reorder Agents
- add LLM Commander
- change route policy
- tune Scanner/Monitor
- change Strategist refresh policy
- change memory policy
- change runtime ownership
- change Supervisor rules
- change execution guards
- change broker mutation ordering
- change Step5C/Step5D
- change UEF
- rename milestone/runtime surfaces yet
- remove compatibility modes yet
- refactor execute_from_packet internals beyond seam-safe call boundaries

## 30. Forbidden Changes

Stop/report rather than improvise if extraction appears to require:

- runtime topology change
- route activation change
- direct broker mutation from Commander
- Supervisor bypass
- mutation guard reorder
- ownership lease semantic change
- retry/cooldown semantic change
- state contract break
- applied-policy meaning change
- new LLM decision point
- compatibility mode deletion
- fast-path forced SELL/CANCEL semantic change
- evidence path/schema change
- UEF or Step5 changes

## 31. Required Validation

Focused Commander/runtime suites must include:

- tests/test_m21_commander_runtime_entry.py
- tests/test_m21_graph_spine_parity.py
- tests/test_runtime_mode_gate.py
- tests/test_commander_contract.py
- tests/test_commander_env_migration_phase1.py
- tests/test_commander_env_migration_phase2.py
- tests/test_commander_memory_policy.py
- tests/test_commander_post_scanner_context.py
- tests/test_reporter_commander_hooks.py
- tests/test_m23_4_commander_incident_cooldown_routing.py
- tests/test_m27_4_runtime_portfolio_guard_integration.py
- tests/test_m23_1_runtime_resilience_state_contract.py
- tests/test_m23_2_runtime_circuit_breaker_core.py
- tests/test_runtime_entrypoint_import_boundaries.py
- tests/test_runtime_entrypoint_common.py
- tests/test_m21_runtime_once_script.py
- tests/test_m28_1_runtime_profile_scaffold.py
- tests/test_m28_2_runtime_lifecycle_hooks.py
- tests/test_p0d_runtime_ownership.py

Then:
- affected Strategist/Scanner/Monitor tests
- execution/Supervisor safety tests
- Step5 regression tests
- UEF replay
- full pytest
- Docker acceptance at the P1.5 integration gate

Acceptance:
- route parity SAME
- runtime path strings SAME
- 46-key compatibility semantics SAME
- Agent order SAME
- new LLM decision points 0
- Commander direct broker mutation NONE
- Supervisor bypass NONE
- runtime ownership semantics SAME
- production-write leakage NONE
- trading-authority leakage NONE
- UEF SAME
- Step5C/D SAME

## 32. Documentation

During implementation:
- update canonical Commander/runtime architecture documentation
- retain historical M21/M23/M28 docs/tests as history
- do not rename milestone artifacts until P1.5.8
- daily technical patch for each major tranche
- update UI/API canonical patch notes for meaningful changes
- verify every referenced source path

## 33. Implementation Gate

P1.5.7 runtime implementation starts only from the frozen P1.5 implementation baseline required by the master plan.

This design branch remains documentation/design only.

## 34. Design Verdict

Commander runtime inventory: COMPLETE
Canonical runtime identified: YES
6,298-line runtime mapped: YES
105 top-level functions mapped: YES
46-key compatibility write surface mapped: YES
existing Commander helper owners mapped: YES
graph-spine/integrated-chain/decision-packet modes frozen: YES
preopen/session/closeout phases frozen: YES
fast-path safety surfaces identified: YES
Supervisor/Executor boundary frozen: YES
runtime ownership/CAS boundary frozen: YES
private/monkeypatch seams mapped: YES
170+ focused/adjacent runtime tests inventoried: YES
Commander deterministic/no-LLM role frozen: YES
CommanderRuntimeInput/Result design frozen: YES
C1-C10 implementation sequence frozen: YES
Runtime implementation: NOT STARTED
