"""AI report holding-story, candidate-watch and memory-layer compaction helpers (deterministic, read-only).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _build_holding_story_summary_r3_impl(hold_count, monitor_reason, status_text, *, facade):
    posture = facade._operator_action_label(facade._clip(monitor_reason.get("posture"), max_len=32) or "WAIT")
    trigger = facade._operator_axis_label(facade._clip(monitor_reason.get("trigger_type"), max_len=48) or "not_captured")
    axis = facade._operator_axis_label(facade._clip(monitor_reason.get("active_exit_axis"), max_len=64) or trigger)
    confirm_required = monitor_reason.get("confirm_required")
    confirm_count = monitor_reason.get("confirm_count")
    exit_triggered = bool(monitor_reason.get("exit_triggered"))
    if hold_count > 0:
        base = f"보유 구간에서는 모니터가 총 {hold_count}회 실행되었고, 마지막 포지션 판단은 {posture}였습니다. 핵심 감시 축은 {axis}{facade._korean_euro_ro(axis)} 유지됐습니다."
    else:
        base = "이번 lifecycle의 보유 구간 기록은 제한적이어서, 저장된 모니터 근거를 중심으로 보수적으로 정리했습니다."
    if confirm_required is not None:
        base += f" 청산 확인 조건은 {int(confirm_count or 0)}/{int(confirm_required or 0)} 단계로 기록되었습니다."
    if status_text.lower() == "open" and not exit_triggered:
        base += " 아직 확정된 매도 신호는 확인되지 않았습니다."
    return base


def _compact_holding_summary_r3_impl(holding, *, facade):
    data = holding if isinstance(holding, dict) else {}
    posture_rows = data.get("posture_history") if isinstance(data.get("posture_history"), list) else []
    recent_posture = [facade._compact_event_row(row) for row in posture_rows[-4:] if isinstance(row, dict)]
    recent_posture = [row for row in recent_posture if row]
    return {
        "run_count": len(list(data.get("run_ids") or [])),
        "recent_run_ids": [str(x or "") for x in list(data.get("run_ids") or [])[-6:] if str(x or "").strip()],
        "holding_event_count": len(list(data.get("holding_events") or [])),
        "recent_posture_history": recent_posture,
        "recent_monitor_updates": facade._tail_list(data.get("monitor_updates"), max_items=6, max_len=200),
    }


def _compact_candidate_watch_proposal_r3_impl(value, *, facade):
    data = facade._as_dict(value)
    if not data:
        return {}
    out = {
        "source": facade._clip(data.get("source"), max_len=80),
        "behavior_effect": facade._clip(data.get("behavior_effect"), max_len=48),
        "tactical_strategy": facade._clip(data.get("tactical_strategy"), max_len=80),
        "tactical_subtype": facade._clip(data.get("tactical_subtype"), max_len=80),
        "max_priority_rank": data.get("max_priority_rank"),
        "max_runner_ups": data.get("max_runner_ups"),
        "cascade_enabled": data.get("cascade_enabled"),
        "reason": facade._clip(data.get("reason"), max_len=220),
        "cascade_allowed_reasons": facade._listify(data.get("cascade_allowed_reasons"), max_items=6, max_len=80),
        "cascade_blocked_reasons": facade._listify(data.get("cascade_blocked_reasons"), max_items=8, max_len=80),
    }
    return {key: value for key, value in out.items() if value not in ("", None, [], {})}


def _compact_memory_layer_decisions_r3_impl(value, *, facade):
    decisions = value if isinstance(value, dict) else {}
    out: Dict[str, Any] = {}
    for layer, row in list(decisions.items())[:6]:
        if not isinstance(row, dict):
            continue
        out[str(layer)] = {
            "status": facade._clip(row.get("status"), max_len=32),
            "active": row.get("active"),
            "visible": row.get("visible"),
            "used": row.get("used"),
            "gate_reason": facade._clip(row.get("gate_reason"), max_len=80),
            "effect": facade._clip(row.get("effect"), max_len=140),
            "reason": facade._clip(row.get("reason"), max_len=220),
            "confidence": row.get("confidence"),
            "application_targets": facade._listify(row.get("application_targets"), max_items=5, max_len=60),
        }
    return out
