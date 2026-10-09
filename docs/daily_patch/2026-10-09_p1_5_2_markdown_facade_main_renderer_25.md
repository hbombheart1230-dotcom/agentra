# P1.5.2 — Markdown Main Renderer & Helper Owner 25 (2026-10-09)

- Base SHA `78db9a7b9fea92ec909d44698ce6a555c253f552` branch `refactor/p1.5`.
- Moved 11 nested output-only helper function bodies AST-identically into `summary_render_parts/render_helpers.py` (130 physical LOC). Each nested public-function-local name remains a wrapper that forwards its original captured helpers at call time.
- Moved the resulting original body of `render_trade_summary_markdown` into `summary_render_parts/main_renderer.py` (326 LOC). Its exported `markdown_summary.render_trade_summary_markdown` remains the same signature and forwards 16 helper bindings at call time.
- `markdown_summary.py` reduced 432 -> 60 LOC, with BOTH public `render_trade_summary_markdown` and `build_trade_summary_input` preserved.
- Eleven moved bodies and full renderer AST-preserved; six original renderer output byte SHA-256 golden tests and explicit façade monkeypatch regression in CI. DAG/size guard updated 23->25 new Owners.
- No real production report, prompt/call/retry or local C:\\Agentra baseline proof. No Broker, strategy, UEF/R6.2, Step5C/D, Docker, Q12 or order mutation. P1.5.2 OPEN.
