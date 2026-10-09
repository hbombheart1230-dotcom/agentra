# 2026-10-09 P1.5.2 Markdown Signals owner split 05

Baseline: 74fec10d5c7ecf113792251f9c49ec3398a72266
Original markdown_signals.py source: 810 LOC; compatibility reexports: 20 LOC.
Seven deterministic functions moved verbatim and still accessible from the old module name.
- libs/reporting/trade_report/markdown_signal_parts/entry_watch.py: 322 LOC
- libs/reporting/trade_report/markdown_signal_parts/entry_metrics.py: 198 LOC
- libs/reporting/trade_report/markdown_signal_parts/exit.py: 296 LOC

No rank/Monitor thresholds/policy changes, no broker path, UEF or Step5 changes. Broad GitHub CI and local real artifact equality required.
