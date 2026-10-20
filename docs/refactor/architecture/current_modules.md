> **PINNED MODULE SNAPSHOT (source f555165b) — HISTORICAL INVENTORY, NOT CURRENT IMPORT/CALLABLE PASS.** Verify current modules at exact active SHA before moving code. The [frozen V3 role target](TREE_V3_FROZEN.md), [D00](../../ENGINEERING_DELIVERY_POLICY.md) and [Issue #20](https://github.com/hbombheart1230-dotcom/agentra/issues/20) determine present task boundaries. This original table is preserved, not promoted to current source truth.

# Current modules — Agentra T4 + PR #5

Source SHA: f555165b1abcf64b03e9c370844611dabe40c949
State: GPT ARCHITECTURE_DRAFT / ARCH_CONVERGENCE_NOT_APPROVED
Scope: merged T4 + PR #5, no source changes or physical module relocation.

## Canonical entrypoints and adapters
| Role | Verified entry | Function-owner candidates and seams | Classification |
|---|---|---|---|
| Commander | graphs/nodes/commander_node.py → graphs/commander_runtime.py | libs/runtime/commander/; policy overlays; State/effects retained in facade | MOVE_WITH_ADAPTER after proof |
| Strategist | graphs/nodes/strategist_node.py | libs/runtime/strategist/context/, llm/, policy/, output/ | MOVE_WITH_ADAPTER after mock/real LLM evidence |
| Scanner | graphs/nodes/scanner_node.py | libs/runtime/scanner/candidate_selection.py, ranking_policy_overlay.py, output_payloads.py | MOVE_WITH_ADAPTER; single rank authority |
| Monitor | graphs/nodes/monitor_node.py | libs/runtime/monitor/ and libs/runtime/monitor_exit/ | MOVE_WITH_ADAPTER; preserve exit and State ordering |
| Reporter | graphs/nodes/reporter_node.py, libs/agent/reporter.py | libs/reporting/intraday_trade_reports.py, trade_report/, trade_story/, evaluation/ | SPLIT_REVIEW / artifact and queue SAFETY_LOCK |
| Supervisor | libs/risk/supervisor.py, libs/supervisor/two_phase.py | libs/supervisor/intent_state_store.py and approval layer | SAFETY_LOCK |
| Executor | graphs/nodes/execute_from_packet.py | libs/execution/guards/broker_mutation.py, executors/ | SAFETY_LOCK; M17 executor_node.py is a stub |

## Important verified legacy cases
- libs/agent/commander.py calls itself a legacy compatibility layer; canonical runtime is graphs/commander_runtime.py.
- libs/agent/strategist.py calls itself a legacy adapter. libs/agent/monitor.py is an explicit placeholder and remains for old tests/wiring.
- libs/agent/scanner.py still implements a concrete Scanner class: distinguish old adapter behavior from canonical Scanner rank authority before any consolidation.
- libs/agent/reporter.py has a real run_reporter_agent interface and must not be deleted as a supposed placeholder.
- apps/operator_ui/data_access_core.py has 3,102 lines after T4-D; _load_operator_brief is LLM-bound and explicitly SAFETY_LOCK.
- libs/reporting/intraday_trade_reports.py has 1,850 lines with queue/lock/IO concerns; file size alone does not authorize behavior relocation.
- graphs/nodes/execute_from_packet.py contains dynamic _import_* loaders, so static-import samples are incomplete.

## Shared and operational boundaries
- Canonical contracts and output objects: libs/contracts/; runtime I/O and analytics: libs/runtime/ and libs/reporting/; risk, approval and order execution remain separate locked authorities.
- apps/web and apps/api are UI and service entrypoints, not trading approval authority.
- Existing Scripts Work Orders 01–03 consolidated pure helpers into libs/diagnostics/; PR5 keeps all public CLI wrappers.
- Reporter and Research/Evaluation ownership overlaps structurally; do not assume every libs/reporting/ module belongs to one Reporter Agent.

## Post-architecture migration rule
Consumer list + dynamic import + injected symbol + State/effect/order + frozen BASE parity + Windows native proof must accompany each moved group. Absence of a static import is not proof of unused code.

Known unproven: REAL_BRIEF_PARITY_NOT_RUN, REAL_REPORT_PARITY_BLOCKED, T4-C Reporter-feedback displaced scenario, cross-seed telemetry and NTFS mtime.
