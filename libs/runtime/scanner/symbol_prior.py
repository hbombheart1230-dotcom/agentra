"""Scanner symbol-prior adjustment computation (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _compute_symbol_prior_adjustment_r3_impl(*, symbol_model, playbook, current_day, facade):
    if not isinstance(symbol_model, dict) or not symbol_model:
        return {
            "adjustment": 0.0,
            "risk_delta": 0.0,
            "confidence_delta": 0.0,
            "reasons": [],
            "summary": {},
        }

    adjustment = 0.0
    risk_delta = 0.0
    confidence_delta = 0.0
    reasons: List[str] = []
    playbook_norm = str(playbook or "").strip().lower()

    if str(symbol_model.get("data_quality", {}).get("data_source") or "").strip() == "symbol_memory":
        reasons.append("symbol_memory")

    avg_pnl_pct = facade._to_float(symbol_model.get("avg_pnl_pct"))
    win_rate = facade._to_float(symbol_model.get("win_rate"))
    loss_count = facade._to_int(symbol_model.get("loss_count"), 0)
    closed_trade_count = facade._to_int(symbol_model.get("closed_trade_count"), 0)
    last_trade_date = str(symbol_model.get("last_trade_date") or "").strip()
    dominant_playbook = str(symbol_model.get("dominant_playbook") or "").strip().lower()
    dominant_blocker = str(symbol_model.get("dominant_monitor_blocker") or "").strip()
    repeated_failures = list(symbol_model.get("repeated_failure_pattern") or [])
    same_day_model = bool(str(current_day or "").strip() and last_trade_date == str(current_day or "").strip())

    if avg_pnl_pct < 0:
        adjustment -= 0.08
        risk_delta += 0.08
        confidence_delta -= 0.06
        reasons.append(f"negative_avg_pnl_pct:{avg_pnl_pct:.2f}")
    elif avg_pnl_pct > 0:
        adjustment += 0.04
        confidence_delta += 0.03
        reasons.append(f"positive_avg_pnl_pct:{avg_pnl_pct:.2f}")

    if win_rate > 0.0 and win_rate < 0.4:
        adjustment -= 0.05
        risk_delta += 0.05
        confidence_delta -= 0.04
        reasons.append(f"low_win_rate:{win_rate:.2f}")
    elif win_rate >= 0.6:
        adjustment += 0.03
        confidence_delta += 0.02
        reasons.append(f"strong_win_rate:{win_rate:.2f}")

    if playbook_norm and dominant_playbook and dominant_playbook != "unknown":
        if playbook_norm == dominant_playbook:
            adjustment += 0.03
            reasons.append(f"playbook_fit:{dominant_playbook}")
        else:
            adjustment -= 0.04
            risk_delta += 0.03
            reasons.append(f"playbook_mismatch:{dominant_playbook}")

    if dominant_blocker and dominant_blocker.lower() != "unknown":
        risk_delta += 0.03
        reasons.append(f"dominant_blocker:{dominant_blocker}")

    if repeated_failures:
        first = repeated_failures[0] if isinstance(repeated_failures[0], dict) else {}
        failure_type = str(first.get("type") or "").strip()
        failure_value = str(first.get("value") or "").strip()
        if failure_value:
            reasons.append(f"repeated_failure:{failure_type}:{failure_value}")

    if same_day_model and closed_trade_count >= 2 and (loss_count >= 2 or avg_pnl_pct < -0.10):
        adjustment -= 0.25
        risk_delta += 0.18
        confidence_delta -= 0.12
        reasons.append(f"same_day_repeat_loss:{loss_count}/{closed_trade_count}")
    if same_day_model and closed_trade_count >= 3 and (loss_count >= 3 or avg_pnl_pct < -0.15):
        adjustment -= 0.20
        risk_delta += 0.12
        confidence_delta -= 0.08
        reasons.append("same_day_trade_lockout_bias")

    adjustment = facade._clamp(adjustment, -0.60, 0.10)
    risk_delta = facade._clamp(risk_delta, 0.0, 0.35)
    confidence_delta = facade._clamp(confidence_delta, -0.30, 0.05)
    return {
        "adjustment": float(adjustment),
        "risk_delta": float(risk_delta),
        "confidence_delta": float(confidence_delta),
        "reasons": reasons[:6],
        "summary": {
            "dominant_playbook": str(symbol_model.get("dominant_playbook") or ""),
            "dominant_monitor_blocker": str(symbol_model.get("dominant_monitor_blocker") or ""),
            "avg_pnl_pct": float(avg_pnl_pct),
            "win_rate": float(win_rate),
            "last_trade_date": str(last_trade_date),
            "same_day_model": bool(same_day_model),
            "closed_trade_count": int(closed_trade_count),
            "loss_count": int(loss_count),
        },
    }
