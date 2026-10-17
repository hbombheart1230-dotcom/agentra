# controlled_mock_lane_report — decision input for Work (no change made; module stays in place)

Consumers (repo grep, BASE-equal code):
- Reporter read paths only: `libs/reporting/single_trade_report.py` (build_controlled_lane_report_surface; R-8 moved caller body now calls it via `facade.`), `libs/reporting/trade_report_markdown_clean.py` (controlled_lane_surface_from_report for Markdown), `scripts/run_ai_trade_report_batch.py` (batch regeneration), `tests/test_controlled_mock_lane_report.py`.
- No graph/runtime/commander/execution code imports it. The WRITER of the ledger it reads is `libs/runtime/controlled_mock_lanes/ledger.py` (coordinator/commander execution) — operational Q10/Q12 lane owner.
Behaviour: read-only: `data/logs/controlled_mock_lanes/<day>/lane_submissions.json` (json read, OSError/decode errors -> {}), fixed lane labels (Q12 BTC-우리기술투자, Q10 반도체/지수), static `_fixed_lane_strategy`, output schema `controlled_mock_lane_report.v2` with `execution_scope: kiwoom_mock_only`.
Options: (A) Reporter read-only presentation owner (move to libs/agents/reporter/read_models with an injected ledger reader; lane labels stay data); (B) Operations/Q-lane owner (libs/runtime/controlled_mock_lanes/report_projection) with Reporter importing it; (C) keep as SHARED in libs/reporting.
Recommendation: (A) only if Work confirms Reporter may own Q10/Q12 presentation labels; otherwise (C). Either way: no change to ledger path, labels, schema or error behaviour without a separate approved change.
