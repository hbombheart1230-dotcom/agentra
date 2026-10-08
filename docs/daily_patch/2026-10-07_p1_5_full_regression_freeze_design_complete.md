# 2026-10-07 — P1.5.11 Full Regression / Docker / UEF Replay / Freeze Design Complete

## Scope

Design-only P1.5.11 final acceptance planning for Agentra.

No runtime code, test semantics, Docker configuration, UEF semantics, execution safety, runtime ownership, state schema, broker behavior, or production topology was changed.

## Final Acceptance Model

P1.5 freeze is layered and candidate-SHA-bound:

1. baseline/candidate identity + diff classification
2. subsystem targeted regression
3. full pytest + artifact hygiene
4. UEF frozen-manifest + deterministic replay
5. Step5 / authority / leakage acceptance
6. Docker source-parity / ownership / restart / SIGTERM / persistence acceptance
7. compatibility / docs / secrets acceptance
8. independent Claude audit
9. human approval + formal freeze tag

A green unit-test subset is not sufficient for formal freeze.

## UEF Rules

Freeze requires:
- scripts/verify_uef_freeze_manifest.py -> 0 mismatch
- UEF-7 candidate conservation
- UEF-8 N*(N-1)/2 pair conservation and unique IDs
- UEF-9 binding + authority_status=VALID
- deterministic replay over the same frozen input
- Daily UEF publication-safety tests

Known representative frozen replay:
- candidates 14
- pairs 91
- COMPARABLE 0
- CONDITIONAL 7
- NOT_COMPARABLE 84

These are fixture regression values, not universal live-day constants.

The 2026-10-06 Daily UEF freshness failure remains an upstream operational freshness incident and must not be "fixed" by weakening freshness or fabricating a canonical publication.

## Docker Rules

Use isolated mock Docker acceptance by default:
- EXECUTION_MODE=mock
- KIWOOM_MODE=mock
- EXECUTION_ENABLED=false
- ALLOW_REAL_EXECUTION=false
- isolated data/reports

Required:
- image/source parity
- startup + health
- exactly one runtime owner
- contender blocked
- restart/recovery
- bounded ownership wait
- SIGTERM/drain
- persistence
- no restart storm
- no OOM
- bounded resource/EOD smoke

Paper read-only acceptance is required if P1.5 touches RealExecutor/request/read-write gating; otherwise it may be recorded as NOT_RUN when no safe credential/window exists.

## Safety Freeze

Required invariants:
- LLM roles 2 -> 2
- Monitor direct broker execution NONE
- Commander direct broker mutation NONE
- Supervisor authority SAME
- execute_owned_order remains mutation choke point
- Step5B/C/D safety PASS
- readiness evidence ordering SAME
- CAS/idempotency SAME
- UNKNOWN quarantine SAME
- broker mutation ordering SAME
- production-write leakage NONE
- trading-authority leakage NONE

## Evidence

Implementation will produce bounded evidence including:
- docs/refactor/p1_5_freeze_report.md
- docs/refactor/p1_5_freeze_manifest.json
- docs/refactor/p1_5_compatibility_inventory.md
- daily formal-freeze patch note

Freeze tag recommendation:
- p1.5-structural-freeze-YYYYMMDD

The tag points to the accepted candidate SHA or to a documentation-only freeze commit whose parent is the accepted candidate.

## Human Gate

No automated agent self-declares the production freeze.

Required chain:
- Codex implementation
- GPT architecture review
- Claude independent audit
- human approval
- freeze tag

P1.6 remains blocked until P1_5_FORMAL_FREEZE=YES.

## Authority

See:
- docs/refactor/p1_5_full_regression_docker_uef_freeze_implementation_packet_v1_0.md
- docs/refactor/p1_5_refactor_constitution.md
- docs/refactor/p1_5_p1_6_master_plan.md
- docs/research/uef_freeze_manifest.md
- prior P1.5 implementation packets

## Status

P1.5.11 DESIGN: COMPLETE
P1.5 DESIGN PROGRAM: COMPLETE
RUNTIME IMPLEMENTATION: NOT STARTED
P1.5 FORMAL FREEZE: NOT YET
