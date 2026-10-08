# 2026-10-07 — P1.5.10 Compatibility-Wrapper Cleanup Design Complete

## Scope

Design-only P1.5.10 repository analysis for Agentra.

No runtime code, wrapper deletion, state/env alias removal, runtime mode change, execution safety change, UEF change, Step5C/Step5D behavior change, or production topology change was made.

## Core Rule

P1.5.10 is proof-based compatibility cleanup.

A wrapper is removable only after active consumers are proven migrated across:
- Python imports
- runtime entrypoints
- tests
- CLI/scripts
- Docker/deploy/scheduler/service definitions
- operator UI/API
- current docs/runbooks
- state/env/schema compatibility
- safety replay

Historical files do not count as current production consumers, but historical regression tests may still justify keeping a compatibility path.

## Key Classifications

- libs/runtime/commander/integrated_chain_support.py:
  MIGRATE_THEN_REMOVE.
  graphs/commander_runtime.py still imports it today.

- apps/operator_ui/data_access.py:
  KEEP_STABLE_FACADE.
  It is an intentional application-layer public import and current tests import it directly.

- libs/reporting/trade_report_ai.py:
  KEEP_STABLE_FACADE through P1.5 freeze.

- libs/agent/strategist.py, libs/agent/scanner.py, libs/agent/monitor.py, libs/agent/commander.py:
  HISTORICAL_COMPATIBILITY.
  Review as one legacy Agent stack rather than deleting children independently.

- graphs/nodes/scan_candidates.py and select_candidate.py:
  HISTORICAL_COMPATIBILITY.
  tests/test_m11_2_scanner.py imports them directly.

- libs/agent/executor.py and libs/agent/executor/agent_executor.py:
  STRONG CLEANUP CANDIDATE.
  Two equivalent AgentExecutor implementations should converge on one canonical owner with a temporary re-export.

- graphs/nodes/execute_from_packet.py private Step5/UNKNOWN wrappers:
  SAFETY_LOCK.

- P1.5.8 M13/M28/M31 module/CLI aliases:
  MIGRATE_THEN_REMOVE after active consumer proof.

- state/env/path aliases:
  CONTRACT_ALIAS.
  More conservative than Python wrapper cleanup.

## Cleanup Philosophy

P1.5 success does not require zero wrappers.

Desired end state:
- one canonical implementation per responsibility
- no active production dependency on obsolete implementation
- stable public facades retained where useful
- historical provenance retained
- safety wrappers retained where cleanup risk exceeds maintenance value

## Frozen Implementation Order

CW1 compatibility inventory
CW2 canonical consumer migration
CW3 zero-consumer pure wrapper cleanup
CW4 historical/test-only review
CW5 config alias review
CW6 safety wrapper review
CW7 full compatibility regression

## Required New Manifest

Implementation must create:
- docs/refactor/p1_5_compatibility_inventory.md

Each compatibility seam records:
- canonical owner
- classification
- runtime/test/deploy/docs references
- cleanup action
- removal proof

## Safety

P1.5.10 does not change:
- runtime topology
- agent order
- LLM roles
- runtime modes
- Supervisor authority
- Executor guard order
- CAS/idempotency
- broker mutation ordering
- UEF semantics
- Step5C/Step5D semantics

## Authority

See:
- docs/refactor/p1_5_compatibility_wrapper_cleanup_implementation_packet_v1_0.md
- docs/refactor/p1_5_refactor_constitution.md
- docs/refactor/p1_5_p1_6_master_plan.md
- prior P1.5.4-P1.5.9 implementation packets

## Status

P1.5.10 DESIGN: COMPLETE
RUNTIME IMPLEMENTATION: NOT STARTED
PATCH NOTE UPDATED: YES
