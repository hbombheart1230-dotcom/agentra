from __future__ import annotations

from typing import Any, Dict, List, Mapping


def entry_watch_execution_lines(report: Dict[str, Any], *, require_trade_symbol_match: bool = False, deps: Mapping[str, Any]) -> List[str]:
    _as_dict = deps["as_dict"]
    _candidate_cascade_matches_trade = deps["candidate_cascade_matches_trade"]
    _candidate_watch_reason_label = deps["candidate_watch_reason_label"]
    _dedupe = deps["dedupe"]
    _display_candidate_symbol = deps["display_candidate_symbol"]
    _listify = deps["listify"]
    _metadata_value = deps["metadata_value"]
    _resolve_entry_execution_visibility = deps["resolve_entry_execution_visibility"]
    _watch_scope_label = deps["watch_scope_label"]
    visibility = _resolve_entry_execution_visibility(report)
    if not visibility:
        return []
    proposal = _as_dict(visibility.get("strategy_candidate_watch_proposal"))
    entry_control = _as_dict(visibility.get("commander_entry_control"))
    cascade = _as_dict(visibility.get("monitor_entry_candidate_cascade"))
    focus_context = _as_dict(visibility.get("monitor_focus_context"))
    shared = _as_dict(report.get("shared_facts"))
    traded_symbol = _display_candidate_symbol(report.get("symbol") or shared.get("symbol"))
    cascade_matches_trade = (
        _candidate_cascade_matches_trade(cascade, traded_symbol)
        if require_trade_symbol_match
        else True
    )
    lines: List[str] = []

    if focus_context:
        entry_symbol = _display_candidate_symbol(
            focus_context.get("entry_final_symbol") or focus_context.get("entry_candidate_symbol")
        )
        position_symbol = _display_candidate_symbol(focus_context.get("position_focus_symbol"))
        if entry_symbol and position_symbol and entry_symbol != position_symbol:
            reason = _metadata_value(
                focus_context.get("entry_guard_reason") or focus_context.get("entry_reason")
            )
            text = f"신규 후보 {entry_symbol} 평가 / 보유 관리 {position_symbol}"
            if reason and reason != "-":
                text += f" / 신규 후보 보류 사유: {_candidate_watch_reason_label(reason)}"
            lines.append(text)

    if entry_control:
        scope = _watch_scope_label(entry_control)
        text = f"감시 범위: {scope}" if scope else ""
        if entry_control.get("cascade_enabled") not in (None, ""):
            cascade_text = f"cascade {'활성' if bool(entry_control.get('cascade_enabled')) else '비활성'}"
            text = f"{text} / {cascade_text}".strip(" /")
        if text:
            lines.append(text)

    if proposal:
        scope = _watch_scope_label(proposal)
        tactical = _metadata_value(proposal.get("tactical_strategy"))
        if scope:
            text = f"전략가 제안: {scope}"
            if tactical and tactical != "-":
                text += f" / 전술={tactical}"
            lines.append(text)
        elif tactical and tactical != "-" and not lines:
            lines.append(f"전술={tactical}.")

    if cascade and cascade_matches_trade:
        top_pick = _display_candidate_symbol(cascade.get("top_pick_symbol"))
        top_reason = _metadata_value(cascade.get("top_pick_reason") or cascade.get("reason"))
        runner_ups = [
            _display_candidate_symbol(symbol)
            for symbol in _listify(cascade.get("runner_up_symbols"))
            if _display_candidate_symbol(symbol)
        ]
        attempted = bool(cascade.get("attempted"))
        if attempted:
            text = f"실제 확인: 1순위 {top_pick or '-'} 보류"
            if runner_ups:
                text += f" -> 차순위 {', '.join(runner_ups)} 확인"
            if top_reason and top_reason != "-":
                text += f" (사유: {_candidate_watch_reason_label(top_reason)})"
            lines.append(text)
        else:
            blocked = _candidate_watch_reason_label(cascade.get("blocked_reason"))
            details: List[str] = []
            if top_pick and top_pick != "-":
                details.append(f"1순위 {top_pick}")
            if blocked:
                details.append(f"사유: {blocked}")
            text = "실제 확인: 차순위 미실행"
            if details:
                text += f" ({', '.join(details)})"
            lines.append(text)
        if bool(cascade.get("fallback_used")):
            final_symbol = _display_candidate_symbol(cascade.get("fallback_to_symbol") or cascade.get("final_selected_symbol"))
            final_rank = cascade.get("fallback_to_rank") or cascade.get("final_selected_rank")
            lines.append(f"최종 후보: {final_symbol or '-'}{f'({final_rank}위)' if final_rank not in (None, '') else ''}")
        elif cascade.get("final_selected_symbol"):
            final_symbol = _display_candidate_symbol(cascade.get("final_selected_symbol"))
            final_rank = cascade.get("final_selected_rank")
            lines.append(f"최종 후보: {final_symbol}{f'({final_rank}위)' if final_rank not in (None, '') else ''}")

    return _dedupe([line for line in lines if line])


def entry_watch_summary_lines(report: Dict[str, Any], *, require_trade_symbol_match: bool = False, deps: Mapping[str, Any]) -> List[str]:
    _as_dict = deps["as_dict"]
    _candidate_cascade_matches_trade = deps["candidate_cascade_matches_trade"]
    _candidate_watch_reason_label = deps["candidate_watch_reason_label"]
    _display_candidate_symbol = deps["display_candidate_symbol"]
    _listify = deps["listify"]
    _resolve_entry_execution_visibility = deps["resolve_entry_execution_visibility"]
    _watch_scope_label = deps["watch_scope_label"]
    visibility = _resolve_entry_execution_visibility(report)
    if not visibility:
        return []
    entry_control = _as_dict(visibility.get("commander_entry_control"))
    cascade = _as_dict(visibility.get("monitor_entry_candidate_cascade"))
    shared = _as_dict(report.get("shared_facts"))
    traded_symbol = _display_candidate_symbol(report.get("symbol") or shared.get("symbol"))
    cascade_matches_trade = (
        _candidate_cascade_matches_trade(cascade, traded_symbol)
        if require_trade_symbol_match
        else True
    )
    lines: List[str] = []

    scope = _watch_scope_label(entry_control)
    if scope:
        parts = [scope]
        if entry_control.get("cascade_enabled") not in (None, ""):
            parts.append(f"cascade {'활성' if bool(entry_control.get('cascade_enabled')) else '비활성'}")
        lines.append(" / ".join(parts))

    attempted = bool(cascade.get("attempted"))
    top_pick = _display_candidate_symbol(cascade.get("top_pick_symbol"))
    if cascade and cascade_matches_trade:
        if attempted:
            runner_ups = [
                _display_candidate_symbol(symbol)
                for symbol in _listify(cascade.get("runner_up_symbols"))
                if _display_candidate_symbol(symbol)
            ]
            if runner_ups:
                lines.append(f"실제 확인: 1순위 {top_pick or '-'} 보류 -> 차순위 {', '.join(runner_ups)} 확인")
        else:
            blocked = _candidate_watch_reason_label(cascade.get("blocked_reason"))
            details: List[str] = []
            if top_pick and top_pick != "-":
                details.append(f"1순위 {top_pick}")
            if blocked:
                details.append(f"사유: {blocked}")
            text = "실제 확인: 차순위 미실행"
            if details:
                text += f" ({', '.join(details)})"
            lines.append(text)

    if cascade and cascade_matches_trade:
        final_symbol = _display_candidate_symbol(cascade.get("final_selected_symbol") or cascade.get("fallback_to_symbol"))
        final_rank = cascade.get("final_selected_rank") or cascade.get("fallback_to_rank")
        if final_symbol and final_symbol != "-":
            rank_text = f"({final_rank}위)" if final_rank not in (None, "") else ""
            lines.append(f"최종 후보: {final_symbol}{rank_text}")

    return lines


def resolve_entry_signal_snapshot(report: Dict[str, Any], *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    _as_dict = deps["as_dict"]
    _first_present_value = deps["first_present_value"]
    _resolve_entry_execution_visibility = deps["resolve_entry_execution_visibility"]
    monitor = _as_dict(report.get("monitor_snapshot"))
    shared = _as_dict(report.get("shared_facts"))
    visibility = _resolve_entry_execution_visibility(report)
    focus_context = _as_dict(visibility.get("monitor_focus_context"))
    entry_metrics = _as_dict(monitor.get("entry_metrics"))
    if not entry_metrics:
        entry_metrics = _as_dict(focus_context.get("entry_metrics"))
    if not entry_metrics:
        entry_metrics = _as_dict(report.get("entry_metrics"))
    if not entry_metrics:
        entry_metrics = _as_dict(shared.get("entry_metrics"))
    human_detail_observed = _as_dict(entry_metrics.get("human_chart_detail_observed"))
    if not human_detail_observed:
        human_detail_observed = _as_dict(_as_dict(monitor.get("human_chart_detail_context")).get("observed"))
    if not human_detail_observed:
        human_detail_observed = _as_dict(_as_dict(focus_context.get("human_chart_detail_context")).get("observed"))

    entry_thresholds = _as_dict(monitor.get("entry_thresholds"))
    if not entry_thresholds:
        entry_thresholds = _as_dict(focus_context.get("entry_thresholds"))
    if not entry_thresholds:
        entry_thresholds = _as_dict(report.get("entry_thresholds"))
    if not entry_thresholds:
        entry_thresholds = _as_dict(shared.get("entry_thresholds"))

    snapshot: Dict[str, Any] = {}
    for key, value in {
        "current_price": _first_present_value(
            entry_metrics.get("current_price"),
            entry_metrics.get("price"),
            focus_context.get("current_price"),
            monitor.get("entry_price"),
            shared.get("broker_buy_price"),
        ),
        "vwap": _first_present_value(
            entry_metrics.get("vwap"),
            focus_context.get("vwap"),
            monitor.get("entry_vwap"),
        ),
        "vwap_distance": _first_present_value(
            entry_metrics.get("vwap_distance"),
            entry_metrics.get("extended_from_vwap_pct"),
            focus_context.get("vwap_distance"),
            monitor.get("entry_vwap_distance"),
            monitor.get("entry_extended_from_vwap_pct"),
        ),
        "volume": _first_present_value(
            entry_metrics.get("current_volume"),
            entry_metrics.get("current_bar_volume"),
            entry_metrics.get("volume"),
            focus_context.get("current_volume"),
        ),
        "volume_ratio": _first_present_value(
            entry_metrics.get("volume_ratio"),
            entry_metrics.get("volume_ratio_effective"),
            focus_context.get("volume_ratio"),
            monitor.get("entry_volume_ratio"),
        ),
        "volume_ratio_raw": _first_present_value(
            entry_metrics.get("volume_ratio_raw"),
            focus_context.get("volume_ratio_raw"),
        ),
        "volume_adjusted": _first_present_value(
            entry_metrics.get("volume_adjusted"),
            focus_context.get("volume_adjusted"),
        ),
        "volume_adjustment_reason": _first_present_value(
            entry_metrics.get("volume_adjustment_reason"),
            focus_context.get("volume_adjustment_reason"),
        ),
        "volume_ratio_min": _first_present_value(
            entry_thresholds.get("volume_ratio_min"),
            focus_context.get("volume_ratio_min"),
            monitor.get("entry_volume_ratio_min"),
        ),
        "min_extended_from_vwap_pct": _first_present_value(
            entry_thresholds.get("min_extended_from_vwap_pct"),
            focus_context.get("min_extended_from_vwap_pct"),
            monitor.get("entry_min_extended_from_vwap_pct"),
        ),
        "max_extended_from_vwap_pct": _first_present_value(
            entry_thresholds.get("max_extended_from_vwap_pct"),
            focus_context.get("max_extended_from_vwap_pct"),
            monitor.get("entry_max_extended_from_vwap_pct"),
        ),
        "recent_high": _first_present_value(entry_metrics.get("recent_high"), focus_context.get("recent_high")),
        "breakout_level": _first_present_value(entry_metrics.get("breakout_level"), focus_context.get("breakout_level")),
        "confidence_score": _first_present_value(entry_metrics.get("confidence_score"), focus_context.get("confidence_score")),
        "confidence_threshold": _first_present_value(
            entry_metrics.get("confidence_threshold"),
            focus_context.get("confidence_threshold"),
        ),
        "entry_quality_score": _first_present_value(
            entry_metrics.get("entry_quality_score"),
            focus_context.get("entry_quality_score"),
        ),
        "entry_quality_tier": _first_present_value(
            entry_metrics.get("entry_quality_tier"),
            focus_context.get("entry_quality_tier"),
        ),
        "entry_hard_gate_passed": _first_present_value(
            entry_metrics.get("entry_hard_gate_passed"),
            focus_context.get("entry_hard_gate_passed"),
        ),
        "entry_hard_gate_blockers": _first_present_value(
            entry_metrics.get("entry_hard_gate_blockers"),
            focus_context.get("entry_hard_gate_blockers"),
        ),
        "entry_quality_vs_gate_summary": _first_present_value(
            entry_metrics.get("entry_quality_vs_gate_summary"),
            focus_context.get("entry_quality_vs_gate_summary"),
        ),
        "breakout_proximity_score": _first_present_value(
            entry_metrics.get("breakout_proximity_score"),
            focus_context.get("breakout_proximity_score"),
            entry_metrics.get("breakout_score"),
            focus_context.get("breakout_score"),
        ),
        "human_candle_quality_score": _first_present_value(
            entry_metrics.get("human_candle_quality_score"),
            focus_context.get("human_candle_quality_score"),
        ),
        "human_vwap_reference_quality_score": _first_present_value(
            entry_metrics.get("human_vwap_reference_quality_score"),
            focus_context.get("human_vwap_reference_quality_score"),
        ),
        "human_reward_room_score": _first_present_value(
            entry_metrics.get("human_reward_room_score"),
            focus_context.get("human_reward_room_score"),
        ),
        "human_multi_window_structure_score": _first_present_value(
            entry_metrics.get("human_multi_window_structure_score"),
            focus_context.get("human_multi_window_structure_score"),
        ),
        "close_location": human_detail_observed.get("close_location"),
        "upper_wick_ratio": human_detail_observed.get("upper_wick_ratio"),
        "lower_wick_ratio": human_detail_observed.get("lower_wick_ratio"),
        "body_ratio": human_detail_observed.get("body_ratio"),
        "vwap_source": human_detail_observed.get("vwap_source"),
        "vwap_bar_count": human_detail_observed.get("vwap_bar_count"),
        "explicit_vwap_count": human_detail_observed.get("explicit_vwap_count"),
        "explicit_vwap_ratio": human_detail_observed.get("explicit_vwap_ratio"),
        "prior_resistance": human_detail_observed.get("prior_resistance"),
        "reward_room_pct": human_detail_observed.get("reward_room_pct"),
        "breakout_extension_pct": human_detail_observed.get("breakout_extension_pct"),
    }.items():
        if value not in (None, ""):
            snapshot[key] = value

    if snapshot:
        snapshot["basis"] = "monitor_entry_metrics"
    return snapshot


