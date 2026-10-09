# 2026-10-09 — P1.5.2 GPT Monitor Policy Display Owner 17

- Baseline SHA `5af56e90ef08d917413a86bc540706c85ea769b0`.
- Extracted the exact contiguous human-facing Monitor stop, profit, trailing and extension-policy bullet statements into `libs/reporting/trade_story_human_parts/monitor_policy_bullets.py` (89 LOC).
- Historical append order, input `monitor_stop_policy_trace` and call-time formatting helpers retained; the new owner neither calculates an order nor changes safety policies.
- Source parent physical LOC 810 -> 736.
- Added explicit ordering and absence tests to pinned Reporting CI; no local broker or production report artifacts touched.
- P1.5.2 remains OPEN pending further giant-function refactoring, local real-data report equivalence and independent audit.
