# 2026-10-07 — P1.5.6 Monitor Design Complete

## Scope

Design-only P1.5.6 repository analysis for Agentra.

No runtime code, entry/exit formula, scoring/shadow policy, candidate cascade, position sizing, exit guard, Supervisor/Executor authority, broker path, UEF contract, Step5C/Step5D behavior, or production topology was changed.

## Findings

- graphs/nodes/monitor_node.py is approximately 3,633 LOC with 14 top-level functions.
- monitor_node() itself is approximately 2,635 LOC.
- _evaluate_monitor_entry_candidate() is approximately 660 LOC.
- libs/runtime/intraday_monitor_signals.py is approximately 3,608 LOC and is a separate deterministic signal/policy/chart/scoring hotspot.
- Existing Monitor entry logic is already distributed across focused owners for candidate cascade, entry guards, cost filtering, policy context, quality, sizing, state, memory bias, minute OHLCV, Monitor policy and strategy frame.
- Existing Monitor exit logic is already strongly decomposed under libs/runtime/monitor_exit/.
- The Monitor compatibility state-write surface contains 27 directly assigned keys.
- The focused/adjacent Monitor test files inspected for this design contain at least 294 tests.

## Authority Freeze

The runtime authority boundary remains:

- Strategist owns strategy frame/policy intent.
- Scanner ranks/selects candidates; chart-fit remains soft ranking context.
- Monitor owns actionable entry/exit timing and emits at most one intent.
- Monitor does not execute orders.
- Supervisor remains approval/safety authority.
- Executor remains broker side-effect authority.

Thus Monitor hard decision ownership does not imply trading execution authority.

## Contract Freeze

Frozen new Agent-level design:
- MonitorAgentInput
- MonitorAgentResult
- run_monitor(input) -> MonitorAgentResult

monitor_node(state) remains the graph compatibility adapter until consumer migration.

## Frozen Implementation Order

MO1 contracts + state-adapter characterization
MO2 existing-owner completion
MO3 entry orchestration extraction
MO4 exit orchestration extraction
MO5 intent arbitration + state adapter
MO6 evidence / IO orchestration
MO7 intraday signal-engine decomposition
MO8 monitor_node façade + staged test migration

## Behavior Locks

P1.5.6 preserves:
- entry policy source precedence and policy interpretation
- shadow/scoring behavior
- hard filters, score formulas and threshold
- chart evidence
- candidate cascade / runner-up policy
- position sizing and cost filters
- cooldown/closeout/max-position/pending-order guards
- Rank-1 controlled probe
- exit price/freshness policy
- min-hold/sell-cooldown/confirmation behavior
- hard/emergency exit semantics
- stop/take-profit/trailing/peak-drawdown logic
- cost-aware exit floor
- overnight carry and EOD handling
- partial-exit semantics
- final BUY/SELL/NOOP arbitration
- at-most-one-intent rule
- all 27 compatibility state keys
- Monitor direct broker execution = NONE

## Deferred Work

Explicitly out of scope:
- promoting/tuning Monitor scoring
- reclaim/volume/breakout threshold changes
- new chart features
- candidate-cascade tuning
- Rank-1 probe tuning
- position-sizing tuning
- exit threshold tuning
- strategy alpha changes
- new LLM decisions

## Authority

See:
- docs/refactor/p1_5_monitor_implementation_packet_v1_0.md
- docs/refactor/p1_5_refactor_constitution.md
- docs/refactor/p1_5_p1_6_master_plan.md
- docs/roadmap/monitor_scoring_defer_note.md
- docs/roadmap/phase_5_3_policy_driven_monitor.md.txt
- docs/strategy_horizon_feedback/scanner_monitor_role_boundary_patch_plan_2026-05-11.md

## Status

P1.5.6 DESIGN: COMPLETE
RUNTIME IMPLEMENTATION: NOT STARTED
PATCH NOTE UPDATED: YES
