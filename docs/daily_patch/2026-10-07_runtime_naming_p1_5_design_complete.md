# 2026-10-07 — P1.5.8 Milestone / Runtime Naming Design Complete

## Scope

Design-only P1.5.8 repository analysis for Agentra.

No runtime code, import target, state key, environment variable, artifact path, runtime mode, execution safety, UEF, Step5C/Step5D behavior or production topology was changed.

## Findings

- Repository-tree inventory found approximately 468 milestone/phase/step-named file paths.
- Distribution:
  - docs: 217
  - tests: 140
  - scripts: 63
  - data: 15
  - deploy: 14
  - libs: 13
  - graphs: 6
- Most milestone names are historical evidence, tests, data or milestone tooling and must not be blindly renamed.
- Active runtime milestone naming is concentrated in:
  - M13 live-loop/tick/EOD runtime
  - M28 deployment/runtime entrypoints
  - M31 agent-chain probe
  - M13/M28/M31 state/env compatibility names
  - M25 notification/ops env names

## Canonical Runtime Mapping

Frozen canonical names include:
- m13_live_loop.py -> live_cycle.py
- run_m13_once -> run_live_cycle_once
- m13_tick.py -> runtime_tick.py
- run_m13_tick -> run_runtime_tick
- m13_eod_report.py -> eod_report.py
- run_m13_eod_report -> run_eod_report
- runtime entrypoint m13_live_loop.py -> live_loop.py
- script run_m13_live_loop.py -> run_live_loop.py
- m13_tick_pipeline -> runtime_tick_pipeline
- legacy_m10 canonical internal value -> legacy_decision_pipeline
- m10_live_pipeline compatibility implementation target -> legacy_decision_pipeline
- m31_agent_chain_probe -> agent_chain_probe

M28 runtime/deployment entrypoints receive responsibility-based canonical module names while old M28 modules remain wrappers.

## Compatibility Rules

- canonical state key read first, legacy fallback
- canonical env read first, legacy fallback
- canonical implementation owns logic
- old module/script remains a thin wrapper
- no wrapper deletion until P1.5.10 consumer proof

Known env migrations include:
- M13_LIVE_LOCK_* -> LIVE_LOOP_LOCK_*
- M28_LIFECYCLE_* -> RUNTIME_LIFECYCLE_*
- M31_MOCK_EXAM_SESSION_HARD_GATE -> MOCK_EXAM_SESSION_HARD_GATE
- M25_BATCH_* -> OPS_BATCH_*
- M25_NOTIFY_* -> NOTIFY_*

## No-Rename / Safety Rules

P1.5.8 preserves:
- historical milestone docs
- historical regression test names
- historical datasets
- serialized event kinds such as m25_ops_batch
- schema version strings such as phase5_validation_bundle.v1
- existing artifact/report/deploy paths unless separately migrated with compatibility proof
- Step5C/Step5D safety identifiers and implementation surfaces
- UEF-7/8/9
- Q10/Q12/Q100

Changing a lock path is explicitly treated as runtime-ownership risk and is not part of a cosmetic rename.

## Frozen Implementation Order

N1 naming manifest / characterization
N2 M13 live runtime canonicalization
N3 M28/M31 runtime/deployment tooling canonicalization
N4 config/state alias migration
N5 active consumer/import migration
N6 current documentation cleanup
N7 compatibility/naming regression freeze

Legacy-wrapper deletion belongs to P1.5.10.

## Test Inventory

At least 66 directly naming-sensitive tests were inspected, plus additional M13 lease/ownership/restart/shutdown and Commander/runtime safety regressions.

## Authority

See:
- docs/refactor/p1_5_runtime_naming_implementation_packet_v1_0.md
- docs/refactor/p1_5_refactor_constitution.md
- docs/refactor/p1_5_p1_6_master_plan.md
- docs/refactor/p1_5_documentation_refactor_plan.md

## Status

P1.5.8 DESIGN: COMPLETE
RUNTIME IMPLEMENTATION: NOT STARTED
PATCH NOTE UPDATED: YES
