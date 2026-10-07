# Agentra P1.5 / P1.6 Refactor Design

Status: DESIGN / PRE-IMPLEMENTATION  
Branch: `design/p1.5-p1.6-modernization`  
Base at creation: `b67934a5baa95f4d329ccf345c14ed591a126a0f`

This directory is the design authority for the Agentra structural refactor and orchestration modernization work.

## Documents

1. `p1_5_p1_6_master_plan.md`
   - overall roadmap
   - P1.2/P1.3 gates
   - P1.5/P1.6 scope
   - relation to 2.E6, Safety 5D/5E/6, Q100, Reporter v2, memory, self-improvement, paper experiments

2. `p1_5_refactor_constitution.md`
   - non-negotiable invariants
   - agent modularity
   - LLM boundaries
   - naming policy
   - test architecture
   - Codex Cloud / Claude Cloud workflow
   - compatibility and migration policy

3. `p1_5_strategist_decomposition.md`
   - Strategist detailed-design seed
   - current known hotspots
   - target responsibilities
   - required analysis before implementation
   - implementation-packet format

## Critical Gate

This branch is for design and preparation only.

Do **not** begin P1.5 runtime implementation until:
- P1.2 cross-day acceptance is frozen,
- P1.3 Docker/operational acceptance is frozen,
- required regression suite is green,
- production-write leakage is NONE,
- trading-authority leakage is NONE,
- a baseline SHA/tag is recorded.

The implementation branch must be cut from that frozen baseline, not automatically from this design branch.


4. `p1_5_documentation_refactor_plan.md`
   - documentation authority model
   - patch-note preservation rules
   - staged navigation/archive/link cleanup

5. `documentation_inventory.md`
   - current documentation size/inventory
   - patch-note source-of-truth map
   - migration risks and classification rules


6. `p1_5_strategist_implementation_packet_v0_1.md`
   - 156-function ownership inventory
   - compatibility/monkeypatch seams
   - target Strategist package tree
   - staged S1-S5 implementation plan
   - GPT-first implementation and Cloud escalation policy


6. `p1_5_strategist_implementation_packet_v0_1.md`
   - detailed Strategist discovery inventory and first ownership map

7. `p1_5_strategist_implementation_packet_v1_0.md`
   - finalized Strategist P1.5 design authority
   - AgentInput/Result boundary
   - 66-key state adapter compatibility surface
   - target package tree
   - compatibility seams
   - S1-S5 implementation sequence
   - pytest gates


6. `p1_5_reporting_implementation_packet_v1_0.md`
   - P1.5.1 definite dead-code cleanup
   - P1.5.2 Reporting decomposition
   - existing helper ownership, compatibility seams, test architecture, and gates

8. p1_5_operator_ui_brief_implementation_packet_v1_0.md
   - P1.5.3 Operator UI / Operator Brief decomposition authority
   - existing Phase-2 owner map and compatibility facade rules
   - canonical Brief truth boundary and artifact-version freeze
   - O1-O6 staged implementation sequence
   - private/public test seams and pytest gates

9. p1_5_scanner_implementation_packet_v1_0.md
   - P1.5.5 Scanner decomposition authority
   - canonical scanner_node inventory and legacy-wrapper classification
   - Scanner/Monitor soft-vs-hard authority freeze
   - ScannerAgentInput/ScannerAgentResult boundary and 21-key compatibility state surface
   - SC1-SC7 staged implementation sequence and pytest gates

10. p1_5_monitor_implementation_packet_v1_0.md
   - P1.5.6 Monitor decomposition authority
   - canonical monitor_node and intraday signal-engine inventory
   - intent-only / hard-timing authority freeze
   - MonitorAgentInput/MonitorAgentResult boundary and 27-key compatibility state surface
   - MO1-MO8 staged implementation sequence and pytest gates

11. p1_5_commander_runtime_implementation_packet_v1_0.md
   - P1.5.7 Commander/runtime decomposition authority
   - 6,298-line runtime inventory and existing owner map
   - deterministic/no-LLM Commander role freeze
   - runtime modes/phases, fast paths, Supervisor/Executor and ownership safety boundaries
   - CommanderRuntimeInput/Result design and C1-C10 staged implementation sequence

12. p1_5_runtime_naming_implementation_packet_v1_0.md
   - P1.5.8 milestone/runtime naming cleanup authority
   - repo-wide milestone-name inventory and classification policy
   - canonical M13/M28/M31 runtime mappings with compatibility wrappers
   - state/env alias migration rules and historical/contract/safety no-rename rules
   - N1-N7 staged implementation sequence and P1.5.10 wrapper-removal gates

13. p1_5_executor_low_risk_implementation_packet_v1_0.md
   - P1.5.9 Executor low-risk extraction authority
   - execute_from_packet safety inventory and exact guard/mutation ordering freeze
   - Supervisor/readiness/evidence/Step5C/BrokerOutcome/UNKNOWN quarantine safety locks
   - observability/artifact-only extraction targets
   - EX1-EX6 staged implementation sequence and safety regression gates

14. p1_5_compatibility_wrapper_cleanup_implementation_packet_v1_0.md
   - P1.5.10 compatibility-wrapper cleanup authority
   - proof-based REMOVE/MIGRATE/KEEP/HISTORICAL/SAFETY classification
   - cross-P1.5 wrapper inventory and consumer-proof manifest requirements
   - canonical-owner migration order with stable facade and safety exceptions
   - CW1-CW7 staged cleanup sequence and P1.5 freeze acceptance gates

15. p1_5_full_regression_docker_uef_freeze_implementation_packet_v1_0.md
   - P1.5.11 final regression / Docker / UEF replay / formal-freeze authority
   - candidate-SHA locking, layered acceptance gates and artifact-hygiene policy
   - UEF frozen-manifest, replay determinism, conservation/binding and cross-day rules
   - Docker source-parity, ownership, restart/recovery, SIGTERM and paper-read acceptance
   - FZ1-FZ9 freeze sequence, independent audit, human approval and freeze-manifest/tag policy

16. p1_5_prep_closure_report.md
   - formal P1.5 PREP / DESIGN closure authority
   - quantified giant-file inventory and façade shrink targets
   - before/after target package tree and Agent responsibility map
   - explicit separation of design-target LOC reduction vs actual runtime LOC reduction
   - implementation gate: runtime remains untouched until the upstream baseline is frozen

