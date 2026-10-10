# 2026-10-10 P1.5.2 — GPT Markdown Clean News Headlines Owner38

- Branch: `refactor/p1.5`; pinned original CODE HEAD `0409687aa76e195bd001d7756419b86b9580c531`.
- Eight existing read-only reporting bodies moved without modifying AST semantics to `libs/reporting/trade_report/markdown_clean_parts/news_headlines.py`. Responsibilities: HTML headline cleanup, title sampling, six-digit news symbol resolution, symbol matching, cross-symbol mismatch bullets and human linkage strength.
- Every 209 Markdown Clean/436 public callable names and original ABI preserved, facade monkeypatch helpers injected at call-time; new Owner <=350 LOC, owner DAG now 37.
- 8 original AST and 21 synthetic fixture comparisons + monkeypatch tests, existing Reporting/ABI/patch-notes CI retained. CI PENDING. Changes restricted to Reporting/test/docs/CI.
- LLM prompt, Broker, Supervisor/Executor, Scanner rank, UEF, R6.2, Step5C/D, Docker and real orders untouched. C:\Agentra real historical report byte parity, LLM call and full repo pytest, independent local Claude/Codex read-only audits NOT RUN. P1.5.2 OPEN, P1.5.3 NOT STARTED.
