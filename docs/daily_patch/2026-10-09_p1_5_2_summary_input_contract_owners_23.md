# P1.5.2 — Summary Input Contract Owners 23 (2026-10-09)

- Base remote code `83b70148ab0822d9434200a058befbc87cfbca84` on `refactor/p1.5`.
- Extracted original `build_trade_summary_input` nested dictionary payloads for broker_alignment, market_and_strategy and decision_flow to three read-only dedicated Owners, retaining literal key order, source selection and evaluation precedence without affecting LLM task hard constraints.
- New Owner LOC: broker_alignment 26, market_and_strategy 34, decision_flow 92. Each output dictionary's AST equals the pre-split AST; no public function signature changed.
- markdown_summary.py 827 -> 740 LOC. Six synthetic original/new summary-input JSON SHA-256 outputs matched, CI fixture checks added. DAG/size static guard covers 22 new Owners.
- Local production C:\\Agentra actual report/LLM call/retry, full repo baseline and independent signoff NOT RUN. Trading, Broker, UEF/R6.2, Step5C/D, Docker, Q12 and P1.5.3 untouched. P1.5.2 remains OPEN.
