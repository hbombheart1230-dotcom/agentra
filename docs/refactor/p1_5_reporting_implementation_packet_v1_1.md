# P1.5.2 Reporting Responsibility-Minimal Implementation Packet v1.1

Status: DESIGN REVISION / IMPLEMENTATION NOT AUTHORIZED BY THIS DOCUMENT
Date: 2026-10-08
Design base: design/p1.5-p1.6-modernization @ 920ebd045b0d894b7182c05f90d6997edec96cf4
Observed implementation: codex/p1.5.2-reporting-r2c-residual-20261008 @ fbfab9b3f56152f08a2ce50e69cc8173496fde7d
Supersedes: p1_5_reporting_implementation_packet_v1_0.md for *remaining P1.5.2 execution guidance only*.
Preserves: original v1.0 as historical approved PREP design, P1.5 master order, constitution, P1.2/P1.3 safety gate.

## 1. Why this revision exists

The original R2-A/R2-B/R2-C extraction plans were executed and each tranche recorded passing targeted regression. However, the three former giant modules still contain considerable compatibility and mixed responsibility surface. Treating the completed extraction batches as proof of full P1.5.2 ownership/test-architecture acceptance would be premature. Conversely, the façade LOC alone does not prove that an extracted responsibility has failed: many retained functions may be mandatory compatibility wrappers.

The next work must finish the **original responsibility-minimal design**, not invent a second parallel Reporting framework, casually repeat completed moves, or delete wrappers merely to hit a line count.

This revision is DESIGN ONLY. It changes no Reporting runtime Python, test expectations, broker calls, UEF outputs, or production configuration. No assertion is made here that the frozen implementation prerequisite is satisfied.

## 2. Current checked facts and baselines

| Surface | Original v1.0 inventory | Observed implementation HEAD | v1.0 façade guidance | Observed top-level defs |
|---|---:|---:|---:|---:|
| libs/reporting/trade_report_ai.py | 8,354 LOC | 3,040 LOC | 300–600 LOC | 182 |
| libs/reporting/trade_report_markdown_clean.py | 5,862 LOC | 3,044 LOC | 300–500 LOC | 209 |
| libs/reporting/trade_story_pipeline.py | 4,527 LOC | 949 LOC | 250–450 LOC | 45 |
| Combined | 18,743 LOC | 7,033 LOC | 850–1,550 LOC | 436 |

The counts are an inventory, not proof of dead/duplicated implementation. Current Reporting/trade-story CI was 337 passed with one pre-existing warning; the added seam/UI checks were 12 passed with one pre-existing warning (see 2026-10-08 R2-C daily patch). This is NOT a full-suite freeze, independent Claude audit, Docker acceptance or baseline-gate certification.

R2-A recorded COMPLETE after service/normalization/operator/section/context ownership moves.
R2-B recorded COMPLETE after summary/signals/memory/translation/diagnostics/strategy/truth moves.
R2-C recorded structural COMPLETE on its feature branch after human payload, evidence, assembly, news, scanner and provenance moves.
Those historical tranche outcomes remain valid. Remaining acceptance is evaluated separately.

## 3. Non-negotiable responsibility contract

**Public façade**: stable public import/export, thin top-level entry-point dispatch, explicitly documented compatibility seam and call-time test injection only where consumer proof requires it. No hidden canonical policy, fact precedence, LLM routing, report-formatting implementation, artifact hydration, evidence derivation or file IO in a façade.

**Implementation owners**: each normalizing/scoring/formatting/orchestration/hydration/evidence responsibility has ONE authoritative module. Prefer an existing owner. Do not introduce another module when an owner exists.

**Dependency direction**: façade -> focused owner -> lower-level pure/IO/evidence module. An owner may receive a typed/explicit dependency bundle from a façade at call time while legacy monkeypatch consumers exist, but must not import the façade at module import time or create cross-owner circular dependencies. Record and shrink injected symbol maps as consumers migrate.

**Public API**: preserve function names, import paths, outputs, exception/timeout semantics, prompt contents and invocation count. Private helper imports directly used by current tests/production are compatibility APIs until consumer migration evidence exists.

**Size guidance**: keep original façade targets 300–600 / 300–500 / 250–450 LOC. Constitution review threshold >=500, >=800 normally disallowed, >=1,000 target zero. These are review thresholds, not permission to delete behavioral seams. A remaining oversized façade must have a named, test-backed compatibility exception with consumers, owner, retirement condition and P1.5.10 handoff. Never mark a size exception as a size target PASS.

## 4. Existing single-owner map to preserve

| Area | Canonical owner / reuse first | Façade retained |
|---|---|---|
| AI report service | libs/reporting/trade_report/service.py | trade_report_ai.py |
| AI normalization | libs/reporting/trade_report/normalization.py | same |
| AI operator text | libs/reporting/trade_report/operator_text.py | same |
| AI section builders | libs/reporting/trade_report/sections.py | same |
| AI report context | libs/reporting/trade_report/context.py | same |
| AI compact/fallback | trade_report_ai_compact_input.py; trade_report_ai_deterministic.py | same |
| AI prompts/LLM/merge/facts | existing prompting, llm, merge_policy, shared_facts modules | same |
| Markdown summary composition | libs/reporting/trade_report/markdown_summary.py | trade_report_markdown_clean.py |
| Markdown signals | libs/reporting/trade_report/markdown_signals.py | same |
| Markdown translation | libs/reporting/trade_report/markdown_translation.py | same |
| Markdown diagnostics | libs/reporting/trade_report/markdown_diagnostics.py | same |
| Markdown strategy | libs/reporting/trade_report/markdown_strategy.py | same |
| Markdown truth/memory | trade_report_markdown_truth.py; trade_report_markdown_strategy_memory.py | same |
| Story human payload | trade_story_pipeline_human_payloads.py | trade_story_pipeline.py |
| Story canonical hydration | trade_story_pipeline_evidence_hydration.py | same |
| Story lifecycle/assembly | trade_story_pipeline_story_assembly.py | same |
| Story news/scanner/provenance | trade_story_pipeline_news.py; trade_story_pipeline_scanner.py; trade_story_pipeline_provenance.py | same |

These are observed ownership candidates and established extraction owners, not permission for another blind bulk move. Confirm exact source-to-owner correspondence before modifying any function.

## 5. Mandatory function-by-function ledger before implementation

Inventory EVERY remaining top-level function, class, imported alias and runtime monkeypatch seam in all three façades. For each row record:
- exact symbol, current file and line range, callers (production/tests), current owner or proposed owner
- classification KEEP, MOVE, WRAPPER, DEAD, SAFETY-LOCK
- responsibility tag (PUBLIC_DISPATCH, PURE_POLICY, NORMALIZATION, IO, EVIDENCE, FORMATTING, LLM, DEPENDENCY_ADAPTER, COMPATIBILITY)
- dependencies injected, import-cycle risk, side effects, source-of-truth/truth precedence
- compatibility removal eligibility, associated test fixture and consumer-migration proof
- planned diff batch, expected output invariants, disposition in P1.5.2 or evidence-backed deferral to P1.5.10

No deletion of names merely because they are private or short. No dynamic wildcard re-export, module __getattr__ indirection, arbitrary global rebinding or broad proxy magic to game LOC. If a test monkeypatches a façade symbol, its binding semantics must remain effective after the move until explicitly migrated.

## 6. Residual-review priorities by R2 track

### R2-A — AI report façade

Investigate the remaining strategist/report context functions (_extract_strategy_detail_from_source, _compact_entry_candidate_cascade, _compact_strategy_refresh_trace), report status/language helpers (_attach_report_status_matrix, _trade_report_language_meta), and dependency bundles (_section_builder_deps). Check actual call sites to decide whether their policies belong in the existing context, section, operator-text, normalization or service owners. Keep public service builders and mandatory monkeypatch wrappers, but do not preserve a second canonical implementation inside the façade.

### R2-B — Markdown façade

Investigate _resolve_prompt_proven_surface, _operatorize_strategist_output_text, _build_reporter_evaluation, _build_final_conclusion, and the numerous *_deps dependency maps. Prefer existing strategy-memory, markdown_strategy, markdown_diagnostics, markdown_summary, markdown_signals and truth owners. Preserve rendering order and exact operator-facing semantics. Do not duplicate Scanner, Monitor, truth, metadata or post-exit shadow owners.

### R2-C — Trade-story façade

Investigate _build_strategist_evidence_trace, normalized_feature_coverage, build_filters_human, build_operator_conclusion_human and render_bundle_markdown. Verify whether they are thin composition at the story entry boundary, or genuine content/evidence formatting owned by existing story human_payloads, scanner, provenance, hydration or assembly modules. All existing public story builders and bundle APIs must remain importable. Keep news/scanner/provenance arithmetic unchanged.

Each item above is an **audit candidate, not a pre-approved MOVE**. MOVE only when owner/caller graph and goldens justify it.

## 7. Work sequence (revised P1.5.2 completion, not a new feature track)

1. **Audit / classification gate** — pin implementation SHA; write the function/consumer ledger; map v1.0 target to completed R2-A/B/C extraction; identify true implementation residuals versus required wrappers; gather full baseline test inventory and known failures.
2. **AI ownership closure** — small revertible diffs, only proved MOVE/KEEP/WRAPPER decisions; keep public entry points; validate targeted tests and representative monkeypatch/fallback/LLM seams after every diff.
3. **Markdown ownership closure** — small revertible diffs for proven residual rendering/formatting responsibilities; preserve all Markdown/JSON section and truth invariants.
4. **Story ownership closure** — small revertible diffs for proven residual human/evidence/composition responsibilities; preserve story IDs, lifecycle and provenance.
5. **Test architecture migration** — split tests gradually into tests/unit/reporting/{trade_report,markdown,trade_story}/, tests/integration/reporting/ and tests/regression/reporting/. Preserve historic regression evidence; keep compatibility collection paths working while consumer migrations are verified.
6. **Closure acceptance** — focused + broad Reporting regressions, full pytest against accepted baseline with exact counts, deterministic snapshots, import compatibility, patch/consumer ledger, UI patch notes + canonical Reporting documentation, independent Claude audit (PASS / PASS_WITH_FINDINGS / FAIL), no production writes or trading authority leakage. Report any unresolved exceptions and do not label full P1.5.2 COMPLETE if these gates are unproven.

Do not conflate R2-A/B/C extraction COMPLETE with final P1.5.2 acceptance. P1.5.3 proceeds only after a documented gate decision; P1.5.10 remains the separately designed, proof-based terminal compatibility cleanup batch.

## 8. Test requirements and forbidden shortcuts

Minimum reuse: tests/test_trade_report_ai.py, tests/test_trade_summary_symbol_metadata.py, tests/test_reporting_provenance_preference.py, tests/test_trade_story_pipeline_enrichment.py, tests/test_live_execution_bundle_report.py, tests/test_trade_report_ai_separated_adapter.py, and the Reporting/API/runtime collection used in the existing 337-test CI matrix. Add focused owner-direct tests, wrapper import and monkeypatch tests, golden report JSON and Markdown snapshots, failure/retry/fallback/LLM-count cases, Scanner/Monitor attribution, provenance and canonical artifact precedence.

Before removing a compatibility wrapper: prove all direct imports and monkeypatch consumers migrated, then run both new tests and preserved legacy regression; otherwise mark WRAPPER with an explicit P1.5.10 handoff. Neither production consumers nor historic tests may be rewritten simply to suppress failing behavior.

Behavior must remain unchanged: report JSON/schema, Markdown ordering, truth preference, lifecycle meaning, Scanner/Monitor attribution, prompt/model/retry/LLM call count, artifacts, UEF, authority boundaries, Step5 safety and broker mutation path. No execution enablement, Docker restart, or new package dependency.

Use session-isolated test temp locations, clean PASS artifacts automatically, retain FAIL evidence under a bounded policy. Update docs/daily_patch and the UI-linked patch_notes.json + patch_notes.md for every implemented batch. Code review must audit owner->façade cycle, direct production-write paths and deterministic replay.

## 9. Acceptance ledger and release decision

| Gate | Proof required | Current v1.1 design-time verdict |
|---|---|---|
| R2-A/B/C high-LOC extraction | implementation tranche logs + CI | RECORDED COMPLETE |
| Single implementation owner per responsibility | classified symbol/consumer ledger + diff audit | NOT YET PROVEN |
| Façade sizes or justified P1.5.10 exceptions | LOC report + exact consumer-backed waiver | NOT YET PROVEN |
| Unit/integration/regression test responsibility split | collected target suites + no lost regression tests | NOT YET PROVEN |
| Full pytest baseline equivalence | baseline/candidate matched run, exact results | NOT YET PROVEN |
| Independent audit | Claude review + disposition | NOT YET PROVEN |
| P1.2/P1.3 implementation baseline gate | freeze SHA/tag, full regression, no authority/write leakage | REVALIDATE |
| Main integration/live deployment | independent later approval and integration | NOT PERFORMED |

Never backfill unproven gates as PASS. This packet changes implementation guidance, not safety gates or historical completed extraction evidence.

## 10. Source authority / branch handoff

Original immutable record: docs/refactor/p1_5_reporting_implementation_packet_v1_0.md.
This revised plan: docs/refactor/p1_5_reporting_implementation_packet_v1_1.md.
Constitution: docs/refactor/p1_5_refactor_constitution.md.
Master order: docs/refactor/p1_5_p1_6_master_plan.md.
Implementation evidence: docs/daily_patch/2026-10-07_p1_5_2_r2a_reporting_service_extraction.md; 2026-10-07_p1_5_2_r2b_markdown_decomposition.md; 2026-10-07_p1_5_2_r2c_trade_story_decomposition.md; 2026-10-08_p1_5_2_r2c_residual_owners.md on the cited implementation branches.

The design branch is documentation-only. Before implementing, port this reviewed v1.1 packet to the active implementation candidate without resetting its commit ancestry or merging the stale design-tree runtime. Confirm baseline freeze eligibility rather than assuming a historical design SHA is the implementation SHA.
