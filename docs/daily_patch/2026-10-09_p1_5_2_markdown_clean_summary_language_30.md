# P1.5.2 — Markdown Clean Summary Language Owner 30 (2026-10-09)

- Base SHA `007e7c2ff757181048bac6d467ff76ec9f4ddce1` branch `refactor/p1.5`.
- Moved 8 unchanged pure report-output/localization function bodies to `libs/reporting/trade_report/markdown_clean_parts/summary_language.py` (140 LOC), maintaining original public functions/signatures and call-time patchable dependencies in `libs/reporting/trade_report_markdown_clean.py`.
- Public Markdown Clean façade 3043 -> 2948 LOC, 209 symbol names/order unchanged, conservative 436-symbol ledger positions refreshed. No symbol DEAD.
- Old body AST, Korean text fixtures and public patch dispatch tests added to CI; 30-owner DAG/size guard extended. CI PASS must be separately observed.
- No trading authority, Broker, UEF/R6.2/Step5C/D, Docker, live reports/LLM or Q12 changed. Local actual report and independent acceptance OPEN; P1.5.3 forbidden.
