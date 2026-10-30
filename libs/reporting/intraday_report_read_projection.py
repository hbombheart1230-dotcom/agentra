"""intraday_trade_reports projections (moved verbatim from intraday_trade_reports).

Module globals and helpers are resolved on ``facade`` (the intraday_trade_reports module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def _read_json(path: Path, *, facade: Any) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = facade.json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}



def _load_story_input(trade_dir: Path, *, facade: Any) -> tuple[Dict[str, Any], str]:
    canonical = trade_dir / "ai_trade_report_input.json"
    normalized_legacy = trade_dir / "ai_trade_report" / "ai_trade_report_input.json"
    legacy = trade_dir / "trade_story_input.json"
    for path in (canonical, normalized_legacy, legacy):
        payload = facade._read_json(path)
        if payload:
            return payload, str(path)
    return {}, ""
