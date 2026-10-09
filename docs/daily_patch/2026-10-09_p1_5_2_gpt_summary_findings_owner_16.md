# 2026-10-09 — P1.5.2 GPT Deterministic Summary Findings Owner 16

- Baseline source SHA `f131d448766c7a2061276994c420fb8523e97588`. `markdown_summary.py::build_trade_summary_input` deterministic positives/problems/causes/validation questions moved as one contiguous read-only report-observation responsibility.
- New `trade_report/summary_parts/findings.py` has 84 physical LOC and receives original call-time `listify/as_dict/num_opt` dependencies.
- No prompt contents, summary output keys, source precedence, strategy, order authority, R6.2, Step5C/D, UEF, Docker, broker writes or live operations modified.
- Added focused tests for baseline, carryover, partial and rank/chart conditions. CI outcome is required; actual local report byte parity remains NOT RUN.
- Remaining Markdown summary rendering/input LOC still OPEN; P1.5.2 not closed.
