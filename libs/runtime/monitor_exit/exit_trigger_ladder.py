"""Exit-policy trigger ladder checks (each returns the finalized result or None; precedence, order and closures stay in evaluate_exit_policy).

T4-B (P1.5 Third Pass): contiguous statement run / value expression of `libs/runtime/exit_policy.py::evaluate_exit_policy` moved verbatim into a
Monitor Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations


def stop_loss_exit_check(_finalize, hard_sl, out, pnl_ratio, sl):
    hard_stop_pnl_ratio = float(out["hard_stop_pnl_ratio"])
    stop_pnl_ratio = float(out["stop_pnl_ratio"])
    if hard_sl > 0.0 and hard_stop_pnl_ratio <= -hard_sl:
        return _finalize(
            triggered=True,
            reason="hard_stop",
            metric_name="hard_stop_pnl_ratio",
            metric_value=hard_stop_pnl_ratio,
            metric_source=str(out.get("hard_stop_pnl_ratio_source") or "effective_pnl_ratio"),
        )
    if sl > 0.0 and stop_pnl_ratio <= -sl:
        return _finalize(
            triggered=True,
            reason="stop_loss",
            metric_name="stop_pnl_ratio",
            metric_value=stop_pnl_ratio,
            metric_source=str(out.get("stop_pnl_ratio_source") or "technical_pnl_ratio"),
        )
    if sl > 0.0 and pnl_ratio <= -sl and stop_pnl_ratio > -sl:
        out["stop_loss_cost_drag_blocked"] = True
        out["stop_loss_cost_drag_blocked_reason"] = "net_pnl_stop_loss_without_technical_stop"
        if not str(out.get("hold_block_reason") or "").strip():
            out["hold_block_reason"] = "stop_loss_cost_drag_only"
    return None

def profit_target_exit_check(_finalize, _mark_profit_floor_blocked, _profit_floor_blocks_current_profit, _profit_threshold, etf_deviation_pct, etf_deviation_source, out, profit_exit_pnl_ratio, tp):
    etf_premium_take_profit_enabled = bool(out["thresholds"].get("etf_premium_take_profit_enabled"))
    etf_premium_take_profit_pct = float(out["thresholds"].get("etf_premium_take_profit_pct") or 0.0)
    etf_premium_take_profit_min_pct = float(out["thresholds"].get("etf_premium_take_profit_min_pct") or 0.0)
    etf_premium_take_profit_armed = bool(
        etf_premium_take_profit_enabled
        and etf_deviation_pct is not None
        and etf_premium_take_profit_pct > 0.0
        and float(etf_deviation_pct) >= etf_premium_take_profit_pct
    )
    out["etf_premium_take_profit_armed"] = bool(etf_premium_take_profit_armed)
    if etf_premium_take_profit_armed:
        min_profit = _profit_threshold(etf_premium_take_profit_min_pct)
        if profit_exit_pnl_ratio >= min_profit and not _profit_floor_blocks_current_profit():
            return _finalize(
                triggered=True,
                reason="etf_premium_take_profit",
                metric_name="etf_deviation_pct",
                metric_value=etf_deviation_pct,
                metric_source=etf_deviation_source or "selected.features.etf_deviation_pct",
            )
        if _profit_floor_blocks_current_profit():
            _mark_profit_floor_blocked()
            out["hold_block_reason"] = "etf_premium_take_profit:cost_aware_profit_floor_not_met"

    if tp > 0.0 and profit_exit_pnl_ratio >= _profit_threshold(tp) and not _profit_floor_blocks_current_profit():
        return _finalize(triggered=True, reason="take_profit")
    return None

def vwap_breakdown_exit_check(_block_protective_exit_below_floor, _finalize, apx, gross_pnl_ratio, hs, out, p, peak_price, *, facade):
    vwap_breakdown_th = float(out["thresholds"]["vwap_breakdown_pct"])
    if vwap_breakdown_th > 0.0:
        vwap_distance = facade._to_float(p.get("vwap_distance"), 0.0)
        out["vwap_distance"] = float(vwap_distance)
        vwap_distance_source = str(p.get("vwap_distance_source") or "selected.features.engine_vwap_distance")
        require_profit = facade._to_bool(p.get("vwap_break_requires_profit"), True)
        if vwap_distance <= -vwap_breakdown_th and (not require_profit or peak_price > apx or gross_pnl_ratio > 0.0):
            confirm_bars_required, confirmation_required, confirmed, consecutive_bars, early_hold_blocked, low_break_confirmed, min_hold_required, volume_confirmed = facade.exit_trigger_confirm_bars_required_confirmation_requi(p=p, out=out, hs=hs, facade=facade)
            if early_hold_blocked:
                out["vwap_breakdown_confirmation_pending"] = True
                out["vwap_breakdown_confirmation_reason"] = (
                    f"need_min_hold_{min_hold_required}s_or_hard_invalidation"
                )
                if not str(out.get("hold_block_reason") or "").strip():
                    out["hold_block_reason"] = "vwap_breakdown_min_hold_pending"
            elif not confirmed:
                out["vwap_breakdown_confirmation_pending"] = True
                out["vwap_breakdown_confirmation_reason"] = (
                    f"need_{confirm_bars_required}_bars_or_low_break_plus_volume"
                )
                if not str(out.get("hold_block_reason") or "").strip():
                    out["hold_block_reason"] = "vwap_breakdown_confirmation_pending"
            elif _block_protective_exit_below_floor("vwap_breakdown"):
                pass
            else:
                return _finalize(
                    triggered=True,
                    reason="vwap_breakdown",
                    metric_name="vwap_distance",
                    metric_value=vwap_distance,
                    metric_source=vwap_distance_source,
                )
    return None

def intraday_low_break_exit_check(_block_protective_exit_below_floor, _finalize, _protective_exit_hard_invalidation, hs, out, p, technical_px, *, facade):
    intraday_low_break_pct = float(out["thresholds"]["intraday_low_break_pct"])
    if intraday_low_break_pct > 0.0:
        prior_bar_low = facade._to_float(p.get("prior_bar_low"), 0.0)
        out["prior_bar_low"] = float(prior_bar_low)
        if prior_bar_low > 0.0 and technical_px <= float(prior_bar_low * (1.0 - intraday_low_break_pct)):
            confirm_bars_required, confirmed, early_hold_blocked, min_hold_required = facade.exit_trigger_confirm_bars_required_confirmed(_protective_exit_hard_invalidation=_protective_exit_hard_invalidation, out=out, p=p, hs=hs, facade=facade)
            if early_hold_blocked:
                out["intraday_low_break_confirmation_pending"] = True
                out["intraday_low_break_confirmation_reason"] = (
                    f"need_min_hold_{min_hold_required}s_or_hard_invalidation"
                )
                if not str(out.get("hold_block_reason") or "").strip():
                    out["hold_block_reason"] = "intraday_low_break_min_hold_pending"
            elif not confirmed:
                out["intraday_low_break_confirmation_pending"] = True
                out["intraday_low_break_confirmation_reason"] = (
                    f"need_{confirm_bars_required}_bars_or_low_break_plus_volume"
                )
                if not str(out.get("hold_block_reason") or "").strip():
                    out["hold_block_reason"] = "intraday_low_break_confirmation_pending"
            elif _block_protective_exit_below_floor("intraday_low_break"):
                pass
            else:
                return _finalize(triggered=True, reason="intraday_low_break")
    return None

def trend_strength_exit_check(_finalize, out, p, *, facade):
    trend_strength_floor = float(out["thresholds"]["trend_strength_floor"])
    if trend_strength_floor != 0.0:
        trend_strength = facade._to_float(p.get("trend_strength"), 0.0)
        out["trend_strength"] = float(trend_strength)
        vwap_distance = facade._to_float(p.get("vwap_distance"), out.get("vwap_distance") or 0.0)
        out["vwap_distance"] = float(vwap_distance)
        if trend_strength <= trend_strength_floor and vwap_distance < 0.0:
            return _finalize(triggered=True, reason="trend_breakdown")
    return None

def trailing_stop_exit_check(_finalize, _profit_floor_blocks_current_profit, out, peak_price, technical_px):
    trail = float(out["thresholds"]["trailing_stop_pct"])
    if trail > 0.0:
        if peak_price > 0.0:
            drawdown = float((technical_px / peak_price) - 1.0)
            out["trailing_drawdown"] = drawdown
            if drawdown <= -trail and not _profit_floor_blocks_current_profit():
                return _finalize(triggered=True, reason="trailing_stop")
    return None

def time_limit_exit_check(_finalize, _mark_profit_floor_blocked, expected_exit_floor_blocked, gross_pnl_ratio, hs, out, profit_floor_enabled, time_limit_reached, time_limit_reason):
    if time_limit_reached:
        if not profit_floor_enabled:
            return _finalize(
                triggered=True,
                reason=time_limit_reason,
                metric_name="hold_sec",
                metric_value=hs,
                metric_source="position_age_seconds",
            )
        if bool(out.get("cost_aware_profit_floor_met")) and not expected_exit_floor_blocked:
            return _finalize(
                triggered=True,
                reason=time_limit_reason,
                metric_name="hold_sec",
                metric_value=hs,
                metric_source="position_age_seconds",
            )

        out["time_limit_reassessment_blocked"] = True
        if gross_pnl_ratio > 0.0:
            _mark_profit_floor_blocked()
            blocked_reason = (
                "expected_exit_profit_floor_not_met"
                if expected_exit_floor_blocked
                else "cost_aware_profit_floor_not_met"
            )
            out["time_limit_reassessment_blocked_reason"] = f"{time_limit_reason}:{blocked_reason}"
            out["hold_block_reason"] = f"{time_limit_reason}:{blocked_reason}"
        else:
            out["time_limit_reassessment_blocked_reason"] = (
                f"{time_limit_reason}:time_limit_reached_without_profit_floor"
            )
            if not str(out.get("hold_block_reason") or "").strip():
                out["hold_block_reason"] = f"{time_limit_reason}:time_limit_reached_without_profit_floor"
    return None
