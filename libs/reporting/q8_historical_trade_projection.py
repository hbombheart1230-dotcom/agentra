"""q8_historical_review projections (moved verbatim from q8_historical_review).

Module globals and helpers are resolved on ``facade`` (the q8_historical_review module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def _extract_trade_rows(reports_root: Path, *, start: str, end: str, facade: Any) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for path in sorted((reports_root / "trades").glob("*/**/reports/ai_trade_summary.json")):
        try:
            day = path.parts[path.parts.index("trades") + 1]
        except Exception:
            continue
        if day < start or day > end:
            continue
        payload = facade._read_json(path)
        trade = payload.get("trade") if isinstance(payload.get("trade"), dict) else {}
        truth = payload.get("truth_surface") if isinstance(payload.get("truth_surface"), dict) else {}
        decision = payload.get("decision_flow") if isinstance(payload.get("decision_flow"), dict) else {}
        quant = payload.get("quant_tactic") if isinstance(payload.get("quant_tactic"), dict) else {}
        pnl_pct = facade._pct_from_ratio(truth.get("pnl_pct"))
        rows.append(
            {
                "day": day,
                "trade_id": facade._text(trade.get("trade_id")) or facade._trade_id_from_path(path),
                "symbol": facade._text(trade.get("symbol")),
                "status": facade._text(trade.get("status")),
                "pnl_pct": pnl_pct,
                "truth_source": facade._text(truth.get("truth_source")),
                "tactic": facade._text(
                    quant.get("tactic_id")
                    or quant.get("selected_tactic")
                    or trade.get("tactical_strategy")
                    or decision.get("tactical_strategy")
                ),
                "playbook": facade._text(quant.get("playbook") or trade.get("playbook") or decision.get("playbook")),
                "entry_reason": facade._text(decision.get("entry_reason") or decision.get("entry_trigger")),
                "exit_reason": facade._text(decision.get("exit_reason") or decision.get("exit_trigger")),
            }
        )
    return rows
