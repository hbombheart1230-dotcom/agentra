# 2026-10-07 — P1.5.2 R2-A Reporting service extraction

## Summary
Started P1.5.2 Reporting decomposition with a behavior-preserving extraction of LLM service orchestration from the giant `libs/reporting/trade_report_ai.py` façade.

## Structural changes
- Added `libs/reporting/trade_report/` as the responsibility-specific implementation package.
- Added `libs/reporting/trade_report/service.py`.
- Moved the implementation bodies of:
  - `build_ai_trade_report()`
  - `build_trade_summary_report()`
  into the service owner.
- Kept the existing public functions in `trade_report_ai.py` as compatibility façades.
- The façade passes its current helper functions and `LLMRouter` into the service at call time so existing tests/monkeypatch seams remain valid.

## Size movement
- `libs/reporting/trade_report_ai.py`: 7,223 -> 6,770 LOC from the P1.5.1 baseline.
- Net façade reduction in this tranche: 453 lines.
- New service owner: 575 LOC.
- No public import path was removed.

## Behavior locks
Unchanged:
- report JSON schema
- Markdown/report section ordering
- truth-source precedence
- LLM call count and roles
- model selection and execution-profile behavior
- retry / repair / timeout semantics
- fallback and merge semantics
- artifact paths
- Supervisor / Executor authority
- trading / UEF / broker behavior

## Verification
Python 3.12 validation:
```text
tests/test_trade_report_ai.py
tests/test_trade_summary_symbol_metadata.py
tests/test_reporting_provenance_preference.py
tests/test_trade_report_ai_separated_adapter.py

151 passed in 1.93s
```

An earlier checkpoint after the first service move also passed the same 151-test selection.

## Scope verdict
```text
P1.5.2 R2-A SERVICE EXTRACTION   PASS
PUBLIC API                       PRESERVED
MONKEYPATCH/TEST SEAMS           PRESERVED
NEW LLM DECISION POINTS          0
TRADING SEMANTICS                SAME
AUTHORITY CHANGES                NONE
NEXT                             Continue R2-A residual normalization/operator-text/section extraction
```

## R2-A residual extraction update

The same R2-A branch continued with three additional behavior-preserving ownership moves:

- `libs/reporting/trade_report/normalization.py`
  - owns the implementation of `_normalize_trade_report_output()`
  - façade wrapper retained
- `libs/reporting/trade_report/operator_text.py`
  - owns operator labels, language normalization, operator-facing text normalization and section operatorization
  - historical logger identity for invalid-regex diagnostics preserved as `libs.reporting.trade_report_ai`
  - façade private wrappers retained for existing callers/tests
- `libs/reporting/trade_report/sections.py`
  - owns the 693-line `_build_shared_summary_seed()` implementation
  - existing helper seams are injected by the façade at call time

### Updated size movement

```text
P1.5.1 baseline trade_report_ai.py   7,223 LOC
service extraction                   6,770 LOC
normalization extraction             6,559 LOC
operator-text extraction             5,827 LOC
shared-section-seed extraction       5,156 LOC
---------------------------------------------
net façade reduction                 2,067 LOC
```

### Additional verification

Each checkpoint ran the same Python 3.12 focused Reporting selection and passed:

```text
normalization extraction     151 passed
operator-text extraction     151 passed
shared-section extraction    151 passed
```

No test expectations were weakened or removed. No runtime topology, report schema, truth precedence, LLM role/count, retry/repair behavior, artifact path, UEF, Supervisor/Executor authority or broker mutation semantics changed.

### Updated next step

R2-A is still active. The next residual targets are the compact-input/fallback/remaining section clusters; R2-B Markdown façade decomposition starts only after the R2-A residual ownership is sufficiently reduced and regression remains green.

## R2-A compact-input / deterministic fallback update

Two further behavior-preserving moves completed the next planned R2-A residual tranche:

- `libs/reporting/trade_report_ai_compact_input.py`
  - now owns the 385-line `_compact_story_input_for_llm()` implementation
  - `trade_report_ai.py` retains the private compatibility wrapper
  - all current helper seams are injected from the façade at call time
- `libs/reporting/trade_report_ai_deterministic.py`
  - now owns the 486-line deterministic `_fallback_report()` implementation
  - fallback section ordering, shared facts, truth/memory surfaces and operator-facing output paths remain unchanged
  - the façade retains `_fallback_report()` and injects the existing helper seams

### Updated façade size

```text
P1.5.1 baseline trade_report_ai.py        7,223 LOC
service extraction                        6,770 LOC
normalization extraction                  6,559 LOC
operator-text extraction                  5,827 LOC
shared-section-seed extraction            5,156 LOC
compact-input + fallback extraction       4,376 LOC
--------------------------------------------------
net façade reduction                      2,847 LOC
```

### Verification

Python 3.12 focused Reporting regression after the combined compact/fallback tranche:

```text
151 passed in 2.08s
```

No expected values were weakened and no tests were removed. No report JSON/Markdown contract, truth precedence, deterministic fallback meaning, LLM call role/count, retry/repair behavior, artifact path, Supervisor/Executor authority, UEF meaning, or broker mutation path changed.

R2-A remains active only for smaller residual section-builder ownership cleanup; the major orchestration/normalization/operator/shared-seed/compact/fallback responsibilities are now outside the giant façade.

## R2-A final section/context extraction and completion

The final R2-A residual pass moved the remaining large section/context responsibilities out of the façade:

- `libs/reporting/trade_report/sections.py`
  - market-context summary/bullets
  - strategist summary section
  - market↔scanner linkage
  - scanner choice summary/bullets/comparison
  - entry decision summary/bullets and entry-detail resolution
  - holding-story bullets
  - reporter evaluation / same-day feedback evaluation
  - execution-quality section
  - exit-decision bullets
- `libs/reporting/trade_report/context.py`
  - entry execution visibility assembly
  - strategist compact report-context assembly

Compatibility wrappers remain in `trade_report_ai.py` and resolve façade helpers at call time.

### Validation findings during extraction

The incremental gates did their job and caught two extraction-only dependency omissions before R2-A closure:

1. Market/scanner extraction initially referenced a nested `_core_value_opt` as if it were façade-owned. The injection was removed and the original local helper ownership preserved.
2. Lifecycle extraction initially omitted `json`, `normalize_reporter_text`, and `build_execution_truth_bullets` from the new owner boundary. These dependencies were restored without changing behavior.

No expected values, test assertions, report semantics, or runtime authority rules were changed to make the tests pass.

### Final size movement

```text
P1.5.1 baseline trade_report_ai.py        7,223 LOC
service extraction                        6,770 LOC
normalization extraction                  6,559 LOC
operator-text extraction                  5,827 LOC
shared-section-seed extraction            5,156 LOC
compact-input + fallback extraction       4,376 LOC
market/scanner builders                   3,847 LOC
lifecycle builders                        3,195 LOC
context builders                          3,040 LOC
--------------------------------------------------
net façade reduction                      4,183 LOC (-57.9%)
```

No function remaining in `trade_report_ai.py` exceeds 80 LOC at the R2-A closure point.

### Final verification

Focused Python 3.12 Reporting gate after the final context extraction:

```text
151 passed
```

Broader Python 3.12 Reporting regression covering 14 relevant Reporting/API/runtime test files:

```text
297 passed, 1 warning in 9.50s
```

The broader set included AI report, compact/separated adapter, provenance, batch runner, live bundle/recovery, metadata alignment, runtime regression, intraday, single-trade, symbol-trade, API trade-report, and closeout-report tests.

### R2-A verdict

```text
P1.5.2 R2-A                       COMPLETE
PUBLIC / PRIVATE COMPATIBILITY    PRESERVED
REPORT CONTRACT                   PRESERVED
TRUTH PRECEDENCE                  PRESERVED
LLM ROLE / CALL COUNT             PRESERVED
SUPERVISOR / EXECUTOR AUTHORITY   PRESERVED
UEF / BROKER SEMANTICS            PRESERVED
FOCUSED REGRESSION                151/151 PASS
BROADER REPORTING REGRESSION      297/297 PASS
NEXT                              R2-B Markdown façade decomposition
```
