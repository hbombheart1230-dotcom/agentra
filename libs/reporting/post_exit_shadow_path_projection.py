"""post_exit_shadow_recap projections (moved verbatim from post_exit_shadow_recap).

Read-only existence check and glob; the body references no module globals, so no facade is needed.
"""
from __future__ import annotations

from pathlib import Path
from typing import List


def iter_trade_report_json_paths(reports_root: Path, day: str) -> List[Path]:
    trade_root = reports_root / "trades" / day
    if not trade_root.exists():
        return []
    return sorted(trade_root.rglob("reports/ai_trade_report.json"))
