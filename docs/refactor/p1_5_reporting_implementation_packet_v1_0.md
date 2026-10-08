# P1.5 Reporting Implementation Packet v1.0

Status: **DESIGN COMPLETE / IMPLEMENTATION GATED**  
Date: 2026-10-07  
Design branch: `design/p1.5-p1.6-modernization`  
Implementation authorization: **NO — wait for P1.2/P1.3 frozen baseline**

## 1. Scope

This packet covers:

- P1.5.1 Reporting definite-dead-code cleanup
- P1.5.2 Reporting decomposition and corresponding test decomposition

Primary giant files:

| File | Current LOC | Top-level defs |
|---|---:|---:|
| `libs/reporting/trade_report_ai.py` | 8,354 | 180 |
| `libs/reporting/trade_report_markdown_clean.py` | 5,862 | 201 |
| `libs/reporting/trade_story_pipeline.py` | 4,527 | 82 |

Combined giant-file surface: **18,743 LOC**.

Reporter Agent itself is not the main problem; this packet targets the Reporting backend.

## 2. Structural Finding

Reporting has already undergone partial extraction. The repository already contains responsibility-specific helpers for deterministic report generation, compact LLM input, prompting, LLM execution, merge policy, truth surfaces, Scanner/Monitor rendering, symbol metadata, post-exit shadow, and trade-story hydration/assembly.

P1.5 must therefore **reuse and promote existing owners**, not create a parallel reporting framework.

## 3. Proven Definite Dead Code

### 3.1 `trade_report_ai.py`

`render_trade_summary_markdown_with_evaluation()` begins around line 7,216 and immediately delegates:

```python
from libs.reporting.trade_report_markdown_clean import (
    render_trade_summary_markdown_with_evaluation_clean
)
return render_trade_summary_markdown_with_evaluation_clean(report, summary_report)
```

Everything nested after that unconditional return through the end of the file is unreachable legacy implementation.

Approximate unreachable tail: **~1,100 LOC**.

P1.5.1 action:
- preserve the public wrapper
- delete only the unreachable nested implementation
- verify no source inspection/golden test depends on literal dead text

### 3.2 `trade_report_markdown_clean.py`

`_playbook_label` is defined twice:
- earlier definition around line 4,026
- later definition around line 4,257

The later top-level definition replaces the earlier binding at module load.

P1.5.1 action:
- retain the later, more complete implementation
- remove the earlier duplicate only after targeted tests confirm identical intended call behavior

## 4. Existing Owners — Reuse, Do Not Duplicate

### AI report generation

| Existing module | Current responsibility |
|---|---|
| `trade_report_ai_deterministic.py` | deterministic report assembly / fallback facts |
| `trade_report_ai_compact_input.py` | compact/sparse story input |
| `trade_report_ai_compact_helpers.py` | compact timeline/monitor helpers |
| `trade_report_ai_merge_policy.py` | fallback-vs-LLM merge policy |
| `trade_report_ai_prompting.py` | output template + prompt/repair message construction |
| `trade_report_ai_shared_facts.py` | canonical fact precedence |
| `trade_report_ai_summary_adapter.py` | summary evaluation normalization/messages |
| `trade_report_ai_llm.py` | LLM attempt execution |

### Markdown rendering

| Existing module | Current responsibility |
|---|---|
| `trade_report_markdown_truth.py` | price/PnL/truth/cost rendering helpers |
| `trade_report_markdown_scanner.py` | Scanner selection/comparison rendering |
| `trade_report_markdown_monitor.py` | Monitor/hold/exit rendering |
| `trade_report_markdown_strategy_memory.py` | strategy-horizon/memory rendering |
| `trade_report_symbol_metadata.py` | symbol name/theme metadata |
| `trade_report_post_exit_shadow.py` | post-exit shadow rendering |

### Trade story

| Existing module | Current responsibility |
|---|---|
| `trade_story_evidence.py` | evidence/provenance helpers |
| `trade_story_pipeline_evidence_hydration.py` | canonical artifact hydration |
| `trade_story_pipeline_human_payloads.py` | human payload/stop/execution rendering |
| `trade_story_pipeline_story_assembly.py` | timeline/warnings/lifecycle assembly |

## 5. Public / Test Compatibility Seams

### `tests/test_trade_report_ai.py`

This 6,204-line / ~130-test file imports the whole module as `mod` and directly exercises both public and private symbols.

Most coupled symbols include:

```text
render_trade_report_markdown                 31 refs
render_trade_summary_markdown                17
build_trade_summary_input                    13
build_deterministic_trade_report             13
build_ai_trade_report                        13
_build_shared_summary_seed                   13
_operatorize_report_text                      9
build_ai_trade_report_compact_input           8
_merge_trade_report_candidate                 6
_fallback_report                              5
_build_repair_messages                        5
_prefer_fallback_summary                      3
```

Additional private helpers are also directly tested.

Implication:
- `trade_report_ai.py` must remain a compatibility façade during P1.5.1/P1.5.2.
- moved implementations should be re-exported/wrapped before test imports are migrated.
- do not bulk-delete private wrappers in the same extraction commit.

### Trade-story seam

`tests/test_trade_story_pipeline_enrichment.py` directly imports public builders including:
- `build_trade_story_input`
- `build_trade_story_input_from_bundle`
- `build_lifecycle_bundle`
- `build_market_context_human`
- `build_scanner_reason_human`
- `build_monitor_reason_human`
- `build_filters_human`
- evidence enrichment helpers

These names remain stable façade exports.

### Markdown seam

`tests/test_trade_summary_symbol_metadata.py` directly imports:
- `_same_day_summary_from_texts`
- `render_trade_summary_markdown_with_evaluation_clean`
- `build_trade_summary_input_clean`
- `render_trade_summary_markdown_clean`

Preserve these names until test migration is complete.

### Live execution seam

`tests/test_live_execution_bundle_report.py` directly imports `build_deterministic_trade_report` and contains broad report-path monkeypatching. Treat this as an integration/regression seam, not a unit-test cleanup target.

## 6. Final Ownership Model

### 6.1 `trade_report_ai.py`

Final role:

```text
compatibility façade
+ high-level AI report service orchestration
+ public entry points
```

Target size after P1.5.2: **~300–600 LOC**, allowing temporary wrappers.

Move/delegate:

- deterministic construction -> existing `trade_report_ai_deterministic.py`
- compact input -> existing compact modules
- prompt/repair messages -> existing prompting module
- merge/fallback preference -> existing merge-policy module
- canonical fact precedence -> existing shared-facts module
- LLM attempt execution -> existing LLM module
- summary adapter -> existing summary-adapter module

New modules should be created only where no existing owner exists.

Candidate new owners:

```text
libs/reporting/trade_report/
  normalization.py
  operator_text.py
  sections.py
  service.py
```

Only create a file when the giant module still contains a coherent responsibility not already owned elsewhere.

### 6.2 `trade_report_markdown_clean.py`

Final role:

```text
public Markdown façade
+ final composition/order only
```

Reuse existing truth/scanner/monitor/memory/symbol/post-exit owners.

Candidate residual extraction:

```text
libs/reporting/trade_report_markdown/
  summary_input.py
  summary_render.py
  strategist.py
  memory.py        # only residual UI composition not already in strategy-memory module
  labels.py
```

Do not create duplicate Scanner/Monitor/truth modules.

Target façade size: **~300–500 LOC**.

### 6.3 `trade_story_pipeline.py`

Final role:

```text
public story-building façade
+ orchestration of canonical artifact hydration and section assembly
```

Candidate residual extraction:

```text
libs/reporting/trade_story/
  market_context.py
  scanner_reason.py
  monitor_reason.py
  filters.py
  lifecycle.py
  service.py
```

Reuse the four existing trade-story helper modules.

Target façade size: **~250–450 LOC**.

## 7. High-LOC Move Priorities

### `trade_report_ai.py`

Priority extraction/reduction:
- `_build_shared_summary_seed` ~693 LOC
- `_fallback_report` ~486
- `_operatorize_report_text` ~427
- `_compact_story_input_for_llm` ~385
- `build_ai_trade_report` ~321
- `_normalize_trade_report_output` ~241
- `build_trade_summary_report` ~210

First check whether each duplicates an existing helper owner before creating anything new.

### `trade_report_markdown_clean.py`

Priority:
- `render_trade_summary_markdown_clean` ~745
- `build_trade_summary_input_clean` ~416
- `_build_summary_exit_trigger_lines` ~179
- `_translate_text` ~170
- `_build_strategist_output_surface` ~162
- `_resolve_entry_signal_snapshot` ~155
- memory/strategist rendering clusters

### `trade_story_pipeline.py`

Priority:
- `build_trade_story_input` ~771
- `build_monitor_reason_human` ~697
- `enrich_scanner_reason_from_evidence` ~304
- `build_scanner_reason_human` ~257
- `enrich_filters_from_evidence` ~256
- `build_lifecycle_bundle` ~239
- `build_market_context_human` ~204

## 8. P1.5.1 — Dead-Code Cleanup Batch

Scope only:

1. remove unreachable body after the early return in `render_trade_summary_markdown_with_evaluation`
2. remove the shadowed earlier `_playbook_label` definition
3. no functional extraction
4. no rename
5. no output/schema change

Required tests:

```bash
pytest -q   tests/test_trade_report_ai.py   tests/test_trade_summary_symbol_metadata.py   tests/test_reporting_provenance_preference.py
```

Then affected reporting regression suite.

Expected result:
- large LOC reduction with zero behavior change
- simplest first proof of the P1.5 workflow

## 9. P1.5.2 — Structural Decomposition Batches

Do not perform all three giant files in one commit.

### R2-A — AI report façade

- promote existing helper modules
- move remaining coherent normalization/operator-text/section responsibilities
- preserve façade imports/wrappers
- split corresponding tests only after moves are green

### R2-B — Markdown façade

- extract summary input/composition
- reuse truth/scanner/monitor/memory/symbol owners
- retain public render functions

### R2-C — Trade-story façade

- extract market/scanner/monitor/filter/lifecycle clusters
- preserve story builder public APIs
- keep evidence hydration/assembly owners

Each R2 sub-batch must be independently revertible.

## 10. Test Architecture Target

Do not move all reporting tests at once.

Target eventual layout:

```text
tests/unit/reporting/trade_report/
  test_normalization.py
  test_shared_facts.py
  test_merge_policy.py
  test_fallback.py
  test_compact_input.py
  test_operator_text.py
  test_sections.py

tests/unit/reporting/markdown/
  test_summary_input.py
  test_truth.py
  test_scanner.py
  test_monitor.py
  test_strategist.py
  test_symbol_metadata.py

tests/unit/reporting/trade_story/
  test_market_context.py
  test_scanner_reason.py
  test_monitor_reason.py
  test_filters.py
  test_lifecycle.py
  test_evidence.py

tests/integration/reporting/
  test_ai_trade_report.py
  test_trade_summary.py
  test_trade_story.py

tests/regression/reporting/
  test_live_execution_bundle_report.py
  test_provenance_preference.py
```

Historical behavior/regression tests are preserved.

## 11. Behavior Locks

```text
report JSON schema                  SAME
Markdown section ordering           SAME
truth precedence                    SAME
broker truth preference             SAME
Scanner/Monitor attribution         SAME
Strategist explanation semantics    SAME
Reporter evaluation semantics       SAME
LLM call count                      SAME
LLM prompt semantics                SAME
fallback/repair semantics           SAME
artifact paths                      SAME
provenance fields                   SAME
trade lifecycle interpretation      SAME
```

## 12. Forbidden Changes

Stop/report rather than improvise if decomposition appears to require:

- changing report schema
- changing truth-source precedence
- changing trade status classification
- changing LLM prompt or model routing
- changing Reporter feedback meaning
- changing artifact paths
- deleting regression tests because they look redundant
- merging historical evidence semantics
- adding a new dependency

## 13. Documentation

During implementation:
- update canonical Reporting architecture documentation
- keep historical report-plan documents intact
- add daily technical patch for each major extraction tranche
- append matching UI/API patch-note entry
- ensure patch-note source paths exist

## 14. Implementation Gate

Do not start P1.5.1 code changes until:

```text
P1.2 FROZEN
P1.3 FROZEN
FULL BASELINE REGRESSION GREEN
PRODUCTION-WRITE LEAKAGE NONE
TRADING-AUTHORITY LEAKAGE NONE
BASELINE SHA/TAG RECORDED
```

## 15. Design Verdict

```text
Reporting inventory                 COMPLETE
Definite dead code                  PROVEN
Existing helper owners              MAPPED
Compatibility/test seams            MAPPED
Target ownership                    FROZEN
P1.5.1 batch                        READY
P1.5.2 batch structure              FROZEN
Runtime implementation              NOT STARTED
Next design target                  OPERATOR UI / OPERATOR BRIEF
```
