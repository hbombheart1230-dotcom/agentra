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
