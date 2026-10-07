from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Mapping


def strategy_horizon_label(value: Any, *, metadata_value: Callable[[Any], str]) -> str:
    raw = str(value or "").strip()
    labels = {
        "scalp": "초단타(scalp)",
        "intraday": "단타/당일(intraday)",
        "overnight_probe": "오버나이트 탐색(overnight_probe)",
        "1_2day_swing": "1~2일 스윙(1_2day_swing)",
    }
    return labels.get(raw, metadata_value(raw) or "-")


def strategy_horizon_reason_label(value: Any, *, metadata_value: Callable[[Any], str]) -> str:
    raw = str(value or "").strip()
    labels = {
        "commander_accepts_strategist_horizon_proposal_observability_only": "전략가 제안을 관측-only로 수용",
        "commander_caps_long_horizon_during_live_validation_observability_only": "장기 보유 제안은 live validation 중이라 단타/당일로 제한",
        "commander_default_intraday_horizon_without_strategist_proposal": "전략가 보유 기간 제안 부재로 기본 단타/당일 적용",
    }
    return labels.get(raw, metadata_value(raw) or "-")


def strategy_horizon_alignment_label(value: Any, *, metadata_value: Callable[[Any], str]) -> str:
    raw = str(value or "").strip()
    labels = {
        "aligned": "전략 보유 구간과 충돌 없음",
        "early_but_justified": "전략 최소 보유 전 조기 청산이지만 하드 리스크로 정당화",
        "early_unproven": "전략 최소 보유 전 조기 청산, 근거 검증 필요",
        "held_beyond_expected_window": "기대 최대 보유시간 초과",
        "unknown": "판단 불가",
    }
    return labels.get(raw, metadata_value(raw) or "-")


def duration_label_compact(value: Any, *, num_opt: Callable[[Any], float | None]) -> str:
    seconds = num_opt(value)
    if seconds is None or seconds <= 0:
        return ""
    total = int(round(seconds))
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, sec = divmod(rem, 60)
    parts: List[str] = []
    if days:
        parts.append(f"{days}일")
    if hours:
        parts.append(f"{hours}시간")
    if minutes:
        parts.append(f"{minutes}분")
    if sec and not days:
        parts.append(f"{sec}초")
    if not parts:
        parts.append("0초")
    return " ".join(parts)


def hold_window_label(
    window: Dict[str, Any],
    *,
    as_dict: Callable[[Any], Dict[str, Any]],
    duration_label_compact_fn: Callable[[Any], str],
) -> str:
    obj = as_dict(window)
    if not obj:
        return "-"
    min_label = duration_label_compact_fn(obj.get("min_sec")) or "-"
    target_label = duration_label_compact_fn(obj.get("target_sec")) or "-"
    max_label = duration_label_compact_fn(obj.get("max_sec")) or "-"
    return f"최소 {min_label} / 목표 {target_label} / 최대 {max_label}"


def strategy_horizon_report_surface(
    report: Dict[str, Any],
    *,
    as_dict: Callable[[Any], Dict[str, Any]],
    first_report_path: Callable[[Dict[str, Any], Iterable[str]], Any],
    compact_post_exit_shadow: Callable[[Dict[str, Any]], Dict[str, Any]],
    post_exit_shadow_surface: Callable[[Dict[str, Any]], Dict[str, Any]],
    carryover_context: Callable[[Dict[str, Any]], Dict[str, Any]],
    num_opt: Callable[[Any], float | None],
    duration_label_compact_fn: Callable[[Any], str],
) -> Dict[str, Any]:
    def _first_non_empty(*values: Any) -> Any:
        for value in values:
            if value not in (None, "", [], {}):
                return value
        return ""

    def _first_dict(*values: Any) -> Dict[str, Any]:
        for value in values:
            obj = as_dict(value)
            if obj:
                return obj
        return {}

    exit_vs_strategy = _first_dict(
        report.get("exit_vs_strategy_intent"),
        first_report_path(
            report,
            [
                "monitor_snapshot.exit_vs_strategy_intent",
                "monitor_snapshot.decision_trace.exit_vs_strategy_intent",
                "fact_payload.trade.exit_vs_strategy_intent",
                "fact_payload.trade.monitor_snapshot.exit_vs_strategy_intent",
                "fact_payload.trade.canonical_agent_artifacts.monitor.exit_vs_strategy_intent",
                "fact_payload.trade.canonical_agent_artifacts.monitor.decision_trace.exit_vs_strategy_intent",
                "lifecycle.exit.monitor_context.exit_vs_strategy_intent",
                "lifecycle_bundle.exit_vs_strategy_intent",
            ],
        ),
    )
    commander_policy = _first_dict(
        report.get("commander_horizon_policy"),
        exit_vs_strategy.get("commander_horizon_policy"),
        first_report_path(
            report,
            [
                "strategy_policy.commander_horizon_policy",
                "strategy_policy.monitor_policy.commander_horizon_policy",
                "strategist_output.commander_horizon_policy",
                "fact_payload.trade.commander_horizon_policy",
                "fact_payload.trade.canonical_agent_artifacts.strategist.commander_horizon_policy",
                "fact_payload.trade.canonical_agent_artifacts.monitor.applied_policy.horizon",
                "fact_payload.trade.shared_facts.commander_route.applied_policy.horizon",
                "shared_facts.commander_route.applied_policy.horizon",
                "monitor_snapshot.applied_policy.horizon",
                "monitor_snapshot.decision_trace.applied_policy.horizon",
            ],
        ),
    )
    feedback = _first_dict(
        report.get("strategy_horizon_feedback"),
        report.get("strategist_horizon_proposal"),
        first_report_path(
            report,
            [
                "strategist_output.strategy_horizon_feedback",
                "strategy_policy.monitor_policy.strategy_horizon_feedback",
                "fact_payload.trade.strategy_horizon_feedback",
                "fact_payload.trade.canonical_agent_artifacts.strategist.strategy_horizon_feedback",
                "entry_summary.strategist_context.strategy_horizon_feedback",
            ],
        ),
    )
    proposal = _first_dict(
        commander_policy.get("strategist_horizon_proposal"),
        commander_policy.get("proposal"),
        exit_vs_strategy.get("strategist_horizon_proposal"),
        feedback,
    )
    shadow = compact_post_exit_shadow(post_exit_shadow_surface(report))
    carryover = carryover_context(report)

    strategist_horizon = _first_non_empty(
        commander_policy.get("source_strategy_horizon"),
        exit_vs_strategy.get("source_strategy_horizon"),
        proposal.get("strategy_horizon"),
        feedback.get("strategy_horizon"),
        shadow.get("source_strategy_horizon"),
        shadow.get("strategy_horizon"),
    )
    commander_horizon = _first_non_empty(
        commander_policy.get("strategy_horizon"),
        exit_vs_strategy.get("strategy_horizon"),
        report.get("strategy_horizon"),
        first_report_path(report, ["fact_payload.trade.strategy_horizon"]),
        shadow.get("strategy_horizon"),
        strategist_horizon,
    )
    expected_window = _first_dict(
        commander_policy.get("expected_hold_window"),
        exit_vs_strategy.get("expected_hold_window"),
        shadow.get("expected_hold_window"),
        feedback.get("expected_hold_window"),
        proposal.get("expected_hold_window"),
    )
    source_window = _first_dict(
        commander_policy.get("source_expected_hold_window"),
        exit_vs_strategy.get("source_expected_hold_window"),
        proposal.get("expected_hold_window"),
        feedback.get("expected_hold_window"),
        expected_window,
    )
    actual_hold_sec = num_opt(
        _first_non_empty(
            exit_vs_strategy.get("actual_hold_sec"),
            first_report_path(
                report,
                [
                    "fact_payload.trade.exit_vs_strategy_intent.actual_hold_sec",
                    "fact_payload.trade.canonical_agent_artifacts.monitor.exit_vs_strategy_intent.actual_hold_sec",
                    "fact_payload.trade.monitor_snapshot.exit_vs_strategy_intent.actual_hold_sec",
                    "monitor_snapshot.exit_vs_strategy_intent.actual_hold_sec",
                    "shared_facts.exit_vs_strategy_intent.actual_hold_sec",
                ],
            ),
            carryover.get("actual_hold_sec"),
        )
    )

    alignment = str(exit_vs_strategy.get("exit_alignment") or "").strip()
    if not alignment and actual_hold_sec is not None and expected_window:
        min_sec = num_opt(expected_window.get("min_sec")) or 0.0
        max_sec = num_opt(expected_window.get("max_sec")) or 0.0
        if min_sec > 0 and actual_hold_sec < min_sec:
            alignment = "early_unproven"
        elif max_sec > 0 and actual_hold_sec > max_sec:
            alignment = "held_beyond_expected_window"
        else:
            alignment = "aligned"

    if not any([strategist_horizon, commander_horizon, expected_window, exit_vs_strategy]):
        return {}
    allow_behavior_change = bool(commander_policy.get("allow_behavior_change", False))
    observability_only = bool(
        _first_non_empty(
            commander_policy.get("observability_only"),
            exit_vs_strategy.get("observability_only"),
            feedback.get("observability_only"),
            True,
        )
    )
    do_not_force_hold = bool(
        _first_non_empty(
            commander_policy.get("do_not_force_hold"),
            as_dict(commander_policy.get("monitor_handoff")).get("do_not_force_hold"),
            True,
        )
    )
    behavior_translation = _first_dict(
        commander_policy.get("behavior_translation"),
        exit_vs_strategy.get("behavior_translation"),
        feedback.get("behavior_translation"),
    )
    return {
        "strategist_horizon": strategist_horizon,
        "commander_horizon": commander_horizon,
        "expected_hold_window": expected_window,
        "source_expected_hold_window": source_window,
        "actual_hold_sec": actual_hold_sec,
        "actual_hold_label": duration_label_compact_fn(actual_hold_sec),
        "exit_alignment": alignment,
        "alignment_reason": str(exit_vs_strategy.get("alignment_reason") or "").strip(),
        "early_exit_flag": bool(exit_vs_strategy.get("early_exit_flag")) if exit_vs_strategy else bool(alignment == "early_unproven"),
        "hard_exit": bool(exit_vs_strategy.get("hard_exit")) if exit_vs_strategy else False,
        "hard_exit_reason": str(exit_vs_strategy.get("hard_exit_reason") or "").strip(),
        "exit_reason": str(exit_vs_strategy.get("exit_reason") or "").strip(),
        "horizon_owner": str(exit_vs_strategy.get("horizon_owner") or ("commander" if commander_policy else "strategist")),
        "observability_only": observability_only,
        "allow_behavior_change": allow_behavior_change,
        "allow_behavior_translation": bool(commander_policy.get("allow_behavior_translation") or behavior_translation),
        "behavior_translation": behavior_translation,
        "do_not_force_hold": do_not_force_hold,
        "decision_reason": str(commander_policy.get("decision_reason") or exit_vs_strategy.get("commander_decision_reason") or "").strip(),
    }


def build_strategy_horizon_lines(
    report: Dict[str, Any],
    *,
    compact: bool = False,
    strategy_horizon_report_surface_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    strategy_horizon_label_fn: Callable[[Any], str],
    strategy_horizon_alignment_label_fn: Callable[[Any], str],
    strategy_horizon_reason_label_fn: Callable[[Any], str],
    as_dict: Callable[[Any], Dict[str, Any]],
    axis_label: Callable[[Any], str],
    hold_window_label_fn: Callable[[Dict[str, Any]], str],
    duration_label_compact_fn: Callable[[Any], str],
) -> List[str]:
    surface = strategy_horizon_report_surface_fn(report)
    if not surface:
        return []
    lines: List[str] = []
    strategist = surface.get("strategist_horizon")
    commander = surface.get("commander_horizon")
    if strategist:
        lines.append(f"* 전략가 제안: {strategy_horizon_label_fn(strategist)}")
    if commander:
        lines.append(f"* 지휘관 적용: {strategy_horizon_label_fn(commander)}")
    authority = "행동 반영 허용" if surface.get("allow_behavior_change") else "관측-only"
    if surface.get("allow_behavior_translation"):
        authority += ", 보유기간 번역 반영"
    if surface.get("do_not_force_hold"):
        authority += ", 보유 강제 없음"
    lines.append(f"* 권한: {authority}")
    translation = as_dict(surface.get("behavior_translation"))
    if translation:
        pieces = [
            str(translation.get("scanner_scope_bias") or ""),
            str(translation.get("hold_control_bias") or ""),
            str(translation.get("exit_policy_bias") or ""),
        ]
        pieces = [item for item in pieces if item]
        if pieces:
            lines.append(f"* 실제 반영: {' / '.join(pieces[:3])}")
        if translation.get("monitor_review_cadence_sec") not in (None, ""):
            lines.append(f"* 모니터 리뷰 주기: {duration_label_compact_fn(translation.get('monitor_review_cadence_sec'))}")
    if surface.get("expected_hold_window"):
        lines.append(f"* 적용 예상 보유 구간: {hold_window_label_fn(as_dict(surface.get('expected_hold_window')))}")
    if not compact and surface.get("source_expected_hold_window") and surface.get("source_expected_hold_window") != surface.get("expected_hold_window"):
        lines.append(f"* 전략가 원 제안 구간: {hold_window_label_fn(as_dict(surface.get('source_expected_hold_window')))}")
    if surface.get("actual_hold_label"):
        lines.append(f"* 실제 보유: {surface.get('actual_hold_label')}")
    if surface.get("exit_alignment"):
        detail = strategy_horizon_alignment_label_fn(surface.get("exit_alignment"))
        if surface.get("hard_exit_reason"):
            detail += f" ({axis_label(surface.get('hard_exit_reason'))})"
        lines.append(f"* 청산 정합성: {detail}")
    reason = strategy_horizon_reason_label_fn(surface.get("decision_reason"))
    if reason and reason != "-":
        lines.append(f"* 지휘관 조정 사유: {reason}")
    if not compact:
        lines.append("* 해석: 이 값은 전략 의도와 실제 보유/청산을 비교하기 위한 기록이며, 현재는 모니터 청산을 강제로 지연시키지 않습니다.")
    return lines

# P1.5.2 R2-B: carryover / prompt-proven memory / memory-application owners.


def carryover_context(report: Dict[str, Any], *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    _action_label = deps["action_label"]
    _as_dict = deps["as_dict"]
    _carry_risk_label = deps["carry_risk_label"]
    _carry_state_label = deps["carry_state_label"]
    _duration_label_seconds = deps["duration_label_seconds"]
    _first_report_path = deps["first_report_path"]
    _format_kst_date = deps["format_kst_date"]
    _format_kst_datetime = deps["format_kst_datetime"]
    _listify = deps["listify"]
    _metadata_value = deps["metadata_value"]
    _num_opt = deps["num_opt"]
    _parse_report_datetime = deps["parse_report_datetime"]
    _to_kst = deps["to_kst"]
    shared = _as_dict(report.get("shared_facts"))
    final = _as_dict(report.get("final_operator_conclusion"))
    action_raw = str(final.get("current_action") or report.get("action") or shared.get("action") or "").strip()
    action_is_sell = action_raw.upper() == "SELL" or _action_label(action_raw) == "매도"

    carry_state = _metadata_value(
        _first_report_path(
            report,
            [
                "shared_facts.commander_route.applied_policy.horizon.runtime_context.carry_state",
                "shared_facts.commander_route.horizon.runtime_context.carry_state",
                "fact_payload.trade.commander_route.applied_policy.horizon.runtime_context.carry_state",
                "fact_payload.trade.shared_facts.commander_route.applied_policy.horizon.runtime_context.carry_state",
                "fact_payload.trade.canonical_agent_artifacts.monitor.applied_policy.horizon.runtime_context.carry_state",
                "monitor_snapshot.applied_policy.horizon.runtime_context.carry_state",
                "monitor_snapshot.decision_trace.applied_policy.horizon.runtime_context.carry_state",
                "runtime_context.carry_state",
            ],
        )
    )
    carry_risk_bias = _metadata_value(
        _first_report_path(
            report,
            [
                "shared_facts.commander_route.applied_policy.horizon.runtime_context.carry_risk_bias",
                "shared_facts.commander_route.horizon.runtime_context.carry_risk_bias",
                "fact_payload.trade.commander_route.applied_policy.horizon.runtime_context.carry_risk_bias",
                "fact_payload.trade.shared_facts.commander_route.applied_policy.horizon.runtime_context.carry_risk_bias",
                "fact_payload.trade.canonical_agent_artifacts.monitor.applied_policy.horizon.runtime_context.carry_risk_bias",
                "monitor_snapshot.applied_policy.horizon.runtime_context.carry_risk_bias",
                "monitor_snapshot.decision_trace.applied_policy.horizon.runtime_context.carry_risk_bias",
                "runtime_context.carry_risk_bias",
            ],
        )
    )
    actual_hold_sec = _num_opt(
        _first_report_path(
            report,
            [
                "fact_payload.trade.exit_vs_strategy_intent.actual_hold_sec",
                "fact_payload.trade.canonical_agent_artifacts.monitor.exit_vs_strategy_intent.actual_hold_sec",
                "fact_payload.trade.canonical_agent_artifacts.monitor.decision_trace.exit_vs_strategy_intent.actual_hold_sec",
                "fact_payload.trade.monitor_snapshot.exit_vs_strategy_intent.actual_hold_sec",
                "monitor_snapshot.exit_vs_strategy_intent.actual_hold_sec",
                "monitor_snapshot.decision_trace.exit_vs_strategy_intent.actual_hold_sec",
                "exit_vs_strategy_intent.actual_hold_sec",
                "shared_facts.exit_vs_strategy_intent.actual_hold_sec",
            ],
        )
    )
    exit_ts = _first_report_path(
        report,
        [
            "fact_payload.trade.exit_summary.ts",
            "fact_payload.trade.lifecycle_summary.exit.ts",
            "shared_facts.exit_ts",
            "exit_summary.ts",
        ],
    )
    if not exit_ts:
        for row in _listify(report.get("full_timeline") if isinstance(report.get("full_timeline"), list) else report.get("timeline")):
            row_obj = _as_dict(row)
            event = str(row_obj.get("event") or row_obj.get("step") or "").lower()
            if "exit" in event or "sell" in event or "청산" in event:
                exit_ts = row_obj.get("ts") or row_obj.get("timestamp")
                break

    exit_dt = _parse_report_datetime(exit_ts)
    estimated_entry_dt = None
    if exit_dt is not None and actual_hold_sec is not None and actual_hold_sec > 0:
        estimated_entry_dt = exit_dt - timedelta(seconds=actual_hold_sec)

    carry_state_key = carry_state.lower()
    explicit_carry = carry_state_key in {
        "overnight_open",
        "multi_session_stale",
        "eod_carry_approved",
        "carry_overnight_approved",
        "overnight",
    }

    entry_kst = _to_kst(estimated_entry_dt)
    exit_kst = _to_kst(exit_dt)
    weekend_carry = False
    crosses_session_date = False
    if entry_kst is not None and exit_kst is not None:
        crosses_session_date = entry_kst.date() != exit_kst.date()
        weekend_carry = (
            entry_kst.weekday() == 4
            and exit_kst.weekday() == 0
            and entry_kst.date() != exit_kst.date()
        ) or (exit_kst.date() - entry_kst.date()).days >= 2
    is_carryover_exit = bool(action_is_sell and (explicit_carry or crosses_session_date))

    return {
        "is_carryover_exit": is_carryover_exit,
        "carry_state": carry_state,
        "carry_state_label": _carry_state_label(carry_state, weekend_carry=weekend_carry),
        "carry_risk_bias": carry_risk_bias,
        "carry_risk_label": _carry_risk_label(carry_risk_bias),
        "actual_hold_sec": actual_hold_sec,
        "duration_label": _duration_label_seconds(actual_hold_sec),
        "exit_ts": exit_ts,
        "exit_kst": _format_kst_datetime(exit_dt),
        "exit_date_kst": _format_kst_date(exit_dt),
        "estimated_entry_kst": _format_kst_datetime(estimated_entry_dt),
        "estimated_entry_date_kst": _format_kst_date(estimated_entry_dt),
        "weekend_carry": weekend_carry,
        "date_basis": "actual_hold_sec와 청산 시각 역산",
    }



def build_prompt_proven_memory(report: Dict[str, Any], *, deps: Mapping[str, Any]) -> List[str]:
    _as_dict = deps["as_dict"]
    _badge = deps["badge"]
    _dedupe = deps["dedupe"]
    _failure_label = deps["failure_label"]
    _fmt_pct = deps["fmt_pct"]
    _humanize_reporter_source_label = deps["humanize_reporter_source_label"]
    _memory_layers_text = deps["memory_layers_text"]
    _memory_packet_state_line = deps["memory_packet_state_line"]
    _memory_status_label = deps["memory_status_label"]
    _metadata_value = deps["metadata_value"]
    _playbook_label = deps["playbook_label"]
    _resolve_prompt_proven_surface = deps["resolve_prompt_proven_surface"]
    memory = _as_dict(report.get("memory_surface"))
    if not memory:
        return []
    prompt = _resolve_prompt_proven_surface(memory)
    status = _as_dict(prompt.get("status"))
    strategy = _as_dict(prompt.get("strategy_memory"))
    packets = _as_dict(prompt.get("memory_packets"))
    policy = _as_dict(prompt.get("commander_memory_policy"))
    selected = _as_dict(prompt.get("selected_symbol_memory"))
    reporter = _as_dict(prompt.get("reporter_feedback_packet"))
    read_model = _as_dict(prompt.get("read_model_facts"))
    lines: List[str] = []

    def _present_label(value: Any) -> str:
        return "확인" if bool(value) else "미확인"

    def _yes_no(value: Any) -> str:
        return "예" if bool(value) else "아니오"

    lines.append(
        f"- {_badge('입력 확인', '#0f766e')} 전략가 호출 당시 프롬프트에 포함된 메모리, 리포터 피드백, 읽기 모델 입력입니다. "
        "최종 전략 해석은 '전략가 출력 근거'에서 분리해 봅니다."
    )

    lines.append(
        "- [포함 여부] 전략 메모리={strategy}, 메모리 패킷={packets}, 지휘관 정책={policy}, 종목 메모리={symbol}, "
        "리포터 피드백={reporter}, 읽기 모델={read_model}.".format(
            strategy=_present_label(status.get("strategy_memory_present")),
            packets=_present_label(status.get("memory_packets_present")),
            policy=_present_label(status.get("commander_memory_policy_present")),
            symbol=_present_label(status.get("selected_symbol_memory_present")),
            reporter=_present_label(status.get("reporter_feedback_present")),
            read_model=_present_label(status.get("read_model_facts_present")),
        )
    )

    if status.get("commander_memory_policy_present") and policy:
        application_mode = _metadata_value(policy.get("application_mode") or "-")
        lines.append(
            f"- [지휘관 정책] 활성 레이어={_memory_layers_text(policy.get('active_layers'))}; "
            f"우선순위={_memory_layers_text(policy.get('priority_order'), arrow=True)}; 적용 모드={application_mode}."
        )
    else:
        lines.append("- [지휘관 정책] 전략가 프롬프트에서 직접 확인되지 않았습니다.")

    if status.get("memory_packets_present") and packets:
        packet_line = "; ".join(
            [
                _memory_packet_state_line("daily", _as_dict(packets.get("daily"))),
                _memory_packet_state_line("weekly", _as_dict(packets.get("weekly"))),
                _memory_packet_state_line("monthly", _as_dict(packets.get("monthly"))),
                _memory_packet_state_line("symbol", _as_dict(packets.get("symbol"))),
            ]
        )
        lines.append(f"- [메모리 패킷] {packet_line}.")
    else:
        lines.append("- [메모리 패킷] 전략가 프롬프트에서 직접 확인되지 않았습니다.")

    if status.get("strategy_memory_present") and strategy:
        requested = _metadata_value(strategy.get("requested_day") or "")
        resolved = _metadata_value(strategy.get("resolved_day") or "")
        strategy_parts = [f"상태={_memory_status_label(strategy.get('status') or '-')}"]
        if requested and resolved:
            strategy_parts.append(f"기준일={requested} -> {resolved}")
        best = _memory_layers_text(strategy.get("best_playbooks"))
        worst = _memory_layers_text(strategy.get("worst_playbooks"))
        failures = _memory_layers_text(strategy.get("recent_failures"))
        if best != "-":
            strategy_parts.append(f"우세={_playbook_label(best)}")
        if worst != "-":
            strategy_parts.append(f"취약={_playbook_label(worst)}")
        if failures != "-":
            strategy_parts.append(f"최근 실패={_failure_label(failures)}")
        lines.append(f"- [전략 메모리] {', '.join(strategy_parts)}.")
    else:
        lines.append("- [전략 메모리] 전략가 프롬프트에서 직접 확인되지 않았습니다.")

    prompt_symbol = _metadata_value(selected.get("symbol") or report.get("symbol") or "-")
    if status.get("selected_symbol_memory_present"):
        trade_count = selected.get("trade_count") if selected.get("trade_count") not in (None, "") else "-"
        win_rate = selected.get("win_rate")
        win_rate_text = _fmt_pct(win_rate) if win_rate not in (None, "") else "-"
        dominant_playbook = _metadata_value(selected.get("dominant_playbook") or "-")
        lines.append(
            f"- [종목 메모리] 종목={prompt_symbol}, 과거 거래={trade_count}건, 승률={win_rate_text}, 우세 전략={_playbook_label(dominant_playbook)}."
        )
    else:
        lines.append(f"- [종목 메모리] {prompt_symbol} 세부 메모리는 전략가 프롬프트에서 직접 확인되지 않았습니다.")

    if status.get("reporter_feedback_present"):
        source_label = _humanize_reporter_source_label(_as_dict(reporter.get("source_reports")))
        reporter_status = _memory_status_label(reporter.get("status") or ("ok" if reporter.get("available") else "-"))
        reporter_parts = [
            f"사용 가능={_yes_no(reporter.get('available'))}",
            f"소비={_yes_no(reporter.get('consumed'))}",
            f"상태={reporter_status}",
            f"신뢰도={_metadata_value(reporter.get('confidence') or '-')}",
            f"소스={source_label}",
        ]
        analysis = _as_dict(reporter.get("trade_report_analysis"))
        if analysis:
            reporter_parts.append(
                "요약=닫힌 거래 {closed}건 / 승패 {wins}/{losses} / 평균 손익률 {avg}".format(
                    closed=analysis.get("closed_trade_count") if analysis.get("closed_trade_count") not in (None, "") else "-",
                    wins=analysis.get("win_count") if analysis.get("win_count") not in (None, "") else "-",
                    losses=analysis.get("loss_count") if analysis.get("loss_count") not in (None, "") else "-",
                    avg=_fmt_pct(analysis.get("avg_pnl_pct")),
                )
            )
        else:
            reporter_parts.append("요약=없음")
        lines.append(f"- [리포터 피드백] {', '.join(reporter_parts)}.")
    else:
        lines.append("- [리포터 피드백] 전략가 프롬프트에서 직접 확인되지 않았습니다.")

    if status.get("read_model_facts_present"):
        symbols = _memory_layers_text(read_model.get("symbols"), humanize=False)
        lines.append(
            f"- [읽기 모델] 최근 거래={read_model.get('recent_trade_count') or 0}건, "
            f"종목 패턴={read_model.get('symbol_pattern_count') or 0}건, "
            f"일간 요약={'있음' if read_model.get('daily_summary_present') else '없음'}."
        )
        if symbols != "-":
            lines.append(f"- [읽기 모델 표본] 종목={symbols}.")
    else:
        lines.append("- [읽기 모델] 전략가 프롬프트에서 직접 확인되지 않았습니다.")

    lines.append("- [해석] 이 값들은 전략가 입력 근거입니다. 실제 수치 조정 여부는 아래 메모리 적용 결과의 스캐너/모니터 라인을 우선 봅니다.")
    return _dedupe(lines)


def build_memory_application(report: Dict[str, Any], *, deps: Mapping[str, Any]) -> List[str]:
    _as_dict = deps["as_dict"]
    _badge = deps["badge"]
    _listify = deps["listify"]
    _memory_layers_text = deps["memory_layers_text"]
    _metadata_value = deps["metadata_value"]
    _monitor_delta_interpretation = deps["monitor_delta_interpretation"]
    _monitor_phase_line = deps["monitor_phase_line"]
    _num_opt = deps["num_opt"]
    _playbook_label = deps["playbook_label"]
    _policy_phase_line = deps["policy_phase_line"]
    _policy_source_label = deps["policy_source_label"]
    _reason_summary_line = deps["reason_summary_line"]
    _resolve_prompt_proven_surface = deps["resolve_prompt_proven_surface"]
    _same_policy_snapshot = deps["same_policy_snapshot"]
    _scanner_phase_line = deps["scanner_phase_line"]
    memory_app = _as_dict(report.get("memory_application_surface"))
    if not memory_app:
        return []
    memory_surface = _as_dict(report.get("memory_surface"))
    prompt_surface = _resolve_prompt_proven_surface(memory_surface) if memory_surface else {}
    prompt_policy = _as_dict(prompt_surface.get("commander_memory_policy"))
    latest_policy = _as_dict(memory_surface.get("commander_memory_policy"))
    scanner = _as_dict(memory_app.get("scanner_memory_bias"))
    monitor = _as_dict(memory_app.get("monitor_memory_bias"))
    lines: List[str] = []

    lines.append(
        f"- {_badge('적용 결과', '#b45309')} 메모리 영향은 전략가 입력, 스캐너 적용, 모니터 적용, 최신 커맨더 상태 순서로 분리했습니다."
    )
    if prompt_policy:
        lines.append(_policy_phase_line("전략가 입력 시점", prompt_policy))
    else:
        lines.append("- [전략가 입력 시점] 지휘관 메모리 정책은 전략가 프롬프트에서 직접 확인되지 않았습니다.")
    if scanner:
        lines.append(_scanner_phase_line(scanner))
    else:
        lines.append("- [스캐너 적용 시점] 스캐너 메모리 적용 trace가 없습니다.")
    if monitor:
        lines.append(_monitor_phase_line(monitor))
    else:
        lines.append("- [모니터 적용 시점] 모니터 메모리 적용 trace가 없습니다.")
    if latest_policy:
        lines.append(_policy_phase_line("최신 커맨더 상태", latest_policy))
        if prompt_policy and not _same_policy_snapshot(prompt_policy, latest_policy):
            lines.append("- [시점 차이] 최신 커맨더 상태는 전략가 프롬프트 이후 실행/복원 기준이라 전략가 입력 시점과 다를 수 있습니다.")
    else:
        lines.append("- [최신 커맨더 상태] 리포트에서 최신 커맨더 메모리 정책을 확인하지 못했습니다.")
    lines.append("- [적용 해석] 전략가 입력 시점의 비활성 여부보다 실제 매매 영향은 스캐너/모니터 적용 시점 라인을 우선 봅니다.")

    if scanner.get("captured"):
        active_layers = _memory_layers_text(scanner.get("active_layers"))
        state = "실제 후보 점수에 적용된 상태" if scanner.get("applied") else "요약만 기록된 상태"
        lines.append(f"- 스캐너 메모리 가중치는 {state}이며, 실제 반영 레이어는 {active_layers}입니다.")
        deltas = _as_dict(scanner.get("source_weight_delta"))
        if deltas:
            ordered = [f"{key} {float(val):+0.3f}" for key, val in deltas.items() if _num_opt(val) is not None]
            if ordered:
                lines.append(f"- 스캐너 소스 가중치 변화는 {', '.join(ordered)}입니다.")
        else:
            lines.append("- 스캐너 쪽은 소스 가중치 변화 상세가 남지 않아, 후보별 가감점만 확인됩니다.")
        symbol = _metadata_value(scanner.get("selected_symbol") or report.get("symbol") or "해당 종목")
        delta = _num_opt(scanner.get("selected_bias_adjustment"))
        if delta is not None:
            if abs(delta) < 1e-12:
                lines.append(f"- 이번 거래 후보 {symbol}에는 메모리 기반 추가 가감점이 없었습니다.")
            else:
                lines.append(f"- 이번 거래 후보 {symbol}에는 메모리 기반 가감점 {delta:+0.3f}이 반영됐습니다.")
        reason = ", ".join(str(x) for x in _listify(scanner.get("reason")) if str(x).strip())
        if reason:
            summary = _reason_summary_line(_listify(scanner.get("reason")), "스캐너 조정은")
            if summary:
                lines.append(summary)
    else:
        lines.append("- 스캐너 메모리 가중치의 실제 delta는 이 거래 artifact에 기록되지 않았습니다.")

    if monitor.get("captured"):
        active_layers_text = _memory_layers_text(monitor.get("active_layers"))
        state = "진입 정책에 적용된 상태" if monitor.get("applied") else "요약만 기록된 상태"
        lines.append(f"- 모니터 메모리 조정은 {state}이며, 실제 반영 레이어는 {active_layers_text}입니다.")
        active_layers = [str(x) for x in _listify(monitor.get("active_layers")) if str(x).strip()]
        if monitor.get("applied") and active_layers:
            lines.append(f"- 이번 거래에서는 모니터가 {_memory_layers_text(active_layers)} 메모리를 진입 판단에 직접 반영했습니다.")
        deltas = []
        for row in _listify(monitor.get("applied_deltas")):
            row = _as_dict(row)
            if not row:
                continue
            deltas.append(
                f"{row.get('field')} {float(row.get('from')):0.3f} -> {float(row.get('to')):0.3f} ({float(row.get('delta')):+0.3f})"
            )
        if deltas:
            lines.append(f"- 진입 정책 변화는 {', '.join(deltas)}입니다.")
            interpretation = _monitor_delta_interpretation(_listify(monitor.get("applied_deltas")))
            if interpretation:
                lines.append(f"- 진입 적용 해석: {interpretation}")
        else:
            lines.append("- 모니터 진입 정책 변화는 이 거래 artifact에 기록되지 않았습니다.")

        hold_deltas = []
        for row in _listify(monitor.get("hold_deltas")):
            row = _as_dict(row)
            if not row:
                continue
            hold_deltas.append(
                f"{row.get('field')} {float(row.get('from')):0.3f} -> {float(row.get('to')):0.3f} ({float(row.get('delta')):+0.3f})"
            )
        if hold_deltas:
            lines.append(f"- 보유 관리 변화는 {', '.join(hold_deltas)}입니다.")
            lines.append("- 보유 관리 해석: 경고 후 재확인 조건을 줄여, 보유 포지션을 더 빨리 정리할 수 있게 했습니다.")

        exit_deltas = []
        for row in _listify(monitor.get("exit_deltas")):
            row = _as_dict(row)
            if not row:
                continue
            exit_deltas.append(
                f"{row.get('field')} {float(row.get('from')):0.3f} -> {float(row.get('to')):0.3f} ({float(row.get('delta')):+0.3f})"
            )
        if exit_deltas:
            lines.append(f"- 청산 정책 변화는 {', '.join(exit_deltas)}입니다.")
            lines.append("- 청산 정책 해석: 손실과 drawdown 기준을 더 타이트하게 잡아, 손상이 확인되면 더 빨리 청산하도록 조정했습니다.")

        lines.append(
            f"- 모니터 위험 자세는 {_playbook_label(monitor.get('risk_posture') or '-')}이었고, 최종 정책 기준은 {_policy_source_label(monitor.get('effective_policy_source') or '-')}이었습니다."
        )
        reason = ", ".join(str(x) for x in _listify(monitor.get("reason")) if str(x).strip())
        if reason:
            summary = _reason_summary_line(_listify(monitor.get("reason")), "모니터 조정은")
            if summary:
                lines.append(summary)
    else:
        lines.append("- 모니터 메모리 조정의 실제 delta는 이 거래 artifact에 기록되지 않았습니다.")

    return lines

