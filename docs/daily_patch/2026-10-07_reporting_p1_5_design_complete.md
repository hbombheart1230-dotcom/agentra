# 2026-10-07 Reporting P1.5 Design Complete

## Summary

Completed the P1.5.1/P1.5.2 Reporting design.

No runtime/report-generation code was changed.

## Scope

Reviewed:
- `libs/reporting/trade_report_ai.py`
- `libs/reporting/trade_report_markdown_clean.py`
- `libs/reporting/trade_story_pipeline.py`
- existing extracted Reporting helpers
- primary Reporting tests and compatibility seams

## Key Findings

- Combined giant-file surface: 18,743 LOC.
- `trade_report_ai.py::render_trade_summary_markdown_with_evaluation` contains an unconditional delegation return followed by roughly 1,100 LOC of unreachable legacy nested implementation.
- `trade_report_markdown_clean.py` defines `_playbook_label` twice; the later definition shadows the earlier one.
- Reporting already has substantial responsibility-specific helper modules; P1.5 should promote/reuse them rather than create a second parallel architecture.
- `tests/test_trade_report_ai.py` is a major compatibility seam and directly exercises numerous private helpers, so façade wrappers must be preserved during early extraction.

## Design Authority

- `docs/refactor/p1_5_reporting_implementation_packet_v1_0.md`

## Implementation Gate

P1.5.1 code changes remain blocked until the P1.2/P1.3 frozen baseline is recorded.

## Runtime Impact

None.
