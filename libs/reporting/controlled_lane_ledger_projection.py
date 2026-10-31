"""controlled_mock_lane_report projections (moved verbatim from controlled_mock_lane_report).

Module globals and helpers are resolved on ``facade`` (the controlled_mock_lane_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def _ledger_row(
    *, root: Path, day: str, symbol: str, order_id: str = "", run_id: str = "",
    facade: Any,
) -> dict[str, Any]:
    path = root / "data" / "logs" / "controlled_mock_lanes" / day / "lane_submissions.json"
    try:
        payload = facade.json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, facade.json.JSONDecodeError):
        return {}
    rows = payload.get("submissions") if isinstance(payload, facade.Mapping) else []
    symbol_matches = [
        dict(row) for row in list(rows or [])
        if isinstance(row, facade.Mapping) and facade._text(row.get("symbol")) == symbol
    ]
    if order_id:
        exact = [row for row in symbol_matches if facade._text(row.get("order_id")).lstrip("0") == order_id.lstrip("0")]
        if exact:
            return exact[-1]
    if run_id:
        exact = [row for row in symbol_matches if facade._text(row.get("run_id")) == run_id]
        if exact:
            return exact[-1]
    return {}
