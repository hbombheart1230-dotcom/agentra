from __future__ import annotations

import os
import re
from typing import Any, Dict, Optional

from libs.runtime.etf_deviation import (
    DEFAULT_PREMIUM_TRIGGER_PCT,
    normalize_deviation_pct,
    score_etf_deviation_for_exit,
)
import sys as _r3_sys
from libs.runtime.monitor_exit.exit_policy_chart_projection import (
    exit_chart_out,
)
from libs.runtime.monitor_exit.exit_policy_pnl_projection import (
    exit_pnl_hs_news_shock_th,
    exit_pnl_apx_crosscheck,
    exit_pnl_gross_pnl_ratio_gross_profit_floor_gap_p,
    exit_pnl_expected_exit_floor_blocked_profit_exit,
    exit_pnl_effective_stop_candidates_effective_stop,
)
from libs.runtime.monitor_exit.exit_policy_trigger_inputs import (
    exit_trigger_peak_drawdown_th_profit_protection_urgen,
    exit_trigger_confirm_bars_required_confirmation_requi,
    exit_trigger_confirm_bars_required_confirmed,
)
from libs.runtime.monitor_exit.exit_trigger_ladder import (
    stop_loss_exit_check,
    profit_target_exit_check,
    vwap_breakdown_exit_check,
    intraday_low_break_exit_check,
    trend_strength_exit_check,
    trailing_stop_exit_check,
    time_limit_exit_check,
)
from libs.runtime.monitor_exit.exit_profit_ladder import (
    opening_gap_profit_take_exit_check,
    volume_exhaustion_exit_check,
    partial_take_profit_exit_check,
    profit_ladder_exit_check,
    risk_reward_exit_check,
    resistance_target_exit_check,
)
from libs.runtime.monitor_exit.account_pnl_crosscheck import (
    resolve_account_pnl_evidence,
    resolve_account_mark_price,
    resolve_effective_price,
)


def _to_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)


def _clamp_non_negative(v: float) -> float:
    return float(v) if v > 0.0 else 0.0


def _to_bool(v: Any, default: bool = False) -> bool:
    if isinstance(v, bool):
        return v
    if v is None:
        return bool(default)
    return str(v).strip().lower() in ("1", "true", "yes", "y", "on")


def _to_ratio(v: Any) -> float | None:
    if v in (None, ""):
        return None
    try:
        out = float(v)
    except Exception:
        return None
    if abs(out) > 1.0:
        out = out / 100.0
    return float(out)


def _to_float_list(v: Any) -> list[float]:
    raw_items: list[Any]
    if isinstance(v, (list, tuple)):
        raw_items = list(v)
    elif isinstance(v, str):
        raw_items = re.split(r"[,;|]\s*", v.strip()) if v.strip() else []
    else:
        raw_items = []
    out: list[float] = []
    for item in raw_items:
        x = _to_float(item, 0.0)
        if x > 0.0:
            out.append(float(x))
    return sorted(set(out))


def apply_account_pnl_crosscheck_context(
    policy: Dict[str, Any] | None,
    *,
    position: Dict[str, Any] | None,
) -> Dict[str, Any]:
    """Attach authoritative account fields used for exit PnL cross-checking.

    The caller keeps ownership of how positions are sourced. This helper only
    normalizes a few optional fields so exit evaluation can reconcile
    raw/live-price PnL with account-authoritative unrealized PnL.
    """
    out = dict(policy or {})
    if not isinstance(position, dict):
        return out

    qty = max(0, int(_to_float(position.get("qty"), 0.0)))
    avg_price = _to_float(position.get("avg_price"), 0.0)
    if qty > 0 and out.get("account_qty") in (None, ""):
        out["account_qty"] = int(qty)
    if avg_price > 0.0 and out.get("account_avg_price") in (None, ""):
        out["account_avg_price"] = float(avg_price)

    for key in ("price", "cur_price", "last_price", "current_price"):
        raw = position.get(key)
        if raw in (None, ""):
            continue
        px = _to_float(raw, 0.0)
        if px > 0.0 and out.get("account_current_price") in (None, ""):
            out["account_current_price"] = float(px)
            out.setdefault("account_current_price_source", f"position.{key}")
            break

    unrealized = position.get("unrealized_pnl")
    if unrealized not in (None, "") and out.get("account_unrealized_pnl") in (None, ""):
        out["account_unrealized_pnl"] = float(_to_float(unrealized, 0.0))
    ratio = _to_ratio(
        position.get("account_pnl_ratio")
        if position.get("account_pnl_ratio") not in (None, "")
        else position.get("unrealized_pnl_rate")
    )
    if ratio is not None and out.get("account_pnl_ratio") in (None, ""):
        out["account_pnl_ratio"] = float(ratio)
        out.setdefault(
            "account_pnl_ratio_source",
            str(position.get("account_pnl_ratio_source") or "position.account_pnl_ratio"),
        )

    out.setdefault("account_crosscheck_mode", "conservative")
    return out


def _build_account_pnl_crosscheck(
    policy: Dict[str, Any],
    *,
    price: Optional[float],
    avg_price: Optional[float],
    qty: int,
) -> Dict[str, Any]:
    q = max(0, int(qty or 0))
    raw_price = _to_float(price, 0.0) if price is not None else 0.0
    avg = _to_float(avg_price, 0.0) if avg_price is not None else 0.0
    raw_pnl_ratio = float((raw_price / avg) - 1.0) if raw_price > 0.0 and avg > 0.0 else None

    account_current_price, account_pnl_ratio, account_pnl_ratio_source, account_ratio_mark_price, account_unrealized_mark_price, account_unrealized_pnl, reference_price = resolve_account_pnl_evidence(avg=avg, policy=policy, q=q, raw_price=raw_price, facade=_r3_sys.modules[__name__])

    def _price_ratio(candidate: Optional[float]) -> float | None:
        if candidate is None or candidate <= 0.0 or reference_price <= 0.0:
            return None
        return float(candidate / reference_price)

    def _price_anomaly_reason(candidate: Optional[float], *, source: str) -> str:
        ratio = _price_ratio(candidate)
        if ratio is None:
            return ""
        if ratio < 0.5:
            return f"{source}_below_reference_ratio:{ratio:.4f}"
        if ratio > 1.5:
            return f"{source}_above_reference_ratio:{ratio:.4f}"
        return ""

    account_mark_price, account_mark_price_source, fallback_price_source, pnl_fallback_applied, price_anomaly_flag, price_anomaly_reason = resolve_account_mark_price(_price_anomaly_reason=_price_anomaly_reason, account_ratio_mark_price=account_ratio_mark_price, account_unrealized_mark_price=account_unrealized_mark_price, raw_price=raw_price)

    applied, effective_price, effective_source, reason = resolve_effective_price(account_mark_price=account_mark_price, account_mark_price_source=account_mark_price_source, account_pnl_ratio=account_pnl_ratio, fallback_price_source=fallback_price_source, pnl_fallback_applied=pnl_fallback_applied, policy=policy, raw_pnl_ratio=raw_pnl_ratio, raw_price=raw_price)

    effective_pnl_ratio = None
    if effective_price is not None and effective_price > 0.0 and avg > 0.0:
        effective_pnl_ratio = float((effective_price / avg) - 1.0)

    pnl_ratio_gap = None
    if raw_pnl_ratio is not None and account_pnl_ratio is not None:
        pnl_ratio_gap = float(account_pnl_ratio - raw_pnl_ratio)

    price_gap = None
    if account_mark_price is not None and raw_price > 0.0:
        price_gap = float(account_mark_price - raw_price)

    return {
        "available": bool(raw_pnl_ratio is not None or account_pnl_ratio is not None),
        "mode": str(policy.get("account_crosscheck_mode") or "conservative"),
        "raw_price": float(raw_price) if raw_price > 0.0 else None,
        "raw_pnl_ratio": raw_pnl_ratio,
        "account_current_price": account_current_price,
        "account_current_price_source": str(policy.get("account_current_price_source") or ""),
        "account_unrealized_pnl": account_unrealized_pnl,
        "account_mark_price": account_mark_price,
        "account_mark_price_source": account_mark_price_source,
        "account_ratio_mark_price": account_ratio_mark_price,
        "account_unrealized_mark_price": account_unrealized_mark_price,
        "account_pnl_ratio": account_pnl_ratio,
        "account_pnl_ratio_source": account_pnl_ratio_source,
        "effective_price": effective_price,
        "effective_price_source": effective_source,
        "effective_pnl_ratio": effective_pnl_ratio,
        "pnl_ratio_gap": pnl_ratio_gap,
        "price_gap": price_gap,
        "applied": bool(applied),
        "reason": reason,
        "price_anomaly_flag": bool(price_anomaly_flag),
        "price_anomaly_reason": str(price_anomaly_reason),
        "pnl_fallback_applied": bool(pnl_fallback_applied),
        "fallback_price_source": str(fallback_price_source),
    }


def _build_chart_context_summary(policy: Dict[str, Any]) -> Dict[str, Any]:
    raw = policy.get("chart_context")
    chart_context = dict(raw) if isinstance(raw, dict) else {}
    features = chart_context.get("chart_structure_features")
    if not isinstance(features, dict):
        features = chart_context if chart_context else {}

    summary = {
        "available": False,
        "schema_version": str(features.get("schema_version") or "") if isinstance(features, dict) else "",
        "structure_hh_hl": None,
        "support_holding": None,
        "trend_regime": None,
        "ma_alignment_state": None,
        "failed_breakout": None,
        "momentum_follow_through": None,
        "structure_breakdown_signal": "",
        "notes": [],
    }
    if not isinstance(features, dict) or not bool(features):
        return summary

    structure = features.get("structure") if isinstance(features.get("structure"), dict) else {}
    trend_alignment = features.get("trend_alignment") if isinstance(features.get("trend_alignment"), dict) else {}
    support_resistance = (
        features.get("support_resistance") if isinstance(features.get("support_resistance"), dict) else {}
    )
    continuity_momentum = (
        features.get("continuity_momentum") if isinstance(features.get("continuity_momentum"), dict) else {}
    )

    summary["structure_hh_hl"] = structure.get("structure_hh_hl")
    summary["support_holding"] = support_resistance.get("support_holding")
    summary["trend_regime"] = trend_alignment.get("trend_regime")
    summary["ma_alignment_state"] = trend_alignment.get("ma_alignment_state")
    summary["failed_breakout"] = support_resistance.get("failed_breakout")
    summary["momentum_follow_through"] = continuity_momentum.get("momentum_follow_through")
    summary["available"] = bool(features.get("available"))
    summary["notes"] = [str(x or "").strip() for x in list(features.get("notes") or []) if str(x or "").strip()]

    if str(summary["failed_breakout"] or "").strip().lower() == "confirmed":
        summary["structure_breakdown_signal"] = "failed_breakout"
    elif str(summary["support_holding"] or "").strip().lower() == "lost":
        summary["structure_breakdown_signal"] = "support_lost"
    elif (
        str(summary["ma_alignment_state"] or "").strip().lower() == "bearish"
        and str(summary["trend_regime"] or "").strip().lower() in {"transition", "ranging"}
    ):
        summary["structure_breakdown_signal"] = "trend_alignment_breakdown"

    return summary


def apply_env_stop_take_fallbacks(policy: Dict[str, Any] | None) -> Dict[str, Any]:
    """Use env stop/take baselines only when policy does not already define them."""
    out = dict(policy or {})
    sl_raw = str(os.getenv("EXIT_POLICY_STOP_LOSS_PCT", "") or "").strip()
    tp_raw = str(os.getenv("EXIT_POLICY_TAKE_PROFIT_PCT", "") or "").strip()

    if sl_raw and _to_float(out.get("stop_loss_pct"), 0.0) <= 0.0:
        sl = _to_float(sl_raw, 0.03)
        out["stop_loss_pct"] = float(sl if sl > 0.0 else 0.03)

    if tp_raw and _to_float(out.get("take_profit_pct"), 0.0) <= 0.0:
        tp = _to_float(tp_raw, 0.05)
        out["take_profit_pct"] = float(tp if tp > 0.0 else 0.05)

    return out


def evaluate_exit_policy(
    *,
    price: Optional[float],
    avg_price: Optional[float],
    qty: int,
    hold_sec: Optional[int] = None,
    policy: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Evaluate stop-loss / take-profit exit policy for one position.

    Returns a deterministic decision payload. It never raises.
    """
    p = dict(policy or {})
    chart_context_summary = _build_chart_context_summary(p)
    out = exit_chart_out(chart_context_summary=chart_context_summary, p=p, facade=_r3_sys.modules[__name__])[0]
    if bool(out["thresholds"].get("cost_aware_profit_floor_enabled")):
        explicit_floor = float(out["thresholds"].get("cost_aware_profit_floor_pct") or 0.0)
        cost_floor = float(out["thresholds"].get("round_trip_cost_floor_pct") or 0.0)
        buffer = float(out["thresholds"].get("min_net_profit_buffer_pct") or 0.0)
        out["thresholds"]["cost_aware_profit_floor_pct"] = float(max(explicit_floor, cost_floor + buffer))
    else:
        out["thresholds"]["cost_aware_profit_floor_pct"] = 0.0
    out["cost_aware_profit_floor_enabled"] = bool(out["thresholds"].get("cost_aware_profit_floor_enabled"))
    out["cost_aware_profit_floor_pct"] = float(out["thresholds"].get("cost_aware_profit_floor_pct") or 0.0)
    out["cost_aware_profit_floor_met"] = False
    out["cost_aware_profit_floor_gap_pct"] = None
    out["cost_aware_profit_floor_blocked"] = False

    def _finalize(
        triggered: bool | None = None,
        reason: str | None = None,
        *,
        metric_name: str = "",
        metric_value: Any = None,
        metric_source: str = "",
    ) -> Dict[str, Any]:
        if triggered is not None:
            out["triggered"] = bool(triggered)
        if reason is not None:
            out["reason"] = str(reason or "")
        final_reason = str(out.get("reason") or "")
        inferred_metric_name = str(metric_name or "")
        inferred_metric_value = metric_value
        inferred_metric_source = str(metric_source or "")
        if not inferred_metric_name and final_reason in {
            "hard_stop",
            "stop_loss",
            "take_profit",
            "partial_take_profit",
            "profit_ladder",
            "risk_reward_take_profit",
            "opening_gap_profit_take",
            "etf_premium_take_profit",
            "time_decay_profit_exit",
        }:
            inferred_metric_name = "effective_pnl_ratio"
            inferred_metric_value = out.get("effective_pnl_ratio")
            inferred_metric_source = "effective_pnl_ratio"
        elif not inferred_metric_name and final_reason == "volume_exhaustion_take_profit":
            inferred_metric_name = "volume_ratio"
            inferred_metric_value = out.get("volume_ratio")
            inferred_metric_source = "selected.features.volume_ratio"
        elif not inferred_metric_name and final_reason == "vwap_extension_take_profit":
            inferred_metric_name = "vwap_distance"
            inferred_metric_value = out.get("vwap_distance")
            inferred_metric_source = "selected.features.engine_vwap_distance"
        elif not inferred_metric_name and final_reason == "resistance_take_profit":
            inferred_metric_name = "resistance_distance_pct"
            inferred_metric_value = out.get("resistance_distance_pct")
            inferred_metric_source = str(out.get("resistance_price_source") or "policy.resistance_price")
        elif not inferred_metric_name and final_reason == "peak_drawdown":
            inferred_metric_name = "peak_drawdown_ratio"
            inferred_metric_value = out.get("final_peak_drawdown_ratio")
            inferred_metric_source = str(out.get("peak_drawdown_source") or "effective_price_vs_peak_price")
        elif not inferred_metric_name and final_reason == "vwap_breakdown":
            inferred_metric_name = "vwap_distance"
            inferred_metric_value = out.get("vwap_distance")
            inferred_metric_source = "selected.features.engine_vwap_distance"
        elif not inferred_metric_name and final_reason == "trend_breakdown":
            inferred_metric_name = "trend_strength"
            inferred_metric_value = out.get("trend_strength")
            inferred_metric_source = "selected.features.engine_trend_strength"
        elif not inferred_metric_name and final_reason == "volatility_expansion":
            inferred_metric_name = "volatility_ratio"
            inferred_metric_value = out.get("volatility_ratio")
            inferred_metric_source = "current_volatility_vs_baseline"
        elif not inferred_metric_name and final_reason == "eod_flat":
            inferred_metric_name = "minutes_to_close"
            inferred_metric_value = out.get("minutes_to_close")
            inferred_metric_source = "session_clock"
        out["exit_trigger_metric_name"] = inferred_metric_name
        out["exit_trigger_metric_value"] = inferred_metric_value
        out["exit_trigger_metric_source"] = inferred_metric_source
        out["exit_trigger_basis"] = {
            "metric_name": inferred_metric_name,
            "metric_value": inferred_metric_value,
            "metric_source": inferred_metric_source,
        }
        out["final_exit_thresholds"] = dict(out.get("thresholds") or {})
        return out

    has_explicit_time_stop = "time_stop_sec" in p

    q = max(0, int(qty or 0))
    if q <= 0:
        return _finalize(reason="no_position")

    def _mark_exit_sizing(*, fraction: float = 1.0, partial: bool = False) -> None:
        frac = max(0.0, min(float(fraction or 0.0), 1.0))
        if frac <= 0.0:
            frac = 1.0
        exit_qty = max(1, int(float(q) * frac))
        exit_qty = min(int(q), int(exit_qty))
        out["exit_qty"] = int(exit_qty)
        out["exit_qty_fraction"] = float(frac)
        out["partial_exit"] = bool(partial and exit_qty < q)

    emergency_halt = _to_bool(p.get("emergency_halt"), False)
    if emergency_halt:
        return _finalize(triggered=True, reason="emergency_halt")

    use_eod_flat = _to_bool(p.get("use_eod_flat"), False)
    minutes_to_close = _to_float(p.get("minutes_to_close"), -1.0)
    eod_cutoff = int(out["thresholds"]["eod_flat_cutoff_min"])
    if use_eod_flat and minutes_to_close >= 0.0 and minutes_to_close <= float(eod_cutoff):
        out["minutes_to_close"] = float(minutes_to_close)
        return _finalize(triggered=True, reason="eod_flat")

    hs, news_shock_th, time_limit_reached, time_limit_reason = exit_pnl_hs_news_shock_th(out=out, hold_sec=hold_sec, has_explicit_time_stop=has_explicit_time_stop, facade=_r3_sys.modules[__name__])
    if news_shock_th > 0.0:
        symbol_sent = _to_float(p.get("symbol_sentiment_score"), 0.0)
        global_sent = _to_float(p.get("global_sentiment_score"), 0.0)
        out["symbol_sentiment_score"] = float(symbol_sent)
        out["global_sentiment_score"] = float(global_sent)
        if symbol_sent <= -news_shock_th or global_sent <= -news_shock_th:
            return _finalize(triggered=True, reason="news_shock")

    apx, crosscheck, px, technical_px = exit_pnl_apx_crosscheck(avg_price=avg_price, p=p, price=price, q=q, out=out, facade=_r3_sys.modules[__name__])
    if px <= 0.0 or technical_px <= 0.0 or apx <= 0.0:
        if out["price_anomaly_flag"] and not out["hold_block_reason"]:
            out["hold_block_reason"] = str(out["price_anomaly_reason"] or "price_anomaly")
        return _finalize(reason="price_unavailable")

    # Volatility expansion stop (optional).
    vol_ratio_th = float(out["thresholds"]["vol_expansion_ratio"])
    if vol_ratio_th > 0.0:
        current_vol = _to_float(p.get("current_volatility"), 0.0)
        baseline_vol = _to_float(p.get("baseline_volatility"), 0.0)
        if baseline_vol > 0.0 and current_vol > 0.0:
            vol_ratio = float(current_vol / baseline_vol)
            out["volatility_ratio"] = vol_ratio
            if vol_ratio >= vol_ratio_th:
                return _finalize(triggered=True, reason="volatility_expansion")

    gross_pnl_ratio, gross_profit_floor_gap_pct, gross_profit_floor_met, min_expected_net_profit_pct, pnl_ratio, profit_floor_enabled, profit_floor_pct, round_trip_cost_floor_pct = exit_pnl_gross_pnl_ratio_gross_profit_floor_gap_p(px=px, apx=apx, crosscheck=crosscheck, technical_px=technical_px, out=out, facade=_r3_sys.modules[__name__])

    def _first_positive_price(*keys: str) -> tuple[float, str]:
        for key in keys:
            value = p.get(key)
            if value in (None, ""):
                continue
            candidate = _to_float(value, 0.0)
            if candidate > 0.0:
                return float(candidate), key
        return 0.0, ""

    expected_exit_floor_blocked, profit_exit_metric_name, profit_exit_pnl_ratio = exit_pnl_expected_exit_floor_blocked_profit_exit(out=out, technical_px=technical_px, px=px, _first_positive_price=_first_positive_price, apx=apx, round_trip_cost_floor_pct=round_trip_cost_floor_pct, profit_floor_enabled=profit_floor_enabled, profit_floor_pct=profit_floor_pct, min_expected_net_profit_pct=min_expected_net_profit_pct, gross_profit_floor_met=gross_profit_floor_met, gross_profit_floor_gap_pct=gross_profit_floor_gap_pct, gross_pnl_ratio=gross_pnl_ratio, facade=_r3_sys.modules[__name__])

    def _profit_threshold(base: float) -> float:
        return float(max(float(base or 0.0), profit_floor_pct if profit_floor_enabled else 0.0))

    def _profit_floor_blocks_current_profit() -> bool:
        return bool(
            profit_floor_enabled
            and 0.0 < gross_pnl_ratio
            and (not bool(out.get("cost_aware_profit_floor_met")) or expected_exit_floor_blocked)
        )

    def _mark_profit_floor_blocked() -> None:
        if not _profit_floor_blocks_current_profit():
            return
        out["cost_aware_profit_floor_blocked"] = True
        if not str(out.get("hold_block_reason") or "").strip():
            out["hold_block_reason"] = (
                "expected_exit_profit_floor_not_met"
                if expected_exit_floor_blocked
                else "cost_aware_profit_floor_not_met"
            )

    def _protective_exit_hard_invalidation(reason: str) -> bool:
        r = str(reason or "").strip().lower()
        if _to_bool(p.get("hard_invalidation_confirmed"), False) or _to_bool(
            p.get(f"{r}_hard_invalidation"),
            False,
        ):
            out["protective_exit_hard_invalidation_reason"] = "explicit_policy_flag"
            return True

        structure_signal = str(out.get("structure_breakdown_signal") or "").strip()
        if structure_signal:
            out["protective_exit_hard_invalidation_reason"] = f"chart_structure:{structure_signal}"
            return True

        if r == "vwap_breakdown":
            threshold = float(out["thresholds"].get("vwap_breakdown_pct") or 0.0)
            vwap_distance = _to_float(out.get("vwap_distance"), 0.0)
            hard_multiplier = max(1.0, _to_float(p.get("vwap_breakdown_hard_multiplier"), 2.0))
            hard_extra = max(0.0, _to_float(p.get("vwap_breakdown_hard_extra_pct"), 0.005))
            hard_threshold = max(float(threshold * hard_multiplier), float(threshold + hard_extra))
            if threshold > 0.0 and vwap_distance <= -hard_threshold:
                out["protective_exit_hard_invalidation_reason"] = f"vwap_breakdown_deep:{vwap_distance:.4f}"
                return True

        if r == "intraday_low_break":
            threshold = float(out["thresholds"].get("intraday_low_break_pct") or 0.0)
            prior_bar_low = _to_float(out.get("prior_bar_low"), 0.0)
            hard_multiplier = max(1.0, _to_float(p.get("intraday_low_break_hard_multiplier"), 2.0))
            hard_extra = max(0.0, _to_float(p.get("intraday_low_break_hard_extra_pct"), 0.005))
            hard_threshold = max(float(threshold * hard_multiplier), float(threshold + hard_extra))
            if threshold > 0.0 and prior_bar_low > 0.0 and technical_px <= float(prior_bar_low * (1.0 - hard_threshold)):
                out["protective_exit_hard_invalidation_reason"] = f"intraday_low_break_deep:{hard_threshold:.4f}"
                return True

        return False

    def _block_protective_exit_below_floor(reason: str) -> bool:
        if not _profit_floor_blocks_current_profit():
            return False
        if _protective_exit_hard_invalidation(reason):
            hard_reason = str(out.get("protective_exit_hard_invalidation_reason") or "")
            metric_only_hard_invalidation = hard_reason.startswith(
                ("vwap_breakdown_deep:", "intraday_low_break_deep:")
            )
            out["protective_exit_hard_invalidation"] = True
            if not (metric_only_hard_invalidation and 0.0 < gross_pnl_ratio < profit_floor_pct):
                return False
            out["protective_exit_hard_invalidation_suppressed_by_cost_floor"] = True
            out["protective_exit_hard_invalidation_suppressed_reason"] = hard_reason
        _mark_profit_floor_blocked()
        out["protective_exit_floor_blocked"] = True
        out["protective_exit_floor_blocked_reason"] = str(reason or "")
        out["hold_block_reason"] = f"{str(reason or 'protective_exit')}:cost_aware_profit_floor_not_met"
        return True

    effective_stop_candidates, effective_stop_pct, effective_stop_reason, etf_deviation_pct, etf_deviation_source, hard_sl, sl, tp = exit_pnl_effective_stop_candidates_effective_stop(out=out, p=p, facade=_r3_sys.modules[__name__])
    if effective_stop_candidates:
        effective_stop_reason, effective_stop_pct = min(
            effective_stop_candidates,
            key=lambda row: float(row[1]),
        )
        out["thresholds"]["effective_stop_loss_pct"] = float(effective_stop_pct)
        out["thresholds"]["effective_stop_reason"] = str(effective_stop_reason)
    else:
        out["thresholds"]["effective_stop_loss_pct"] = 0.0
        out["thresholds"]["effective_stop_reason"] = ""

    _t4_ret = stop_loss_exit_check(_finalize=_finalize, hard_sl=hard_sl, out=out, pnl_ratio=pnl_ratio, sl=sl)
    if _t4_ret is not None:
        return _t4_ret

    _t4_ret = profit_target_exit_check(_finalize=_finalize, _mark_profit_floor_blocked=_mark_profit_floor_blocked, _profit_floor_blocks_current_profit=_profit_floor_blocks_current_profit, _profit_threshold=_profit_threshold, etf_deviation_pct=etf_deviation_pct, etf_deviation_source=etf_deviation_source, out=out, profit_exit_pnl_ratio=profit_exit_pnl_ratio, tp=tp)
    if _t4_ret is not None:
        return _t4_ret

    peak_price = _to_float(p.get("peak_price"), 0.0)
    if peak_price <= 0.0:
        peak_price = max(apx, technical_px)
    if peak_price > 0.0:
        max_runup_pct = float((peak_price / apx) - 1.0) if apx > 0.0 else 0.0
        peak_drawdown = float((technical_px / peak_price) - 1.0)
        peak_drawdown_mode = str(out["thresholds"].get("peak_drawdown_mode") or "profit_protection").strip().lower()
        if not peak_drawdown_mode:
            peak_drawdown_mode = "profit_protection"
        activation_pct = _profit_threshold(float(out["thresholds"].get("profit_protection_activation_pct") or 0.0))
        peak_profit_floor_required_pct = float(activation_pct)
        peak_profit_floor_met = bool(max_runup_pct >= peak_profit_floor_required_pct)
        peak_drawdown_block_reason = ""
        if peak_drawdown_mode in {"disabled", "off", "none"}:
            peak_drawdown_armed = False
        elif peak_drawdown_mode in {"profit_protection", "profit-protection"}:
            peak_drawdown_armed = bool(peak_profit_floor_met)
            if not peak_drawdown_armed:
                peak_drawdown_block_reason = "profit_floor_not_reached"
        else:
            peak_drawdown_armed = True
            peak_profit_floor_met = True
        peak_drawdown_th, profit_protection_urgent = exit_trigger_peak_drawdown_th_profit_protection_urgen(max_runup_pct=max_runup_pct, out=out, peak_drawdown=peak_drawdown, peak_drawdown_armed=peak_drawdown_armed, peak_drawdown_mode=peak_drawdown_mode, peak_drawdown_block_reason=peak_drawdown_block_reason, peak_profit_floor_required_pct=peak_profit_floor_required_pct, peak_profit_floor_met=peak_profit_floor_met, profit_floor_enabled=profit_floor_enabled, profit_floor_pct=profit_floor_pct, gross_pnl_ratio=gross_pnl_ratio, facade=_r3_sys.modules[__name__])
        if (
            peak_drawdown_th > 0.0
            and peak_drawdown_armed
            and peak_drawdown <= -peak_drawdown_th
            and (profit_protection_urgent or not _profit_floor_blocks_current_profit())
        ):
            return _finalize(
                triggered=True,
                reason="peak_drawdown",
                metric_name="peak_drawdown_ratio",
                metric_value=peak_drawdown,
                metric_source=str(out.get("peak_drawdown_source") or "technical_price_vs_peak_price"),
            )

    _t4_ret = vwap_breakdown_exit_check(_block_protective_exit_below_floor=_block_protective_exit_below_floor, _finalize=_finalize, apx=apx, gross_pnl_ratio=gross_pnl_ratio, hs=hs, out=out, p=p, peak_price=peak_price, facade=_r3_sys.modules[__name__])
    if _t4_ret is not None:
        return _t4_ret

    _t4_ret = intraday_low_break_exit_check(_block_protective_exit_below_floor=_block_protective_exit_below_floor, _finalize=_finalize, _protective_exit_hard_invalidation=_protective_exit_hard_invalidation, hs=hs, out=out, p=p, technical_px=technical_px, facade=_r3_sys.modules[__name__])
    if _t4_ret is not None:
        return _t4_ret

    _t4_ret = trend_strength_exit_check(_finalize=_finalize, out=out, p=p, facade=_r3_sys.modules[__name__])
    if _t4_ret is not None:
        return _t4_ret

    _t4_ret = opening_gap_profit_take_exit_check(_finalize=_finalize, _mark_exit_sizing=_mark_exit_sizing, _profit_floor_blocks_current_profit=_profit_floor_blocks_current_profit, _profit_threshold=_profit_threshold, hs=hs, out=out, p=p, profit_exit_metric_name=profit_exit_metric_name, profit_exit_pnl_ratio=profit_exit_pnl_ratio, facade=_r3_sys.modules[__name__])
    if _t4_ret is not None:
        return _t4_ret

    _t4_ret = volume_exhaustion_exit_check(_finalize=_finalize, _profit_floor_blocks_current_profit=_profit_floor_blocks_current_profit, _profit_threshold=_profit_threshold, out=out, p=p, profit_exit_pnl_ratio=profit_exit_pnl_ratio, facade=_r3_sys.modules[__name__])
    if _t4_ret is not None:
        return _t4_ret

    partial_take_profit_pct = float(out["thresholds"]["partial_take_profit_pct"])
    partial_take_profit_effective_pct = _profit_threshold(partial_take_profit_pct)
    partial_take_profit_taken = _to_bool(p.get("partial_take_profit_taken"), False)
    out["partial_take_profit_taken"] = bool(partial_take_profit_taken)
    _t4_ret = partial_take_profit_exit_check(_finalize=_finalize, _mark_exit_sizing=_mark_exit_sizing, _profit_floor_blocks_current_profit=_profit_floor_blocks_current_profit, out=out, partial_take_profit_effective_pct=partial_take_profit_effective_pct, partial_take_profit_pct=partial_take_profit_pct, partial_take_profit_taken=partial_take_profit_taken, profit_exit_metric_name=profit_exit_metric_name, profit_exit_pnl_ratio=profit_exit_pnl_ratio)
    if _t4_ret is not None:
        return _t4_ret

    _t4_ret = profit_ladder_exit_check(_finalize=_finalize, _mark_exit_sizing=_mark_exit_sizing, _profit_floor_blocks_current_profit=_profit_floor_blocks_current_profit, _profit_threshold=_profit_threshold, out=out, p=p, partial_take_profit_pct=partial_take_profit_pct, profit_exit_metric_name=profit_exit_metric_name, profit_exit_pnl_ratio=profit_exit_pnl_ratio, facade=_r3_sys.modules[__name__])
    if _t4_ret is not None:
        return _t4_ret

    _t4_ret = risk_reward_exit_check(_finalize=_finalize, _mark_exit_sizing=_mark_exit_sizing, _profit_floor_blocks_current_profit=_profit_floor_blocks_current_profit, _profit_threshold=_profit_threshold, effective_stop_pct=effective_stop_pct, out=out, p=p, profit_exit_metric_name=profit_exit_metric_name, profit_exit_pnl_ratio=profit_exit_pnl_ratio, facade=_r3_sys.modules[__name__])
    if _t4_ret is not None:
        return _t4_ret

    _t4_ret = resistance_target_exit_check(_finalize=_finalize, _profit_floor_blocks_current_profit=_profit_floor_blocks_current_profit, _profit_threshold=_profit_threshold, hs=hs, out=out, p=p, peak_drawdown=peak_drawdown, peak_price=peak_price, profit_exit_metric_name=profit_exit_metric_name, profit_exit_pnl_ratio=profit_exit_pnl_ratio, technical_px=technical_px, facade=_r3_sys.modules[__name__])
    if _t4_ret is not None:
        return _t4_ret

    # Trailing stop (optional).
    _t4_ret = trailing_stop_exit_check(_finalize=_finalize, _profit_floor_blocks_current_profit=_profit_floor_blocks_current_profit, out=out, peak_price=peak_price, technical_px=technical_px)
    if _t4_ret is not None:
        return _t4_ret

    _t4_ret = time_limit_exit_check(_finalize=_finalize, _mark_profit_floor_blocked=_mark_profit_floor_blocked, expected_exit_floor_blocked=expected_exit_floor_blocked, gross_pnl_ratio=gross_pnl_ratio, hs=hs, out=out, profit_floor_enabled=profit_floor_enabled, time_limit_reached=time_limit_reached, time_limit_reason=time_limit_reason)
    if _t4_ret is not None:
        return _t4_ret

    _mark_profit_floor_blocked()
    if out["price_anomaly_flag"] and not out["hold_block_reason"]:
        out["hold_block_reason"] = f"price_anomaly_fallback:{str(out.get('price_anomaly_reason') or '')}".strip(":")
    return _finalize(reason="hold")
