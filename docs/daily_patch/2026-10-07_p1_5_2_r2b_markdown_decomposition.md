# 2026-10-07 — P1.5.2 R2-B Markdown façade decomposition

## Summary
Started R2-B by moving the largest trade-summary Markdown responsibilities and entry/exit signal presentation logic out of `libs/reporting/trade_report_markdown_clean.py` while preserving the existing public functions and private helper seams.

## Structural changes

### Summary Markdown owner
Added `libs/reporting/trade_report/markdown_summary.py`.

Moved the implementations of:
- `render_trade_summary_markdown_clean()` — 745 LOC at the R2-B baseline
- `build_trade_summary_input_clean()` — 416 LOC at the R2-B baseline

The original functions remain in `trade_report_markdown_clean.py` as compatibility façades.

The first extraction gate caught one wiring issue: helper names defined locally inside the original functions (for example `_compact_decimal`) had initially been treated as façade dependencies. The owner boundary was corrected so local helper ownership remains local and only true external dependencies are injected.

### Signal Markdown owner
Added `libs/reporting/trade_report/markdown_signals.py`.

Moved:
- `_entry_watch_execution_lines()`
- `_entry_watch_summary_lines()`
- `_resolve_entry_signal_snapshot()`
- `_entry_signal_metric_summary_lines()`
- `_enrich_exit_signal_snapshot_from_monitor()`
- `_build_summary_exit_trigger_lines()`

The original private names remain compatibility wrappers in `trade_report_markdown_clean.py`.

## Size movement

```text
R2-B baseline trade_report_markdown_clean.py     5,852 LOC
summary renderer/input extraction                4,810 LOC after local-helper fix
signal builder extraction                        4,187 LOC
----------------------------------------------------------
net façade reduction                             1,665 LOC (-28.5%)
```

## Verification

Focused Python 3.12 Markdown/Reporting regression after the corrected summary extraction:

```text
168 passed in 3.43s
```

Focused regression after signal extraction:

```text
168 passed in 3.52s
```

Broader Reporting/API/runtime regression:

```text
297 passed, 1 warning in 8.34s
```

The warning is the existing Starlette/httpx test-client deprecation warning and is unrelated to this refactor.

## Behavior locks
Unchanged:
- Markdown section ordering and operator-facing meaning
- report JSON contract
- truth-source precedence
- symbol metadata resolution
- same-day result semantics
- entry/exit signal interpretation
- quant-tactic/control-lane rendering
- LLM role and call count
- artifact paths
- Supervisor / Executor authority
- UEF and broker semantics

## R2-B status

```text
P1.5.2 R2-B                      ACTIVE / PARTIAL PASS
SUMMARY RENDERER / INPUT OWNER   PASS
ENTRY / EXIT SIGNAL OWNER        PASS
FOCUSED REGRESSION               168/168 PASS
BROADER REPORTING REGRESSION     297/297 PASS
TRADE MARKDOWN FAÇADE            5,852 -> 4,187 LOC
NEXT                             carryover / memory / translation residuals
```

## Carryover / memory / translation residual update

R2-B continued with three responsibility moves:

- `libs/reporting/trade_report_markdown_strategy_memory.py`
  - now owns `_carryover_context()`
  - now owns `_build_prompt_proven_memory()`
  - now owns `_build_memory_application()`
  - existing façade names remain wrappers
- `libs/reporting/trade_report/markdown_translation.py`
  - now owns the 170-line `_translate_text()` implementation
  - action/axis/reason helper seams remain injected from the façade

### Incremental validation findings

The focused gate caught two extraction-boundary import omissions before closure:

1. `_carryover_context()` used the original module-level `timedelta` import; the new strategy-memory owner now imports it explicitly.
2. `_translate_text()` used the original module-level `html` and `re` imports; the new translation owner now imports both explicitly.

These were wiring/import fixes only. No assertions, expected strings, ordering, truth precedence or trading behavior were changed.

### Updated size movement

```text
R2-B baseline trade_report_markdown_clean.py      5,852 LOC
summary + signal extraction                       4,187 LOC
carryover + memory extraction                     3,868 LOC
translation extraction                            3,713 LOC
-----------------------------------------------------------
net façade reduction                              2,139 LOC (-36.6%)
```

### Verification

Focused Python 3.12 Markdown/Reporting gate after carryover/memory fix:

```text
168 passed
```

Focused gate after translation import fix:

```text
168 passed
```

Broader Reporting/API/runtime regression after the complete tranche:

```text
297 passed, 1 warning in 10.94s
```

The single warning remains the existing Starlette/httpx test-client deprecation warning.

### Updated R2-B status

```text
P1.5.2 R2-B                      ACTIVE / PARTIAL PASS
SUMMARY RENDERER / INPUT OWNER   PASS
ENTRY / EXIT SIGNAL OWNER        PASS
CARRYOVER / MEMORY OWNER         PASS
TRANSLATION OWNER                PASS
FOCUSED REGRESSION               168/168 PASS
BROADER REPORTING REGRESSION     297/297 PASS
TRADE MARKDOWN FAÇADE            5,852 -> 3,713 LOC
NEXT                             diagnostics / market / strategist residuals
```
