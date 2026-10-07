# 2026-10-07 — P1.5.5 Scanner Design Complete

## Scope

Design-only P1.5.5 repository analysis for Agentra.

No runtime code, ranking logic, candidate-source behavior, Monitor authority, trading semantics, broker path, UEF contract, Step5C/Step5D behavior, or production topology was changed.

## Findings

- graphs/nodes/scanner_node.py is approximately 4,179 LOC with 61 top-level functions/classes.
- scanner_node() itself is approximately 1,945 LOC and is the primary decomposition hotspot.
- The Scanner already has focused owners for candidate selection, theme filtering, practical filters, market-representative guard, candidate risk, output snapshots/payloads, feature hydration, Scanner policy, Scanner bias and memory bias.
- libs/agent/scanner.py is explicitly a legacy adapter and must not silently become the new canonical Scanner authority.
- graphs/nodes/scan_candidates.py is an explicit compatibility candidate-stage helper; graphs/nodes/select_candidate.py is a historical minimal selector.
- The current Scanner compatibility state-write surface contains 21 observable keys, including selected, top_stock, ranked_candidates, scan_results, scanner_output and risk.
- At least 113 Scanner-specific/adjacent tests were inspected for this design, including direct private imports and monkeypatch seams.

## Authority Freeze

The existing role boundary remains authoritative:

- Strategist defines the strategy frame.
- Scanner ranks/selects the candidate worth Monitor attention.
- Scanner chart-fit and Monitor-readiness signals remain soft ranking context.
- Monitor remains the actionable entry/exit hard gate.
- Commander/Supervisor/Executor authority remains unchanged.

P1.5.5 does not tune weights, thresholds, candidate sources, chart-fit formulas, market-representative guard, blocker-family overlay, selection-veto semantics, or rank/tie-break behavior.

## New Component Boundary

Frozen design contracts:
- ScannerAgentInput
- ScannerAgentResult

Target standalone surface:
- run_scanner(input) -> ScannerAgentResult

scanner_node(state) remains a compatibility graph adapter that builds the Agent input, calls the component, and applies the compatibility state patch.

## Frozen Implementation Order

SC1 contracts + state-adapter shell
SC2 existing-owner completion
SC3 guidance + repeat/prior extraction
SC4 compatibility/chart-fit extraction
SC5 deterministic scoring service
SC6 evidence / IO orchestration
SC7 scanner_node façade + test migration

## Deferred Work

Known tuning ideas remain explicitly out of scope, including trading_value vs volume_surge reweighting, defensive-playbook liquidity tuning, new candidate sources, new chart features, broader selection veto, and Monitor threshold changes.

## Authority

See:
- docs/refactor/p1_5_scanner_implementation_packet_v1_0.md
- docs/refactor/p1_5_refactor_constitution.md
- docs/refactor/p1_5_p1_6_master_plan.md
- docs/strategy_horizon_feedback/scanner_monitor_role_boundary_patch_plan_2026-05-11.md
- docs/strategy_horizon_feedback/scanner_monitor_chart_reading_runtime_alignment_2026-05-12.md

## Status

P1.5.5 DESIGN: COMPLETE
RUNTIME IMPLEMENTATION: NOT STARTED
PATCH NOTE UPDATED: YES
