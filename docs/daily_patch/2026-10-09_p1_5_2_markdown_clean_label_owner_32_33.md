# P1.5.2 Markdown Clean Operators 32-33 — 2026-10-09

- Source SHA `52508ade9d0d246fa4e848525fe62f2fe067acb7`, branch `refactor/p1.5` only.
- Extracted 21 body AST-identical **report display** label/Strategist wording functions into `libs/reporting/trade_report/markdown_clean_parts/operator_labels.py` (227 LOC) and `libs/reporting/trade_report/markdown_clean_parts/strategist_language.py` (79 LOC).
- Public facade 2948->2717 LOC with all **209** function names/signatures and call-time monkeypatchs intact. All **436** ledger symbols retained.
- CI pins 21 AST body comparisons, 21 synthetic output cases, public patch seams and 33-owner size/dependency DAG guard. No real report data baseline, complete pytest, independent audits or LLM prompt/call comparison. P1.5.2 OPEN.
- No Broker/Executor/Supervisor strategy authority, UEF/R6.2/Step5C/D, Docker, Q12 or production writes.
