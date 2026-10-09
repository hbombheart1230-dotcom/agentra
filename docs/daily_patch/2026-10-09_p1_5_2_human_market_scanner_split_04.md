# P1.5.2 Market/Scanner human projections split 04 — 2026-10-09

Baseline 9a5f95731a6610dafe6c80bfa91d9e40f2fb6660
libs/reporting/trade_story_pipeline_human_payloads.py: 1335 -> 859 physical LOC
Original two independent functions moved verbatim; old import names reexported.
libs/reporting/trade_story_human_parts/market_context.py: 221 LOC
libs/reporting/trade_story_human_parts/scanner_reason.py: 278 LOC
Next outstanding: long build_monitor_reason_human ~706 LOC. No production writes, broker or UEF changes. Requires broad Reporting CI and independent real-data parity.
