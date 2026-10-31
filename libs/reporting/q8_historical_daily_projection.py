"""q8_historical_review projections (moved verbatim from q8_historical_review).

Module globals and helpers are resolved on ``facade`` (the q8_historical_review module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def _daily_summary_rows(reports_root: Path, *, start: str, end: str, facade: Any) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for day in facade._iter_days(start, end):
        path = reports_root / "operator_summary" / "daily" / day / "daily_summary.json"
        if not path.exists():
            continue
        payload = facade._read_json(path)
        metrics = payload.get("metrics") if isinstance(payload.get("metrics"), dict) else {}
        q = (
            payload.get("quant_shadow_candidate_evaluation")
            if isinstance(payload.get("quant_shadow_candidate_evaluation"), dict)
            else {}
        )
        gate = q.get("evaluation_trust_gate") if isinstance(q.get("evaluation_trust_gate"), dict) else {}
        rail = payload.get("market_regime_rail_review") if isinstance(payload.get("market_regime_rail_review"), dict) else {}
        rows.append(
            {
                "day": day,
                "trade_count": facade._int(metrics.get("trade_count")),
                "closed_trade_count": facade._int(metrics.get("closed_trade_count")),
                "return_sample_count": facade._int(metrics.get("return_sample_count")),
                "unavailable_return_count": facade._int(metrics.get("unavailable_return_count")),
                "win_rate": facade._float(metrics.get("win_rate")) or 0.0,
                "avg_return_pct": facade._float(metrics.get("avg_return_pct")) or 0.0,
                "truth_surface_count": facade._int(metrics.get("truth_surface_count")),
                "shadow_candidate_count": facade._int(q.get("candidate_count")),
                "shadow_deduped_candidate_count": facade._int(q.get("deduped_candidate_count")),
                "shadow_duplicate_candidate_count": facade._int(q.get("duplicate_candidate_count")),
                "shadow_evaluated_count": facade._int(q.get("evaluated_count")),
                "shadow_would_enter_count": facade._int(q.get("would_enter_count")),
                "shadow_forward_outcome_coverage": facade._float(q.get("forward_outcome_coverage")),
                "q8_trust_gate_status": facade._text(gate.get("status")),
                "q8_promotion_allowed": bool(gate.get("promotion_allowed")),
                "q8_trusted_forward_count": facade._int(gate.get("trusted_forward_count")),
                "q8_trusted_forward_coverage": facade._float(gate.get("trusted_forward_coverage")),
                "q8_duplicate_rate": facade._float(gate.get("duplicate_rate")),
                "market_regime_rail": facade._text(rail.get("rail_id") or rail.get("market_regime_rail")),
            }
        )
    return rows
