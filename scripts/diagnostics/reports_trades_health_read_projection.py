from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def _read_json(path: Path, *, facade: Any) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = facade.json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _iter_trade_dirs(reports_root: Path, day: str = "", *, facade: Any) -> List[Path]:
    trades_root = reports_root / "trades"
    if not trades_root.exists():
        return []
    if day:
        day_root = trades_root / day
        if not day_root.exists():
            return []
        return facade._iter_trade_dirs_under_day(day_root)
    out: List[Path] = []
    for path in sorted(trades_root.iterdir()):
        if not path.is_dir():
            continue
        if len(path.name) == 10 and path.name.count("-") == 2:
            out.extend(facade._iter_trade_dirs_under_day(path))
    return out


def _artifact_path(trade_dir: Path, *candidates: str, facade: Any) -> Path:
    for raw in candidates:
        path = trade_dir / raw
        if path.exists():
            return path
    return trade_dir / candidates[0]


def _ai_trade_report_is_complete(trade_dir: Path, *, facade: Any) -> bool:
    report_path = facade._artifact_path(trade_dir, "ai_trade_report/ai_trade_report.json", "trade_report.json")
    report = facade._read_json(report_path)
    if not report:
        return False
    required_sections = (
        "executive_summary", "market_context_at_entry", "why_this_symbol_was_chosen", "entry_decision",
        "holding_monitoring_story", "exit_decision", "execution_quality", "scanner_filters",
        "guard_approval_result", "reporter_evaluation", "errors_weaknesses_improvement_points",
        "final_operator_conclusion",
    )
    return all(isinstance(report.get(key), dict) for key in required_sections)
