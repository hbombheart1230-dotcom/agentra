# 2026-10-07 — P1.5.2 R2-C Trade-story façade decomposition

## Summary

Completed the final Reporting structural sub-batch by moving market/scanner/monitor human payload construction, scanner/filter evidence enrichment, lifecycle/report-section assembly, main story-input assembly, and residual scanner evidence helpers out of `libs/reporting/trade_story_pipeline.py`.

The existing public functions remain compatibility façades. Evidence hydration and story assembly owners were extended rather than replaced.

## Structural changes

### Human payload owner

Extended `libs/reporting/trade_story_pipeline_human_payloads.py` to own:

- `build_market_context_human()`
- `build_scanner_reason_human()`
- `build_monitor_reason_human()`
- `build_filters_human()`

The first focused gate exposed an extraction-only helper-name wiring error: shared helpers such as `safe_int`, `safe_float`, and `format_pct` were initially rebound with underscore-prefixed local names while the moved bodies still referenced their historical global names. The aliases were corrected without changing behavior.

### Evidence hydration / enrichment owner

Extended `libs/reporting/trade_story_pipeline_evidence_hydration.py` to own:

- `enrich_scanner_reason_from_evidence()`
- `enrich_filters_from_evidence()`
- scanner selection trace assembly
- news/scanner contribution trace assembly
- news/scanner contribution attachment
- normalized scanner feature-coverage extraction

Evidence semantics and scanner/monitor attribution were preserved.

### Story assembly owner

Extended `libs/reporting/trade_story_pipeline_story_assembly.py` to own:

- `build_lifecycle_bundle()`
- `build_report_section_seeds()`
- `build_trade_story_input()`

The public `trade_story_pipeline.py` entry points remain in place and inject the existing helper/authority seams at call time.

## Size movement

```text
R2-C baseline trade_story_pipeline.py       4,527 LOC
human payload extraction                    3,403 LOC
evidence enrichment extraction              2,883 LOC
story assembly extraction                   1,884 LOC
residual scanner/filter extraction          1,552 LOC
----------------------------------------------------
net façade reduction                        2,975 LOC (-65.7%)
```

At R2-C closure, no function remaining in `trade_story_pipeline.py` is 70 LOC or larger.

## Verification

Focused Python 3.12 trade-story regression:

```text
tests/test_trade_story_pipeline_enrichment.py
tests/test_phase3_lifecycle_bundle.py

40 passed
```

The focused gate was rerun after each major extraction tranche.

Final broader Reporting + trade-story regression:

```text
337 passed, 1 warning in 8.14s
```

The single warning is the existing Starlette/httpx test-client deprecation warning.

## Behavior locks

Unchanged:

- report JSON schema
- Markdown contract
- truth-source precedence
- broker truth preference
- Scanner/Monitor attribution
- Strategist explanation semantics
- Reporter evaluation semantics
- evidence provenance fields
- lifecycle interpretation
- LLM role / call count
- fallback / repair semantics
- artifact paths
- Supervisor / Executor authority
- UEF semantics
- broker mutation behavior

## P1.5.2 verdict

```text
P1.5.1 DEAD-CODE CLEANUP              COMPLETE
P1.5.2 R2-A AI REPORT FAÇADE         COMPLETE
P1.5.2 R2-B MARKDOWN FAÇADE          COMPLETE
P1.5.2 R2-C TRADE-STORY FAÇADE       COMPLETE
P1.5.2 REPORTING DECOMPOSITION        COMPLETE

trade_report_ai.py                    7,223 -> 3,040 LOC
trade_report_markdown_clean.py        5,852 -> 3,044 LOC
trade_story_pipeline.py               4,527 -> 1,552 LOC

FINAL BROADER REGRESSION               337/337 PASS
TRADING SEMANTICS                      PRESERVED
AUTHORITY BOUNDARIES                   PRESERVED
NEXT                                   P1.5.3 Operator UI / Operator Brief
```
