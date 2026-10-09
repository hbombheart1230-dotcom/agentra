# P1.5.2 — Markdown Render Section Owners 22 (2026-10-09)

- Original code SHA `23c4d82daa945d133e895dee0133485bce098188` on `refactor/p1.5`.
- Four original contiguous Markdown list-append blocks moved into read-only bounded Owners: overview 98 LOC; market_news 93 LOC; decision_lifecycle 144 LOC; closing 90 LOC.
- Parent `markdown_summary.py` 1,145 -> 827 physical LOC. All moved formatting statements retain their original order and use explicit caller-provided dependencies. No public API was renamed.
- Six synthetic old-vs-new report scenarios returned byte-identical outputs locally. Their pre-split SHA-256 goldens are pinned in CI (empty, BUY, loss, carryover, recovered partial, Scanner fallback). Real C:\\Agentra report corpus NOT RUN.
- CI size and no-reverse-import/cycle guard expanded 15 to 19 new Owners. Remote CI must pass before acceptance.
- No Broker, UEF/R6.2, Step5C/D, Docker, trading/strategy/production report writer or LLM authority changes. P1.5.2 OPEN.
