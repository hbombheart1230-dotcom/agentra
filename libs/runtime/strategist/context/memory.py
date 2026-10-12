"""Strategist LLM-context memory/feedback compaction and playbook memory neutralisation (pure projections).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _strategy_memory_usage_disabled_r3_impl(policy_or_payload, *, facade):
    obj = dict(policy_or_payload or {}) if isinstance(policy_or_payload, dict) else {}
    commander_policy = (
        dict(obj.get("commander_memory_policy") or {})
        if isinstance(obj.get("commander_memory_policy"), dict)
        else obj
    )
    applied_policy = obj.get("applied_policy") if isinstance(obj.get("applied_policy"), dict) else {}
    commander_applied = applied_policy.get("commander") if isinstance(applied_policy.get("commander"), dict) else {}
    strategist_applied = applied_policy.get("strategist") if isinstance(applied_policy.get("strategist"), dict) else {}
    commander_memory_usage = (
        commander_applied.get("memory_usage")
        if isinstance(commander_applied.get("memory_usage"), dict)
        else {}
    )
    strategist_memory_usage = (
        strategist_applied.get("memory_usage")
        if isinstance(strategist_applied.get("memory_usage"), dict)
        else {}
    )
    return bool(
        facade._env_bool("STRATEGIST_MEMORY_USAGE_DISABLED", False)
        or facade._env_bool("COMMANDER_MEMORY_USAGE_DISABLED", False)
        or bool(obj.get("strategist_memory_usage_disabled"))
        or bool(obj.get("commander_memory_usage_disabled"))
        or bool(strategist_memory_usage.get("disabled"))
        or bool(commander_memory_usage.get("disabled"))
        or str(commander_policy.get("application_mode") or "").strip().lower() == "disabled"
        or bool(commander_policy.get("disabled"))
    )


def _neutralize_ambiguous_playbook_memory_r3_impl(memory, *, facade):
    out = dict(memory or {})
    best = [str(x or "").strip() for x in list(out.get("best_playbooks") or []) if str(x or "").strip()]
    worst = [str(x or "").strip() for x in list(out.get("worst_playbooks") or []) if str(x or "").strip()]
    overlap = {x.lower() for x in best}.intersection({x.lower() for x in worst})
    if not overlap:
        return out

    out["best_playbooks"] = [x for x in best if x.lower() not in overlap]
    out["worst_playbooks"] = [x for x in worst if x.lower() not in overlap]
    flags = [str(x or "") for x in list(out.get("memory_quality_flags") or []) if str(x or "").strip()]
    flags.append("ambiguous_playbook_performance:best_worst_overlap")
    out["memory_quality_flags"] = list(dict.fromkeys(flags))
    notes = [str(x or "") for x in list(out.get("advisory_notes") or []) if str(x or "").strip()]
    notes.append("best_playbooks and worst_playbooks overlapped; overlapping playbooks are not used as directional bias.")
    out["advisory_notes"] = list(dict.fromkeys(notes))
    out["directional_bias_usable"] = bool(out["best_playbooks"] or out["worst_playbooks"])
    return out


def _symbol_memory_model_has_signal_r3_impl(model, *, facade):
    if not isinstance(model, dict) or not model:
        return False
    if int(model.get("trade_count") or 0) > 0:
        return True
    if int(model.get("closed_trade_count") or 0) > 0:
        return True
    if list(model.get("repeated_failure_pattern") or []):
        return True
    if list(model.get("recent_success_pattern") or []):
        return True
    if str(model.get("dominant_playbook") or "").strip().lower() not in ("", "unknown"):
        return True
    if str(model.get("dominant_monitor_blocker") or "").strip().lower() not in ("", "unknown"):
        return True
    if str(model.get("dominant_exit_reason") or "").strip().lower() not in ("", "unknown"):
        return True
    return False


def _compact_recent_strategy_feedback_for_llm_r3_impl(feedback, *, facade):
    src = feedback if isinstance(feedback, dict) else {}
    status = str(src.get("status") or "")
    if status in {"stale", "disabled", "empty"}:
        return {
            "schema_version": str(
                src.get("schema_version") or "recent_strategy_feedback.v2"
            ),
            "status": status,
            "feedback_window_size": int(src.get("feedback_window_size") or 0),
            "latest_feedback_day": str(src.get("latest_feedback_day") or ""),
            "age_days": src.get("age_days"),
            "performance_authority": str(
                src.get("performance_authority")
                or "reports.performance.strategy_memory"
            ),
            "legacy_reporter_feedback_role": "excluded_from_strategy_input",
            "quality_flags": [
                str(value)
                for value in list(src.get("quality_flags") or [])[:4]
                if str(value or "").strip()
            ],
            "advisory_only": True,
        }
    return {
        "schema_version": str(
            src.get("schema_version") or "recent_strategy_feedback.v2"
        ),
        "status": status or "ok",
        "feedback_window_size": int(src.get("feedback_window_size") or 0),
        "latest_feedback_day": str(src.get("latest_feedback_day") or ""),
        "age_days": src.get("age_days"),
        "performance_authority": str(
            src.get("performance_authority")
            or "reports.performance.strategy_memory"
        ),
        "legacy_reporter_feedback_role": str(
            src.get("legacy_reporter_feedback_role") or "qualitative_only"
        ),
        "performance_metric_usable": bool(
            src.get("performance_metric_usable")
        ),
        "top_recent_strengths": [str(x or "") for x in list(src.get("top_recent_strengths") or [])[:3]],
        "top_recent_weaknesses": [str(x or "") for x in list(src.get("top_recent_weaknesses") or [])[:4]],
        "recent_reporter_summary": [str(x or "") for x in list(src.get("recent_reporter_summary") or [])[:2]],
        "suggested_report_focus": [str(x or "") for x in list(src.get("suggested_report_focus") or [])[:4]],
        "recent_theme_performance": facade._compact_performance_summary_map(src.get("recent_theme_performance"), max_items=3),
        "recent_playbook_performance": facade._compact_performance_summary_map(src.get("recent_playbook_performance"), max_items=3),
        "quality_flags": [
            str(value)
            for value in list(src.get("quality_flags") or [])[:4]
            if str(value or "").strip()
        ],
        "advisory_only": bool(src.get("advisory_only", True)),
    }


def _compact_reporter_feedback_for_llm_r3_impl(packet, *, facade):
    src = packet if isinstance(packet, dict) else {}
    route_analysis = src.get("route_analysis") if isinstance(src.get("route_analysis"), dict) else {}
    blocker_analysis = list(src.get("blocker_analysis") or [])
    dominant_patterns = list(src.get("dominant_patterns") or [])
    return {
        "available": bool(src.get("available")),
        "status": str(src.get("status") or ""),
        "feedback_mode": str(src.get("feedback_mode") or "deterministic"),
        "reporter_feedback_mode": str(src.get("reporter_feedback_mode") or "auto"),
        "reporter_feedback_mode_source": str(src.get("reporter_feedback_mode_source") or "default_auto"),
        "consumed": bool(src.get("consumed")),
        "feedback_gate_reason": str(src.get("feedback_gate_reason") or ""),
        "confidence": str(src.get("confidence") or "none"),
        "insight_summary": str(src.get("insight_summary") or "")[:240],
        "route_analysis": {
            "route_source": str(route_analysis.get("route_source") or ""),
            "route_selected_total": dict(route_analysis.get("route_selected_total") or {}),
            "monitor_only_ratio": facade._round_optional(route_analysis.get("monitor_only_ratio"), 4),
            "cached_strategist_ratio": facade._round_optional(route_analysis.get("cached_strategist_ratio"), 4),
            "full_cycle_ratio": facade._round_optional(route_analysis.get("full_cycle_ratio"), 4),
        },
        "blocker_analysis": [
            {
                "blocker": str((item or {}).get("blocker") or ""),
                "count": int((item or {}).get("count") or 0),
                "ratio": facade._round_optional((item or {}).get("ratio"), 4),
            }
            for item in blocker_analysis[:3]
            if isinstance(item, dict)
        ],
        "dominant_patterns": [
            {
                "name": str((item or {}).get("name") or ""),
                "value": (item or {}).get("value"),
                "detail": str((item or {}).get("detail") or ""),
            }
            for item in dominant_patterns[:4]
            if isinstance(item, dict)
        ],
        "recommendation": [str(x or "") for x in list(src.get("recommendation") or [])[:3] if str(x or "").strip()],
        "advisory_only": True,
    }


def _compact_strategy_memory_for_llm_r3_impl(memory, *, facade):
    src = memory if isinstance(memory, dict) else {}
    market_bias = src.get("market_condition_bias") if isinstance(src.get("market_condition_bias"), dict) else {}
    reporter_digest = src.get("reporter_analysis_digest") if isinstance(src.get("reporter_analysis_digest"), dict) else {}
    playbook_snapshot_src = (
        src.get("playbook_performance_snapshot")
        if isinstance(src.get("playbook_performance_snapshot"), dict)
        else {}
    )
    playbook_snapshot: Dict[str, Any] = {}
    for key, value in list(playbook_snapshot_src.items())[:4]:
        item = value if isinstance(value, dict) else {}
        playbook_snapshot[str(key)] = {
            "usage_count": int(item.get("usage_count") or 0),
            "win_rate": facade._round_optional(item.get("win_rate"), 4),
            "avg_return": facade._round_optional(item.get("avg_return"), 4),
            "stability_score": facade._round_optional(item.get("stability_score"), 4),
        }
    pattern_snapshot = facade._compact_pattern_performance_for_llm(src.get("pattern_performance_snapshot"))
    preferred_regimes = [
        str(x or "")
        for x in list(market_bias.get("preferred_regimes") or [])[:3]
        if str(x or "").strip()
    ]
    avoid_regimes = [
        str(x or "")
        for x in list(market_bias.get("avoid_regimes") or [])[:3]
        if str(x or "").strip()
    ]
    compact = {
        "status": str(src.get("status") or ""),
        "day": str(src.get("day") or ""),
        "best_playbooks": [str(x or "") for x in list(src.get("best_playbooks") or [])[:3] if str(x or "").strip()],
        "worst_playbooks": [str(x or "") for x in list(src.get("worst_playbooks") or [])[:3] if str(x or "").strip()],
        "recent_failures": [str(x or "") for x in list(src.get("recent_failures") or [])[:4] if str(x or "").strip()],
        "recent_success_patterns": [
            str(x or "")
            for x in list(src.get("recent_success_patterns") or [])[:4]
            if str(x or "").strip()
        ],
        "market_condition_bias": {
            "preferred_regimes": preferred_regimes,
            "avoid_regimes": avoid_regimes,
        },
        "playbook_performance_snapshot": playbook_snapshot,
        "pattern_performance_snapshot": pattern_snapshot,
        "reporter_analysis_digest": {
            "available": bool(reporter_digest.get("available")),
            "ai_run_grade": str(reporter_digest.get("ai_run_grade") or ""),
            "ai_summary": str(reporter_digest.get("ai_summary") or "")[:220],
            "top_improvement_suggestions": [str(x or "") for x in list(reporter_digest.get("top_improvement_suggestions") or [])[:3] if str(x or "").strip()],
            "recommended_actions": [str(x or "") for x in list(reporter_digest.get("recommended_actions") or [])[:3] if str(x or "").strip()],
            "dominant_risks": [str(x or "") for x in list(reporter_digest.get("dominant_risks") or [])[:3] if str(x or "").strip()],
            "system_health": str(reporter_digest.get("system_health") or ""),
            "report_focus_targets": [str(x or "") for x in list(reporter_digest.get("report_focus_targets") or [])[:4] if str(x or "").strip()],
            "scanner_selection_status": str(reporter_digest.get("scanner_selection_status") or ""),
            "monitor_status": str(reporter_digest.get("monitor_status") or ""),
            "top_monitor_reasons": [str(x or "") for x in list(reporter_digest.get("top_monitor_reasons") or [])[:4] if str(x or "").strip()],
            "top_scanner_sources": [str(x or "") for x in list(reporter_digest.get("top_scanner_sources") or [])[:3] if str(x or "").strip()],
            "top_supervisor_blockers": [str(x or "") for x in list(reporter_digest.get("top_supervisor_blockers") or [])[:3] if str(x or "").strip()],
            "incident_total": int(reporter_digest.get("incident_total") or 0),
            "route_mix": {
                "route_selected_total": dict(((reporter_digest.get("route_mix") or {}).get("route_selected_total") or {})),
                "monitor_only_ratio": facade._round_optional((reporter_digest.get("route_mix") or {}).get("monitor_only_ratio"), 4),
                "cached_strategist_ratio": facade._round_optional((reporter_digest.get("route_mix") or {}).get("cached_strategist_ratio"), 4),
                "full_cycle_ratio": facade._round_optional((reporter_digest.get("route_mix") or {}).get("full_cycle_ratio"), 4),
                "route_source": str(((reporter_digest.get("route_mix") or {}).get("route_source") or "")),
            },
        },
        "advisory_only": bool(src.get("advisory_only", True)),
    }
    if (
        src.get("requested_day")
        or src.get("resolved_day")
        or src.get("freshness_status")
        or src.get("directional_bias_usable") is False
    ):
        compact["freshness"] = {
            "requested_day": str(src.get("requested_day") or ""),
            "resolved_day": str(src.get("resolved_day") or src.get("day") or ""),
            "age_days": facade._to_int(src.get("age_days"), 0),
            "status": str(src.get("freshness_status") or ""),
            "directional_bias_usable": bool(src.get("directional_bias_usable", True)),
        }
    return compact


def _hide_stage1_symbol_memory_r3_impl(compact, *, facade):
    reason = "stage1_market_frame_excludes_symbol_memory"
    if isinstance(compact.get("commander_refresh_context"), dict):
        compact["commander_refresh_context"]["selected_symbol_memory"] = {}
    read_model_facts = compact.get("read_model_facts") if isinstance(compact.get("read_model_facts"), dict) else {}
    compact["read_model_facts"] = {
        **dict(read_model_facts),
        "symbol_patterns": {},
        "symbol_pattern_count": 0,
        "symbol_memory_visible_to_llm": False,
        "symbol_memory_exclusion_reason": reason,
    }
    memory_packets = compact.get("memory_packets") if isinstance(compact.get("memory_packets"), dict) else {}
    compact["memory_packets"] = {
        **dict(memory_packets),
        "symbol_memory_packet": {
            "status": "excluded",
            "visible_to_llm": False,
            "reason": reason,
        },
    }
    compact["memory_boundary"] = {
        "stage": "stage1_market_frame",
        "broad_memory_visible_to_llm": True,
        "symbol_memory_visible_to_llm": False,
        "reason": reason,
    }


def _pick_playbook_r3_impl(*, market_structure, market_regime, market_sentiment, facade):
    if str(market_structure).startswith("high_volatility") or market_regime == "risk_off":
        return "defensive"
    if str(market_structure).startswith("trend") and market_regime == "risk_on" and market_sentiment == "bullish":
        return "breakout"
    if str(market_structure).startswith("trend"):
        return "pullback"
    if str(market_structure).startswith("range") and market_regime == "risk_on":
        return "reversal"
    return "defensive"
