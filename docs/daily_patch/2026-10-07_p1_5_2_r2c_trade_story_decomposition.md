# 2026-10-07 — P1.5.2 R2-C Trade-story façade decomposition

## Summary
Started R2-C by moving the largest market/scanner/monitor human payload builders, scanner/filter evidence enrichment, lifecycle assembly, report section seeds, and final trade-story assembly out of `libs/reporting/trade_story_pipeline.py` while preserving the existing public APIs and helper seams.

## Structural changes

### Human payload owner
Expanded `libs/reporting/trade_story_pipeline_human_payloads.py`.

Moved implementations of:
- `build_market_context_human()`
- `build_scanner_reason_human()`
- `build_monitor_reason_human()`

The public functions remain in `trade_story_pipeline.py` as compatibility façades.

### Evidence enrichment owner
Expanded `libs/reporting/trade_story_pipeline_evidence_hydration.py`.

Moved:
- `enrich_scanner_reason_from_evidence()`
- `enrich_filters_from_evidence()`

Existing scanner-evidence helper seams remain injected through the façade.

### Story assembly owner
Expanded `libs/reporting/trade_story_pipeline_story_assembly.py`.

Moved:
- `build_lifecycle_bundle()`
- `build_report_section_seeds()`
- `build_trade_story_input()`

The public entry points remain in `trade_story_pipeline.py` and resolve current dependencies at call time, preserving monkeypatch and compatibility seams.

## Size movement

```text
R2-C baseline trade_story_pipeline.py          4,527 LOC
human payload extraction                      3,403 LOC
scanner/filter evidence extraction            2,880 LOC
lifecycle/story assembly extraction           1,873 LOC
-------------------------------------------------------
net façade reduction                          2,654 LOC (-58.6%)
```

## Validation

Focused trade-story validation after the human payload extraction:

```text
40 passed in 0.55s
```

Final broader Reporting + trade-story regression after evidence and story-assembly extraction:

```text
337 passed, 1 warning in 10.66s
```

The warning is the existing Starlette/httpx test-client deprecation warning.

## Incremental gate findings

The extraction gates caught two wiring-only mistakes before closure of this tranche:

1. Human-payload helpers such as `safe_int` were initially rebound with the wrong local names after the move. Exact historical helper names were restored.
2. Literal action labels `BUY/HOLD/WAIT` were initially mistaken for dependency symbols by the automated extraction pass. They were removed from the dependency map and remain local literals.

No test expectation, report field, trade classification, truth precedence, LLM behavior, UEF meaning, trading authority, or broker behavior was changed to make the tests pass.

## Behavior locks
Unchanged:
- story JSON schema
- lifecycle interpretation
- report section seeds and provenance
- Scanner / Monitor attribution
- Strategist explanation semantics
- evidence hydration precedence
- canonical artifact paths
- LLM role and call count
- Supervisor / Executor authority
- UEF and broker semantics

## R2-C status

```text
P1.5.2 R2-C                      ACTIVE / PARTIAL PASS
HUMAN PAYLOAD OWNER              PASS
SCANNER/FILTER EVIDENCE OWNER    PASS
LIFECYCLE / STORY ASSEMBLY       PASS
FOCUSED TRADE-STORY              40/40 PASS
BROADER REPORTING + TRADE-STORY  337/337 PASS
TRADE STORY FAÇADE               4,527 -> 1,873 LOC (-58.6%)
NEXT                             residual scanner/news/provenance helpers
```
