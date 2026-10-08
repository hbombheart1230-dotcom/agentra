# 2026-10-07 — P1.5.9 Executor Low-Risk Extraction Design Complete

## Scope

Design-only P1.5.9 repository analysis for Agentra.

No runtime code, guard order, Supervisor behavior, execution readiness, readiness evidence, Step5C ownership, broker mutation ordering, BrokerOutcome classification, quarantine, recovery, UEF, or Step5D behavior was changed.

## Findings

- graphs/nodes/execute_from_packet.py is approximately 4,190 LOC with 101 top-level functions.
- execute_from_packet() itself is approximately 1,192 LOC.
- The execution monolith already delegates critical ownership to focused modules:
  - execution_readiness.py
  - readiness_evidence.py
  - intent_admission.py
  - intent_identity.py
  - intent_execution_owner.py
  - broker_mutation.py
  - unknown_quarantine.py
  - recent_order_guard.py
  - order_lifecycle_policy.py
  - RealExecutor / MockExecutor
- The focused execution/safety tests inspected for this design contain at least 267 tests.

## Safety Freeze

The exact main-path ordering is frozen from readiness/guards through Supervisor, pre-admission evidence, intent admission, physical-order claim, intent CAS, broker dispatch, BrokerOutcome normalization, UNKNOWN quarantine and recovery.

P1.5.9 explicitly does NOT move:
- guard implementations or guard sequence
- _prepare_request
- order construction
- execution-mode semantics
- Supervisor invocation/context
- BrokerOutcome normalization
- readiness evidence
- execute_owned_order / Step5C claim order
- UNKNOWN quarantine
- recent-order persistence
- upper-limit cancel / unfilled recovery
- exception-phase NOT_SENT vs UNKNOWN semantics

## Low-Risk Extraction

Only low-risk responsibilities are approved for extraction:

1. executor observability projection
   - execution observability aliases
   - Supervisor/Executor decision-trace projection

2. canonical execution artifact coordination
   - Supervisor artifact
   - Executor artifact
   - artifact-only quote/guard enrichment
   - best-effort failure behavior

3. optional pure order-view helpers
   - simple symbol/qty/exit projections only

The execution facade may remain large after P1.5.9. Safety auditability has priority over LOC targets.

## Frozen Implementation Order

EX1 characterization / safety freeze
EX2 observability projection extraction
EX3 artifact coordination extraction
EX4 optional pure order-view helper extraction
EX5 compatibility/import stabilization
EX6 full safety regression

Compatibility-wrapper deletion remains P1.5.10 work.

## Authority

See:
- docs/refactor/p1_5_executor_low_risk_implementation_packet_v1_0.md
- docs/refactor/p1_5_refactor_constitution.md
- docs/refactor/p1_5_p1_6_master_plan.md
- libs/execution/intent_execution_owner.py
- libs/execution/readiness_evidence.py

## Status

P1.5.9 DESIGN: COMPLETE
RUNTIME IMPLEMENTATION: NOT STARTED
PATCH NOTE UPDATED: YES
