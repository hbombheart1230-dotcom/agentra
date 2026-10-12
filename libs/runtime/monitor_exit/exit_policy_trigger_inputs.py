"""Exit-policy trigger input/result-interpretation projections (pure; no trigger selection).

Second Pass (P1.5) intra-function extraction from `libs/runtime/exit_policy.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def exit_trigger_peak_drawdown_th_profit_protection_urgen(max_runup_pct, out, peak_drawdown, peak_drawdown_armed, peak_drawdown_mode, peak_drawdown_block_reason, peak_profit_floor_required_pct, peak_profit_floor_met, profit_floor_enabled, profit_floor_pct, gross_pnl_ratio, *, facade):
    if True:
        out["max_runup_pct"] = max_runup_pct
        out["peak_drawdown"] = peak_drawdown
        out["peak_drawdown_from_peak"] = peak_drawdown
        out["peak_drawdown_armed"] = bool(peak_drawdown_armed)
        out["peak_drawdown_mode"] = str(peak_drawdown_mode)
        out["peak_drawdown_blocked"] = bool(not peak_drawdown_armed and bool(peak_drawdown_block_reason))
        out["peak_drawdown_block_reason"] = str(peak_drawdown_block_reason)
        out["peak_drawdown_profit_floor_required_pct"] = float(peak_profit_floor_required_pct)
        out["peak_drawdown_profit_floor_met"] = bool(peak_profit_floor_met)
        out["final_peak_drawdown_ratio"] = peak_drawdown
        out["peak_drawdown_source"] = f"{str(out.get('technical_price_source') or 'technical_price')}_vs_peak_price"

        peak_drawdown_th = float(out["thresholds"]["peak_drawdown_exit_pct"])
        profit_protection_urgent = bool(
            peak_drawdown_th > 0.0
            and peak_drawdown_armed
            and peak_drawdown <= -peak_drawdown_th
            and profit_floor_enabled
            and profit_floor_pct > 0.0
            and peak_profit_floor_met
            and gross_pnl_ratio < profit_floor_pct
        )
        out["peak_drawdown_profit_protection_urgent"] = bool(profit_protection_urgent)
        if profit_protection_urgent:
            out["peak_drawdown_profit_protection_reason"] = "max_runup_crossed_cost_floor_then_gave_back"
    return (peak_drawdown_th, profit_protection_urgent)


def exit_trigger_confirm_bars_required_confirmation_requi(p, out, hs, *, facade):
    if True:
            confirmation_required = facade._to_bool(p.get("vwap_breakdown_confirmation_required"), True)
            confirm_bars_required = int(out["thresholds"].get("vwap_breakdown_confirm_bars") or 2)
            min_hold_required = int(out["thresholds"].get("vwap_breakdown_min_hold_sec") or 120)
            consecutive_bars = max(0, int(facade._to_float(p.get("vwap_breakdown_consecutive_bars"), 0.0)))
            low_break_confirmed = facade._to_bool(p.get("vwap_breakdown_low_break_confirmed"), False)
            volume_confirmed = facade._to_bool(p.get("vwap_breakdown_volume_confirmed"), False)
            confirmed = bool(
                not confirmation_required
                or consecutive_bars >= confirm_bars_required
                or (low_break_confirmed and volume_confirmed)
                or facade._to_bool(p.get("hard_invalidation_confirmed"), False)
                or facade._to_bool(p.get("vwap_breakdown_hard_invalidation"), False)
            )
            early_hold_blocked = bool(
                min_hold_required > 0
                and hs is not None
                and int(hs) < int(min_hold_required)
                and not facade._to_bool(p.get("hard_invalidation_confirmed"), False)
                and not facade._to_bool(p.get("vwap_breakdown_hard_invalidation"), False)
            )
            out["vwap_breakdown_confirmation_required"] = bool(confirmation_required)
            out["vwap_breakdown_consecutive_bars"] = int(consecutive_bars)
            out["vwap_breakdown_confirm_bars_required"] = int(confirm_bars_required)
            out["vwap_breakdown_min_hold_sec"] = int(min_hold_required)
            out["vwap_breakdown_low_break_confirmed"] = bool(low_break_confirmed)
            out["vwap_breakdown_volume_confirmed"] = bool(volume_confirmed)
            out["vwap_breakdown_confirmed"] = bool(confirmed)
    return (confirm_bars_required, confirmation_required, confirmed, consecutive_bars, early_hold_blocked, low_break_confirmed, min_hold_required, volume_confirmed)


def exit_trigger_confirm_bars_required_confirmed(_protective_exit_hard_invalidation, out, p, hs, *, facade):
    if True:
            hard_invalidation = _protective_exit_hard_invalidation("intraday_low_break")
            hard_invalidation_reason = str(out.get("protective_exit_hard_invalidation_reason") or "")
            explicit_hard_invalidation = bool(
                hard_invalidation
                and not hard_invalidation_reason.startswith("intraday_low_break_deep:")
            )
            min_hold_required = int(out["thresholds"].get("intraday_low_break_min_hold_sec") or 60)
            confirm_bars_required = int(out["thresholds"].get("intraday_low_break_confirm_bars") or 2)
            consecutive_bars = max(0, int(facade._to_float(p.get("intraday_low_break_consecutive_bars"), 0.0)))
            low_break_confirmed = facade._to_bool(p.get("intraday_low_break_low_break_confirmed"), False)
            volume_confirmed = facade._to_bool(p.get("intraday_low_break_volume_confirmed"), False)
            confirmation_required = facade._to_bool(p.get("intraday_low_break_confirmation_required"), True)
            confirmed = bool(
                explicit_hard_invalidation
                or not confirmation_required
                or consecutive_bars >= confirm_bars_required
                or (low_break_confirmed and volume_confirmed)
                or facade._to_bool(p.get("hard_invalidation_confirmed"), False)
                or facade._to_bool(p.get("intraday_low_break_hard_invalidation"), False)
            )
            early_hold_blocked = bool(
                not explicit_hard_invalidation
                and min_hold_required > 0
                and hs is not None
                and int(hs) < int(min_hold_required)
            )
            out["intraday_low_break_confirmation_required"] = bool(confirmation_required)
            out["intraday_low_break_consecutive_bars"] = int(consecutive_bars)
            out["intraday_low_break_confirm_bars_required"] = int(confirm_bars_required)
            out["intraday_low_break_low_break_confirmed"] = bool(low_break_confirmed)
            out["intraday_low_break_volume_confirmed"] = bool(volume_confirmed)
            out["intraday_low_break_confirmed"] = bool(confirmed)
            out["intraday_low_break_min_hold_sec"] = int(min_hold_required)
            out["intraday_low_break_min_hold_blocked"] = bool(early_hold_blocked)
    return (confirm_bars_required, confirmed, early_hold_blocked, min_hold_required)
