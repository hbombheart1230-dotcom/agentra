"""Strategist stage-specific LLM review normalisation helpers (post-processing of already received output).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _stage_text_list_r3_impl(raw, *, limit, upper, facade):
    values = facade._parse_text_list_fragment(raw)
    out: List[str] = []
    seen: set[str] = set()
    for item in values:
        text = str(item or "").strip()
        if upper:
            text = text.upper()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
        if len(out) >= int(limit):
            break
    return out


def _stage_bool_r3_impl(raw, default, *, facade):
    if raw is None:
        return bool(default)
    text = str(raw).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return bool(raw) if isinstance(raw, bool) else bool(default)


def _stage_float_r3_impl(raw, default, *, facade):
    try:
        if raw in (None, ""):
            return default
        return float(raw)
    except Exception:
        return default


def _normalize_stage2_selected_symbol_review_r3_impl(raw, *, facade):
    if not isinstance(raw, dict) or "selected_symbol_decision" not in raw:
        return {}
    allowed_decisions = {
        "watch_rank1",
        "avoid_rank1",
        "watch_rank1_with_tighter_gates",
        "cascade_to_runner_up",
        "no_trade",
    }
    decision = str(raw.get("selected_symbol_decision") or "").strip().lower()
    if decision not in allowed_decisions:
        decision = "watch_rank1"
    monitor_instruction_raw = (
        dict(raw.get("monitor_instruction") or {})
        if isinstance(raw.get("monitor_instruction"), dict)
        else {}
    )
    watch_intensity = str(monitor_instruction_raw.get("watch_intensity") or "normal").strip().lower()
    if watch_intensity not in {"normal", "strict", "aggressive"}:
        watch_intensity = "normal"
    entry_delta_raw = (
        dict(raw.get("entry_policy_delta") or {})
        if isinstance(raw.get("entry_policy_delta"), dict)
        else {}
    )
    memory_usage_raw = dict(raw.get("memory_usage") or {}) if isinstance(raw.get("memory_usage"), dict) else {}
    memory_status = str(memory_usage_raw.get("status") or "").strip().lower()
    if memory_status not in {"used", "disabled", "insufficient", "stale"}:
        memory_status = "disabled" if facade._strategy_memory_usage_disabled(raw) else "insufficient"
    actionability = str(raw.get("commander_actionability") or "advisory_only").strip().lower()
    if actionability not in {"advisory_only", "policy_delta_allowed", "hard_block_recommended"}:
        actionability = "advisory_only"
    news_event_usage = (
        dict(raw.get("news_event_intelligence_usage") or {})
        if isinstance(raw.get("news_event_intelligence_usage"), dict)
        else {}
    )
    if news_event_usage:
        status = str(news_event_usage.get("status") or "insufficient").strip().lower()
        if status not in {"used", "ignored", "insufficient"}:
            status = "insufficient"
        news_event_usage = {
            "status": status,
            "used_event_ids": facade._stage_text_list(news_event_usage.get("used_event_ids"), limit=8),
            "theme_watchlist": facade._stage_text_list(news_event_usage.get("theme_watchlist"), limit=8),
            "symbol_watchlist": facade._stage_text_list(news_event_usage.get("symbol_watchlist"), limit=8, upper=True),
            "reason": str(news_event_usage.get("reason") or "").strip(),
            "observation_only": True,
        }
    return {
        "schema_version": "strategist.stage2.selected_symbol_tactical_review.v1",
        "stage_name": "selected_symbol_tactical_refresh",
        "selected_symbol_decision": decision,
        "target_symbol": str(raw.get("target_symbol") or "").strip().upper(),
        "target_rank": max(0, facade._to_int(raw.get("target_rank"), 0)),
        "runner_up_order": facade._stage_text_list(raw.get("runner_up_order"), limit=8, upper=True),
        "monitor_instruction": {
            "watch_intensity": watch_intensity,
            "required_confirmations": facade._stage_text_list(
                monitor_instruction_raw.get("required_confirmations"),
                limit=8,
            ),
            "avoid_if": facade._stage_text_list(monitor_instruction_raw.get("avoid_if"), limit=8),
        },
        "entry_policy_delta": {
            "tighten_confidence_threshold": facade._stage_bool(entry_delta_raw.get("tighten_confidence_threshold")),
            "require_prev_close_context": facade._stage_bool(entry_delta_raw.get("require_prev_close_context"), True),
            "require_cost_hurdle": facade._stage_bool(entry_delta_raw.get("require_cost_hurdle"), True),
        },
        "memory_usage": {
            "status": memory_status,
            "sample_count": max(0, facade._to_int(memory_usage_raw.get("sample_count"), 0)),
            "confidence": str(memory_usage_raw.get("confidence") or "").strip().lower(),
            "data_quality": str(memory_usage_raw.get("data_quality") or "").strip().lower(),
            "effect": str(memory_usage_raw.get("effect") or "neutral").strip().lower(),
            "reason": str(memory_usage_raw.get("reason") or "").strip(),
        },
        "commander_actionability": actionability,
        "confidence": facade._stage_float(raw.get("confidence"), 0.0),
        "market_regime_rail": str(raw.get("market_regime_rail") or "").strip(),
        "news_quality": dict(raw.get("news_quality") or {}) if isinstance(raw.get("news_quality"), dict) else {},
        "news_event_intelligence_usage": dict(news_event_usage),
        "risk_off_exception_conditions": facade._stage_text_list(raw.get("risk_off_exception_conditions"), limit=8),
        "reason": str(raw.get("reason") or "").strip(),
    }


def _normalize_stage3_hold_review_r3_impl(raw, *, facade):
    if not isinstance(raw, dict) or "hold_review_decision" not in raw:
        return {}
    decision = str(raw.get("hold_review_decision") or "").strip().lower()
    if decision not in {"hold", "tighten_exit", "exit_now", "wait_until_next_check"}:
        decision = "wait_until_next_check"
    exit_pressure = str(raw.get("exit_pressure") or "medium").strip().lower()
    if exit_pressure not in {"low", "medium", "high"}:
        exit_pressure = "medium"
    thesis_status = str(raw.get("thesis_status") or "weakened").strip().lower()
    if thesis_status not in {"intact", "weakened", "broken"}:
        thesis_status = "weakened"
    adjustment_raw = (
        dict(raw.get("monitor_adjustment") or {})
        if isinstance(raw.get("monitor_adjustment"), dict)
        else {}
    )
    next_check = max(1, facade._to_int(raw.get("next_check_minutes") or adjustment_raw.get("next_check_minutes"), 5))
    return {
        "schema_version": "strategist.stage3.stale_intraday_hold_review.v1",
        "stage_name": "stale_intraday_hold_review",
        "hold_review_decision": decision,
        "horizon_action": str(raw.get("horizon_action") or "maintain").strip().lower(),
        "current_horizon": str(raw.get("current_horizon") or "").strip().lower(),
        "proposed_horizon": str(raw.get("proposed_horizon") or "").strip().lower(),
        "revised_hold_window": (
            dict(raw.get("revised_hold_window") or {})
            if isinstance(raw.get("revised_hold_window"), dict)
            else {}
        ),
        "exit_pressure": exit_pressure,
        "thesis_status": thesis_status,
        "evidence_confidence": str(raw.get("evidence_confidence") or "low").strip().lower(),
        "data_quality": str(raw.get("data_quality") or "insufficient").strip().lower(),
        "monitor_adjustment": {
            "tighten_stop": facade._stage_bool(adjustment_raw.get("tighten_stop")),
            "tighten_time_decay": facade._stage_bool(adjustment_raw.get("tighten_time_decay")),
            "allow_profit_recovery_wait": facade._stage_bool(adjustment_raw.get("allow_profit_recovery_wait")),
            "next_check_minutes": next_check,
        },
        "priority_exit_triggers": facade._stage_text_list(raw.get("priority_exit_triggers"), limit=8),
        "next_check_minutes": next_check,
        "reason": str(raw.get("reason") or "").strip(),
    }


def _normalize_stage4_carry_review_r3_impl(raw, *, facade):
    if not isinstance(raw, dict) or "carry_review" not in raw:
        return {}
    rows: List[Dict[str, Any]] = []
    for item in list(raw.get("carry_review") or [])[:8]:
        if not isinstance(item, dict):
            continue
        decision = str(item.get("decision") or "").strip().lower()
        if decision not in {"carry_overnight", "flatten_today", "reduce_or_flatten"}:
            decision = "flatten_today"
        confidence = str(item.get("carry_confidence") or "low").strip().lower()
        if confidence not in {"low", "medium", "high"}:
            confidence = "low"
        plan = dict(item.get("required_next_day_plan") or {}) if isinstance(item.get("required_next_day_plan"), dict) else {}
        rows.append(
            {
                "symbol": str(item.get("symbol") or "").strip().upper(),
                "decision": decision,
                "carry_confidence": confidence,
                "required_next_day_plan": {
                    "gap_down_action": str(plan.get("gap_down_action") or "").strip(),
                    "gap_up_action": str(plan.get("gap_up_action") or "").strip(),
                    "flat_open_action": str(plan.get("flat_open_action") or "").strip(),
                },
                "reason": str(item.get("reason") or "").strip(),
            }
        )
    portfolio_level = str(raw.get("portfolio_level_decision") or "flatten_all").strip().lower()
    if portfolio_level not in {"carry_allowed", "flatten_all", "carry_only_best_one"}:
        portfolio_level = "flatten_all"
    return {
        "schema_version": "strategist.stage4.end_of_day_carry_review.v1",
        "stage_name": "end_of_day_carry_review",
        "carry_review": rows,
        "portfolio_level_decision": portfolio_level,
        "risk_note": str(raw.get("risk_note") or "").strip(),
    }
