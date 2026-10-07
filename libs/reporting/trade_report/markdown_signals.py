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


def entry_signal_metric_summary_lines(snapshot: Dict[str, Any], *, prefix: str = "진입 수치", deps: Mapping[str, Any]) -> List[str]:
    _as_dict = deps["as_dict"]
    _fmt_multiple = deps["fmt_multiple"]
    _fmt_pct = deps["fmt_pct"]
    _fmt_signed_pct = deps["fmt_signed_pct"]
    _metadata_value = deps["metadata_value"]
    _num_opt = deps["num_opt"]
    _summary_money = deps["summary_money"]
    row = _as_dict(snapshot)
    if not row:
        return []

    parts: List[str] = []
    if row.get("current_price") not in (None, ""):
        parts.append(f"현재가 {_summary_money(row.get('current_price'))}")
    if row.get("vwap") not in (None, ""):
        parts.append(f"VWAP {_summary_money(row.get('vwap'))}")
    if row.get("vwap_distance") not in (None, ""):
        distance_text = f"VWAP 대비 {_fmt_signed_pct(row.get('vwap_distance'))}"
        min_vwap = row.get("min_extended_from_vwap_pct")
        max_vwap = row.get("max_extended_from_vwap_pct")
        if min_vwap not in (None, "") or max_vwap not in (None, ""):
            distance_text += f" (허용 {_fmt_signed_pct(min_vwap) if min_vwap not in (None, '') else '-'}~{_fmt_signed_pct(max_vwap) if max_vwap not in (None, '') else '-'})"
        parts.append(distance_text)
    if row.get("volume") not in (None, ""):
        parts.append(f"거래량 {_summary_money(row.get('volume'))}")
    if row.get("volume_ratio") not in (None, ""):
        volume_text = f"거래량 비율 {_fmt_multiple(row.get('volume_ratio'))}"
        if row.get("volume_ratio_min") not in (None, ""):
            volume_text += f" (기준 {_fmt_multiple(row.get('volume_ratio_min'))})"
        if row.get("volume_ratio_raw") not in (None, "") and row.get("volume_ratio_raw") != row.get("volume_ratio"):
            volume_text += f" / 원비율 {_fmt_multiple(row.get('volume_ratio_raw'))}"
        if row.get("volume_adjusted") is True and row.get("volume_adjustment_reason"):
            volume_text += f" / 보정 {row.get('volume_adjustment_reason')}"
        parts.append(volume_text)
    if row.get("recent_high") not in (None, ""):
        parts.append(f"최근 고점 {_summary_money(row.get('recent_high'))}")
    if row.get("breakout_level") not in (None, ""):
        parts.append(f"돌파 기준 {_summary_money(row.get('breakout_level'))}")
    if row.get("confidence_score") not in (None, ""):
        confidence_text = f"신뢰도 {_summary_money(row.get('confidence_score'))}"
        if row.get("confidence_threshold") not in (None, ""):
            confidence_text += f" (기준 {_summary_money(row.get('confidence_threshold'))})"
        parts.append(confidence_text)
    if row.get("breakout_proximity_score") not in (None, ""):
        parts.append(f"돌파 근접 점수 {_summary_money(row.get('breakout_proximity_score'))}")
    lines = [f"{prefix}: " + " / ".join(parts)] if parts else []

    gate_parts: List[str] = []
    if row.get("entry_quality_score") not in (None, ""):
        quality_text = f"진입 품질 {_summary_money(row.get('entry_quality_score'))}"
        if row.get("entry_quality_tier") not in (None, ""):
            quality_text += f" ({row.get('entry_quality_tier')})"
        gate_parts.append(quality_text)
    if row.get("entry_hard_gate_passed") is True:
        gate_parts.append("hard gate 통과")
    elif row.get("entry_hard_gate_passed") is False:
        blockers = row.get("entry_hard_gate_blockers")
        blocker_text = ""
        if isinstance(blockers, list):
            blocker_text = ", ".join(str(x or "").replace("_", " ") for x in blockers[:4] if str(x or "").strip())
        gate_parts.append(f"hard gate 미통과{f' ({blocker_text})' if blocker_text else ''}")
    if row.get("entry_quality_vs_gate_summary") not in (None, ""):
        gate_parts.append(str(row.get("entry_quality_vs_gate_summary")).replace("_", " "))
    if gate_parts:
        lines.append("진입 품질 vs 허가: " + " / ".join(gate_parts))

    setup_parts: List[str] = []
    if row.get("human_candle_quality_score") not in (None, ""):
        setup_parts.append(f"캔들 품질 {_summary_money(row.get('human_candle_quality_score'))}")
    if row.get("human_vwap_reference_quality_score") not in (None, ""):
        setup_parts.append(f"VWAP 신뢰도 {_summary_money(row.get('human_vwap_reference_quality_score'))}")
    if row.get("human_reward_room_score") not in (None, ""):
        setup_parts.append(f"위쪽 여지 점수 {_summary_money(row.get('human_reward_room_score'))}")
    if row.get("human_multi_window_structure_score") not in (None, ""):
        setup_parts.append(f"다중 구간 구조 {_summary_money(row.get('human_multi_window_structure_score'))}")
    if setup_parts:
        lines.append("진입 자리 품질: " + " / ".join(setup_parts))

    candle_parts: List[str] = []
    if row.get("close_location") not in (None, ""):
        candle_parts.append(f"종가 위치 {_summary_money(row.get('close_location'))}")
    if row.get("upper_wick_ratio") not in (None, ""):
        candle_parts.append(f"윗꼬리 {_summary_money(row.get('upper_wick_ratio'))}")
    if row.get("lower_wick_ratio") not in (None, ""):
        candle_parts.append(f"아랫꼬리 {_summary_money(row.get('lower_wick_ratio'))}")
    if row.get("body_ratio") not in (None, ""):
        candle_parts.append(f"몸통 {_summary_money(row.get('body_ratio'))}")
    if candle_parts:
        lines.append("캔들 근거: " + " / ".join(candle_parts))

    vwap_parts: List[str] = []
    if row.get("vwap_source") not in (None, ""):
        vwap_parts.append(f"소스 {_metadata_value(row.get('vwap_source'))}")
    if row.get("vwap_bar_count") not in (None, ""):
        vwap_parts.append(f"사용 분봉 {int(_num_opt(row.get('vwap_bar_count')) or 0)}개")
    if row.get("explicit_vwap_count") not in (None, ""):
        vwap_parts.append(f"원본 VWAP {int(_num_opt(row.get('explicit_vwap_count')) or 0)}개")
    if row.get("explicit_vwap_ratio") not in (None, ""):
        vwap_parts.append(f"원본 비율 {_summary_money(row.get('explicit_vwap_ratio'))}")
    if vwap_parts:
        lines.append("VWAP 근거: " + " / ".join(vwap_parts))

    reward_parts: List[str] = []
    if row.get("prior_resistance") not in (None, ""):
        reward_parts.append(f"근접 저항 {_summary_money(row.get('prior_resistance'))}")
    if row.get("reward_room_pct") not in (None, ""):
        reward_parts.append(f"저항까지 {_fmt_pct(row.get('reward_room_pct'))}")
    if row.get("breakout_extension_pct") not in (None, ""):
        reward_parts.append(f"돌파 후 이격 {_fmt_pct(row.get('breakout_extension_pct'))}")
    if reward_parts:
        lines.append("위쪽 여지: " + " / ".join(reward_parts))

    return lines


def enrich_exit_signal_snapshot_from_monitor(
    snapshot: Dict[str, Any],
    monitor: Dict[str, Any],
    *,
    deps: Mapping[str, Any],
) -> Dict[str, Any]:
    _as_dict = deps["as_dict"]
    out = dict(snapshot or {})
    monitor = _as_dict(monitor)
    if not monitor:
        return out

    def _first_present(*keys: str) -> Any:
        for key in keys:
            value = monitor.get(key)
            if value not in (None, ""):
                return value
        return None

    def _set_if_present(key: str, *candidates: str) -> None:
        if out.get(key) not in (None, ""):
            return
        value = _first_present(*candidates)
        if value not in (None, ""):
            out[key] = value

    _set_if_present("gross_pnl_ratio", "gross_pnl_ratio", "exit_gross_pnl_ratio")
    _set_if_present("technical_pnl_ratio", "technical_pnl_ratio", "exit_technical_pnl_ratio")
    _set_if_present("effective_pnl_ratio", "effective_pnl_ratio", "exit_effective_pnl_ratio", "pnl_ratio", "exit_pnl_ratio")
    _set_if_present("stop_pnl_ratio", "stop_pnl_ratio", "exit_stop_pnl_ratio")
    _set_if_present("stop_pnl_ratio_source", "stop_pnl_ratio_source", "exit_stop_pnl_ratio_source")
    _set_if_present("hard_stop_pnl_ratio", "hard_stop_pnl_ratio", "exit_hard_stop_pnl_ratio")
    _set_if_present("hard_stop_pnl_ratio_source", "hard_stop_pnl_ratio_source", "exit_hard_stop_pnl_ratio_source")
    _set_if_present("cost_drag_pressure_pct", "cost_drag_pressure_pct", "exit_cost_drag_pressure_pct")
    _set_if_present("cost_drag_pressure_reason", "cost_drag_pressure_reason", "exit_cost_drag_pressure_reason")
    _set_if_present("expected_exit_price", "expected_exit_price", "exit_expected_exit_price")
    _set_if_present("expected_exit_price_source", "expected_exit_price_source", "exit_expected_exit_price_source")
    _set_if_present("expected_exit_pnl_ratio", "expected_exit_pnl_ratio", "exit_expected_exit_pnl_ratio")
    _set_if_present("expected_exit_net_pnl_ratio", "expected_exit_net_pnl_ratio", "exit_expected_exit_net_pnl_ratio")
    _set_if_present(
        "expected_exit_profit_floor_gap_pct",
        "expected_exit_profit_floor_gap_pct",
        "exit_expected_exit_profit_floor_gap_pct",
    )
    _set_if_present(
        "expected_exit_profit_floor_blocked_reason",
        "expected_exit_profit_floor_blocked_reason",
        "exit_expected_exit_profit_floor_blocked_reason",
    )
    _set_if_present(
        "stop_loss_cost_drag_blocked_reason",
        "stop_loss_cost_drag_blocked_reason",
        "exit_stop_loss_cost_drag_blocked_reason",
    )
    _set_if_present("technical_price", "technical_price", "exit_technical_price")
    _set_if_present("technical_price_source", "technical_price_source", "exit_technical_price_source")
    _set_if_present("vwap", "vwap", "exit_vwap")
    _set_if_present("vwap_distance", "vwap_distance", "exit_vwap_distance")
    _set_if_present("vwap_distance_source", "vwap_distance_source", "exit_vwap_distance_source")
    _set_if_present("exit_trigger_metric_name", "exit_trigger_metric_name")
    _set_if_present("exit_trigger_metric_value", "exit_trigger_metric_value")
    _set_if_present("exit_trigger_metric_source", "exit_trigger_metric_source")
    _set_if_present("trend_strength", "trend_strength", "engine_trend_strength", "exit_trend_strength")
    _set_if_present("trend_strength_floor", "trend_strength_floor", "exit_trend_strength_floor")

    thresholds = _as_dict(_as_dict(monitor.get("thresholds_guards_used")).get("thresholds")) or _as_dict(monitor.get("thresholds"))
    if out.get("trend_strength_floor") in (None, "") and thresholds.get("trend_strength_floor") not in (None, ""):
        out["trend_strength_floor"] = thresholds.get("trend_strength_floor")
    if out.get("vwap_breakdown_pct") in (None, ""):
        threshold = _first_present(
            "vwap_breakdown_pct",
            "exit_vwap_breakdown_pct",
            "monitor_vwap_breakdown_pct",
        )
        if threshold in (None, ""):
            threshold = thresholds.get("vwap_breakdown_pct")
        if threshold not in (None, ""):
            out["vwap_breakdown_pct"] = threshold

    for key, candidates in {
        "cost_drag_pressure": ("cost_drag_pressure", "exit_cost_drag_pressure"),
        "stop_loss_cost_drag_blocked": (
            "stop_loss_cost_drag_blocked",
            "exit_stop_loss_cost_drag_blocked",
        ),
        "expected_exit_profit_floor_met": (
            "expected_exit_profit_floor_met",
            "exit_expected_exit_profit_floor_met",
        ),
        "expected_exit_profit_floor_blocked": (
            "expected_exit_profit_floor_blocked",
            "exit_expected_exit_profit_floor_blocked",
        ),
    }.items():
        if out.get(key) not in (None, ""):
            continue
        value = _first_present(*candidates)
        if value not in (None, ""):
            out[key] = bool(value)

    if out:
        out.setdefault("basis", "monitor_signal_snapshot")
        out.setdefault("truth_note", "체결가와 실현손익은 Truth Surface 기준입니다.")
    return out


def build_summary_exit_trigger_lines(
    exit_trigger: Any,
    exit_signal_snapshot: Dict[str, Any],
    *,
    fallback_reason: Any = "",
    buy_price: Any = "",
    exit_price: Any = "",
    pnl_pct: Any = "",
    truth_source: Any = "",
    deps: Mapping[str, Any],
) -> List[str]:
    _fmt_pct = deps["fmt_pct"]
    _fmt_signed_pct = deps["fmt_signed_pct"]
    _metadata_value = deps["metadata_value"]
    _normalize_exit_trigger_label = deps["normalize_exit_trigger_label"]
    _num_opt = deps["num_opt"]
    _summary_money = deps["summary_money"]
    _truth_source_label = deps["truth_source_label"]
    raw_trigger_value = exit_signal_snapshot.get("trigger") or exit_trigger
    raw_trigger_text = " ".join(
        str(part or "")
        for part in (raw_trigger_value, fallback_reason)
        if str(part or "").strip()
    )
    trigger_label = _normalize_exit_trigger_label(
        raw_trigger_value,
        fallback_reason,
    )
    raw_trigger_lower = raw_trigger_text.strip().lower()
    execution_only_exit = (
        "sell_execution_confirmed" in raw_trigger_lower
        or "full_sell_quantity_reconciled" in raw_trigger_lower
        or "sell 실행 및 잔여수량" in raw_trigger_text
        or "매도 실행 확인" in trigger_label
        or "전량 매도 수량 확인" in trigger_label
    )
    missing_trigger = (
        execution_only_exit
        or "exit_trigger_not_captured" in raw_trigger_lower
        or "monitor_exit_trigger_not_captured" in raw_trigger_lower
        or "청산 트리거 미확인" in raw_trigger_text
        or "청산 이유는 기록되지" in raw_trigger_text
        or "exit reasoning was not captured" in raw_trigger_lower
    )
    if missing_trigger:
        trigger_label = "모니터 청산 트리거 미확인"
    lines = [f"트리거: {trigger_label}"]
    if execution_only_exit:
        lines.append("체결 상태: SELL 실행 및 잔여수량 0 확인으로 전량 청산")
    trigger_metric_name = str(exit_signal_snapshot.get("exit_trigger_metric_name") or "").strip().lower()
    trigger_metric_value = exit_signal_snapshot.get("exit_trigger_metric_value")
    vwap_distance = exit_signal_snapshot.get("vwap_distance")
    if vwap_distance in (None, "") and trigger_metric_name == "vwap_distance":
        vwap_distance = trigger_metric_value
    vwap_distance_num = _num_opt(vwap_distance)
    is_vwap_trigger = "VWAP" in trigger_label or "vwap" in trigger_label.lower() or trigger_metric_name == "vwap_distance"
    if is_vwap_trigger and vwap_distance_num is not None:
        lines[0] = f"트리거: {trigger_label} (VWAP 대비 {_fmt_signed_pct(vwap_distance_num)})"

    trend_strength = exit_signal_snapshot.get("trend_strength")
    if trend_strength in (None, "") and trigger_metric_name == "trend_strength":
        trend_strength = trigger_metric_value
    trend_strength_num = _num_opt(trend_strength)
    trend_floor_num = _num_opt(exit_signal_snapshot.get("trend_strength_floor"))
    is_trend_trigger = (
        trigger_metric_name == "trend_strength"
        or "추세" in trigger_label
        or "trend" in str(trigger_label or "").lower()
    )
    if is_trend_trigger and trend_strength_num is not None:
        floor_text = f" <= 기준 {trend_floor_num:.4f}" if trend_floor_num is not None else ""
        lines[0] = f"트리거: 추세 훼손 (추세강도 {trend_strength_num:.4f}{floor_text})"

    observation_parts: List[str] = []
    if exit_signal_snapshot.get("confirm_state"):
        observation_parts.append(f"확인 조건 {exit_signal_snapshot.get('confirm_state')}")
    if exit_signal_snapshot.get("monitor_current_price") not in (None, ""):
        observation_parts.append(f"현재가 {_summary_money(exit_signal_snapshot.get('monitor_current_price'))}")
    if is_vwap_trigger and vwap_distance_num is not None:
        vwap_value = _num_opt(exit_signal_snapshot.get("vwap"))
        current_value = _num_opt(exit_signal_snapshot.get("monitor_current_price"))
        if vwap_value is None and current_value is not None and (1.0 + vwap_distance_num) > 0.0:
            vwap_value = current_value / (1.0 + vwap_distance_num)
        vwap_parts = []
        if vwap_value is not None:
            vwap_parts.append(f"VWAP {_summary_money(vwap_value)}")
        vwap_parts.append(f"VWAP 대비 {_fmt_signed_pct(vwap_distance_num)}")
        threshold_num = _num_opt(exit_signal_snapshot.get("vwap_breakdown_pct"))
        if threshold_num is not None:
            vwap_parts.append(f"이탈 기준 {_fmt_signed_pct(-abs(threshold_num))}")
        observation_parts.append(" / ".join(vwap_parts))
    if is_trend_trigger and trend_strength_num is not None:
        trend_parts = [f"추세강도 {trend_strength_num:.4f}"]
        if trend_floor_num is not None:
            trend_parts.append(f"훼손 기준 {trend_floor_num:.4f}")
        source = _metadata_value(exit_signal_snapshot.get("exit_trigger_metric_source"))
        if source and source != "-":
            trend_parts.append(f"소스 {source}")
        observation_parts.append(" / ".join(trend_parts))
    if exit_signal_snapshot.get("position_avg_price") not in (None, ""):
        observation_parts.append(
            f"포지션 평균단가(모니터 신호 계산용) {_summary_money(exit_signal_snapshot.get('position_avg_price'))}"
        )
    if exit_signal_snapshot.get("peak_price") not in (None, ""):
        observation_parts.append(f"고점 {_summary_money(exit_signal_snapshot.get('peak_price'))}")
    monitor_drawdown_pct = (
        exit_signal_snapshot.get("monitor_drawdown_pct_text")
        or exit_signal_snapshot.get("monitor_pnl_pct_text")
    )
    if monitor_drawdown_pct:
        observation_parts.append(f"고점 대비 하락폭 {monitor_drawdown_pct}")
    if observation_parts:
        observation_label = (
            "마지막 모니터 관측값(청산 트리거 아님)"
            if missing_trigger
            else "모니터 관측값(신호 판단용)"
        )
        lines.append(f"{observation_label}: " + " / ".join(observation_parts))

    pnl_basis_parts: List[str] = []
    gross_pnl = exit_signal_snapshot.get("gross_pnl_ratio")
    effective_pnl = exit_signal_snapshot.get("effective_pnl_ratio")
    stop_pnl = exit_signal_snapshot.get("stop_pnl_ratio")
    hard_stop_pnl = exit_signal_snapshot.get("hard_stop_pnl_ratio")
    if gross_pnl not in (None, ""):
        pnl_basis_parts.append(f"가격 기준 손익 {_fmt_pct(gross_pnl)}")
    if effective_pnl not in (None, ""):
        pnl_basis_parts.append(f"비용/계좌 반영 손익 {_fmt_pct(effective_pnl)}")
    if stop_pnl not in (None, ""):
        source = _metadata_value(exit_signal_snapshot.get("stop_pnl_ratio_source"))
        suffix = f", {source}" if source and source != "-" else ""
        pnl_basis_parts.append(f"일반 손절 판단 기준 {_fmt_pct(stop_pnl)}{suffix}")
    if hard_stop_pnl not in (None, ""):
        source = _metadata_value(exit_signal_snapshot.get("hard_stop_pnl_ratio_source"))
        suffix = f", {source}" if source and source != "-" else ""
        pnl_basis_parts.append(f"하드스탑 판단 기준 {_fmt_pct(hard_stop_pnl)}{suffix}")
    if pnl_basis_parts:
        lines.append("손익 기준 분리: " + " / ".join(pnl_basis_parts))

    if exit_signal_snapshot.get("cost_drag_pressure"):
        pressure_pct = _fmt_pct(exit_signal_snapshot.get("cost_drag_pressure_pct"))
        reason = _metadata_value(exit_signal_snapshot.get("cost_drag_pressure_reason"))
        detail = f" ({pressure_pct})" if pressure_pct != "-" else ""
        if reason and reason != "-":
            detail += f", {reason}"
        lines.append("비용 압박: 비용/계좌 반영 손익이 가격 기준보다 낮게 잡혔습니다" + detail)
    if exit_signal_snapshot.get("stop_loss_cost_drag_blocked"):
        reason = _metadata_value(exit_signal_snapshot.get("stop_loss_cost_drag_blocked_reason"))
        suffix = f" ({reason})" if reason and reason != "-" else ""
        lines.append("일반 손절 차단: 가격 기준 손절선은 미통과했고 비용 반영 손익만 손절선을 건드렸습니다" + suffix)
    if exit_signal_snapshot.get("expected_exit_price") not in (None, ""):
        source = _metadata_value(exit_signal_snapshot.get("expected_exit_price_source"))
        source_suffix = f", {source}" if source and source != "-" else ""
        expected_parts = [
            f"예상 체결가 {_summary_money(exit_signal_snapshot.get('expected_exit_price'))}{source_suffix}",
        ]
        if exit_signal_snapshot.get("expected_exit_pnl_ratio") not in (None, ""):
            expected_parts.append(f"예상 가격 손익 {_fmt_pct(exit_signal_snapshot.get('expected_exit_pnl_ratio'))}")
        if exit_signal_snapshot.get("expected_exit_net_pnl_ratio") not in (None, ""):
            expected_parts.append(f"예상 비용 차감 손익 {_fmt_pct(exit_signal_snapshot.get('expected_exit_net_pnl_ratio'))}")
        if exit_signal_snapshot.get("expected_exit_profit_floor_met") not in (None, ""):
            expected_parts.append(
                "비용 바닥 통과" if exit_signal_snapshot.get("expected_exit_profit_floor_met") else "비용 바닥 미통과"
            )
        lines.append("예상 체결가 비용 점검: " + " / ".join(expected_parts))
    if exit_signal_snapshot.get("expected_exit_profit_floor_blocked"):
        reason = _metadata_value(exit_signal_snapshot.get("expected_exit_profit_floor_blocked_reason"))
        suffix = f" ({reason})" if reason and reason != "-" else ""
        lines.append("익절 보류: 예상 체결가 기준 비용 바닥을 통과하지 못했습니다" + suffix)

    truth_parts: List[str] = []
    if buy_price not in (None, ""):
        truth_parts.append(f"매수가 {_summary_money(buy_price)}")
    if exit_price not in (None, ""):
        truth_parts.append(f"매도가 {_summary_money(exit_price)}")
    elif buy_price not in (None, ""):
        truth_parts.append("매도 체결가 미확정")
    if pnl_pct not in (None, ""):
        truth_parts.append(f"실현손익률 {_fmt_pct(pnl_pct)}")
    truth_label = _truth_source_label(truth_source)
    if truth_label and truth_label != "-":
        truth_parts.append(truth_label)
    if truth_parts:
        lines.append("체결/실현손익 기준: Truth Surface의 " + " / ".join(truth_parts))
    return lines


