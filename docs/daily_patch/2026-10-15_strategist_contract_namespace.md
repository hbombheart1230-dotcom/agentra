# 2026-10-15 - Isolated Strategist Contract Namespace (P0)

## Scope

Added `libs/contracts/agents/strategist.py` as a behavior-preserving,
identity-preserving re-export of the current Strategist contract implementation
in `libs/strategies/contracts.py`. Added its package init, focused regression
tests and an incremental architecture note under `docs/refactor/`.

## Behavior / safety

- Observation and import-boundary change only. No existing import was changed.
- Strategy DTO definitions and the normalization function remain the same
  objects; there is no copied or competing schema.
- No policy, signal, order, approval, guard, broker, CAS, or runtime change.
- Claude T4 runtime files were not touched.

## Evidence / limits

Added `tests/test_strategist_contract_namespace.py` for identity, default
serialization, additive-field preservation, and legacy DTO compatibility.
A full repository test run and UI production build are still required before
merging this isolated branch.

## Rollback

Drop this branch / revert the additive namespace, tests and docs. No runtime
migration is necessary because existing callers use the original import path.
