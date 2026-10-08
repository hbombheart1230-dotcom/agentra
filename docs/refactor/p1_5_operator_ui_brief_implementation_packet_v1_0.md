# P1.5 Operator UI / Operator Brief Implementation Packet v1.0

Status: DESIGN COMPLETE / IMPLEMENTATION GATED
Date: 2026-10-07
Design branch: design/p1.5-p1.6-modernization

## 1. Scope

P1.5.3 covers Operator UI data-access decomposition, Operator Brief decomposition, operator-facing visibility/read-model cleanup, and corresponding test decomposition.

Primary current surfaces:

| File | Current LOC | Role |
|---|---:|---|
| apps/operator_ui/data_access_core.py | ~6,872 | mixed UI read model, run detail, Brief generation, LLM, persistence, rendering |
| libs/reporting/operator_period_summary.py | ~3,205 | period/daily/symbol truth aggregation + rendering + generation |
| libs/reporting/operator_visibility.py | ~1,848 | daily/run visibility projections + report generation |

The first implementation priority is data_access_core.py, especially the Operator Brief cluster. The reporting modules are later P1.5.3 tranches and must not be mixed into the first extraction commit.

## 2. Structural Finding

Operator UI is already part-way through decomposition.

Existing focused owners:
- apps/operator_ui/data_access.py: compatibility facade over data_access_core
- apps/operator_ui/data_access_brief.py: brief parsing, required-key completeness, retry classification
- apps/operator_ui/data_access_status.py: report/status labels, portfolio-sync projection, report diagnostics
- apps/operator_ui/data_access_runs.py: canonical run artifact loading and preference
- apps/operator_ui/data_access_reports.py: compatibility facade over reporting trade read model
- apps/operator_ui/data_access_linkage.py: canonical/legacy trade artifact path linkage
- libs/reporting/trade_read_model.py: normalized trade/report/brief read projections

data_access_core.py already delegates selected helpers into these modules, but retains most orchestration and nearly the entire Operator Brief service.

P1.5.3 therefore finishes the existing ownership migration. It must not create a second Operator UI framework.

## 3. Current Responsibility Map

KEEP/WRAPPER temporarily in data_access_core.py:
- OperatorUIConfig
- load_overview
- load_recent_trades_for_day
- summarize_trades_by_symbol
- build_overtrading_warning
- load_symbol_run_chain
- load_latest_strategist_prompt_summary
- load_recent_runs
- load_trade_report_detail
- load_operator_brief_detail
- load_run_detail
- load_strategy_memory_timeline
- load_health

Already-delegated wrappers prove the target direction:
- status helpers -> data_access_status.py
- portfolio sync -> data_access_status.py
- AI report diagnostics -> data_access_status.py
- canonical run source preference -> data_access_runs.py
- trade path linkage -> data_access_linkage.py
- trade-report/detail normalization -> libs.reporting.trade_read_model
- brief parsing/completeness/retry classification -> data_access_brief.py

MOVE the remaining Operator Brief cluster by responsibility:
1. canonical trade facts / truth precedence
2. per-agent Brief section assembly
3. payload normalization / schema compatibility
4. deterministic fallback text
5. compact LLM input construction
6. Korean language / internal-marker sanitation
7. prompt + JSON repair + line-repair construction
8. LLM execution / retry / attempt evidence
9. cache and source-signature validation
10. input/compact-input/brief/LLM-response persistence
11. trade-health / lifecycle-bundle mirror synchronization
12. Markdown rendering
13. high-level service orchestration

## 4. Operator Brief Contract Freeze

Required fields remain:
- headline
- commander_summary
- strategist_summary
- scanner_summary
- monitor_summary
- supervisor_summary
- executor_summary
- reporter_summary
- operator_takeaways

Optional compatibility fields remain:
- executive_summary
- scanner_reason
- entry_summary
- holding_summary
- exit_plan_summary
- risk_summary
- next_checkpoints

Current artifact version: 14.

P1.5.3 must not silently change required/optional meaning, schema interpretation, artifact-version acceptance, completeness scoring, canonical shared-fact precedence, cache invalidation/source signature, fallback behavior, Korean language policy, retry policy, LLM routing/call flow, or artifact paths.

## 5. Canonical Truth Boundary

_build_canonical_trade_brief_input() is a truth/read-model boundary, not template code.

It merges or normalizes trade story input, lifecycle, AI trade report, shared trade facts, Scanner rank/coverage, Monitor snapshot/thresholds, execution/guard facts, and market/news context. It also reuses Reporting shared-trade-fact precedence.

Target flow:

canonical artifacts -> Brief canonical read model -> deterministic sections/fallback, compact LLM input, Operator UI rendering

Templates or LLM output must never override canonical trade truth.

## 6. Target Ownership Model

Reuse existing modules first. Suggested ownership:

apps/operator_ui/
- data_access.py: stable legacy import facade
- data_access_core.py: temporary compatibility/orchestration facade
- data_access_status.py: existing
- data_access_runs.py: existing
- data_access_reports.py: existing
- data_access_linkage.py: existing
- data_access_brief.py: existing parsing/contract facade
- brief/canonical_input.py
- brief/sections.py
- brief/compact_input.py
- brief/sanitation.py
- brief/prompting.py
- brief/generation.py
- brief/persistence.py
- brief/rendering.py
- brief/service.py
- views/overview.py
- views/run_detail.py
- views/health.py

Filenames may be adjusted during implementation if dependency analysis produces a smaller coherent split. Responsibility boundaries are authoritative.

Final role rules:
- data_access.py keeps legacy imports stable.
- data_access_core.py becomes a small facade/orchestrator, not a giant embedded LLM/Markdown implementation.
- brief/service.py owns high-level generate/load/cache orchestration only.
- brief/generation.py owns LLM calls, retries, repair, salvage and attempt evidence, not artifact paths or truth precedence.
- brief/persistence.py owns paths, save/load/source-signature/cache validation and health/bundle mirrors.
- brief/canonical_input.py owns canonical truth projection with no LLM behavior.
- brief/sections.py owns deterministic per-agent section assembly.
- brief/rendering.py owns Markdown composition only.

## 7. Test and Compatibility Seams

tests/test_operator_ui.py is ~2,479 LOC with 52 tests and directly reaches private names through apps.operator_ui.data_access.

Important directly exercised seams:
- _build_canonical_trade_brief_input
- _build_operator_brief_input
- _build_operator_brief_sections
- _compact_operator_brief_input_for_llm
- _build_operator_brief_messages
- _fallback_operator_brief
- _sanitize_operator_brief_result
- _render_operator_brief_markdown
- _save_operator_brief_artifact
- _operator_brief_input_artifact_path
- _operator_brief_compact_input_artifact_path

Behavioral coverage includes canonical artifact preference, shared-fact precedence, route/monitor blockers, Scanner reasoning, Monitor exit metrics, artifact locations, health synchronization, saved-artifact reuse/invalidation, force regeneration, OpenRouter defaults, mixed-language repair, prompt-leak sanitation, fallback Korean readability, JSON repair, free-model line repair, attempt history, missing report linkage, and canonical run artifact preference.

tests/test_operator_ui_data_access_phase2.py is ~920 LOC with 28 tests and already proves the intended compatibility direction: data_access remains the facade while focused modules and trade_read_model own implementation.

These tests are migration assets, not cleanup noise.

## 8. P1.5.3 Implementation Batches

O1 — Existing-owner completion
- remove implementation duplication where focused modules already exist
- retain data_access_core wrappers
- no Brief algorithm move yet
- validate Phase-2 and focused Operator UI tests

O2 — Brief canonical read model + sections
- move canonical trade-brief input and deterministic per-agent sections
- keep original private wrapper names
- truth precedence and agent attribution must stay identical

O3 — Brief deterministic/fallback + LLM input
- move deterministic fallback, compact input, Korean labels, sanitation/language checks and prompt/repair/line message construction
- do not change prompt text, token budgets, retries or timeout policy

O4 — Brief LLM service + persistence/rendering
- move LLM execution, retry/repair/salvage flow, attempt evidence, cache/source signature, artifact persistence, health/bundle synchronization and Markdown rendering
- preserve artifact version 14 and all current paths

O5 — Operator UI page/read orchestration
- split overview, recent-runs, run-detail, health and memory-timeline responsibilities after Brief is green
- keep OperatorUIConfig and legacy imports stable

O6 — Operator visibility / period summary
- only after O1-O5 are independently green
- decompose operator_visibility.py into read/normalization, daily/run projection, rendering/generation, bundle orchestration
- decompose operator_period_summary.py into reconciliation, row normalization, aggregation, pattern performance, payloads, rendering and generation
- do not mix O6 with Brief LLM changes

## 9. Target Test Architecture

Migrate gradually toward:
- tests/unit/operator_ui/test_status.py
- tests/unit/operator_ui/test_linkage.py
- tests/unit/operator_ui/test_run_sources.py
- tests/unit/operator_ui/test_brief_canonical_input.py
- tests/unit/operator_ui/test_brief_sections.py
- tests/unit/operator_ui/test_brief_fallback.py
- tests/unit/operator_ui/test_brief_compact_input.py
- tests/unit/operator_ui/test_brief_sanitation.py
- tests/unit/operator_ui/test_brief_prompting.py
- tests/unit/operator_ui/test_brief_persistence.py
- tests/unit/operator_ui/test_brief_rendering.py
- tests/integration/operator_ui/test_overview.py
- tests/integration/operator_ui/test_run_detail.py
- tests/integration/operator_ui/test_operator_brief_service.py
- tests/regression/operator_ui/test_operator_brief_language_and_repair.py
- tests/regression/operator_ui/test_operator_brief_artifact_compatibility.py

Do not bulk-move all tests.

## 10. Behavior Locks

All remain SAME:
- FastAPI routes
- template-visible semantics
- Brief required keys
- Brief artifact version 14
- Brief JSON schema and section meaning
- canonical truth precedence and shared facts
- Scanner/Monitor/Strategist attribution
- portfolio-sync semantics
- AI report status semantics
- LLM role/call flow
- prompt/repair semantics
- free-model line salvage
- fallback semantics
- Korean sanitation policy
- cache/source-signature semantics
- artifact paths
- trade-health mirror semantics
- lifecycle-bundle linkage

## 11. Forbidden Changes

Stop/report rather than improvise if extraction appears to require changing Brief schema/version, required keys, truth-source precedence, lifecycle/report classification, prompt/model routing, retry/token/timeout policy, Korean language policy, artifact paths, cache semantics, trade-health/bundle meaning, adding dependencies, or touching strategy/runtime/execution/UEF semantics.

## 12. Size Guidance

After compatibility migration:
- data_access_core.py: roughly 300-700 LOC facade/orchestration
- individual Brief modules: preferably below 300-500 LOC
- brief/service.py: roughly 150-300 LOC
- brief/generation.py: roughly 250-450 LOC
- brief/rendering.py: roughly 250-500 LOC
- operator_visibility.py final facade/orchestrator: below roughly 400-600 LOC
- operator_period_summary.py final facade/orchestrator: below roughly 500-700 LOC

Responsibility wins over mechanical LOC targets.

## 13. Required Validation

Focused minimum:
- tests/test_operator_ui.py
- tests/test_operator_ui_data_access_phase2.py
- tests/test_run_operator_brief_batch.py
- tests/test_operator_visibility_reports.py
- tests/test_operator_summary_reports.py
- tests/test_operator_summary_broker_day_reconciliation.py
- tests/test_operator_summary_memory_linkage.py
- tests/test_operator_summary_refresh.py

Then affected integration/regression tests and full pytest.

Acceptance also requires:
- production-write leakage NONE
- trading-authority leakage NONE
- new LLM decision roles 0
- UEF semantics SAME
- Step5C/Step5D semantics SAME
- artifact-path drift NONE

## 14. Documentation

During implementation:
- update canonical Operator UI architecture docs
- keep historical milestone/incident docs unchanged
- add daily technical patches for major tranches
- append matching UI/API patch notes
- verify patch-note source paths exist

## 15. Implementation Gate

P1.5.3 runtime code changes begin only from the frozen implementation baseline required by the P1.5 master plan. This design branch remains documentation/design only.

## 16. Design Verdict

Operator UI inventory: COMPLETE
Operator Brief giant cluster: MAPPED
Existing focused owners: MAPPED
Canonical truth boundary: IDENTIFIED
Compatibility/private seams: MAPPED
Target ownership model: FROZEN
O1-O6 implementation order: FROZEN
Runtime implementation: NOT STARTED
