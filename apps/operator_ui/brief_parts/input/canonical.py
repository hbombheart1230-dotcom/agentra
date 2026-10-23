"""Operator Brief canonical trade input assembly (read model over canonical artifacts; no persistence, no LLM).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _build_canonical_trade_brief_input_r3_impl(trade_report, *, facade):
    def _normalize_shared_facts(raw: Dict[str, Any]) -> Dict[str, Any]:
        payload = dict(raw or {})
        return {
            "action": str(payload.get("action") or "unavailable").strip() or "unavailable",
            "status": str(payload.get("status") or "unavailable").strip() or "unavailable",
            "holding_duration": str(payload.get("holding_duration") or "unavailable").strip() or "unavailable",
            "exit_reason": str(payload.get("exit_reason") or "unavailable").strip() or "unavailable",
            "pnl": payload.get("pnl", "unavailable"),
            "pnl_pct": payload.get("pnl_pct", "unavailable"),
            "data_source": dict(payload.get("data_source") or {}),
        }

    def _build_story_for_shared_facts(
        *,
        story_input: Dict[str, Any],
        lifecycle: Dict[str, Any],
        report: Dict[str, Any],
    ) -> Dict[str, Any]:
        out = dict(story_input or {})
        if isinstance(lifecycle, dict) and lifecycle:
            out.setdefault("trade_lifecycle", dict(lifecycle))
            lifecycle_summary = lifecycle.get("summary") if isinstance(lifecycle.get("summary"), dict) else {}
            out.setdefault("lifecycle_summary", dict(lifecycle_summary))
            if isinstance(lifecycle.get("entry"), dict):
                out.setdefault("entry_summary", dict(lifecycle.get("entry")))
            if isinstance(lifecycle.get("exit"), dict):
                out.setdefault("exit_summary", dict(lifecycle.get("exit")))
            if not str(out.get("status") or "").strip():
                out["status"] = str(lifecycle.get("status") or "")
        shared = report.get("shared_facts") if isinstance(report.get("shared_facts"), dict) else {}
        if shared:
            if not str(out.get("action") or "").strip():
                out["action"] = str(shared.get("action") or "")
            if not str(out.get("status") or "").strip():
                out["status"] = str(shared.get("status") or "")
        return out

    story_input = facade._trade_report_artifact_payload(trade_report, "story_input_data")
    lifecycle = facade._trade_report_artifact_payload(trade_report, "lifecycle_data")
    report = facade._trade_report_artifact_payload(trade_report, "report_data")
    shared_facts_from_report = report.get("shared_facts") if isinstance(report.get("shared_facts"), dict) else {}
    if shared_facts_from_report:
        shared_facts = _normalize_shared_facts(shared_facts_from_report)
    else:
        shared_story_input = _build_story_for_shared_facts(
            story_input=story_input,
            lifecycle=lifecycle,
            report=report,
        )
        shared_facts = _normalize_shared_facts(facade.resolve_shared_trade_facts(shared_story_input))
    if not (story_input or lifecycle or report):
        unavailable_facts = {
            "action": "unavailable",
            "status": "unavailable",
            "holding_duration": "unavailable",
            "exit_reason": "unavailable",
            "pnl": "unavailable",
            "pnl_pct": "unavailable",
            "data_source": {
                "action": "unavailable",
                "status": "unavailable",
                "holding_duration": "unavailable",
                "exit_reason": "unavailable",
                "pnl": "unavailable",
                "pnl_pct": "unavailable",
            },
        }
        return {
            "available": False,
            "trade_id": str(trade_report.get("trade_id") or ""),
            "story_type": str(trade_report.get("story_type_label") or trade_report.get("story_type") or ""),
            "execution_mode_label": str(trade_report.get("execution_mode_label") or ""),
            "lifecycle_status": "unavailable",
            "lifecycle_summary": str(trade_report.get("lifecycle_summary") or ""),
            "report_summary": str(trade_report.get("report_summary") or ""),
            "reporter_summary": str(trade_report.get("reporter_status_human") or ""),
            "action": "unavailable",
            "current_action": "unavailable",
            "holding_duration": "unavailable",
            "exit_reason": "unavailable",
            "pnl": "unavailable",
            "pnl_pct": "unavailable",
            "data_source": dict(unavailable_facts.get("data_source") or {}),
            "shared_facts": unavailable_facts,
        }

    market_context = facade._prefer_richer_trade_report_section(
        story_input.get("market_context_human"),
        report.get("market_context_at_entry"),
        report.get("market_context"),
    )
    selection = facade._prefer_richer_trade_report_section(
        story_input.get("scanner_reason_human"),
        report.get("why_this_symbol_was_chosen"),
        report.get("why_this_symbol"),
    )
    filters = facade._prefer_richer_trade_report_section(
        story_input.get("filters_human"),
        report.get("scanner_filters"),
        report.get("scanner_logic_and_filters"),
    )
    monitor = facade._prefer_richer_trade_report_section(
        story_input.get("monitor_reason_human"),
        report.get("holding_monitoring_story"),
        report.get("monitor_trigger_reasoning"),
    )
    guard = facade._prefer_richer_trade_report_section(
        story_input.get("guard_reason_human"),
        report.get("guard_approval_result"),
    )
    execution = facade._prefer_richer_trade_report_section(
        story_input.get("execution_outcome_human"),
        report.get("execution_quality"),
        report.get("execution_result"),
    )
    reporter_eval = facade._prefer_richer_trade_report_section(
        story_input.get("reporter_status_human"),
        report.get("reporter_evaluation"),
        lifecycle.get("reporter"),
    )
    conclusion = facade._prefer_richer_trade_report_section(
        story_input.get("operator_conclusion_human"),
        report.get("final_operator_conclusion"),
        lifecycle.get("summary"),
    )
    executive = facade._prefer_richer_trade_report_section(report.get("executive_summary"))
    lifecycle_summary = lifecycle.get("summary") if isinstance(lifecycle.get("summary"), dict) else {}
    entry_summary = story_input.get("entry_summary") if isinstance(story_input.get("entry_summary"), dict) else {}
    exit_summary = story_input.get("exit_summary") if isinstance(story_input.get("exit_summary"), dict) else {}
    story_monitor = story_input.get("monitor_reason_human") if isinstance(story_input.get("monitor_reason_human"), dict) else {}
    report_monitor_snapshot = report.get("monitor_snapshot") if isinstance(report.get("monitor_snapshot"), dict) else {}
    monitor_snapshot = facade._normalize_canonical_monitor_snapshot(report_monitor_snapshot, story_monitor)

    market_bullets = facade._trade_report_section_bullets(market_context)
    selection_bullets = facade._trade_report_section_bullets(selection)
    filter_bullets = facade._trade_report_section_bullets(filters, limit=8)
    monitor_bullets = facade._trade_report_section_bullets(monitor)
    execution_bullets = facade._trade_report_section_bullets(execution)
    market_regime = str(
        market_context.get("regime")
        or facade._extract_labeled_bullet(market_bullets, ["market regime", "regime", "시장 레짐", "시장 환경"])
        or ""
    )
    market_sentiment = str(
        market_context.get("market_sentiment")
        or facade._extract_labeled_bullet(market_bullets, ["market sentiment", "시장 심리"])
        or ""
    )
    global_sentiment = str(
        market_context.get("global_sentiment_score")
        or facade._extract_labeled_bullet(market_bullets, ["global sentiment score", "global sentiment", "글로벌 감성 점수"])
        or ""
    )
    vix_level = str(
        market_context.get("vix_level")
        or facade._extract_labeled_bullet(market_bullets, ["vix / fear index level", "vix", "vix 수준", "vix / fear index", "vix / 공포 지수 수준"])
        or ""
    )
    universe_size = facade._extract_labeled_int(selection_bullets, ["universe scanned", "스캐너 후보 수", "후보 수"])
    selected_rank = facade._extract_labeled_int(selection_bullets, ["selected rank", "최종 선정 순위", "선정 순위"])
    canonical_filter_rows = facade._parse_canonical_filter_bullets(filter_bullets)
    strategist_evidence = story_input.get("strategist_evidence") if isinstance(story_input.get("strategist_evidence"), dict) else {}
    scanner_evidence = story_input.get("scanner_evidence") if isinstance(story_input.get("scanner_evidence"), dict) else {}
    monitor_timeline = story_input.get("monitor_timeline") if isinstance(story_input.get("monitor_timeline"), dict) else {}
    top_candidates = [dict(row) for row in list(selection.get("top_candidates") or []) if isinstance(row, dict)][:3]
    runner_ups = [dict(row) for row in list(selection.get("runner_ups") or []) if isinstance(row, dict)][:3]
    selection_reason_rows = [dict(row) for row in list(scanner_evidence.get("candidate_selection_reasons") or []) if isinstance(row, dict)]
    selection_reason_payload = (
        selection_reason_rows[0].get("payload")
        if selection_reason_rows and isinstance(selection_reason_rows[0].get("payload"), dict)
        else {}
    )
    why_selected = [str(x or "") for x in list(selection.get("why_selected") or selection_reason_payload.get("why_selected") or []) if str(x or "").strip()][:4]
    runner_ups_lost: List[Dict[str, Any]] = []
    for row in list(selection.get("runner_ups_lost") or selection_reason_payload.get("runner_ups_lost") or selection_reason_payload.get("runner_up_reasons") or []):
        if not isinstance(row, dict):
            continue
        symbol = str(row.get("symbol") or "").strip()
        why_lost = [
            str(x or "")
            for x in list(row.get("why_lost") or row.get("lost_because") or [])
            if str(x or "").strip()
        ][:4]
        summary = str(row.get("summary") or "; ".join(why_lost)).strip()
        if not symbol and not summary:
            continue
        runner_ups_lost.append(
            {
                "symbol": symbol,
                "why_lost": why_lost,
                "summary": summary,
            }
        )
        if len(runner_ups_lost) >= 3:
            break
    selection_basis = str(selection.get("selection_basis") or selection_reason_payload.get("final_decision_basis") or "").strip()
    tie_break_rule = str(selection.get("tie_break_rule") or selection_reason_payload.get("tie_break_rule") or "").strip()
    scanner_selection_trace = (
        story_input.get("scanner_selection_trace")
        if isinstance(story_input.get("scanner_selection_trace"), dict)
        else selection.get("scanner_selection_trace")
        if isinstance(selection.get("scanner_selection_trace"), dict)
        else {}
    )
    monitor_stop_policy_trace = (
        story_input.get("monitor_stop_policy_trace")
        if isinstance(story_input.get("monitor_stop_policy_trace"), dict)
        else monitor.get("monitor_stop_policy_trace")
        if isinstance(monitor.get("monitor_stop_policy_trace"), dict)
        else {}
    )

    return {
        "available": True,
        "trade_id": str(trade_report.get("trade_id") or story_input.get("trade_id") or lifecycle.get("trade_id") or ""),
        "story_type": str(trade_report.get("story_type_label") or trade_report.get("story_type") or story_input.get("story_type") or ""),
        "execution_mode_label": str(trade_report.get("execution_mode_label") or story_input.get("execution_mode_label") or lifecycle.get("execution_mode_label") or ""),
        "lifecycle_status": str(shared_facts.get("status") or "unavailable"),
        "lifecycle_summary": str(
            trade_report.get("lifecycle_summary")
            or lifecycle_summary.get("lifecycle_summary_human")
            or conclusion.get("summary")
            or ""
        ),
        "action": str(shared_facts.get("action") or "unavailable"),
        "headline": str(executive.get("headline") or ""),
        "current_action": str(shared_facts.get("action") or "unavailable"),
        "holding_duration": str(shared_facts.get("holding_duration") or "unavailable"),
        "pnl": shared_facts.get("pnl", "unavailable"),
        "pnl_pct": shared_facts.get("pnl_pct", "unavailable"),
        "data_source": dict(shared_facts.get("data_source") or {}),
        "shared_facts": dict(shared_facts),
        "symbol": str(report.get("symbol") or story_input.get("symbol") or trade_report.get("symbol") or ""),
        "market_regime": market_regime,
        "market_sentiment": market_sentiment,
        "global_sentiment": global_sentiment,
        "vix": vix_level,
        "playbook": str(market_context.get("playbook") or ""),
        "themes": [str(x or "") for x in list(market_context.get("themes") or [])[:6] if str(x or "").strip()],
        "headline_count": market_context.get("headline_count"),
        "news_query_count": market_context.get("news_query_count"),
        "news_query_targets": [str(x or "") for x in list(market_context.get("news_query_targets") or [])[:6] if str(x or "").strip()],
        "market_news_titles": [str(x or "") for x in list(market_context.get("market_news_titles") or [])[:3] if str(x or "").strip()],
        "candidate_news_titles": [str(x or "") for x in list(market_context.get("candidate_news_titles") or [])[:3] if str(x or "").strip()],
        "strategist_candidate_hints": [str(x or "") for x in list(story_input.get("strategist_candidate_hints") or market_context.get("candidate_hints") or [])[:8] if str(x or "").strip()],
        "strategist_market_headlines": [str(x or "") for x in list(story_input.get("strategist_market_headlines") or market_context.get("market_headlines") or [])[:3] if str(x or "").strip()],
        "strategist_symbol_headlines": [str(x or "") for x in list(story_input.get("strategist_symbol_headlines") or market_context.get("symbol_headlines") or [])[:3] if str(x or "").strip()],
        "market_context_summary": facade._trade_report_section_summary(market_context),
        "market_context_bullets": market_bullets,
        "selection_summary": facade._trade_report_section_summary(selection),
        "selection_bullets": selection_bullets,
        "universe_size": universe_size,
        "selected_rank": selected_rank,
        "selected_score": selection.get("selected_score"),
        "selected_sources": [str(x or "") for x in list(selection.get("selected_sources") or [])[:5] if str(x or "").strip()],
        "why_selected": why_selected,
        "selection_basis": selection_basis,
        "tie_break_rule": tie_break_rule,
        "top_candidates": top_candidates,
        "runner_ups": runner_ups,
        "runner_ups_lost": runner_ups_lost,
        "scanner_selection_trace": dict(scanner_selection_trace or {}),
        "filters_summary": facade._trade_report_section_summary(filters),
        "filter_bullets": filter_bullets,
        "filter_rows": canonical_filter_rows,
        "monitor_summary": facade._trade_report_section_summary(monitor),
        "monitor_bullets": monitor_bullets,
        "monitor_snapshot": monitor_snapshot if isinstance(monitor_snapshot, dict) else {},
        "monitor_stop_policy_trace": dict(monitor_stop_policy_trace or {}),
        "monitor_decision_chain": [str(x or "") for x in list(monitor.get("decision_reason_chain") or [])[:6] if str(x or "").strip()],
        "guard_summary": facade._trade_report_section_summary(guard),
        "execution_summary": facade._trade_report_section_summary(execution),
        "execution_bullets": execution_bullets,
        "report_summary": str(trade_report.get("report_summary") or executive.get("summary") or ""),
        "reporter_status": str(reporter_eval.get("status") or lifecycle.get("reporter", {}).get("status_human") or ""),
        "reporter_grade": str(reporter_eval.get("grade") or lifecycle.get("reporter", {}).get("grade") or ""),
        "reporter_summary": facade._trade_report_section_summary(reporter_eval, str(trade_report.get("reporter_status_human") or "")),
        "entry_reason": str(entry_summary.get("reason_human") or lifecycle_summary.get("entry_reason_human") or ""),
        "exit_reason": str(shared_facts.get("exit_reason") or "unavailable"),
        "timeline": [dict(x) for x in list(story_input.get("timeline") or lifecycle.get("timeline") or report.get("timeline") or []) if isinstance(x, dict)][:10],
        "evidence": {
            "strategist": {
                "market_context_snapshots": len(list(strategist_evidence.get("market_context_snapshots") or [])),
                "global_sentiment_breakdowns": len(list(strategist_evidence.get("global_sentiment_breakdowns") or [])),
                "news_evidence_ranked": len(list(strategist_evidence.get("news_evidence_ranked") or [])),
                "decision_frames": len(list(strategist_evidence.get("decision_frames") or [])),
                "llm_response_saved": len(list(strategist_evidence.get("llm_response_saved") or [])),
            },
            "scanner": {
                "candidate_pool_snapshots": len(list(scanner_evidence.get("candidate_pool_snapshots") or [])),
                "candidate_ranking_tables": len(list(scanner_evidence.get("candidate_ranking_tables") or [])),
                "candidate_selection_reasons": len(list(scanner_evidence.get("candidate_selection_reasons") or [])),
                "selection_outputs": len(list(scanner_evidence.get("selection_outputs") or [])),
            },
            "monitor": {
                "threshold_snapshots": len(list(monitor_timeline.get("threshold_snapshots") or [])),
                "state_transitions": len(list(monitor_timeline.get("state_transitions") or [])),
                "exit_decision_details": len(list(monitor_timeline.get("exit_decision_details") or [])),
                "cycle_summaries": len(list(monitor_timeline.get("cycle_summaries") or [])),
            },
        },
    }
