# P1.5.2 — Summary Input Main Builder Owner 24 (2026-10-09)

- Baseline code SHA `211af9a92a6925f8792cf1c9bf8c86be9e20563e` on `refactor/p1.5`.
- Moved the **unchanged** body of `build_trade_summary_input` into `summary_input_parts/main_builder.py` (328 LOC) and retained the original public callable at `markdown_summary.py::build_trade_summary_input` as an adapter.
- Public wrapper passes the three contract builders and deterministic-findings function at CALL TIME; legacy monkeypatch integrations remain effective.
- markdown_summary.py 740 -> 432 physical LOC. Input implementation remains <=350 LOC; former render function is still oversized and OPEN.
- Six original JSON synthetic goldens and explicit wrapper monkeypatch CI test; baseline real data/LLM prompts/full repo and independent approvals are NOT RUN.
- No strategy, Broker, UEF/R6.2, Step5C/D, Docker, Q12, production report or live trade path changes. P1.5.2 OPEN.
