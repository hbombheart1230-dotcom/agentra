# P1.5.2 — AI Reporter Text Owner 31 (2026-10-09)

- Baseline `9242d6e30c1c9917bf434bed99e7cca373876678`, `refactor/p1.5` only.
- Six untouched report-only helper AST bodies moved to `libs/reporting/trade_report/ai_facade_parts/text_helpers.py` (47 LOC): low-information label, Hangul/Latin counts, nonempty text, evidence payload indicator and action *display label*.
- Public `trade_report_ai.py` 3039->3027 LOC. All 182 original function names/signatures retained with call-time `_safe_fullmatch` and `_clip` monkeypatch seams. Conservative 436-symbol ledger line positions refreshed; no DEAD classification.
- Pinned AST/output/monkeypatch tests and 31-Owner static DAG/size guard added to CI. Production C:\\Agentra local reports/LLM/independent acceptance remain OPEN.
- No actual order/action, strategy, Broker/Executor, UEF/R6.2, Step5C/D, Docker, Q12 or LLM calls/prompts changed. P1.5.2 OPEN.
