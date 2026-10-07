# 2026-10-07 — P1.5.1 Reporting definite dead-code cleanup

## Summary
P1.5.1 implemented the first behavior-preserving structural cleanup on the frozen P1.3-era baseline branch.

## Code changes
- `libs/reporting/trade_report_ai.py`: removed the unreachable legacy implementation nested after the unconditional delegation return in `render_trade_summary_markdown_with_evaluation()`.
  - 8,354 -> 7,223 LOC
  - 1,131 lines removed
  - public wrapper preserved
- `libs/reporting/trade_report_markdown_clean.py`: removed the earlier shadowed `_playbook_label` definition.
  - 5,862 -> 5,852 LOC
  - later/more complete binding preserved
- No report schema, truth precedence, artifact path, LLM prompt/routing, trading logic, Supervisor/Executor authority, UEF semantics, or broker behavior changed.

## Test hygiene
The broader reporting regression exposed two tests that created production-shaped directories under the repository during pytest. The tests were isolated to `tmp_path`:
- `tests/test_live_execution_bundle_report.py`: runtime lock path redirected to session temp storage.
- `tests/test_report_metadata_alignment.py`: metrics output already uses the per-test `reports_root`.

These are test-only path-isolation corrections and do not alter runtime behavior.

## Verification
- Required P1.5.1 suite:
  - `tests/test_trade_report_ai.py`
  - `tests/test_trade_summary_symbol_metadata.py`
  - `tests/test_reporting_provenance_preference.py`
  - **149 passed**
- Broader affected reporting selection executed **280 tests; all 280 test assertions passed**.
- That broader session initially exited non-zero only because the repository production-path audit detected `reports/metrics` and `reports/runtime` creation; the two responsible test paths were then isolated as described above.
- No full-repository regression or Docker/live acceptance is claimed by this P1.5.1 batch.

## Scope verdict
```text
P1.5.1 CODE CLEANUP          COMPLETE
REQUIRED TESTS               PASS (149/149)
BEHAVIOR CHANGE              NONE INTENDED / NONE OBSERVED
TRADING AUTHORITY CHANGE     NONE
PRODUCTION CODE WRITE PATH   UNCHANGED
TEMP CI WORKFLOW             REMOVED BEFORE FINALIZATION
NEXT                         P1.5.2 Reporting decomposition
```
