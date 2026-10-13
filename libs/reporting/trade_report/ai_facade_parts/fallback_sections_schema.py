"""Deterministic fallback section selection and final schema assembly.

Second Pass (P1.5) intra-function extraction from `libs/reporting/trade_report_ai_deterministic.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def fb_sections_entry_decision_exit_decision(_build_report_strategist_refresh_trace, story_input, why_symbol_bullets, _listify, why_symbol_seed, _build_scanner_filters_summary, filters_human, _build_scanner_filters_bullets, _clip, scanner_filters_seed, _build_entry_decision_bullets, entry_summary, scanner_reason, market_context, entry_monitor_reason, action, _build_entry_decision_summary, shared_seed, has_runtime_scanner_reason, _is_low_information_bullet, entry_decision_seed, holding_summary, _build_holding_story_summary, monitor_reason, status_text, _build_holding_story_bullets, has_runtime_monitor_reason, holding_story_seed, _holding_duration_label, exit_summary, _build_exit_decision_bullets, _build_exit_decision_summary, exit_decision_seed, *, facade):
    strategist_refresh_trace = _build_report_strategist_refresh_trace(story_input)
    if not why_symbol_bullets and isinstance(why_symbol_seed.get("bullets"), list):
        why_symbol_bullets = _listify(why_symbol_seed.get("bullets"), max_items=16, max_len=260)
    scanner_filters_summary = _build_scanner_filters_summary(filters_human)
    scanner_filters_bullets = _build_scanner_filters_bullets(filters_human)
    if not filters_human and str(scanner_filters_seed.get("summary") or "").strip():
        scanner_filters_summary = _clip(scanner_filters_seed.get("summary"), max_len=600)
    if not filters_human and isinstance(scanner_filters_seed.get("bullets"), list):
        scanner_filters_bullets = _listify(scanner_filters_seed.get("bullets"), max_items=10, max_len=260)

    entry_decision = {
        "summary": (
            _build_entry_decision_summary(entry_summary, scanner_reason, market_context, entry_monitor_reason, action)
            if bool(shared_seed.get("entry_exists"))
            else "Entry evidence was insufficient, so entry timing is marked as unavailable."
        ),
        "bullets": _build_entry_decision_bullets(entry_summary, scanner_reason, market_context, entry_monitor_reason, action),
    }
    if (
        not has_runtime_scanner_reason
        or not _clip(entry_decision.get("summary"), max_len=600)
        or _is_low_information_bullet(entry_decision.get("summary"))
    ) and str(entry_decision_seed.get("summary") or "").strip():
        entry_decision["summary"] = _clip(entry_decision_seed.get("summary"), max_len=600)
    if (not entry_decision.get("bullets")) and isinstance(entry_decision_seed.get("bullets"), list):
        entry_decision["bullets"] = _listify(entry_decision_seed.get("bullets"), max_items=12, max_len=260)
    hold_count = len(list(holding_summary.get("run_ids") or []))
    holding_story = {
        "summary": _build_holding_story_summary(hold_count, monitor_reason, status_text),
        "bullets": _build_holding_story_bullets(holding_summary, monitor_reason),
    }
    if (
        not has_runtime_monitor_reason
        or not _clip(holding_story.get("summary"), max_len=600)
        or _is_low_information_bullet(holding_story.get("summary"))
    ) and str(holding_story_seed.get("summary") or "").strip():
        holding_story["summary"] = _clip(holding_story_seed.get("summary"), max_len=600)
    if (not holding_story.get("bullets")) and isinstance(holding_story_seed.get("bullets"), list):
        holding_story["bullets"] = _listify(holding_story_seed.get("bullets"), max_items=12, max_len=260)
    if _clip(shared_seed.get("holding_duration"), max_len=80):
        holding_story["bullets"] = [_holding_duration_label(_clip(shared_seed.get('holding_duration'), max_len=80))] + list(
            holding_story.get("bullets") or []
        )
    exit_monitor_context = exit_summary.get("monitor_context") if isinstance(exit_summary.get("monitor_context"), dict) else {}
    if exit_monitor_context:
        exit_monitor_context = dict(exit_monitor_context)
    else:
        exit_monitor_context = dict(monitor_reason or {})
    exit_decision = {
        "summary": (
            _build_exit_decision_summary(exit_summary, exit_monitor_context, status_text=status_text)
            if bool(shared_seed.get("exit_exists")) or status_text.lower() != "open"
            else "Exit evidence is not captured yet because this lifecycle remains open."
        ),
        "bullets": _build_exit_decision_bullets(exit_summary, exit_monitor_context, status_text=status_text),
    }
    if (
        not has_runtime_monitor_reason
        or not _clip(exit_decision.get("summary"), max_len=600)
        or _is_low_information_bullet(exit_decision.get("summary"))
    ) and str(exit_decision_seed.get("summary") or "").strip():
        exit_decision["summary"] = _clip(exit_decision_seed.get("summary"), max_len=600)
    if (not exit_decision.get("bullets")) and isinstance(exit_decision_seed.get("bullets"), list):
        exit_decision["bullets"] = _listify(exit_decision_seed.get("bullets"), max_items=12, max_len=260)
    return (entry_decision, exit_decision, holding_story, scanner_filters_bullets, scanner_filters_summary, strategist_refresh_trace, why_symbol_bullets)


def fb_sections_out(trade_id, symbol, action, status_text, strategist_summary, strategist_refresh_trace, entry_execution_visibility, entry_decision, exit_decision, execution_quality, reporter_eval, full_timeline, _utc_now_iso, _clip, status, mode, executive_reason, market_context_summary, effective_scanner_selection_trace, news_scanner_contribution, holding_story, monitor_snapshot, scanner_filters_summary, scanner_filters_bullets, weaknesses_bullets, _build_report_shared_facts, model, reason, confidence, _build_market_context_bullets, market_context, _listify, _compact_scalar_dict, _as_dict, _build_market_scanner_linkage_bullet, scanner_reason, why_symbol_bullets, _scanner_basis_text, shared_seed, story_input, scanner_choice_summary, lifecycle_summary_text, strategist_context, strategist_evidence, guard_reason, guard_approval_seed, operator_conclusion, final_operator_conclusion_seed, build_trade_report_truth_surface, memory_surface, build_trade_memory_application_surface, _compact_strategist_report_context, *, facade):
    out = {
        "schema_version": "ai_trade_report.v2",
        "generated_at": _utc_now_iso(),
        "trade_id": trade_id,
        "story_id": _clip(story_input.get("story_id"), max_len=120) or trade_id,
        "run_id": _clip(story_input.get("run_id"), max_len=120),
        "symbol": symbol,
        "action": action,
        "status": status_text,
        "story_type": _clip(story_input.get("story_type"), max_len=40),
        "execution_mode_label": _clip(story_input.get("execution_mode_label"), max_len=80),
        "generation": {
            "status": status,
            "mode": mode,
            "model": _clip(model, max_len=120),
            "reason": _clip(reason, max_len=320),
        },
        "executive_summary": {
            "headline": f"{action} {symbol}",
            "action": action,
            "symbol": symbol,
            "confidence": confidence or "not_captured",
            "summary": executive_reason,
        },
        "market_context_at_entry": {
            "summary": market_context_summary,
            "bullets": _build_market_context_bullets(market_context, scanner_reason=scanner_reason),
            "regime": _clip(market_context.get("regime"), max_len=40),
            "market_sentiment": _clip(market_context.get("market_sentiment"), max_len=40),
            "playbook": _clip(market_context.get("playbook"), max_len=40),
            "policy_source": _clip(market_context.get("policy_source"), max_len=80),
            "themes": _listify(market_context.get("themes"), max_items=6, max_len=80),
            "theme_strength_packet": _compact_scalar_dict(
                market_context.get("theme_strength_packet"),
                max_items=8,
                max_len=120,
            ),
            "theme_source": _clip(market_context.get("theme_source"), max_len=80),
            "theme_source_status": _clip(market_context.get("theme_source_status"), max_len=80),
            "theme_source_reason": _clip(market_context.get("theme_source_reason"), max_len=160),
            "theme_strength_top_themes": _listify(market_context.get("theme_strength_top_themes"), max_items=6, max_len=80),
            "risk_tone": _clip(market_context.get("risk_tone"), max_len=40),
            "risk_mode": _clip(market_context.get("risk_mode"), max_len=40),
            "selected_playbook": _clip(market_context.get("selected_playbook"), max_len=40),
            "preferred_themes": _listify(market_context.get("preferred_themes"), max_items=6, max_len=80),
            "avoid_themes": _listify(market_context.get("avoid_themes"), max_items=6, max_len=80),
            "scanner_bias_summary": {
                "enabled": (market_context.get("scanner_bias_summary") or {}).get("enabled"),
                "active_biases": _listify((market_context.get("scanner_bias_summary") or {}).get("active_biases"), max_items=6, max_len=80),
                "bias_strength": _clip((market_context.get("scanner_bias_summary") or {}).get("bias_strength"), max_len=24),
                "bias_source": _clip((market_context.get("scanner_bias_summary") or {}).get("bias_source"), max_len=80),
                "summary": _clip((market_context.get("scanner_bias_summary") or {}).get("summary"), max_len=220),
            },
            "global_sentiment_score": market_context.get("global_sentiment_score"),
            "vix_level": market_context.get("vix_level"),
            "stress_flags": _listify(market_context.get("stress_flags"), max_items=6, max_len=80),
            "strategist_candidate_hints": _listify(
                market_context.get("candidate_hints") or strategist_evidence.get("candidate_hints"), max_items=8, max_len=24
            ),
            "strategist_market_headlines": _listify(
                market_context.get("market_headlines") or strategist_evidence.get("market_headlines"), max_items=3, max_len=180
            ),
            "strategist_symbol_headlines": _listify(
                market_context.get("symbol_headlines") or strategist_evidence.get("symbol_headlines"), max_items=3, max_len=180
            ),
            "global_sentiment_signal": _compact_scalar_dict(
                market_context.get("global_sentiment_signal") or strategist_evidence.get("global_sentiment_signal"), max_items=8, max_len=120
            ),
            "korea_indices": _as_dict(market_context.get("korea_indices") or strategist_evidence.get("korea_indices")),
            "fear_index": _compact_scalar_dict(
                market_context.get("fear_index") or strategist_evidence.get("fear_index"), max_items=8, max_len=120
            ),
            "key_events": _listify(
                market_context.get("key_events") or market_context.get("key_events_hint") or strategist_evidence.get("key_events"),
                max_items=6,
                max_len=180,
            ),
            "strategist_market_context_summary": _clip(
                strategist_context.get("market_context_summary"),
                max_len=320,
            ),
            "scanner_linkage_summary": _build_market_scanner_linkage_bullet(market_context, scanner_reason),
        },
        "strategist_summary": strategist_summary,
        "strategist_refresh_trace": strategist_refresh_trace,
        "entry_execution_visibility": entry_execution_visibility,
        "why_this_symbol_was_chosen": {
            "summary": _clip(scanner_choice_summary or scanner_reason.get("summary"), max_len=600),
            "bullets": _listify(why_symbol_bullets, max_items=16, max_len=260),
            "selected_rank": scanner_reason.get("selected_rank"),
            "universe_size": scanner_reason.get("universe_size"),
            "symbol": _clip(scanner_reason.get("selected_symbol") or story_input.get("symbol"), max_len=32),
            "basis": _scanner_basis_text(scanner_reason),
            "strategist_candidate_hints": _listify(
                market_context.get("candidate_hints") or strategist_evidence.get("candidate_hints"), max_items=8, max_len=24
            ),
            "scanner_selection_trace": effective_scanner_selection_trace,
            "news_scanner_contribution": news_scanner_contribution,
        },
        "entry_decision": entry_decision,
        "holding_monitoring_story": {
            **holding_story,
            "monitor_stop_policy_trace": _as_dict(story_input.get("monitor_stop_policy_trace")),
            "monitor_blocker_trace": _as_dict(story_input.get("monitor_blocker_trace")),
        },
        "exit_decision": exit_decision,
        "execution_quality": execution_quality,
        "monitor_snapshot": {
            **monitor_snapshot,
            "monitor_stop_policy_trace": _as_dict(story_input.get("monitor_stop_policy_trace")),
        },
        "scanner_filters": {
            "summary": scanner_filters_summary,
            "bullets": scanner_filters_bullets,
        },
        "guard_approval_result": {
            "summary": (
                _clip(guard_reason.get("summary"), max_len=600)
                or _clip(guard_approval_seed.get("summary"), max_len=600)
            ),
            "bullets": (
                _listify(guard_reason.get("bullets"), max_items=8, max_len=260)
                or _listify(guard_approval_seed.get("bullets"), max_items=8, max_len=260)
            ),
        },
        "reporter_evaluation": reporter_eval,
        "errors_weaknesses_improvement_points": {
            "summary": (
                "Warnings and missing links were recorded for operator follow-up."
                if weaknesses_bullets
                else "No explicit weaknesses were surfaced beyond the recorded trace."
            ),
            "bullets": weaknesses_bullets,
        },
        "full_timeline": full_timeline,
        "timeline": full_timeline,
        "final_operator_conclusion": {
            "summary": (
                executive_reason
                if status_text.strip().lower() == "closed" and lifecycle_summary_text
                else (
                    _clip(operator_conclusion.get("summary"), max_len=600)
                    or _clip(final_operator_conclusion_seed.get("summary"), max_len=600)
                    or executive_reason
                )
            ),
            "current_action": (
                action
                if status_text.strip().lower() == "closed"
                else (
                    _clip(operator_conclusion.get("current_action"), max_len=24)
                    or _clip(final_operator_conclusion_seed.get("current_action"), max_len=24)
                    or action
                )
            ),
            "watch_next": (
                _listify(operator_conclusion.get("watch_next"), max_items=6, max_len=200)
                or _listify(final_operator_conclusion_seed.get("watch_next"), max_items=6, max_len=200)
            ),
            "thesis_invalidation": (
                _listify(operator_conclusion.get("thesis_invalidation"), max_items=6, max_len=200)
                or _listify(final_operator_conclusion_seed.get("thesis_invalidation"), max_items=6, max_len=200)
            ),
        },
        "shared_facts": _build_report_shared_facts(
            shared_seed=shared_seed,
            action=action,
            symbol=symbol,
            trade_id=trade_id,
            status_text=status_text,
        ),
    }
    out["truth_surface"] = build_trade_report_truth_surface(out.get("shared_facts"))
    out["memory_surface"] = memory_surface
    out["memory_application_surface"] = build_trade_memory_application_surface(story_input)
    strategist_output = _compact_strategist_report_context(story_input)
    if strategist_output:
        out["strategist_output"] = strategist_output
    return (out,)
