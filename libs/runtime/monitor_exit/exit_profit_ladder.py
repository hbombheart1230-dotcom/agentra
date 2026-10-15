"""Exit-policy trigger ladder checks (each returns the finalized result or None; precedence, order and closures stay in evaluate_exit_policy).

T4-B (P1.5 Third Pass): contiguous statement run / value expression of `libs/runtime/exit_policy.py::evaluate_exit_policy` moved verbatim into a
Monitor Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations


def opening_gap_profit_take_exit_check(_finalize, _mark_exit_sizing, _profit_floor_blocks_current_profit, _profit_threshold, hs, out, p, profit_exit_metric_name, profit_exit_pnl_ratio, *, facade):
    opening_gap_min_pct = float(out["thresholds"]["opening_gap_profit_take_min_pct"])
    opening_gap_min_pct = _profit_threshold(opening_gap_min_pct)
    opening_gap_window_sec = int(out["thresholds"]["opening_gap_profit_take_window_sec"])
    if opening_gap_min_pct > 0.0 and profit_exit_pnl_ratio >= opening_gap_min_pct and not _profit_floor_blocks_current_profit():
        opening_gap_observed = facade._to_bool(p.get("opening_gap_chase_observed"), False)
        open_gap_pct = facade._to_float(p.get("open_gap_pct"), 0.0)
        prev_close_distance_pct = facade._to_float(p.get("prev_close_distance_pct"), 0.0)
        out["opening_gap_chase_observed"] = bool(opening_gap_observed)
        out["open_gap_pct"] = float(open_gap_pct)
        out["prev_close_distance_pct"] = float(prev_close_distance_pct)
        if opening_gap_observed and (opening_gap_window_sec <= 0 or hs is None or hs <= opening_gap_window_sec):
            _mark_exit_sizing(
                fraction=float(out["thresholds"]["opening_gap_profit_take_fraction"] or 1.0),
                partial=False,
            )
            return _finalize(
                triggered=True,
                reason="opening_gap_profit_take",
                metric_name=profit_exit_metric_name,
                metric_value=profit_exit_pnl_ratio,
                metric_source=profit_exit_metric_name,
            )
    return None

def volume_exhaustion_exit_check(_finalize, _profit_floor_blocks_current_profit, _profit_threshold, out, p, profit_exit_pnl_ratio, *, facade):
    volume_exhaustion_min_pct = float(out["thresholds"]["volume_exhaustion_take_profit_min_pct"])
    volume_exhaustion_min_pct = _profit_threshold(volume_exhaustion_min_pct)
    if (
        volume_exhaustion_min_pct > 0.0
        and profit_exit_pnl_ratio >= volume_exhaustion_min_pct
        and not _profit_floor_blocks_current_profit()
    ):
        volume_ratio = facade._to_float(p.get("volume_ratio"), 0.0)
        execution_strength = facade._to_float(p.get("execution_strength"), 0.0)
        trade_strength = facade._to_float(p.get("trade_strength"), 0.0)
        volume_ratio_max = float(out["thresholds"]["volume_exhaustion_volume_ratio_max"])
        strength_max = float(out["thresholds"]["volume_exhaustion_strength_max"])
        out["volume_ratio"] = float(volume_ratio)
        out["execution_strength"] = float(execution_strength)
        out["trade_strength"] = float(trade_strength)
        volume_exhausted = bool(volume_ratio_max > 0.0 and 0.0 < volume_ratio <= volume_ratio_max)
        strength_exhausted = bool(
            strength_max > 0.0
            and (
                (execution_strength > 0.0 and execution_strength <= strength_max)
                or (trade_strength > 0.0 and trade_strength <= strength_max)
            )
        )
        if volume_exhausted or strength_exhausted:
            return _finalize(
                triggered=True,
                reason="volume_exhaustion_take_profit",
                metric_name="volume_ratio" if volume_exhausted else "execution_strength",
                metric_value=volume_ratio if volume_exhausted else execution_strength or trade_strength,
                metric_source="selected.features.volume_ratio" if volume_exhausted else "selected.features.execution_strength",
            )
    return None

def partial_take_profit_exit_check(_finalize, _mark_exit_sizing, _profit_floor_blocks_current_profit, out, partial_take_profit_effective_pct, partial_take_profit_pct, partial_take_profit_taken, profit_exit_metric_name, profit_exit_pnl_ratio):
    if (
        partial_take_profit_pct > 0.0
        and not partial_take_profit_taken
        and profit_exit_pnl_ratio >= partial_take_profit_effective_pct
        and not _profit_floor_blocks_current_profit()
    ):
        _mark_exit_sizing(
            fraction=float(out["thresholds"]["partial_take_profit_fraction"] or 0.5),
            partial=True,
        )
        return _finalize(
            triggered=True,
            reason="partial_take_profit",
            metric_name=profit_exit_metric_name,
            metric_value=profit_exit_pnl_ratio,
            metric_source=profit_exit_metric_name,
        )
    return None

def profit_ladder_exit_check(_finalize, _mark_exit_sizing, _profit_floor_blocks_current_profit, _profit_threshold, out, p, partial_take_profit_pct, profit_exit_metric_name, profit_exit_pnl_ratio, *, facade):
    profit_ladder_levels = list(out["thresholds"].get("profit_ladder_levels_pct") or [])
    profit_ladder_taken = set(round(x, 6) for x in facade._to_float_list(p.get("profit_ladder_taken_levels")))
    if profit_ladder_levels:
        ladder_candidates = [
            float(level)
            for level in profit_ladder_levels
            if float(level) >= _profit_threshold(0.0)
            and profit_exit_pnl_ratio >= float(level)
            and round(float(level), 6) not in profit_ladder_taken
            and not (partial_take_profit_pct > 0.0 and float(level) <= partial_take_profit_pct)
        ]
        if ladder_candidates and not _profit_floor_blocks_current_profit():
            selected_ladder = max(ladder_candidates)
            out["profit_ladder_level_pct"] = float(selected_ladder)
            out["profit_ladder_level_index"] = int(profit_ladder_levels.index(selected_ladder))
            ladder_fraction = float(out["thresholds"]["profit_ladder_fraction"] or 0.34)
            if selected_ladder >= max(profit_ladder_levels):
                ladder_fraction = 1.0
            _mark_exit_sizing(fraction=ladder_fraction, partial=ladder_fraction < 1.0)
            return _finalize(
                triggered=True,
                reason="profit_ladder",
                metric_name=profit_exit_metric_name,
                metric_value=profit_exit_pnl_ratio,
                metric_source=profit_exit_metric_name,
            )
    return None

def risk_reward_exit_check(_finalize, _mark_exit_sizing, _profit_floor_blocks_current_profit, _profit_threshold, effective_stop_pct, out, p, profit_exit_metric_name, profit_exit_pnl_ratio, *, facade):
    rr_take_profit_rungs = list(out["thresholds"].get("risk_reward_take_profit_rungs") or [])
    rr_single = float(out["thresholds"]["risk_reward_take_profit_r"])
    if not rr_take_profit_rungs and rr_single > 0.0:
        rr_take_profit_rungs = [rr_single]
    rr_taken = set(round(x, 6) for x in facade._to_float_list(p.get("risk_reward_take_profit_taken_rungs")))
    if rr_take_profit_rungs and effective_stop_pct > 0.0:
        rr_candidates = [
            float(rung)
            for rung in rr_take_profit_rungs
            if profit_exit_pnl_ratio >= _profit_threshold(
                max(float(effective_stop_pct * float(rung)), float(out["thresholds"]["risk_reward_take_profit_min_pct"]))
            )
            and round(float(rung), 6) not in rr_taken
        ]
        if rr_candidates and not _profit_floor_blocks_current_profit():
            selected_rung = max(rr_candidates)
            rr_target_pct = max(
                float(effective_stop_pct * selected_rung),
                float(out["thresholds"]["risk_reward_take_profit_min_pct"]),
                _profit_threshold(0.0),
            )
            out["risk_reward_take_profit_rung"] = float(selected_rung)
            out["risk_reward_take_profit_target_pct"] = float(rr_target_pct)
            rr_fraction = float(out["thresholds"]["risk_reward_take_profit_fraction"] or 0.34)
            if selected_rung >= max(rr_take_profit_rungs):
                rr_fraction = 1.0
            _mark_exit_sizing(fraction=rr_fraction, partial=rr_fraction < 1.0)
            return _finalize(
                triggered=True,
                reason="risk_reward_take_profit",
                metric_name=profit_exit_metric_name,
                metric_value=profit_exit_pnl_ratio,
                metric_source=profit_exit_metric_name,
            )
    return None

def resistance_target_exit_check(_finalize, _profit_floor_blocks_current_profit, _profit_threshold, hs, out, p, peak_drawdown, peak_price, profit_exit_metric_name, profit_exit_pnl_ratio, technical_px, *, facade):
    if peak_price > 0.0:
        resistance_near_pct = float(out["thresholds"]["resistance_take_profit_near_pct"])
        resistance_min_pct = _profit_threshold(float(out["thresholds"]["resistance_take_profit_min_pct"]))
        if (
            resistance_near_pct > 0.0
            and profit_exit_pnl_ratio >= resistance_min_pct
            and not _profit_floor_blocks_current_profit()
        ):
            resistance_candidates: list[tuple[str, float]] = []
            for resistance_key in (
                "resistance_price",
                "target_resistance_price",
                "upper_resistance_price",
                "day_high",
                "intraday_high",
                "recent_high",
                "breakout_level",
                "prior_bar_high",
            ):
                resistance_value = facade._to_float(p.get(resistance_key), 0.0)
                if resistance_value > 0.0 and resistance_value >= technical_px:
                    resistance_candidates.append((resistance_key, resistance_value))
            if resistance_candidates:
                resistance_source, resistance_price = min(resistance_candidates, key=lambda row: float(row[1]))
                resistance_distance = float((resistance_price / technical_px) - 1.0)
                out["resistance_price"] = float(resistance_price)
                out["resistance_price_source"] = f"policy.{resistance_source}"
                out["resistance_distance_pct"] = float(resistance_distance)
                if 0.0 <= resistance_distance <= resistance_near_pct:
                    return _finalize(
                        triggered=True,
                        reason="resistance_take_profit",
                        metric_name="resistance_distance_pct",
                        metric_value=resistance_distance,
                        metric_source=f"policy.{resistance_source}",
                    )

        vwap_extension_th = float(out["thresholds"]["vwap_extension_take_profit_pct"])
        vwap_extension_min_pct = _profit_threshold(float(out["thresholds"]["vwap_extension_take_profit_min_pct"]))
        if (
            vwap_extension_th > 0.0
            and profit_exit_pnl_ratio >= vwap_extension_min_pct
            and not _profit_floor_blocks_current_profit()
        ):
            vwap_distance = facade._to_float(p.get("vwap_distance"), 0.0)
            out["vwap_distance"] = float(vwap_distance)
            if vwap_distance >= vwap_extension_th:
                return _finalize(
                    triggered=True,
                    reason="vwap_extension_take_profit",
                    metric_name="vwap_distance",
                    metric_value=vwap_distance,
                    metric_source="selected.features.engine_vwap_distance",
                )

        profit_time_stop_sec = int(out["thresholds"]["profit_time_stop_sec"])
        profit_time_stop_min_pct = _profit_threshold(float(out["thresholds"]["profit_time_stop_min_pct"]))
        profit_time_stop_giveback_pct = float(out["thresholds"]["profit_time_stop_peak_giveback_pct"])
        out["profit_time_stop_peak_giveback_pct"] = float(profit_time_stop_giveback_pct)
        if (
            profit_time_stop_sec > 0
            and hs is not None
            and hs >= profit_time_stop_sec
            and profit_exit_pnl_ratio >= profit_time_stop_min_pct
            and (profit_time_stop_giveback_pct <= 0.0 or peak_drawdown <= -profit_time_stop_giveback_pct)
            and not _profit_floor_blocks_current_profit()
        ):
            return _finalize(
                triggered=True,
                reason="time_decay_profit_exit",
                metric_name=profit_exit_metric_name,
                metric_value=profit_exit_pnl_ratio,
                metric_source=profit_exit_metric_name,
            )
    return None
