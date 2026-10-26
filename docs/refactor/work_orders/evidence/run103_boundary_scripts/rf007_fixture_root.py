# Build a SYNTHETIC repository root for the read-only observability API (uses the repo's own test fixture writers).
import sys, shutil
from pathlib import Path
repo = Path(sys.argv[1]); root = Path(sys.argv[2])
sys.path.insert(0, str(repo / "tests" / "apps" / "api")); sys.path.insert(0, str(repo))
from artifact_fixtures import (write_trade_bundle, write_performance_day, write_operator_day, write_opportunity_day,
                               write_market_day, write_llm_events, trade_row)
shutil.rmtree(root, ignore_errors=True)
reports, logs, state = root / "reports", root / "logs", root / "state"
for p in (reports, logs, state): p.mkdir(parents=True)
days = ["2026-10-20", "2026-10-21", "2026-10-22", "2026-10-23", "2026-10-24"]
syms = ["005930", "000660", "035420", "051910"]
ids = []
for i, d in enumerate(days):
    day_ids = []
    for j, s in enumerate(syms[: 2 + (i % 3)]):
        tid, _ = write_trade_bundle(reports, d, s, f"{j+1:02d}"); day_ids.append(tid)
    ids += day_ids
    write_performance_day(reports, d, [trade_row(t, d, 0.01 * (k + 1) - 0.015 * i, 1000.0 * (k + 1) - 700.0 * i) for k, t in enumerate(day_ids)])
    write_operator_day(reports, d, [{"symbol": "005930", "quantity": 3 + i, "avg_price": 70000 + i * 100, "market_value": 210000 + i}] if i % 2 == 0 else [])
    write_opportunity_day(reports, d)
    write_market_day(logs, d, kospi_change=0.4 - 0.3 * i)
    write_llm_events(logs, d, include_usage=bool(i % 2))
print("FIXTURE_ROOT_OK", root, "trades", len(ids))
