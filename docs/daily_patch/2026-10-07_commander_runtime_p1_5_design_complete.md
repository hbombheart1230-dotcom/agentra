# 2026-10-07 — P1.5.7 Commander / Runtime Design Complete

## Scope

Design-only P1.5.7 repository analysis for Agentra.

No runtime code, route topology, policy semantics, fast-path behavior, Supervisor/Executor authority, runtime ownership, UEF, Step5C/Step5D behavior, broker mutation ordering, or production topology was changed.

## Findings

- graphs/commander_runtime.py is approximately 6,298 LOC with 105 top-level functions.
- Direct compatibility assignments touch 46 state keys.
- Largest hotspots include:
  - _build_commander_decision (~859 LOC)
  - _resolve_commander_behavior_policy (~742 LOC)
  - _assess_open_position_commander_override (~439 LOC)
  - _attach_commander_applied_policy (~398 LOC)
  - _run_commander_runtime_impl (~300 LOC)
  - _build_commander_entry_control (~280 LOC)
- Existing focused owners already exist under libs/runtime/commander/ for runtime modes, environment compatibility defaults, route/report policy, Strategist cache/fingerprint/refresh, integrated-chain nodes, fast paths, execution bridge and shadow runtime.
- graphs/trading_graph.py remains the current custom graph-spine surface; P1.5 does not adopt LangGraph.
- Runtime ownership/CAS lives above Commander cycle execution and remains an external SAFETY-LOCK dependency.
- execute_from_packet remains the Supervisor/guard/execution-mutation authority boundary.

## Role Freeze

Commander remains deterministic orchestration/policy only.

LLM decision roles remain:
- Strategist: ALLOWED
- Reporter: ALLOWED
- Commander: NOT ALLOWED
- Scanner/Monitor/Supervisor/Executor: deterministic

## Runtime Boundary

Frozen design contracts:
- CommanderRuntimeInput
- CommanderRuntimeResult
- CommanderRoutePlan
- CommanderDecision

Target internal core:
- run_commander_cycle(input) -> CommanderRuntimeResult

Public compatibility surface remains:
- run_commander_runtime(state, ...) -> state

## Safety Locks

P1.5.7 must preserve:
- graph_spine / decision_packet / integrated_chain mode behavior
- preopen / session / closeout phase behavior
- runtime agent order
- monitor-only / closeout / pre-entry-sweep fast paths
- forced closeout SELL and pending BUY cancellation semantics
- Strategist cache/refresh behavior
- Commander policy ownership
- resilience/cooldown/operator-resume semantics
- runtime ownership/CAS behavior
- execute_from_packet Supervisor/guard ordering
- broker mutation ordering
- UEF and Step5C/Step5D semantics

## Frozen Implementation Order

C1 contracts + characterization/state adapter
C2 policy composition extraction
C3 entry control + Commander decision builder
C4 open-position control extraction
C5 lifecycle + reporter hooks
C6 phase routing
C7 fast-path/execution seam hardening
C8 evidence/artifact orchestration
C9 commander_runtime compatibility façade
C10 staged test migration

## Test Inventory

At least 170 focused/adjacent Commander/runtime tests were inventoried during this design, including the 84-test test_m21_commander_runtime_entry.py suite plus runtime mode, graph parity, ownership, resilience, env migration, memory, portfolio-preflight, reporter-hook and lifecycle suites.

## Authority

See:
- docs/refactor/p1_5_commander_runtime_implementation_packet_v1_0.md
- docs/refactor/p1_5_refactor_constitution.md
- docs/refactor/p1_5_p1_6_master_plan.md
- libs/runtime/commander/
- graphs/commander_runtime.py
- graphs/trading_graph.py

## Status

P1.5.7 DESIGN: COMPLETE
RUNTIME IMPLEMENTATION: NOT STARTED
PATCH NOTE UPDATED: YES
