"""Daily report generator trade event/directory read projections (moved verbatim from daily_report_generator).

Read-only; ``json`` is resolved on ``facade`` (the daily_report_generator module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable


def _iter_events(path: Path, *, facade: Any) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []
    def gen():
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield facade.json.loads(line)
                except Exception:
                    continue
    return gen()


def _find_trade_dir(reports_root: Path, day: str, trade_id: str) -> Path | None:
    direct = reports_root / "trades" / day / trade_id
    if direct.exists():
        return direct
    matches = sorted((reports_root / "trades" / day).glob(f"*/{trade_id}"))
    return matches[0] if matches else None
