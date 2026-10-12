"""Scanner repeat-symbol / blocker-cooldown penalty policy and blocker-family normalisation (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _resolve_scanner_repeat_guard_policy_r3_impl(policy, *, facade):
    raw_policy = policy.get("scanner_repeat_guard") if isinstance(policy.get("scanner_repeat_guard"), dict) else {}
    lookback_sec = facade._to_int(
        raw_policy.get("lookback_sec", facade.os.getenv("SCANNER_REPEAT_LOOKBACK_SEC", "1800")),
        1800,
    )
    per_hit_penalty = facade._to_float(
        raw_policy.get("per_hit_penalty", facade.os.getenv("SCANNER_REPEAT_SYMBOL_PENALTY", "0.06"))
    )
    recent_trade_penalty = facade._to_float(
        raw_policy.get("recent_trade_penalty", facade.os.getenv("SCANNER_RECENT_TRADE_SYMBOL_PENALTY", "0.10"))
    )
    trade_lookback_sec = facade._to_int(
        raw_policy.get("trade_lookback_sec", facade.os.getenv("SCANNER_RECENT_TRADE_LOOKBACK_SEC", "5400")),
        5400,
    )
    max_penalty = facade._to_float(
        raw_policy.get("max_penalty", facade.os.getenv("SCANNER_REPEAT_SYMBOL_MAX_PENALTY", "0.40"))
    )
    streak_threshold = facade._to_int(
        raw_policy.get("streak_threshold", facade.os.getenv("SCANNER_REPEAT_STREAK_THRESHOLD", "3")),
        3,
    )
    streak_penalty = facade._to_float(
        raw_policy.get("streak_penalty", facade.os.getenv("SCANNER_REPEAT_STREAK_PENALTY", "0.12"))
    )
    history_limit = facade._to_int(
        raw_policy.get("history_limit", facade.os.getenv("SCANNER_REPEAT_HISTORY_LIMIT", "40")),
        40,
    )
    blocker_lookback_sec = facade._to_int(
        raw_policy.get("blocker_lookback_sec", facade.os.getenv("SCANNER_REPEAT_BLOCK_LOOKBACK_SEC", "900")),
        900,
    )
    blocker_per_hit_penalty = facade._to_float(
        raw_policy.get("blocker_per_hit_penalty", facade.os.getenv("SCANNER_REPEAT_BLOCK_PENALTY", "0.08"))
    )
    blocker_max_penalty = facade._to_float(
        raw_policy.get("blocker_max_penalty", facade.os.getenv("SCANNER_REPEAT_BLOCK_MAX_PENALTY", "0.18"))
    )
    return {
        "lookback_sec": max(0, int(lookback_sec)),
        "per_hit_penalty": max(0.0, float(per_hit_penalty)),
        "recent_trade_penalty": max(0.0, float(recent_trade_penalty)),
        "trade_lookback_sec": max(0, int(trade_lookback_sec)),
        "max_penalty": max(0.0, float(max_penalty)),
        "streak_threshold": max(2, int(streak_threshold)),
        "streak_penalty": max(0.0, float(streak_penalty)),
        "history_limit": max(5, int(history_limit)),
        "blocker_lookback_sec": max(0, int(blocker_lookback_sec)),
        "blocker_per_hit_penalty": max(0.0, float(blocker_per_hit_penalty)),
        "blocker_max_penalty": max(0.0, float(blocker_max_penalty)),
    }


def _scanner_recent_selection_history_r3_impl(state, *, facade):
    persisted = state.get("persisted_state") if isinstance(state.get("persisted_state"), dict) else {}
    rows = persisted.get("recent_scanner_selected")
    if not isinstance(rows, list):
        return []
    out: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        sym = facade._norm_symbol(row.get("symbol"))
        epoch = facade._to_int(row.get("epoch"), 0)
        if sym and epoch > 0:
            out.append({"symbol": sym, "epoch": epoch})
    return out


def _scanner_recent_block_history_r3_impl(state, *, facade):
    persisted = state.get("persisted_state") if isinstance(state.get("persisted_state"), dict) else {}
    rows = persisted.get("recent_monitor_blocks")
    if not isinstance(rows, list):
        return []
    out: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        sym = facade._norm_symbol(row.get("symbol"))
        reason = str(row.get("reason") or "").strip()
        epoch = facade._to_int(row.get("epoch"), 0)
        if sym and reason and epoch > 0:
            out.append({"symbol": sym, "reason": reason, "epoch": epoch})
    return out


def _repeat_symbol_penalty_r3_impl(state, *, symbol, policy, facade):
    cfg = facade._resolve_scanner_repeat_guard_policy(policy)
    now_epoch = facade._resolve_now_epoch(state)
    history = facade._scanner_recent_selection_history(state)
    sel = facade._norm_symbol(symbol)
    repeat_count = 0
    streak_count = 0
    if cfg["lookback_sec"] > 0 and sel:
        cutoff = max(0, now_epoch - cfg["lookback_sec"])
        for row in history:
            if row.get("symbol") == sel and facade._to_int(row.get("epoch"), 0) >= cutoff:
                repeat_count += 1
        for row in reversed(history):
            if facade._to_int(row.get("epoch"), 0) < cutoff:
                break
            if row.get("symbol") != sel:
                break
            streak_count += 1

    persisted = state.get("persisted_state") if isinstance(state.get("persisted_state"), dict) else {}
    last_trade_symbol = facade._norm_symbol(persisted.get("last_trade_symbol"))
    last_trade_epoch = facade._to_int(persisted.get("last_trade_epoch"), 0)
    recent_trade_same_symbol = False
    if (
        sel
        and last_trade_symbol == sel
        and last_trade_epoch > 0
        and cfg["trade_lookback_sec"] > 0
        and (now_epoch - last_trade_epoch) <= cfg["trade_lookback_sec"]
    ):
        recent_trade_same_symbol = True

    streak_extra = cfg["streak_penalty"] if streak_count >= cfg["streak_threshold"] else 0.0
    penalty = min(
        cfg["max_penalty"],
        (repeat_count * cfg["per_hit_penalty"])
        + streak_extra
        + (cfg["recent_trade_penalty"] if recent_trade_same_symbol else 0.0),
    )
    return {
        "penalty": float(max(0.0, penalty)),
        "repeat_count": int(repeat_count),
        "streak_count": int(streak_count),
        "recent_trade_same_symbol": bool(recent_trade_same_symbol),
        "now_epoch": int(now_epoch),
        "history_count": int(len(history)),
        "config": cfg,
    }


def _repeat_blocker_cooldown_penalty_r3_impl(state, *, symbol, policy, facade):
    cfg = facade._resolve_scanner_repeat_guard_policy(policy)
    now_epoch = facade._resolve_now_epoch(state)
    sel = facade._norm_symbol(symbol)
    if not sel or cfg["blocker_lookback_sec"] <= 0:
        return {
            "penalty": 0.0,
            "reason": "",
            "repeat_count": 0,
            "config": cfg,
        }

    cutoff = max(0, now_epoch - cfg["blocker_lookback_sec"])
    history = facade._scanner_recent_block_history(state)
    reason_counter: Dict[str, int] = {}
    for row in history:
        if row.get("symbol") != sel:
            continue
        if facade._to_int(row.get("epoch"), 0) < cutoff:
            continue
        reason = str(row.get("reason") or "").strip()
        if not reason:
            continue
        reason_counter[reason] = int(reason_counter.get(reason, 0)) + 1

    if not reason_counter:
        return {
            "penalty": 0.0,
            "reason": "",
            "repeat_count": 0,
            "config": cfg,
        }

    dominant_reason, repeat_count = max(reason_counter.items(), key=lambda item: item[1])
    weight = 0.0
    if dominant_reason == "too_extended_from_vwap":
        weight = 1.0
    elif dominant_reason in {"volume_insufficient", "volume_confirmation_missing"}:
        weight = 0.5
    elif dominant_reason in {"breakout_not_ready", "below_vwap_reclaim_not_ready", "pullback_below_vwap_reclaim_not_ready"}:
        weight = 0.35

    penalty = min(
        cfg["blocker_max_penalty"],
        float(repeat_count) * cfg["blocker_per_hit_penalty"] * float(weight),
    )
    return {
        "penalty": float(max(0.0, penalty)),
        "reason": str(dominant_reason),
        "repeat_count": int(repeat_count),
        "config": cfg,
    }


def _normalize_scanner_blocker_family_r3_impl(value, *, facade):
    text = str(value or "").strip().lower()
    if not text or text in {"mixed", "none"}:
        return ""
    if text in {"buy_blocked_open_position", "open_position_blocked"}:
        return "open_position_guard"
    if text.startswith("entry_guard_cooldown") or "cooldown" in text:
        return "cooldown_guard"
    if text in {
        "pullback_not_mature",
        "pullback_mature",
        "pullback_ok",
        "pullback_structure_ok",
        "pullback_volume_path_ok",
        "pullback_below_vwap_reclaim_not_ready",
    } or "pullback" in text:
        return "pullback_timing"
    if "extend" in text or "overextended" in text:
        return "overextension_guard"
    if text in {
        "below_vwap_reclaim_not_ready",
        "vwap_reclaim_ok",
        "reclaim_gate_ok",
        "vwap_hold_ok",
    } or "reclaim" in text or "vwap" in text:
        return "reclaim_readiness"
    if text in {"volume_confirmation_missing", "volume_insufficient", "volume_ok"} or "volume" in text:
        return "volume_confirmation"
    if text in {
        "breakout_not_ready",
        "breakout_ok",
        "breakout_path_ok",
        "wait_for_confirmation",
    } or "breakout" in text or "confirmation" in text:
        return "breakout_confirmation"
    if text in {"rebound_ok"} or "rebound" in text:
        return "rebound_confirmation"
    if text in {"structure_hh_hl", "chart_structure_guard"} or "structure" in text:
        return "structure_confirmation"
    if text in {"confidence_gate_ok"} or "confidence" in text:
        return "confidence_gate"
    if text.startswith("risk_") or text == "risk_blocked":
        return "risk_guard"
    if text == "unknown":
        return "unknown"
    return "other"


def _candidate_blocker_families_r3_impl(row, *, facade):
    if not isinstance(row, facade.Mapping):
        return []
    out: List[str] = []
    seen = set()
    for raw in (
        row.get("expected_monitor_block_reason"),
        row.get("dominant_block_reason"),
    ):
        family = facade._normalize_scanner_blocker_family(raw)
        if not family or family in {"unknown", "other"} or family in seen:
            continue
        seen.add(family)
        out.append(family)
    return out
