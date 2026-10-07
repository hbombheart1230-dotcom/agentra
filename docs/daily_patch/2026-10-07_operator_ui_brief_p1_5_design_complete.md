# 2026-10-07 — P1.5.3 Operator UI / Operator Brief Design Complete

## Scope

Design-only P1.5.3 repository analysis for Agentra.

No runtime code, trading logic, broker path, UEF contract, Step5C/Step5D behavior, strategy semantics, or production topology was changed.

## Findings

- apps/operator_ui/data_access_core.py is approximately 6,872 LOC and still mixes UI read-model logic, run-detail construction, Operator Brief canonical truth projection, LLM generation, fallback, caching, persistence and Markdown rendering.
- Existing focused modules already prove the intended decomposition direction:
  - data_access_brief.py
  - data_access_status.py
  - data_access_runs.py
  - data_access_reports.py
  - data_access_linkage.py
  - libs/reporting/trade_read_model.py
- The Operator Brief required-field contract and artifact version 14 must remain behaviorally frozen during P1.5.3.
- tests/test_operator_ui.py contains 52 tests and directly exercises multiple private compatibility symbols through apps.operator_ui.data_access.
- tests/test_operator_ui_data_access_phase2.py contains 28 tests and explicitly verifies the existing compatibility-facade migration pattern.
- libs/reporting/operator_period_summary.py (~3,205 LOC) and libs/reporting/operator_visibility.py (~1,848 LOC) are later P1.5.3 decomposition tranches, not part of the first Brief extraction commit.

## Frozen Implementation Order

O1 existing-owner completion
O2 Brief canonical read model + deterministic sections
O3 Brief deterministic/fallback + compact/prompt/sanitation
O4 Brief LLM service + persistence/rendering
O5 Operator UI page/read orchestration
O6 operator visibility / period-summary decomposition

Each tranche must preserve public and private compatibility wrappers until consumers are migrated.

## Behavior Locks

The following remain unchanged:

- FastAPI routes and template-visible semantics
- Operator Brief required keys and artifact version
- canonical truth precedence and shared trade facts
- Scanner/Monitor/Strategist attribution
- portfolio-sync and report-status semantics
- LLM routing, prompt/repair meaning, retry flow and call roles
- Korean language/sanitation policy
- fallback semantics
- cache/source-signature behavior
- artifact paths
- trade-health and lifecycle-bundle linkage
- runtime/trading/UEF/Step5C/Step5D behavior

## Authority

See:
- docs/refactor/p1_5_operator_ui_brief_implementation_packet_v1_0.md
- docs/refactor/p1_5_refactor_constitution.md
- docs/refactor/p1_5_p1_6_master_plan.md

## Status

P1.5.3 DESIGN: COMPLETE
RUNTIME IMPLEMENTATION: NOT STARTED
PATCH NOTE UPDATED: YES
