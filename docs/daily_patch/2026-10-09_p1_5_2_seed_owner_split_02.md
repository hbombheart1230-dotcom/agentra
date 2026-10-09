# P1.5.2 Reporting shared seed split — 02 (2026-10-09)

Baseline SHA dd9eb04b96be71f550c51fa9c03e55ed4ff6b118
Source sections.py BEFORE 763 LOC, AFTER 246 LOC. Build_shared_summary_seed now delegates commander, scanner, monitor, strategist construction into owner files. Original truth selection/price and output dict remain verbatim in outer function, preserving ordering. Scanner enrichment and Monitor enrichment remain separate in the original sequence.

- libs/reporting/trade_report/section_seed_parts/commander.py: 104 LOC <=350
- libs/reporting/trade_report/section_seed_parts/scanner.py: 114 LOC <=350
- libs/reporting/trade_report/section_seed_parts/monitor.py: 197 LOC <=350
- libs/reporting/trade_report/section_seed_parts/strategist.py: 170 LOC <=350

Legacy module section exports retained. No production runtime, Step5C/D, R6.2, broker, UEF or Docker changes. CI regression applies; independent local real-data output parity is pending and is not represented as PASS.
