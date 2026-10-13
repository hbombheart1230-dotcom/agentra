from __future__ import annotations

from typing import Any, Callable, Dict, List
import sys as _r3_sys
from libs.reporting.trade_report.ai_facade_parts.fallback_seed_context import (
    fallback_report_seed,
)
from libs.reporting.trade_report.ai_facade_parts.fallback_summary_status import (
    fb_summary_effective_scanner_selection_trace_exit_s,
    fb_summary_confidence_executive_reason,
)
from libs.reporting.trade_report.ai_facade_parts.fallback_sections_schema import (
    fb_sections_entry_decision_exit_decision,
    fb_sections_out,
)


def build_shared_facts(
    *,
    shared_seed: Dict[str, Any],
    action: str,
    symbol: str,
    trade_id: str,
    status_text: str,
    clip: Callable[..., str],
    as_dict: Callable[[Any], Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "symbol": symbol,
        "trade_id": trade_id,
        "action": action,
        "status": status_text,
        "holding_duration": clip(shared_seed.get("holding_duration"), max_len=80) or "unavailable",
        "exit_reason": clip(shared_seed.get("exit_reason"), max_len=280) or "unavailable",
        "pnl": shared_seed.get("pnl", "unavailable"),
        "pnl_pct": shared_seed.get("pnl_pct", "unavailable"),
        "broker_fee": shared_seed.get("broker_fee"),
        "broker_tax": shared_seed.get("broker_tax"),
        "pnl_truth_source": clip(shared_seed.get("pnl_truth_source"), max_len=80) or "unavailable",
        "broker_day_truth_source": clip(shared_seed.get("broker_day_truth_source"), max_len=80) or "",
        "broker_day_match_mode": clip(shared_seed.get("broker_day_match_mode"), max_len=40) or "",
        "broker_day_authoritative": bool(shared_seed.get("broker_day_authoritative")),
        "broker_day_row_count": shared_seed.get("broker_day_row_count"),
        "broker_truth_attempted": bool(shared_seed.get("broker_truth_attempted")),
        "broker_truth_error": clip(shared_seed.get("broker_truth_error"), max_len=240) or "",
        "broker_day_truth_attempted": bool(shared_seed.get("broker_day_truth_attempted")),
        "broker_day_truth_error": clip(shared_seed.get("broker_day_truth_error"), max_len=240) or "",
        "broker_fill_price": shared_seed.get("broker_fill_price"),
        "broker_buy_price": shared_seed.get("broker_buy_price"),
        "account_mark_price": shared_seed.get("account_mark_price"),
        "monitor_mark_price": shared_seed.get("monitor_mark_price"),
        "price_truth_source": clip(shared_seed.get("price_truth_source"), max_len=40) or "unavailable",
        "monitor_price_source": clip(shared_seed.get("monitor_price_source"), max_len=120) or "unavailable",
        "data_source": dict((as_dict(shared_seed.get("resolved_trade_facts")).get("data_source"))),
        "resolved_trade_facts": dict(shared_seed.get("resolved_trade_facts") or {}),
        "lifecycle_action": action,
        "lifecycle_status": status_text,
        "monitor_decision": dict(shared_seed.get("monitor_decision") or {}),
        "scanner_evidence_status": clip(shared_seed.get("scanner_evidence_status"), max_len=24),
        "strategist_evidence_status": clip(shared_seed.get("strategist_evidence_status"), max_len=24),
        "commander_route": dict(shared_seed.get("commander_route") or {}),
    }


def attach_backward_compatible_aliases(report: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(report or {})
    out["market_context"] = dict(out.get("market_context_at_entry") or {})
    out["why_this_symbol"] = dict(out.get("why_this_symbol_was_chosen") or {})
    out["scanner_logic_and_filters"] = dict(out.get("scanner_filters") or {})
    out["monitor_trigger_reasoning"] = dict(out.get("holding_monitoring_story") or {})
    out["execution_result"] = dict(out.get("execution_quality") or {})
    return out


def fallback_section_seeds(
    shared_seed: Dict[str, Any],
    *,
    as_dict: Callable[[Any], Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    seeds = (
        shared_seed.get("report_section_seeds")
        if isinstance(shared_seed.get("report_section_seeds"), dict)
        else {}
    )
    return {
        "market_context": as_dict(seeds.get("market_context_at_entry")),
        "strategist_summary": as_dict(seeds.get("strategist_summary")),
        "why_symbol": as_dict(seeds.get("why_this_symbol_was_chosen")),
        "entry_decision": as_dict(seeds.get("entry_decision")),
        "holding_story": as_dict(seeds.get("holding_monitoring_story")),
        "exit_decision": as_dict(seeds.get("exit_decision")),
        "scanner_filters": as_dict(seeds.get("scanner_filters")),
        "execution_quality": as_dict(seeds.get("execution_quality")),
        "guard_approval": as_dict(seeds.get("guard_approval_result")),
        "reporter_evaluation": as_dict(seeds.get("reporter_evaluation")),
        "final_operator_conclusion": as_dict(seeds.get("final_operator_conclusion")),
    }


def append_news_scanner_choice_details(
    why_symbol_bullets: List[str],
    news_scanner_contribution: Dict[str, Any],
    *,
    listify: Callable[..., List[Any]],
) -> List[str]:
    if not news_scanner_contribution:
        return list(why_symbol_bullets or [])

    core = (
        news_scanner_contribution.get("core_score_contributions")
        if isinstance(news_scanner_contribution.get("core_score_contributions"), dict)
        else {}
    )
    sentiment_inputs = (
        news_scanner_contribution.get("sentiment_inputs")
        if isinstance(news_scanner_contribution.get("sentiment_inputs"), dict)
        else {}
    )
    theme_trace = (
        news_scanner_contribution.get("theme_alignment_trace")
        if isinstance(news_scanner_contribution.get("theme_alignment_trace"), dict)
        else {}
    )
    news_linkage = (
        news_scanner_contribution.get("news_linkage_trace")
        if isinstance(news_scanner_contribution.get("news_linkage_trace"), dict)
        else {}
    )

    def _core_value(key: str) -> float:
        row = core.get(key)
        if isinstance(row, dict):
            return float(row.get("value") or 0.0)
        try:
            return float(row or 0.0)
        except Exception:
            return 0.0

    extra_rows: List[str] = [
        "점수 기여 세부값은 "
        f"거래대금 {_core_value('trading_value'):+.3f}, "
        f"모멘텀 {_core_value('momentum'):+.3f}, "
        f"추세 {_core_value('trend'):+.3f}, "
        f"테마 가점 {_core_value('theme_boost'):+.3f}, "
        f"감성 {_core_value('sentiment'):+.3f}였습니다.",
        "감성 입력은 "
        f"뉴스 {float(sentiment_inputs.get('news_sentiment_score') or 0.0):+.3f}, "
        f"글로벌 {float(sentiment_inputs.get('global_sentiment_score') or 0.0):+.3f}, "
        f"혼합 {float(sentiment_inputs.get('blended_sentiment_component') or 0.0):+.3f}, "
        f"최종 반영 {float(sentiment_inputs.get('weighted_sentiment_score_contribution') or 0.0):+.3f}였습니다.",
        "테마 정렬은 "
        f"일치 여부 {bool(theme_trace.get('theme_source_matched'))}, "
        f"테마 가점 {float(theme_trace.get('theme_boost_score_contribution') or 0.0):+.3f}, "
        f"전략가 테마 {', '.join(listify(theme_trace.get('strategist_themes'), max_items=4, max_len=60)) or '기록 없음'} 기준으로 반영됐습니다.",
    ]
    if theme_trace.get("theme_source") or theme_trace.get("theme_source_status") or theme_trace.get("theme_source_reason"):
        extra_rows.append(
            "테마 packet 출처는 "
            f"source={theme_trace.get('theme_source') or 'not_captured'}, "
            f"status={theme_trace.get('theme_source_status') or 'not_captured'}, "
            f"reason={theme_trace.get('theme_source_reason') or 'not_captured'} 기준으로 남았습니다."
        )
    extra_rows.append(
        "뉴스 연계는 "
        f"종목 헤드라인 {int(float(news_linkage.get('symbol_headline_count') or 0))}건, "
        f"시장 헤드라인 {int(float(news_linkage.get('market_headline_count') or 0))}건, "
        f"조회 대상 {', '.join(listify(news_linkage.get('news_query_targets'), max_items=6, max_len=60)) or '기록 없음'} 기준으로 남았습니다."
    )

    out = list(why_symbol_bullets or [])
    existing = set(str(row) for row in out)
    for row in extra_rows:
        if row not in existing:
            out.append(row)
    return out


def build_monitor_snapshot(
    *,
    monitor_reason: Dict[str, Any],
    story_input: Dict[str, Any],
    action: str,
    clip: Callable[..., str],
    listify: Callable[..., List[Any]],
    as_dict: Callable[[Any], Dict[str, Any]],
    entry_execution_visibility: Dict[str, Any] | None = None,
    compact_entry_candidate_cascade: Callable[[Any], Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    monitor_stop_trace = as_dict(
        monitor_reason.get("monitor_stop_policy_trace")
        or story_input.get("monitor_stop_policy_trace")
    )
    out = {
        "posture": clip(monitor_reason.get("posture"), max_len=40) or action or "WAIT",
        "trigger_type": clip(monitor_reason.get("trigger_type"), max_len=80) or "not_captured",
        "position_age_seconds": int(monitor_reason.get("position_age_seconds") or 0),
        "hard_stop_pct": monitor_reason.get("hard_stop_pct") or monitor_stop_trace.get("hard_stop_pct"),
        "adaptive_stop_loss_pct": monitor_reason.get("adaptive_stop_loss_pct") or monitor_stop_trace.get("adaptive_stop_loss_pct"),
        "stop_loss_pct": monitor_reason.get("stop_loss_pct"),
        "effective_stop_loss_pct": monitor_reason.get("effective_stop_loss_pct") or monitor_stop_trace.get("effective_stop_loss_pct"),
        "effective_stop_reason": clip(monitor_reason.get("effective_stop_reason"), max_len=80) or "not_captured",
        "strategist_baseline_stop_loss_pct": monitor_reason.get("strategist_baseline_stop_loss_pct")
        or monitor_stop_trace.get("strategist_baseline_stop_loss_pct"),
        "strategist_baseline_take_profit_pct": monitor_reason.get("strategist_baseline_take_profit_pct")
        or monitor_stop_trace.get("strategist_baseline_take_profit_pct"),
        "strategist_baseline_trailing_stop_pct": monitor_reason.get("strategist_baseline_trailing_stop_pct")
        or monitor_stop_trace.get("strategist_baseline_trailing_stop_pct"),
        "take_profit_pct": monitor_reason.get("take_profit_pct") or monitor_stop_trace.get("take_profit_pct"),
        "trailing_stop_pct": monitor_reason.get("trailing_stop_pct") or monitor_stop_trace.get("trailing_stop_pct"),
        "exit_triggered": bool(monitor_reason.get("exit_triggered")),
        "current_price": monitor_reason.get("current_price"),
        "average_price": monitor_reason.get("average_price"),
        "peak_price": monitor_reason.get("peak_price"),
        "current_drawdown": monitor_reason.get("current_drawdown"),
        "peak_drawdown": monitor_reason.get("peak_drawdown"),
        "vwap_distance": monitor_reason.get("vwap_distance"),
        "active_exit_axis": clip(monitor_reason.get("active_exit_axis"), max_len=80),
        "watch_axes": listify(monitor_reason.get("watch_axes"), max_items=8, max_len=120),
        "price_source": clip(monitor_reason.get("price_source"), max_len=120) or "not_captured",
        "feature_source": clip(monitor_reason.get("feature_source"), max_len=120) or "not_captured",
        "price_source_policy": clip(monitor_reason.get("price_source_policy"), max_len=260) or "",
    }
    entry_visibility = entry_execution_visibility if isinstance(entry_execution_visibility, dict) else {}
    cascade = as_dict(entry_visibility.get("monitor_entry_candidate_cascade"))
    if not cascade and compact_entry_candidate_cascade is not None:
        cascade = compact_entry_candidate_cascade(monitor_reason.get("entry_candidate_cascade"))
    if cascade:
        out["entry_candidate_cascade"] = cascade
    for key in ("quant_factor_snapshot", "entry_quant_decision", "exit_quant_decision"):
        value = monitor_reason.get(key)
        if not isinstance(value, dict):
            value = story_input.get(key)
        if isinstance(value, dict) and value:
            out[key] = dict(value)
    return out


def enrich_market_context_for_fallback(
    *,
    market_context: Dict[str, Any],
    strategist_context: Dict[str, Any],
    policy_ref_context: Dict[str, Any],
    scanner_bias_summary: Dict[str, Any],
) -> Dict[str, Any]:
    out = dict(market_context or {})
    if strategist_context.get("playbook") and not out.get("playbook"):
        out["playbook"] = strategist_context.get("playbook")
    if strategist_context.get("selected_playbook") and not out.get("selected_playbook"):
        out["selected_playbook"] = strategist_context.get("selected_playbook")
    if strategist_context.get("policy_source") and not out.get("policy_source"):
        out["policy_source"] = strategist_context.get("policy_source")
    if strategist_context.get("risk_tone") and not out.get("risk_tone"):
        out["risk_tone"] = strategist_context.get("risk_tone")
    if strategist_context.get("trade_aggressiveness") and not out.get("trade_aggressiveness"):
        out["trade_aggressiveness"] = strategist_context.get("trade_aggressiveness")
    if strategist_context.get("monitor_guidance") and not out.get("monitor_guidance"):
        out["monitor_guidance"] = strategist_context.get("monitor_guidance")
    if strategist_context.get("themes") and not out.get("themes"):
        out["themes"] = list(strategist_context.get("themes") or [])
    if strategist_context.get("preferred_themes") and not out.get("preferred_themes"):
        out["preferred_themes"] = list(strategist_context.get("preferred_themes") or [])
    for theme_key in (
        "theme_strength_packet",
        "theme_source",
        "theme_source_status",
        "theme_source_reason",
        "theme_strength_top_themes",
        "theme_strength_scores",
    ):
        if strategist_context.get(theme_key) not in (None, "", [], {}) and not out.get(theme_key):
            out[theme_key] = strategist_context.get(theme_key)
    if strategist_context.get("market_context_summary") and not out.get("summary"):
        out["summary"] = strategist_context.get("market_context_summary")
    if policy_ref_context.get("risk_mode") and not out.get("risk_mode"):
        out["risk_mode"] = policy_ref_context.get("risk_mode")
    if policy_ref_context.get("selected_playbook") and not out.get("selected_playbook"):
        out["selected_playbook"] = policy_ref_context.get("selected_playbook")
    if policy_ref_context.get("preferred_themes") and not out.get("preferred_themes"):
        out["preferred_themes"] = policy_ref_context.get("preferred_themes")
    if policy_ref_context.get("avoid_themes") and not out.get("avoid_themes"):
        out["avoid_themes"] = policy_ref_context.get("avoid_themes")
    if scanner_bias_summary and not out.get("scanner_bias_summary"):
        out["scanner_bias_summary"] = scanner_bias_summary
    return out


def enrich_scanner_reason_for_fallback(
    *,
    scanner_reason: Dict[str, Any],
    shared_scanner_reasoning: Dict[str, Any],
    shared_selection_trace: Dict[str, Any],
) -> Dict[str, Any]:
    out = dict(scanner_reason or {})
    if shared_scanner_reasoning.get("selection_reason_with_bias") and not out.get("selection_reason_with_bias"):
        out["selection_reason_with_bias"] = shared_scanner_reasoning.get("selection_reason_with_bias")
    if shared_scanner_reasoning.get("selection_reason_with_bias") and not out.get("summary"):
        out["summary"] = shared_scanner_reasoning.get("selection_reason_with_bias")
    if shared_selection_trace.get("selected_symbol") and not out.get("selected_symbol"):
        out["selected_symbol"] = shared_selection_trace.get("selected_symbol")
    if shared_selection_trace.get("selected_rank") and not out.get("selected_rank"):
        out["selected_rank"] = shared_selection_trace.get("selected_rank")
    if shared_selection_trace.get("selected_symbol_score_drivers") and not out.get("selected_symbol_score_drivers"):
        out["selected_symbol_score_drivers"] = dict(shared_selection_trace.get("selected_symbol_score_drivers") or {})
    if shared_selection_trace.get("ranked_candidates") and not out.get("top_candidates"):
        out["top_candidates"] = list(shared_selection_trace.get("ranked_candidates") or [])
    return out


def merge_trade_report_candidate(
    story_input: Dict[str, Any],
    candidate: Dict[str, Any],
    *,
    status: str,
    mode: str,
    model: str,
    reason: str,
    fallback_report: Callable[..., Dict[str, Any]],
    normalize_section: Callable[..., Dict[str, Any]],
    merge_section_with_fallback: Callable[..., Dict[str, Any]],
    prefer_fallback_text: Callable[[Any, Any], str],
    listify: Callable[..., List[Any]],
    clip: Callable[..., str],
    normalize_trade_report_output: Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]],
) -> Dict[str, Any]:
    out = fallback_report(
        story_input,
        status=status,
        mode=mode,
        model=model,
        reason=reason,
    )
    out["generation"] = {
        "status": status,
        "mode": mode,
        "model": clip(model, max_len=120),
        "reason": clip(reason, max_len=320),
    }
    used_fallback_sections: List[str] = []

    def _merge_into(section_key: str, source_value: Any, fallback_key: str | None = None) -> None:
        normalized = normalize_section(
            source_value,
            default_summary=(out.get(section_key) or {}).get("summary") or "",
        )
        merged = merge_section_with_fallback(
            normalized,
            out.get(section_key) if isinstance(out.get(section_key), dict) else {},
            section_key=section_key,
        )
        if not (isinstance(source_value, dict) and source_value):
            used_fallback_sections.append(section_key)
        out[section_key] = merged
        if fallback_key:
            out[fallback_key] = dict(merged)

    _merge_into("executive_summary", candidate.get("executive_summary"))
    _merge_into("market_context_at_entry", candidate.get("market_context_at_entry") or candidate.get("market_context"), "market_context")
    _merge_into("strategist_summary", candidate.get("strategist_summary"))
    _merge_into("strategist_refresh_trace", candidate.get("strategist_refresh_trace"))
    _merge_into("why_this_symbol_was_chosen", candidate.get("why_this_symbol_was_chosen") or candidate.get("why_this_symbol"), "why_this_symbol")
    _merge_into("entry_decision", candidate.get("entry_decision"))
    _merge_into("holding_monitoring_story", candidate.get("holding_monitoring_story") or candidate.get("monitor_trigger_reasoning"), "monitor_trigger_reasoning")
    _merge_into("exit_decision", candidate.get("exit_decision"))
    _merge_into("execution_quality", candidate.get("execution_quality") or candidate.get("execution_result"), "execution_result")
    _merge_into("scanner_filters", candidate.get("scanner_filters") or candidate.get("scanner_logic_and_filters"), "scanner_logic_and_filters")
    _merge_into("guard_approval_result", candidate.get("guard_approval_result"))
    out["reporter_evaluation"] = merge_section_with_fallback(
        normalize_section(candidate.get("reporter_evaluation"), default_summary=out["reporter_evaluation"]["summary"]),
        out["reporter_evaluation"],
        section_key="reporter_evaluation",
    )
    if not isinstance(candidate.get("reporter_evaluation"), dict):
        used_fallback_sections.append("reporter_evaluation")
    out["errors_weaknesses_improvement_points"] = merge_section_with_fallback(
        normalize_section(
            candidate.get("errors_weaknesses_improvement_points"),
            default_summary=out["errors_weaknesses_improvement_points"]["summary"],
        ),
        out["errors_weaknesses_improvement_points"],
        section_key="errors_weaknesses_improvement_points",
    )
    if not isinstance(candidate.get("errors_weaknesses_improvement_points"), dict):
        used_fallback_sections.append("errors_weaknesses_improvement_points")

    final_conclusion = candidate.get("final_operator_conclusion") if isinstance(candidate.get("final_operator_conclusion"), dict) else {}
    out["final_operator_conclusion"] = {
        "summary": prefer_fallback_text(final_conclusion.get("summary"), out["final_operator_conclusion"]["summary"]),
        "current_action": clip(final_conclusion.get("current_action"), max_len=24) or out["final_operator_conclusion"]["current_action"],
        "watch_next": listify(final_conclusion.get("watch_next"), max_items=6, max_len=200) or out["final_operator_conclusion"]["watch_next"],
        "thesis_invalidation": listify(final_conclusion.get("thesis_invalidation"), max_items=6, max_len=200)
        or out["final_operator_conclusion"]["thesis_invalidation"],
    }
    if not final_conclusion:
        used_fallback_sections.append("final_operator_conclusion")

    timeline_rows: List[Dict[str, Any]] = []
    parsed_timeline = candidate.get("full_timeline")
    if isinstance(parsed_timeline, list):
        timeline_rows = [row for row in parsed_timeline if isinstance(row, dict)][:24]
    if not timeline_rows:
        timeline_rows = [row for row in list(candidate.get("timeline") or []) if isinstance(row, dict)][:24]
    if timeline_rows:
        out["full_timeline"] = timeline_rows
        out["timeline"] = timeline_rows
    else:
        used_fallback_sections.append("timeline")

    out["used_fallback_sections"] = sorted(set(used_fallback_sections))
    return normalize_trade_report_output(story_input, out)


def build_deterministic_trade_report(
    story_input: Dict[str, Any],
    *,
    fallback_report: Callable[..., Dict[str, Any]],
    attach_report_status_matrix: Callable[..., Dict[str, Any]],
) -> Dict[str, Any]:
    report = fallback_report(
        story_input,
        status="ok",
        mode="deterministic",
        model="",
        reason="deterministic_report_generated",
    )
    return attach_report_status_matrix(
        report,
        story_input,
        ai_trade_report_status="skipped",
        deterministic_report_status="ok",
    )


def failure_report(
    story_input: Dict[str, Any],
    *,
    status: str,
    mode: str,
    model: str,
    reason: str,
    error: str = "",
    build_shared_summary_seed: Callable[[Dict[str, Any]], Dict[str, Any]],
    clip: Callable[..., str],
    actual_lifecycle_action: Callable[[Dict[str, Any]], str],
    as_dict: Callable[[Any], Dict[str, Any]],
    utc_now_iso: Callable[[], str],
    build_report_strategist_refresh_trace: Callable[[Dict[str, Any]], Dict[str, Any]],
    listify: Callable[..., List[Any]],
    build_monitor_snapshot_fn: Callable[..., Dict[str, Any]],
    normalize_trade_report_output: Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]],
) -> Dict[str, Any]:
    shared_seed = build_shared_summary_seed(story_input)
    trade_id = clip(shared_seed.get("trade_id"), max_len=120) or clip(story_input.get("trade_id") or story_input.get("story_id"), max_len=120)
    action = clip(shared_seed.get("lifecycle_action"), max_len=24) or actual_lifecycle_action(story_input)
    symbol = clip(shared_seed.get("symbol"), max_len=32) or clip(story_input.get("symbol"), max_len=32) or "unknown"
    status_text = clip(shared_seed.get("lifecycle_status"), max_len=32) or clip(story_input.get("status"), max_len=32) or "unknown"
    reporter_status = story_input.get("reporter_status_human") if isinstance(story_input.get("reporter_status_human"), dict) else {}
    monitor_reason = story_input.get("monitor_reason_human") if isinstance(story_input.get("monitor_reason_human"), dict) else {}
    full_timeline = [
        row
        for row in list(story_input.get("timeline") or [])
        if isinstance(row, dict)
    ][:24]
    out = {
        "schema_version": "ai_trade_report.v2",
        "generated_at": utc_now_iso(),
        "trade_id": trade_id,
        "story_id": clip(story_input.get("story_id"), max_len=120) or trade_id,
        "run_id": clip(story_input.get("run_id"), max_len=120),
        "symbol": symbol,
        "action": action,
        "status": status_text,
        "story_type": clip(story_input.get("story_type"), max_len=40),
        "execution_mode_label": clip(story_input.get("execution_mode_label"), max_len=80),
        "generation": {
            "status": status,
            "mode": mode,
            "model": clip(model, max_len=120),
            "reason": clip(reason, max_len=320),
        },
        "failure": {
            "status": status,
            "reason": clip(reason, max_len=320),
            "error": clip(error, max_len=500),
        },
        "executive_summary": {
            "headline": f"AI trade report failed for {symbol}",
            "action": action,
            "symbol": symbol,
            "confidence": "not_available",
            "summary": "AI trade report generation failed after retry attempts. Review the saved LLM response artifact for details.",
        },
        "market_context_at_entry": {
            "summary": "AI generation failed before a rendered market-context section was produced.",
            "bullets": [],
        },
        "strategist_summary": {
            "summary": "AI generation failed before a rendered strategist-summary section was produced.",
            "bullets": [],
        },
        "strategist_refresh_trace": build_report_strategist_refresh_trace(story_input),
        "why_this_symbol_was_chosen": {
            "summary": "AI generation failed before a rendered symbol-selection section was produced.",
            "bullets": [],
        },
        "entry_decision": {
            "summary": "AI generation failed before a rendered entry-decision section was produced.",
            "bullets": [],
        },
        "holding_monitoring_story": {
            "summary": "AI generation failed before a rendered holding-monitoring section was produced.",
            "bullets": listify(monitor_reason.get("bullets"), max_items=8, max_len=260),
        },
        "exit_decision": {
            "summary": "AI generation failed before a rendered exit-decision section was produced.",
            "bullets": [],
        },
        "execution_quality": {
            "summary": "AI generation failed before a rendered execution-quality section was produced.",
            "bullets": [],
        },
        "monitor_snapshot": build_monitor_snapshot_fn(
            monitor_reason=monitor_reason,
            story_input=story_input,
            action=action,
        ),
        "scanner_filters": {
            "summary": "AI generation failed before a rendered scanner-filter section was produced.",
            "bullets": [],
        },
        "guard_approval_result": {
            "summary": "AI generation failed before a rendered guard-approval section was produced.",
            "bullets": [],
        },
        "reporter_evaluation": {
            "summary": clip(reporter_status.get("summary"), max_len=600) or "Reporter linkage status was recorded separately.",
            "status": clip(reporter_status.get("status"), max_len=40) or "missing",
            "grade": clip(reporter_status.get("grade"), max_len=16) or "N/A",
            "bullets": listify(reporter_status.get("bullets"), max_items=8, max_len=260),
        },
        "errors_weaknesses_improvement_points": {
            "summary": "AI generation failed and no rendered improvement section is available.",
            "bullets": [entry for entry in [clip(reason, max_len=240), clip(error, max_len=240)] if entry],
        },
        "full_timeline": full_timeline,
        "timeline": full_timeline,
        "final_operator_conclusion": {
            "summary": "AI generation failed. Review lifecycle artifacts and the saved LLM response artifact before taking action.",
            "current_action": "HOLD" if status_text.lower() == "open" and action == "BUY" else action,
            "watch_next": [],
            "thesis_invalidation": [],
        },
    }
    out["market_context"] = dict(out.get("market_context_at_entry") or {})
    out["why_this_symbol"] = dict(out.get("why_this_symbol_was_chosen") or {})
    out["scanner_logic_and_filters"] = dict(out.get("scanner_filters") or {})
    out["monitor_trigger_reasoning"] = dict(out.get("holding_monitoring_story") or {})
    out["execution_result"] = dict(out.get("execution_quality") or {})
    return normalize_trade_report_output(story_input, out)

def fallback_report(
    story_input: Dict[str, Any],
    *,
    status: str,
    mode: str,
    model: str,
    reason: str,
    deps: Dict[str, Any],
) -> Dict[str, Any]:
    """Build the deterministic fallback report behind the compatibility façade."""

    _build_shared_summary_seed = deps["build_shared_summary_seed"]
    build_trade_report_memory_surface = deps["build_trade_report_memory_surface"]
    _as_dict = deps["as_dict"]
    _extract_policy_ref_context = deps["extract_policy_ref_context"]
    _extract_scanner_bias_summary = deps["extract_scanner_bias_summary"]
    _enrich_market_context_for_fallback = deps["enrich_market_context_for_fallback"]
    _fallback_section_seeds = deps["fallback_section_seeds"]
    _enrich_scanner_reason_for_fallback = deps["enrich_scanner_reason_for_fallback"]
    _clip = deps["clip"]
    _build_report_monitor_snapshot = deps["build_report_monitor_snapshot"]
    _resolve_entry_monitor_reason = deps["resolve_entry_monitor_reason"]
    _listify = deps["listify"]
    _scanner_chart_feature_coverage = deps["scanner_chart_feature_coverage"]
    _build_scanner_choice_bullets = deps["build_scanner_choice_bullets"]
    _append_news_scanner_choice_details = deps["append_news_scanner_choice_details"]
    _lifecycle_summary_conflicts_with_status = deps["lifecycle_summary_conflicts_with_status"]
    _build_scanner_choice_summary = deps["build_scanner_choice_summary"]
    _build_market_context_summary = deps["build_market_context_summary"]
    _build_market_context_bullets = deps["build_market_context_bullets"]
    _build_market_scanner_linkage_bullet = deps["build_market_scanner_linkage_bullet"]
    _build_strategist_summary_section = deps["build_strategist_summary_section"]
    _build_entry_decision_summary = deps["build_entry_decision_summary"]
    _build_entry_decision_bullets = deps["build_entry_decision_bullets"]
    _build_holding_story_summary = deps["build_holding_story_summary"]
    _build_holding_story_bullets = deps["build_holding_story_bullets"]
    _build_exit_decision_summary = deps["build_exit_decision_summary"]
    _build_exit_decision_bullets = deps["build_exit_decision_bullets"]
    _build_execution_quality_section = deps["build_execution_quality_section"]
    _build_scanner_filters_summary = deps["build_scanner_filters_summary"]
    _build_scanner_filters_bullets = deps["build_scanner_filters_bullets"]
    _build_reporter_evaluation_section = deps["build_reporter_evaluation_section"]
    _holding_duration_label = deps["holding_duration_label"]
    _exit_reason_label = deps["exit_reason_label"]
    _is_low_information_bullet = deps["is_low_information_bullet"]
    _reporter_summary_is_placeholder = deps["reporter_summary_is_placeholder"]
    _scanner_basis_text = deps["scanner_basis_text"]
    _build_report_shared_facts = deps["build_report_shared_facts"]
    _attach_backward_compatible_aliases = deps["attach_backward_compatible_aliases"]
    _build_report_strategist_refresh_trace = deps["build_report_strategist_refresh_trace"]
    _compact_strategist_report_context = deps["compact_strategist_report_context"]
    _compact_scalar_dict = deps["compact_scalar_dict"]
    _story_post_exit_shadow = deps["story_post_exit_shadow"]
    _utc_now_iso = deps["utc_now_iso"]
    build_trade_report_truth_surface = deps["build_trade_report_truth_surface"]
    build_trade_memory_application_surface = deps["build_trade_memory_application_surface"]
    execution_outcome_summary_is_placeholder = deps["execution_outcome_summary_is_placeholder"]

    action, entry_decision_seed, entry_execution_visibility, execution_outcome, execution_quality_seed, exit_decision_seed, filters_human, final_operator_conclusion_seed, guard_approval_seed, guard_reason, has_runtime_market_context, has_runtime_monitor_reason, has_runtime_scanner_reason, holding_story_seed, market_context, market_context_seed, memory_surface, monitor_reason, operator_conclusion, reporter_evaluation_seed, reporter_feedback_packet, reporter_status, scanner_filters_seed, scanner_reason, shared_seed, shared_selection_trace, strategist_context, strategist_evidence, strategist_summary_seed, why_symbol_seed = fallback_report_seed(_build_shared_summary_seed=_build_shared_summary_seed, story_input=story_input, build_trade_report_memory_surface=build_trade_report_memory_surface, _as_dict=_as_dict, _extract_policy_ref_context=_extract_policy_ref_context, _extract_scanner_bias_summary=_extract_scanner_bias_summary, _enrich_market_context_for_fallback=_enrich_market_context_for_fallback, _fallback_section_seeds=_fallback_section_seeds, _enrich_scanner_reason_for_fallback=_enrich_scanner_reason_for_fallback, _clip=_clip, facade=_r3_sys.modules[__name__])
    monitor_snapshot = _build_report_monitor_snapshot(
        monitor_reason=monitor_reason,
        story_input=story_input,
        action=action,
        entry_execution_visibility=entry_execution_visibility,
    )
    entry_summary = story_input.get("entry_summary") if isinstance(story_input.get("entry_summary"), dict) else {}
    entry_monitor_reason = _resolve_entry_monitor_reason(story_input, monitor_reason, entry_summary)
    for key in (
        "entry_metrics",
        "entry_thresholds",
        "entry_condition_scores",
        "entry_grouped_logic_trace",
        "entry_condition_path",
        "entry_condition_paths_passed",
        "entry_reason",
    ):
        value = entry_monitor_reason.get(key)
        if value not in (None, "", [], {}) and monitor_snapshot.get(key) in (None, "", [], {}):
            monitor_snapshot[key] = value
    effective_scanner_selection_trace, exit_summary, holding_summary, improvement_points, lifecycle_summary, news_scanner_contribution, scanner_selection_trace, warnings = fb_summary_effective_scanner_selection_trace_exit_s(story_input=story_input, _listify=_listify, _as_dict=_as_dict, entry_summary=entry_summary, scanner_reason=scanner_reason, shared_selection_trace=shared_selection_trace, facade=_r3_sys.modules[__name__])
    if isinstance(effective_scanner_selection_trace.get("chart_feature_coverage"), dict):
        effective_scanner_selection_trace["chart_feature_coverage"] = _scanner_chart_feature_coverage(
            {"scanner_selection_trace": effective_scanner_selection_trace}
        )
    why_symbol_bullets = _build_scanner_choice_bullets(scanner_reason, market_context)
    why_symbol_bullets = _append_news_scanner_choice_details(why_symbol_bullets, news_scanner_contribution)
    raw_scanner_bullets = _listify(scanner_reason.get("bullets"), max_items=8, max_len=220)
    raw_scanner_bullets.extend(_listify(scanner_reason.get("why_selected"), max_items=4, max_len=180))
    selection_basis_text = _clip(scanner_reason.get("selection_basis"), max_len=220)
    if selection_basis_text:
        raw_scanner_bullets.append(f"Final decision basis: {selection_basis_text}")
    tie_break_text = _clip(scanner_reason.get("tie_break_rule"), max_len=220)
    if tie_break_text:
        raw_scanner_bullets.append(f"Tie-break rule: {tie_break_text}")
    runner_up_summaries = [
        f"Runner-ups lost because: {_clip((row or {}).get('symbol'), max_len=24)}: {_clip((row or {}).get('summary'), max_len=160)}"
        for row in list(scanner_reason.get("runner_ups_lost") or [])[:4]
        if isinstance(row, dict) and str((row or {}).get("symbol") or "").strip() and str((row or {}).get("summary") or "").strip()
    ]
    raw_scanner_bullets.extend(runner_up_summaries)
    for row in raw_scanner_bullets:
        if row and row not in why_symbol_bullets:
            why_symbol_bullets.append(row)

    confidence, executive_reason, lifecycle_summary_text, market_context_summary, scanner_choice_summary, status_text, strategist_summary, strategist_summary_summary, symbol, trade_id = fb_summary_confidence_executive_reason(_clip=_clip, shared_seed=shared_seed, story_input=story_input, operator_conclusion=operator_conclusion, lifecycle_summary=lifecycle_summary, _lifecycle_summary_conflicts_with_status=_lifecycle_summary_conflicts_with_status, execution_outcome=execution_outcome, scanner_reason=scanner_reason, _build_scanner_choice_summary=_build_scanner_choice_summary, market_context=market_context, _is_low_information_bullet=_is_low_information_bullet, has_runtime_scanner_reason=has_runtime_scanner_reason, scanner_selection_trace=scanner_selection_trace, why_symbol_seed=why_symbol_seed, _build_market_context_summary=_build_market_context_summary, has_runtime_market_context=has_runtime_market_context, market_context_seed=market_context_seed, _build_strategist_summary_section=_build_strategist_summary_section, facade=_r3_sys.modules[__name__])
    if (
        not has_runtime_market_context
        or not strategist_summary_summary
        or _is_low_information_bullet(strategist_summary_summary)
    ) and str(strategist_summary_seed.get("summary") or "").strip():
        strategist_summary["summary"] = _clip(strategist_summary_seed.get("summary"), max_len=600)
    if (not strategist_summary.get("bullets")) and isinstance(strategist_summary_seed.get("bullets"), list):
        strategist_summary["bullets"] = _listify(strategist_summary_seed.get("bullets"), max_items=10, max_len=260)
    entry_decision, exit_decision, holding_story, scanner_filters_bullets, scanner_filters_summary, strategist_refresh_trace, why_symbol_bullets = fb_sections_entry_decision_exit_decision(_build_report_strategist_refresh_trace=_build_report_strategist_refresh_trace, story_input=story_input, why_symbol_bullets=why_symbol_bullets, _listify=_listify, why_symbol_seed=why_symbol_seed, _build_scanner_filters_summary=_build_scanner_filters_summary, filters_human=filters_human, _build_scanner_filters_bullets=_build_scanner_filters_bullets, _clip=_clip, scanner_filters_seed=scanner_filters_seed, _build_entry_decision_bullets=_build_entry_decision_bullets, entry_summary=entry_summary, scanner_reason=scanner_reason, market_context=market_context, entry_monitor_reason=entry_monitor_reason, action=action, _build_entry_decision_summary=_build_entry_decision_summary, shared_seed=shared_seed, has_runtime_scanner_reason=has_runtime_scanner_reason, _is_low_information_bullet=_is_low_information_bullet, entry_decision_seed=entry_decision_seed, holding_summary=holding_summary, _build_holding_story_summary=_build_holding_story_summary, monitor_reason=monitor_reason, status_text=status_text, _build_holding_story_bullets=_build_holding_story_bullets, has_runtime_monitor_reason=has_runtime_monitor_reason, holding_story_seed=holding_story_seed, _holding_duration_label=_holding_duration_label, exit_summary=exit_summary, _build_exit_decision_bullets=_build_exit_decision_bullets, _build_exit_decision_summary=_build_exit_decision_summary, exit_decision_seed=exit_decision_seed, facade=_r3_sys.modules[__name__])
    if _clip(shared_seed.get("exit_reason"), max_len=240):
        exit_reason_label = _exit_reason_label(_clip(shared_seed.get("exit_reason"), max_len=240))
        exit_decision["bullets"] = [f"정규화된 청산 사유는 {exit_reason_label or _clip(shared_seed.get('exit_reason'), max_len=240)}입니다."] + list(
            exit_decision.get("bullets") or []
        )
    execution_quality = _build_execution_quality_section(
        story_input,
        execution_outcome,
        lifecycle_summary,
    )
    if execution_outcome_summary_is_placeholder(execution_quality_seed.get("summary")) and _clip(execution_quality.get("summary"), max_len=600):
        execution_quality_seed = dict(execution_quality_seed)
        execution_quality_seed["summary"] = _clip(execution_quality.get("summary"), max_len=600)
        if execution_quality.get("bullets"):
            execution_quality_seed["bullets"] = _listify(execution_quality.get("bullets"), max_items=12, max_len=260)
    if (
        not execution_outcome
        or not _clip(execution_quality.get("summary"), max_len=600)
        or _is_low_information_bullet(execution_quality.get("summary"))
    ) and str(execution_quality_seed.get("summary") or "").strip():
        execution_quality["summary"] = _clip(execution_quality_seed.get("summary"), max_len=600)
    if (not execution_quality.get("bullets")) and isinstance(execution_quality_seed.get("bullets"), list):
        execution_quality["bullets"] = _listify(execution_quality_seed.get("bullets"), max_items=12, max_len=260)
    reporter_eval = _build_reporter_evaluation_section(
        shared_seed,
        scanner_reason,
        monitor_reason,
        execution_outcome,
        reporter_status,
        reporter_feedback_packet,
    )
    if _reporter_summary_is_placeholder(reporter_eval.get("summary")) and _clip(reporter_evaluation_seed.get("summary"), max_len=600):
        reporter_eval["summary"] = _clip(reporter_evaluation_seed.get("summary"), max_len=600)
        if reporter_evaluation_seed.get("bullets"):
            reporter_eval["bullets"] = _listify(reporter_evaluation_seed.get("bullets"), max_items=12, max_len=260)
        if reporter_evaluation_seed.get("status"):
            reporter_eval["status"] = _clip(reporter_evaluation_seed.get("status"), max_len=48)
        if reporter_evaluation_seed.get("grade"):
            reporter_eval["grade"] = _clip(reporter_evaluation_seed.get("grade"), max_len=24)
    if (
        not reporter_status
        or not _clip(reporter_eval.get("summary"), max_len=600)
        or _is_low_information_bullet(reporter_eval.get("summary"))
    ) and str(reporter_evaluation_seed.get("summary") or "").strip():
        reporter_eval["summary"] = _clip(reporter_evaluation_seed.get("summary"), max_len=600)
    if (not reporter_eval.get("bullets")) and isinstance(reporter_evaluation_seed.get("bullets"), list):
        reporter_eval["bullets"] = _listify(reporter_evaluation_seed.get("bullets"), max_items=12, max_len=260)
    reporter_eval_status = _clip(reporter_eval.get("status"), max_len=48)
    if (
        not reporter_status
        or not reporter_eval_status
        or reporter_eval_status.lower() in {"missing", "not_captured", "unknown", "n/a"}
    ) and str(reporter_evaluation_seed.get("status") or "").strip():
        reporter_eval["status"] = _clip(reporter_evaluation_seed.get("status"), max_len=48)
    reporter_eval_grade = _clip(reporter_eval.get("grade"), max_len=24)
    if (
        not reporter_status
        or not reporter_eval_grade
        or reporter_eval_grade.lower() in {"missing", "not_captured", "unknown", "n/a"}
    ) and str(reporter_evaluation_seed.get("grade") or "").strip():
        reporter_eval["grade"] = _clip(reporter_evaluation_seed.get("grade"), max_len=24)
    weaknesses_bullets = warnings + [item for item in improvement_points if item not in warnings]
    full_timeline = [
        row
        for row in list(story_input.get("timeline") or [])
        if isinstance(row, dict)
    ][:24]

    out = fb_sections_out(trade_id=trade_id, symbol=symbol, action=action, status_text=status_text, strategist_summary=strategist_summary, strategist_refresh_trace=strategist_refresh_trace, entry_execution_visibility=entry_execution_visibility, entry_decision=entry_decision, exit_decision=exit_decision, execution_quality=execution_quality, reporter_eval=reporter_eval, full_timeline=full_timeline, _utc_now_iso=_utc_now_iso, _clip=_clip, status=status, mode=mode, executive_reason=executive_reason, market_context_summary=market_context_summary, effective_scanner_selection_trace=effective_scanner_selection_trace, news_scanner_contribution=news_scanner_contribution, holding_story=holding_story, monitor_snapshot=monitor_snapshot, scanner_filters_summary=scanner_filters_summary, scanner_filters_bullets=scanner_filters_bullets, weaknesses_bullets=weaknesses_bullets, _build_report_shared_facts=_build_report_shared_facts, model=model, reason=reason, confidence=confidence, _build_market_context_bullets=_build_market_context_bullets, market_context=market_context, _listify=_listify, _compact_scalar_dict=_compact_scalar_dict, _as_dict=_as_dict, _build_market_scanner_linkage_bullet=_build_market_scanner_linkage_bullet, scanner_reason=scanner_reason, why_symbol_bullets=why_symbol_bullets, _scanner_basis_text=_scanner_basis_text, shared_seed=shared_seed, story_input=story_input, scanner_choice_summary=scanner_choice_summary, lifecycle_summary_text=lifecycle_summary_text, strategist_context=strategist_context, strategist_evidence=strategist_evidence, guard_reason=guard_reason, guard_approval_seed=guard_approval_seed, operator_conclusion=operator_conclusion, final_operator_conclusion_seed=final_operator_conclusion_seed, build_trade_report_truth_surface=build_trade_report_truth_surface, memory_surface=memory_surface, build_trade_memory_application_surface=build_trade_memory_application_surface, _compact_strategist_report_context=_compact_strategist_report_context, facade=_r3_sys.modules[__name__])[0]
    post_exit_shadow = _story_post_exit_shadow(story_input)
    if post_exit_shadow:
        out["post_exit_shadow"] = dict(post_exit_shadow)
    return _attach_backward_compatible_aliases(out)



