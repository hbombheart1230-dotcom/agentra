"""Strategist policy-adjustment directive normalisation (post-processing of already received output).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations
from libs.runtime.strategist.llm.adjustment_directives_infer_policy_adjustment_direction_r3 import _infer_policy_adjustment_direction_r3_impl as _infer_policy_adjustment_direction_owner
from libs.runtime.strategist.llm.adjustment_directives_normalize_rejected_strategy_reasons_ import _normalize_rejected_strategy_reasons_r3_impl as _normalize_rejected_strategy_reasons_owner


def _infer_policy_adjustment_direction_r3_impl(baseline_summary, current_summary, *, facade):
    return _infer_policy_adjustment_direction_owner(baseline_summary, current_summary, facade=facade)


def _normalize_policy_adjustment_surface_r3_impl(
    *,
    raw_adjustment,
    baseline_summary,
    current_summary,
    refresh_requested,
    recent_strategy_feedback,
    facade,
):
    raw = dict(raw_adjustment or {}) if isinstance(raw_adjustment, dict) else {}
    delta_fields = facade._monitor_entry_policy_adjustment_delta_fields(baseline_summary, current_summary)
    adjustment_required = (
        bool(raw.get("adjustment_required"))
        if raw.get("adjustment_required") is not None
        else bool(refresh_requested)
    )
    dominant_failure_pattern = str(raw.get("dominant_failure_pattern") or "").strip()
    if not dominant_failure_pattern:
        dominant_failure_pattern = str(((recent_strategy_feedback or {}).get("top_recent_weaknesses") or [""])[0] or "").strip()
    baseline_retained = bool(raw.get("baseline_retained")) if raw.get("baseline_retained") is not None else not bool(delta_fields)
    baseline_retained_reason = str(raw.get("baseline_retained_reason") or "").strip()
    if not baseline_retained_reason and baseline_retained:
        baseline_retained_reason = (
            "no_material_delta_from_baseline"
            if adjustment_required
            else "conservative_baseline_retained"
        )
    direction = str(raw.get("adjustment_direction") or "").strip().lower()
    if direction not in {"tighten", "relax", "mixed", "none"}:
        direction = facade._infer_policy_adjustment_direction(baseline_summary, current_summary)
    return {
        "adjustment_required": bool(adjustment_required),
        "baseline_retained": bool(baseline_retained),
        "baseline_retained_reason": baseline_retained_reason,
        "adjustment_direction": direction,
        "dominant_failure_pattern": dominant_failure_pattern,
        "addressed_failure_patterns": [str(x) for x in list(raw.get("addressed_failure_patterns") or []) if str(x or "").strip()][:8],
        "delta_fields": list(delta_fields),
        "delta_count": int(len(delta_fields)),
        "hold_refresh_considered": bool(refresh_requested),
        "baseline_summary": dict(baseline_summary or {}),
        "current_summary": dict(current_summary or {}),
    }


def _clean_directive_reason_r3_impl(value, *, default, facade):
    text = str(value or "").strip()
    if not text:
        return str(default or "").strip()
    lowered = text.lower()
    if any(token in lowered for token in facade._GENERIC_DIRECTIVE_TOKENS):
        return str(default or "").strip()
    return text


def _normalize_strategy_adjustment_directives_r3_impl(
    *,
    raw_directives,
    playbook,
    policy_adjustment,
    commander_context,
    strategy_memory,
    selected_symbol_memory,
    facade,
):
    raw = dict(raw_directives or {}) if isinstance(raw_directives, dict) else {}
    memory_usage_disabled = facade._strategy_memory_usage_disabled(commander_context.get("commander_memory_policy"))
    if memory_usage_disabled:
        strategy_memory = {}
        selected_symbol_memory = {}
    refresh_context = (
        dict((commander_context.get("strategist_refresh_context") or {}))
        if isinstance(commander_context.get("strategist_refresh_context"), dict)
        else {}
    )
    refresh_reason = str(commander_context.get("strategist_refresh_reason") or "").strip().lower()
    delta_fields = [str(x) for x in list(policy_adjustment.get("delta_fields") or []) if str(x or "").strip()][:8]
    current_playbook = str(playbook or "").strip()
    best_playbooks = [str(x) for x in list(strategy_memory.get("best_playbooks") or []) if str(x or "").strip()]
    worst_playbooks = [str(x) for x in list(strategy_memory.get("worst_playbooks") or []) if str(x or "").strip()]
    dominant_blocker = str(selected_symbol_memory.get("dominant_monitor_blocker") or "").strip()
    repeated_failures = list(selected_symbol_memory.get("repeated_failure_pattern") or [])
    dominant_failure_pattern = str(policy_adjustment.get("dominant_failure_pattern") or "").strip()
    direction = str(policy_adjustment.get("adjustment_direction") or "none").strip().lower()

    playbook_default_action = "maintain"
    playbook_default_target = current_playbook or None
    playbook_default_reason = "결정적 메모리 근거가 약해 현재 플레이북을 유지합니다"
    if current_playbook and current_playbook in worst_playbooks:
        replacement = next((x for x in best_playbooks if x and x != current_playbook), "")
        if replacement:
            playbook_default_action = "switch"
            playbook_default_target = replacement
            playbook_default_reason = f"최근 메모리에서 {current_playbook} 성과가 약해 {replacement}로 전환합니다"
        else:
            playbook_default_action = "deprioritize"
            playbook_default_target = current_playbook
            playbook_default_reason = f"최근 메모리에서 {current_playbook} 성과가 약해 우선순위를 낮춥니다"
    elif current_playbook and current_playbook in best_playbooks:
        playbook_default_action = "prefer"
        playbook_default_target = current_playbook
        playbook_default_reason = f"최근 메모리에서 {current_playbook} 성과가 상대적으로 우세해 유지 우선합니다"

    entry_default_action = "maintain"
    if direction == "tighten":
        entry_default_action = "tighten"
    elif direction == "relax":
        entry_default_action = "relax"
    elif direction == "mixed":
        entry_default_action = "rebalance"
    entry_default_reason = (
        f"결정적 패턴이 {dominant_failure_pattern}로 반복돼 진입 조건을 {entry_default_action}합니다"
        if entry_default_action != "maintain" and dominant_failure_pattern
        else "결정적 메모리 근거가 약해 보수적 진입 기준을 유지합니다"
    )

    focus_axes_default = facade._focus_axes_from_strings(
        dominant_failure_pattern,
        dominant_blocker,
        str(refresh_context.get("monitor_reason") or ""),
        " ".join(str((row or {}).get("value") or "") for row in repeated_failures if isinstance(row, dict)),
    )
    monitor_focus_default_action = "increase_focus" if focus_axes_default else "maintain"
    monitor_focus_default_reason = (
        f"반복 실패 축이 {', '.join(focus_axes_default)}에 집중돼 해당 축 확인을 강화합니다"
        if focus_axes_default
        else "결정적 축 집중 근거가 약해 현재 모니터 초점을 유지합니다"
    )

    selected_bias_default_action = "none"
    selected_bias_default_reason = "선택 종목 편향 조정 근거가 약합니다"
    dominant_symbol_playbook = str(selected_symbol_memory.get("dominant_playbook") or "").strip().lower()
    if dominant_symbol_playbook == "pullback" and current_playbook != "pullback":
        selected_bias_default_action = "prefer_pullback"
        selected_bias_default_reason = "종목 메모리에서 pullback 성향이 우세해 눌림 우선으로 봅니다"
    elif "breakout" in dominant_blocker.lower() or any("breakout" in str((row or {}).get("value") or "").lower() for row in repeated_failures if isinstance(row, dict)):
        selected_bias_default_action = "avoid_breakout"
        selected_bias_default_reason = "종목 메모리에서 breakout 구조 불일치가 반복돼 추격 진입을 피합니다"
    elif "reclaim" in dominant_blocker.lower():
        selected_bias_default_action = "prefer_reclaim"
        selected_bias_default_reason = "종목 메모리에서 reclaim 확인 부족이 반복돼 reclaim 우선으로 봅니다"
    elif "extended" in dominant_blocker.lower() or "vwap" in dominant_blocker.lower():
        selected_bias_default_action = "avoid_extension"
        selected_bias_default_reason = "종목 메모리에서 과확장 진입 실패가 반복돼 extension 구간을 피합니다"

    refresh_default_action = "none"
    refresh_default_reason = "추가 refresh 지시가 필요하지 않습니다"
    if refresh_reason == "repeated_hold_monitor_only":
        refresh_default_action = "refresh_for_repeated_hold"
        refresh_default_reason = "반복 hold가 누적돼 보유 프레임 재평가가 필요합니다"
    elif bool(commander_context.get("strategist_refresh_requested")) and str(refresh_context.get("active_exit_axis") or "").strip():
        refresh_default_action = "refresh_for_exit_axis_mismatch"
        refresh_default_reason = "활성 exit 축과 현재 프레임 불일치 가능성을 재평가합니다"
    elif bool(commander_context.get("strategist_refresh_requested")):
        refresh_default_action = "refresh_for_holding"
        refresh_default_reason = "보유 상태 refresh 요청이 있어 현재 프레임을 재검토합니다"

    playbook_action_raw = dict(raw.get("playbook_action") or {}) if isinstance(raw.get("playbook_action"), dict) else {}
    entry_action_raw = dict(raw.get("entry_policy_action") or {}) if isinstance(raw.get("entry_policy_action"), dict) else {}
    monitor_focus_raw = dict(raw.get("monitor_focus_action") or {}) if isinstance(raw.get("monitor_focus_action"), dict) else {}
    selected_bias_raw = dict(raw.get("selected_symbol_bias_action") or {}) if isinstance(raw.get("selected_symbol_bias_action"), dict) else {}
    refresh_action_raw = dict(raw.get("refresh_action") or {}) if isinstance(raw.get("refresh_action"), dict) else {}

    playbook_action = str(playbook_action_raw.get("action") or playbook_default_action).strip().lower()
    if playbook_action not in facade._PLAYBOOK_ACTIONS:
        playbook_action = playbook_default_action
    playbook_target = str(playbook_action_raw.get("target") or (playbook_default_target or "")).strip() or None
    playbook_reason = facade._clean_directive_reason(
        playbook_action_raw.get("reason"),
        default=playbook_default_reason,
    )

    entry_policy_action = str(entry_action_raw.get("action") or entry_default_action).strip().lower()
    if entry_policy_action not in facade._ENTRY_POLICY_ACTIONS:
        entry_policy_action = entry_default_action
    target_fields = [str(x) for x in list(entry_action_raw.get("target_fields") or delta_fields) if str(x or "").strip()][:6]
    entry_reason = facade._clean_directive_reason(entry_action_raw.get("reason"), default=entry_default_reason)

    monitor_focus_action = str(monitor_focus_raw.get("action") or monitor_focus_default_action).strip().lower()
    if monitor_focus_action not in facade._MONITOR_FOCUS_ACTIONS:
        monitor_focus_action = monitor_focus_default_action
    target_axes = [str(x) for x in list(monitor_focus_raw.get("target_axes") or focus_axes_default) if str(x or "").strip() in facade._MONITOR_FOCUS_AXES][:4]
    monitor_focus_reason = facade._clean_directive_reason(monitor_focus_raw.get("reason"), default=monitor_focus_default_reason)

    selected_symbol_bias_action = str(selected_bias_raw.get("action") or selected_bias_default_action).strip().lower()
    if selected_symbol_bias_action not in facade._SELECTED_SYMBOL_BIAS_ACTIONS:
        selected_symbol_bias_action = selected_bias_default_action
    selected_symbol_bias_reason = facade._clean_directive_reason(
        selected_bias_raw.get("reason"),
        default=selected_bias_default_reason,
    )

    refresh_action = str(refresh_action_raw.get("action") or refresh_default_action).strip().lower()
    if refresh_action not in facade._REFRESH_ACTIONS:
        refresh_action = refresh_default_action
    refresh_reason_text = facade._clean_directive_reason(refresh_action_raw.get("reason"), default=refresh_default_reason)

    return {
        "playbook_action": {
            "action": playbook_action,
            "target": playbook_target,
            "reason": playbook_reason,
        },
        "entry_policy_action": {
            "action": entry_policy_action,
            "target_fields": list(target_fields),
            "reason": entry_reason,
        },
        "monitor_focus_action": {
            "action": monitor_focus_action,
            "target_axes": list(target_axes),
            "reason": monitor_focus_reason,
        },
        "selected_symbol_bias_action": {
            "action": selected_symbol_bias_action,
            "reason": selected_symbol_bias_reason,
        },
        "refresh_action": {
            "action": refresh_action,
            "reason": refresh_reason_text,
        },
    }


def _normalize_rejected_strategy_reasons_r3_impl(raw, *, tactical_strategy, strategy_scores, facade):
    return _normalize_rejected_strategy_reasons_owner(raw, tactical_strategy=tactical_strategy, strategy_scores=strategy_scores, facade=facade)


def _sanitize_reason_list_r3_impl(raw, defaults, *, facade):
    allowed = {str(x).strip() for x in defaults if str(x).strip()}
    values = raw if isinstance(raw, list) else []
    out: List[str] = []
    for item in values:
        text = str(item or "").strip().lower()
        if text and text in allowed and text not in out:
            out.append(text)
    return out or list(defaults)
