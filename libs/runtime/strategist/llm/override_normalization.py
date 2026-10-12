"""Strategist LLM override derivation/normalisation (post-processing of already received output).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _derive_stage_specific_common_overrides_r3_impl(out, *, facade):
    stage2 = dict(out.get("selected_symbol_tactical_review") or {})
    if stage2:
        decision = str(stage2.get("selected_symbol_decision") or "").strip()
        runner_ups = list(stage2.get("runner_up_order") or [])
        reason = str(stage2.get("reason") or "selected-symbol tactical refresh").strip()
        if "candidate_watch_policy" not in out:
            cascade = decision == "cascade_to_runner_up" and bool(runner_ups)
            max_rank = 1 + len(runner_ups) if cascade else 1
            if cascade and "tactical_strategy" not in out:
                out["tactical_strategy"] = "vwap_reclaim_pullback"
            out["candidate_watch_policy"] = {
                "max_priority_rank": max(1, min(10, int(max_rank))),
                "max_runner_ups": len(runner_ups) if cascade else 0,
                "cascade_enabled": bool(cascade),
                "cascade_allowed_reasons": [
                    "breakout_not_ready",
                    "volume_confirmation_missing",
                    "below_vwap_reclaim_not_ready",
                    "pullback_not_mature",
                ],
                "cascade_blocked_reasons": [
                    "cost_filter_failed",
                    "risk_policy_block",
                    "closeout_window",
                    "open_position_present",
                    "broker_truth_mismatch",
                ],
                "reason": reason,
            }
        if "strategy_adjustment_directives" not in out:
            monitor_instruction = dict(stage2.get("monitor_instruction") or {})
            entry_delta = dict(stage2.get("entry_policy_delta") or {})
            required = list(monitor_instruction.get("required_confirmations") or [])
            avoid_if = list(monitor_instruction.get("avoid_if") or [])
            tighten = (
                decision in {"avoid_rank1", "watch_rank1_with_tighter_gates", "no_trade"}
                or bool(entry_delta.get("tighten_confidence_threshold"))
            )
            out["strategy_adjustment_directives"] = {
                "playbook_action": {"action": "maintain", "target": None, "reason": reason},
                "entry_policy_action": {
                    "action": "tighten" if tighten else "maintain",
                    "target_fields": [
                        field
                        for field, enabled in (
                            ("confidence_threshold", entry_delta.get("tighten_confidence_threshold")),
                            ("previous_close_context", entry_delta.get("require_prev_close_context")),
                            ("cost_hurdle", entry_delta.get("require_cost_hurdle")),
                        )
                        if bool(enabled)
                    ][:6],
                    "reason": reason,
                },
                "monitor_focus_action": {
                    "action": "increase_focus" if required or avoid_if else "maintain",
                    "target_axes": facade._focus_axes_from_strings(" ".join(required), " ".join(avoid_if)),
                    "reason": reason,
                },
                "selected_symbol_bias_action": {
                    "action": "avoid_breakout"
                    if decision in {"avoid_rank1", "no_trade"}
                    else "prefer_reclaim"
                    if decision == "watch_rank1_with_tighter_gates"
                    else "none",
                    "reason": reason,
                },
                "refresh_action": {"action": "none", "reason": "Stage 2 review completed before monitor entry."},
            }
        out.setdefault(
            "strategy_refresh_trace",
            {
                "summary": reason,
                "bullets": [reason] if reason else [],
                "stages": [
                    {
                        "stage": "post_scanner_refresh",
                        "label": "Stage 2 selected-symbol tactical refresh",
                        "summary": reason,
                        "requested": True,
                        "effective": True,
                        "reason": decision,
                    }
                ],
            },
        )

    stage3 = dict(out.get("stale_intraday_hold_review") or {})
    if stage3:
        decision = str(stage3.get("hold_review_decision") or "").strip()
        reason = str(stage3.get("reason") or "stale intraday hold review").strip()
        if "strategy_adjustment_directives" not in out:
            out["strategy_adjustment_directives"] = {
                "playbook_action": {"action": "maintain", "target": None, "reason": reason},
                "entry_policy_action": {"action": "maintain", "target_fields": [], "reason": reason},
                "monitor_focus_action": {
                    "action": "increase_focus" if decision in {"tighten_exit", "exit_now"} else "maintain",
                    "target_axes": ["exit_axis"],
                    "reason": reason,
                },
                "selected_symbol_bias_action": {"action": "none", "reason": reason},
                "refresh_action": {
                    "action": "refresh_for_exit_axis_mismatch"
                    if decision in {"tighten_exit", "exit_now"}
                    else "refresh_for_holding",
                    "reason": reason,
                },
            }
        out.setdefault(
            "strategy_refresh_trace",
            {
                "summary": reason,
                "bullets": [reason] if reason else [],
                "stages": [
                    {
                        "stage": "stale_intraday_hold_review",
                        "label": "Stage 3 stale intraday hold review",
                        "summary": reason,
                        "requested": True,
                        "effective": True,
                        "reason": decision,
                    }
                ],
            },
        )

    stage4 = dict(out.get("end_of_day_carry_review") or {})
    if stage4:
        reason = str(stage4.get("risk_note") or "end-of-day carry review").strip()
        portfolio_level = str(stage4.get("portfolio_level_decision") or "").strip()
        carry_allowed = portfolio_level in {"carry_allowed", "carry_only_best_one"}
        out.setdefault(
            "strategy_horizon_feedback",
            {
                "strategy_horizon": "overnight_probe" if carry_allowed else "intraday",
                "exit_guidance": {
                    "allow_overnight": bool(carry_allowed),
                    "preferred_exit": "carry_review" if carry_allowed else "flatten_today",
                },
                "monitor_handoff": {
                    "hold_bias": "neutral_to_patient" if carry_allowed else "defensive",
                    "preferred_exit": "carry_review" if carry_allowed else "flatten_today",
                    "do_not_force_hold": True,
                },
            },
        )
        out.setdefault(
            "strategy_refresh_trace",
            {
                "summary": reason,
                "bullets": [reason] if reason else [],
                "stages": [
                    {
                        "stage": "end_of_day_carry_review",
                        "label": "Stage 4 end-of-day carry review",
                        "summary": reason,
                        "requested": True,
                        "effective": True,
                        "reason": portfolio_level,
                    }
                ],
            },
        )


def _normalize_llm_overrides_r3_impl(raw, *, facade):
    if not isinstance(raw, dict):
        return {}
    normalized = facade.coerce_strategist_output(raw)
    allowed = {
        "market_regime",
        "market_sentiment",
        "key_events",
        "themes",
        "avoid_themes",
        "playbook",
        "scanner_bias",
        "scanner_priority",
        "trade_aggressiveness",
        "risk_tone",
        "monitor_guidance",
        "report_focus",
        "market_regime_summary",
        "policy_rationale",
        "confidence",
        "policy_source",
        "strategy_thesis",
        "strategy_delta_trace",
        "strategy_refresh_trace",
        "memory_usage_trace",
        "news_usage_trace",
        "news_event_intelligence_usage",
        "scanner_handoff",
        "monitor_handoff",
        "conflict_analysis",
        "trade_permission_frame",
        "responsibility_boundary",
        "selected_symbol_tactical_review",
        "stale_intraday_hold_review",
        "end_of_day_carry_review",
    }
    out: Dict[str, Any] = {}
    for key in allowed:
        if key in raw and key not in {
            "strategy_thesis",
            "strategy_delta_trace",
            "strategy_refresh_trace",
            "memory_usage_trace",
            "news_usage_trace",
            "scanner_handoff",
            "monitor_handoff",
            "conflict_analysis",
            "trade_permission_frame",
            "responsibility_boundary",
        }:
            out[key] = normalized.get(key)
        elif key in raw and isinstance(raw.get(key), dict):
            out[key] = dict(raw.get(key) or {})
    if isinstance(raw.get("monitor_policy"), dict):
        out["monitor_policy"] = dict(raw.get("monitor_policy") or {})
    if isinstance(raw.get("monitor_entry_policy"), dict):
        out["monitor_entry_policy"] = dict(raw.get("monitor_entry_policy") or {})
    if isinstance(raw.get("policy_adjustment"), dict):
        out["policy_adjustment"] = dict(raw.get("policy_adjustment") or {})
    if isinstance(raw.get("strategy_adjustment_directives"), dict):
        out["strategy_adjustment_directives"] = dict(raw.get("strategy_adjustment_directives") or {})
    if isinstance(raw.get("strategy_scores"), dict):
        out["strategy_scores"] = dict(raw.get("strategy_scores") or {})
    if isinstance(raw.get("rejected_strategy_reasons"), dict):
        out["rejected_strategy_reasons"] = dict(raw.get("rejected_strategy_reasons") or {})
    if isinstance(raw.get("candidate_watch_policy"), dict):
        out["candidate_watch_policy"] = dict(raw.get("candidate_watch_policy") or {})
    if raw.get("tactical_strategy") not in (None, ""):
        out["tactical_strategy"] = str(raw.get("tactical_strategy") or "").strip().lower()
    if raw.get("tactical_subtype") not in (None, ""):
        out["tactical_subtype"] = str(raw.get("tactical_subtype") or "").strip().lower()
    if isinstance(raw.get("selected_themes"), list):
        out["selected_themes"] = facade._extract_theme_names_from_any(raw.get("selected_themes"))
    if isinstance(raw.get("theme_strategy"), dict):
        out["theme_strategy"] = dict(raw.get("theme_strategy") or {})
    if raw.get("market_regime_rail") not in (None, ""):
        out["market_regime_rail"] = str(raw.get("market_regime_rail") or "").strip()
    if isinstance(raw.get("news_quality"), dict):
        out["news_quality"] = dict(raw.get("news_quality") or {})
    if isinstance(raw.get("news_event_intelligence_usage"), dict):
        out["news_event_intelligence_usage"] = {
            **dict(raw.get("news_event_intelligence_usage") or {}),
            "observation_only": True,
        }
    if isinstance(raw.get("risk_off_exception_conditions"), list):
        out["risk_off_exception_conditions"] = facade._stage_text_list(raw.get("risk_off_exception_conditions"), limit=10)
    stage2 = facade._normalize_stage2_selected_symbol_review(raw)
    if stage2:
        out["selected_symbol_tactical_review"] = dict(stage2)
        out["selected_symbol_decision"] = str(stage2.get("selected_symbol_decision") or "")
        out["target_symbol"] = str(stage2.get("target_symbol") or "")
        out["target_rank"] = int(stage2.get("target_rank") or 0)
        out["runner_up_order"] = list(stage2.get("runner_up_order") or [])
        out["monitor_instruction"] = dict(stage2.get("monitor_instruction") or {})
        out["entry_policy_delta"] = dict(stage2.get("entry_policy_delta") or {})
        out["memory_usage"] = dict(stage2.get("memory_usage") or {})
        out["market_regime_rail"] = str(stage2.get("market_regime_rail") or out.get("market_regime_rail") or "")
        out["news_quality"] = dict(stage2.get("news_quality") or out.get("news_quality") or {})
        if isinstance(stage2.get("news_event_intelligence_usage"), dict):
            out["news_event_intelligence_usage"] = dict(stage2.get("news_event_intelligence_usage") or {})
        out["risk_off_exception_conditions"] = list(
            stage2.get("risk_off_exception_conditions") or out.get("risk_off_exception_conditions") or []
        )
        out["commander_actionability"] = str(stage2.get("commander_actionability") or "")
    stage3 = facade._normalize_stage3_hold_review(raw)
    if stage3:
        out["stale_intraday_hold_review"] = dict(stage3)
        out["hold_review_decision"] = str(stage3.get("hold_review_decision") or "")
    stage4 = facade._normalize_stage4_carry_review(raw)
    if stage4:
        out["end_of_day_carry_review"] = dict(stage4)
        out["carry_review"] = list(stage4.get("carry_review") or [])
        out["portfolio_level_decision"] = str(stage4.get("portfolio_level_decision") or "")
    facade._derive_stage_specific_common_overrides(out)
    return out
