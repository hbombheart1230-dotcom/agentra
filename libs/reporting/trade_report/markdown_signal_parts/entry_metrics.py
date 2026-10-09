from __future__ import annotations

from typing import Any, Dict, List, Mapping


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


def resolve_entry_execution_visibility(report: Dict[str, Any], *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    _as_dict = deps["as_dict"]
    _first_dict = deps["first_dict"]
    _metadata_value = deps["metadata_value"]
    _resolve_entry_monitor_artifact = deps["resolve_entry_monitor_artifact"]
    visibility = _as_dict(report.get("entry_execution_visibility"))
    entry_monitor = _resolve_entry_monitor_artifact(report)
    strategist_output = _as_dict(report.get("strategist_output"))
    strategy_detail = _as_dict(strategist_output.get("strategy_detail"))
    monitor = _as_dict(report.get("monitor_snapshot"))
    shared = _as_dict(report.get("shared_facts"))
    commander_route = _as_dict(shared.get("commander_route"))
    entry_policy_ref = _as_dict(entry_monitor.get("policy_ref"))
    entry_applied_policy = _as_dict(entry_policy_ref.get("applied_policy"))

    proposal = _as_dict(visibility.get("strategy_candidate_watch_proposal"))
    if not proposal:
        proposal = _as_dict(strategy_detail.get("candidate_watch_policy"))

    entry_control = _first_dict(
        _as_dict(entry_policy_ref.get("entry_control")),
        _as_dict(entry_applied_policy.get("commander_entry_control")),
        _as_dict(entry_applied_policy.get("entry_control")),
        _as_dict(visibility.get("commander_entry_control")),
    )
    if not entry_control:
        entry_control = _as_dict(commander_route.get("entry_control"))
    if not proposal:
        proposal = _as_dict(entry_control.get("proposal")) or _as_dict(entry_control.get("candidate_watch_policy_proposal"))
    if proposal and entry_control:
        proposal = dict(proposal)
        nested = _as_dict(entry_control.get("proposal")) or _as_dict(entry_control.get("candidate_watch_policy_proposal"))
        if proposal.get("max_priority_rank") in (None, "") and entry_control.get("proposed_max_priority_rank") not in (None, ""):
            proposal["max_priority_rank"] = entry_control.get("proposed_max_priority_rank")
        if proposal.get("max_runner_ups") in (None, "") and entry_control.get("proposed_max_runner_ups") not in (None, ""):
            proposal["max_runner_ups"] = entry_control.get("proposed_max_runner_ups")
        if proposal.get("cascade_enabled") in (None, "") and nested.get("cascade_enabled") not in (None, ""):
            proposal["cascade_enabled"] = nested.get("cascade_enabled")
        for key in ("source", "behavior_effect", "tactical_strategy", "reason"):
            if proposal.get(key) in (None, "") and nested.get(key) not in (None, ""):
                proposal[key] = nested.get(key)
        for key in ("cascade_allowed_reasons", "cascade_blocked_reasons"):
            if proposal.get(key) in (None, "", []) and nested.get(key) not in (None, "", []):
                proposal[key] = nested.get(key)

    cascade = _first_dict(
        _as_dict(entry_monitor.get("entry_candidate_cascade")),
        _as_dict(_as_dict(entry_monitor.get("scanner_monitor_handoff")).get("entry_candidate_cascade")),
        _as_dict(visibility.get("monitor_entry_candidate_cascade")),
        _as_dict(monitor.get("entry_candidate_cascade")),
    )
    focus_context = _first_dict(
        _as_dict(entry_monitor.get("monitor_focus_context")),
        _as_dict(visibility.get("monitor_focus_context")),
        _as_dict(monitor.get("monitor_focus_context")),
    )
    grouped_trace = _first_dict(
        _as_dict(entry_monitor.get("entry_grouped_logic_trace")),
        _as_dict(_as_dict(entry_monitor.get("threshold_snapshot")).get("entry_grouped_logic_trace")),
        _as_dict(visibility.get("entry_grouped_logic_trace")),
    )

    out: Dict[str, Any] = {}
    if proposal:
        out["strategy_candidate_watch_proposal"] = proposal
    if entry_control:
        out["commander_entry_control"] = entry_control
    if cascade:
        out["monitor_entry_candidate_cascade"] = cascade
    if focus_context:
        out["monitor_focus_context"] = focus_context
    if grouped_trace:
        out["entry_grouped_logic_trace"] = grouped_trace
    summary = _metadata_value(visibility.get("summary"))
    if summary:
        out["summary"] = summary
    return out


