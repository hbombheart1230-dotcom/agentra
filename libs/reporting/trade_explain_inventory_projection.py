"""Trade explain report inventory (moved verbatim from trade_explain).

``operator_summary_artifact_root`` is resolved on ``facade`` (the trade_explain module) at call time; this module never imports it.
Read-only existence checks.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, List


def _report_inventory(day: str, reports_root: Path, *, facade: Any) -> List[str]:
    operator_root = facade.operator_summary_artifact_root(reports_root)
    candidates = [
        operator_root / "daily" / day / "operator_summary.md",
        reports_root / "decision_story" / f"decision_story_{day}.md",
        reports_root / "run_cards" / f"run_cards_{day}.md",
        reports_root / "metrics" / f"metrics_{day}.md",
        operator_root / "daily" / day / "daily_report.md",
        operator_root / "daily" / f"daily_{day}.md",
        reports_root / "live_watch" / "live_watch_latest.md",
    ]
    out: List[str] = []
    for p in candidates:
        if p.exists():
            out.append(str(p))
    return out
