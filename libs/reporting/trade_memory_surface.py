from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

from libs.reporting.reporter_feedback import build_strategist_feedback_packet
from libs.reporting.symbol_read_model import build_symbol_read_model
from libs.runtime.commander_memory_policy import build_commander_memory_policy
from libs.runtime.memory_packet_loader import load_commander_memory_packets
import sys as _r3_sys
from libs.reporting.trade_memory_projection_parts.memory_input_visibility import (
    memory_input_commander_memory_policy_daily_packet,
    memory_input_monitor_guidance_monthly_packet,
)
from libs.reporting.trade_memory_projection_parts.memory_feedback_rebuild import (
    memory_feedback_best_playbooks_commander_memory_policy_r,
)
from libs.reporting.trade_memory_projection_parts.memory_status_summary import (
    memory_status_active_layers_priority_order,
)
from libs.reporting.trade_memory_projection_parts.memory_surface_payload import (
    memory_status_value_result,
)


def _dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, list) else []


def _text(value: Any, *, max_len: int = 120) -> str:
    text = str(value or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max(0, max_len - 3)] + "..."


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return int(default)


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def _first_dict(*values: Any) -> Dict[str, Any]:
    for value in values:
        if isinstance(value, dict) and value:
            return dict(value)
    return {}


def _load_json_artifact(path_value: Any) -> Dict[str, Any]:
    path_text = str(path_value or "").strip()
    if not path_text:
        return {}
    path = Path(path_text)
    if not path.is_absolute():
        path = Path.cwd() / path
    try:
        if not path.exists():
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def _join_text(values: Any, *, max_items: int = 3, max_len: int = 32) -> str:
    items: List[str] = []
    for value in _list(values):
        text = _text(value, max_len=max_len)
        if not text:
            continue
        items.append(text)
        if len(items) >= max(1, int(max_items)):
            break
    return ", ".join(items)


def _strategy_anchor_artifacts(container: Any) -> Dict[str, Any]:
    obj = _dict(container)
    direct = _dict(obj.get("artifacts"))
    anchor = _dict(obj.get("strategy_anchor"))
    anchor_artifacts = _dict(anchor.get("artifacts"))
    return _first_dict(anchor_artifacts, direct)


def _strategist_input_artifact_paths(story_input: Dict[str, Any]) -> List[str]:
    paths: List[str] = []

    def _append(value: Any) -> None:
        text = str(value or "").strip()
        if text and text not in paths:
            paths.append(text)

    for container in (
        story_input,
        story_input.get("artifacts"),
        story_input.get("paths"),
        story_input.get("strategy_anchor"),
        story_input.get("market_context_human"),
        story_input.get("scanner_reason_human"),
        story_input.get("monitor_reason_human"),
        story_input.get("filters_human"),
    ):
        obj = _dict(container)
        _append(obj.get("strategist_input_json"))
        artifacts = _strategy_anchor_artifacts(obj)
        _append(artifacts.get("strategist_input_json"))
    return paths


def _resolve_strategist_input_artifact(story_input: Dict[str, Any]) -> Dict[str, Any]:
    direct = _dict(story_input.get("strategist_input"))
    if direct:
        return direct
    for path in _strategist_input_artifact_paths(story_input):
        payload = _load_json_artifact(path)
        if payload:
            return payload
    return {}


def _symbol_pattern_memory(symbol: str, read_model_facts: Dict[str, Any]) -> Dict[str, Any]:
    normalized_symbol = str(symbol or "").strip()
    if not normalized_symbol:
        return {}
    symbol_patterns = _dict(read_model_facts.get("symbol_patterns"))
    pattern = _dict(symbol_patterns.get(normalized_symbol))
    if not pattern:
        return {}
    trade_count = _safe_int(pattern.get("trade_count"))
    if trade_count <= 0:
        return {}
    return {
        "symbol": str(pattern.get("symbol") or normalized_symbol).strip(),
        "trade_count": trade_count,
        "closed_trade_count": _safe_int(pattern.get("closed_trade_count")),
        "win_rate": _safe_float(pattern.get("win_rate")),
        "dominant_playbook": str(pattern.get("dominant_playbook") or "").strip(),
        "dominant_monitor_blocker": str(pattern.get("dominant_monitor_blocker") or "").strip(),
        "override_eligible": trade_count >= 5 and _safe_int(pattern.get("closed_trade_count")) >= 3,
        "source": "prompt_read_model_symbol_patterns",
    }


def _packet_symbol_memory(symbol: str, memory_packets: Dict[str, Any]) -> Dict[str, Any]:
    packet = _dict(memory_packets.get("symbol_memory_packet"))
    packet_symbol = str(packet.get("symbol") or "").strip()
    if not packet or (symbol and packet_symbol and packet_symbol != str(symbol).strip()):
        return {}
    if not packet_symbol and _safe_int(packet.get("trade_count")) <= 0:
        return {}
    return dict(packet)


def _read_model_recent_trade_count(read_model_facts: Dict[str, Any], visibility: Dict[str, Any]) -> int:
    explicit = read_model_facts.get("recent_trade_count")
    if explicit not in (None, ""):
        return _safe_int(explicit)
    recent_trades = _list(read_model_facts.get("recent_trades"))
    if recent_trades:
        return len(recent_trades)
    return _safe_int(visibility.get("recent_trade_count"))


def _read_model_symbol_pattern_count(read_model_facts: Dict[str, Any], visibility: Dict[str, Any]) -> int:
    explicit = read_model_facts.get("symbol_pattern_count")
    if explicit not in (None, ""):
        return _safe_int(explicit)
    symbol_patterns = _dict(read_model_facts.get("symbol_patterns"))
    if symbol_patterns:
        return len(symbol_patterns)
    return _safe_int(visibility.get("symbol_pattern_count"))


def _read_model_symbols(read_model_facts: Dict[str, Any], visibility: Dict[str, Any]) -> List[Any]:
    symbols = _list(read_model_facts.get("symbols") or visibility.get("symbols"))
    if symbols:
        return symbols
    symbol_patterns = _dict(read_model_facts.get("symbol_patterns"))
    return list(symbol_patterns.keys())


def _read_model_daily_summary_present(read_model_facts: Dict[str, Any], visibility: Dict[str, Any]) -> bool:
    if read_model_facts.get("daily_summary_present") not in (None, ""):
        return bool(read_model_facts.get("daily_summary_present"))
    if read_model_facts.get("daily_summary") not in (None, "", {}, []):
        return True
    return bool(visibility.get("daily_summary_present"))


def _nested_memory_sources(
    story_input: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    reasoning_trace = _dict(story_input.get("reasoning_trace"))
    commander_summary = _dict(reasoning_trace.get("commander_summary"))
    strategist_summary = _dict(reasoning_trace.get("strategist_summary"))
    llm_output = _dict(strategist_summary.get("llm_parsed_output"))
    strategist_input_artifact = _resolve_strategist_input_artifact(story_input)
    strategist_source_input = _dict(strategist_input_artifact.get("source_input"))
    strategist_evidence = _dict(story_input.get("strategist_evidence"))
    decision_frames = _list(strategist_evidence.get("decision_frames"))
    first_frame = decision_frames[0] if decision_frames and isinstance(decision_frames[0], dict) else {}
    frame_payload = _dict(_dict(first_frame).get("payload"))
    visibility = _first_dict(
        story_input.get("memory_packet_visibility"),
        strategist_summary.get("memory_packet_visibility"),
        commander_summary.get("memory_packet_visibility"),
    )
    return commander_summary, strategist_summary, llm_output, frame_payload, visibility, strategist_source_input


def _resolve_day(source: Dict[str, Any], commander_summary: Dict[str, Any]) -> str:
    for value in (
        source.get("day"),
        source.get("trade_day"),
        commander_summary.get("day"),
        commander_summary.get("ts"),
        source.get("ts"),
    ):
        text = str(value or "").strip()
        if len(text) >= 10:
            return text[:10]
    return ""


def _resolve_reports_root(source: Dict[str, Any]) -> Path:
    reports_root = str(source.get("reports_root") or os.getenv("REPORTS_ROOT", "reports")).strip() or "reports"
    return Path(reports_root)


def _build_symbol_memory_from_persisted(symbol: str, reports_root: Path) -> Dict[str, Any]:
    if not symbol:
        return {}
    model = build_symbol_read_model(str(reports_root / "trades"), symbol, persisted_only=True)
    if not isinstance(model, dict):
        return {}
    trade_count = _safe_int(model.get("trade_count"))
    closed_trade_count = _safe_int(model.get("closed_trade_count"))
    if trade_count <= 0:
        return {}
    return {
        "symbol": str(model.get("symbol") or symbol).strip(),
        "trade_count": trade_count,
        "closed_trade_count": closed_trade_count,
        "win_rate": _safe_float(model.get("win_rate")),
        "dominant_playbook": str(model.get("dominant_playbook") or "").strip(),
        "dominant_monitor_blocker": str(model.get("dominant_monitor_blocker") or "").strip(),
        "override_eligible": trade_count >= 5 and closed_trade_count >= 3,
    }


def _reporter_feedback_strength(packet: Dict[str, Any]) -> tuple[int, int, int, int]:
    source_reports = _dict(packet.get("source_reports"))
    trade_report_analysis = _dict(packet.get("trade_report_analysis"))
    return (
        1 if bool(packet.get("available")) else 0,
        sum(1 for key in ("metrics", "trade_explain", "reporter_analysis", "trade_reports") if source_reports.get(key)),
        _safe_int(trade_report_analysis.get("closed_trade_count")),
        len(_list(packet.get("recommendation") or [])),
    )


def _resolve_reporter_feedback_packet(
    *,
    source: Dict[str, Any],
    commander_summary: Dict[str, Any],
    reporter_feedback: Dict[str, Any],
) -> Dict[str, Any]:
    reports_root = _resolve_reports_root(source)
    day = _resolve_day(source, commander_summary)
    fallback_packet = (
        build_strategist_feedback_packet(
            mode="trade_report_fallback",
            payload={},
            reports_root=reports_root,
            day=day,
        )
        if day
        else {}
    )
    current = dict(reporter_feedback or {})
    if _reporter_feedback_strength(fallback_packet) > _reporter_feedback_strength(current):
        return fallback_packet
    return current


def _build_fallback_memory_context(
    *,
    source: Dict[str, Any],
    commander_summary: Dict[str, Any],
    selected_symbol_memory: Dict[str, Any],
    memory_packets: Dict[str, Any],
    commander_memory_policy: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    reports_root = _resolve_reports_root(source)
    day = _resolve_day(source, commander_summary)
    symbol = str(source.get("symbol") or source.get("selected_symbol") or "").strip()

    resolved_selected_symbol_memory = dict(selected_symbol_memory or {})
    if not resolved_selected_symbol_memory and symbol:
        resolved_selected_symbol_memory = _build_symbol_memory_from_persisted(symbol, reports_root)

    fallback_state = {
        "day": day,
        "reports_root": str(reports_root),
        "selected": {"symbol": symbol} if symbol else {},
        "selected_symbol_memory": dict(resolved_selected_symbol_memory or {}),
    }
    resolved_packets = dict(memory_packets or {})
    if not resolved_packets:
        resolved_packets = load_commander_memory_packets(state=fallback_state)

    resolved_policy = dict(commander_memory_policy or {})
    if not resolved_policy and resolved_packets:
        session_bias = str(
            commander_summary.get("session_bias")
            or _dict(commander_summary.get("commander_decision")).get("session_bias")
            or "active_selection"
        ).strip() or "active_selection"
        resolved_policy = build_commander_memory_policy(
            session_bias=session_bias,
            memory_packets=resolved_packets,
        )
    return resolved_selected_symbol_memory, resolved_packets, resolved_policy


def build_trade_report_memory_surface(story_input: Dict[str, Any] | None) -> Dict[str, Any]:
    commander_memory_policy, daily_packet, frame_payload, llm_output, memory_packets, packets_visibility, policy_visibility, prompt_commander_memory_policy, prompt_daily_packet, prompt_memory_packets, prompt_monthly_packet, prompt_read_model_facts, prompt_reporter_feedback, prompt_selected_symbol_memory, prompt_strategy_memory, prompt_symbol_packet, prompt_weekly_packet, read_model_facts, read_model_visibility, recent_feedback_visibility, reporter_feedback, reporter_visibility, selected_symbol_memory, selected_visibility, source, strategist_source_input, strategist_summary, strategy_memory, strategy_visibility, weekly_packet = memory_input_commander_memory_policy_daily_packet(story_input=story_input, facade=_r3_sys.modules[__name__])
    monitor_guidance, monthly_packet, playbook, prompt_best_playbooks, prompt_read_model_present, prompt_recent_failures, prompt_recent_success_patterns, prompt_reporter_available, prompt_reporter_consumed, prompt_reporter_present, prompt_reporter_status, prompt_selected_blocker, prompt_selected_playbook, prompt_selected_present, prompt_selected_trade_count, prompt_selected_win_rate, prompt_strategy_present, prompt_strategy_requested_day, prompt_strategy_resolved_day, prompt_strategy_status, prompt_worst_playbooks, read_model_present, reporter_available, reporter_consumed, reporter_present, scanner_bias, selected_present, strategy_present, symbol, symbol_packet = memory_input_monitor_guidance_monthly_packet(memory_packets=memory_packets, source=source, selected_visibility=selected_visibility, selected_symbol_memory=selected_symbol_memory, llm_output=llm_output, frame_payload=frame_payload, strategist_summary=strategist_summary, strategist_source_input=strategist_source_input, prompt_strategy_memory=prompt_strategy_memory, strategy_visibility=strategy_visibility, prompt_selected_symbol_memory=prompt_selected_symbol_memory, prompt_reporter_feedback=prompt_reporter_feedback, reporter_visibility=reporter_visibility, prompt_read_model_facts=prompt_read_model_facts, read_model_visibility=read_model_visibility, strategy_memory=strategy_memory, reporter_feedback=reporter_feedback, read_model_facts=read_model_facts, facade=_r3_sys.modules[__name__])
    best_playbooks, commander_memory_policy_rebuilt, memory_packets_rebuilt, prompt_active_layers, prompt_priority_order, prompt_read_model_daily_summary_present, prompt_read_model_recent_trade_count, prompt_read_model_symbol_pattern_count, prompt_read_model_symbols, prompt_reporter_confidence, prompt_reporter_dominant_patterns, prompt_reporter_gate_reason, prompt_reporter_insight_summary, prompt_reporter_recommendations, prompt_reporter_source_reports, prompt_reporter_trade_report_analysis, prompt_symbol, recent_failures, recent_success_patterns, reconstructed_notes, reporter_feedback_rebuilt, selected_blocker, selected_playbook, selected_symbol_memory_rebuilt, selected_trade_count, selected_win_rate, strategy_requested_day, strategy_resolved_day, strategy_status, worst_playbooks = memory_feedback_best_playbooks_commander_memory_policy_r(prompt_reporter_feedback=prompt_reporter_feedback, reporter_visibility=reporter_visibility, prompt_read_model_facts=prompt_read_model_facts, read_model_visibility=read_model_visibility, prompt_commander_memory_policy=prompt_commander_memory_policy, policy_visibility=policy_visibility, reporter_feedback=reporter_feedback, selected_symbol_memory=selected_symbol_memory, prompt_selected_symbol_memory=prompt_selected_symbol_memory, memory_packets=memory_packets, prompt_memory_packets=prompt_memory_packets, commander_memory_policy=commander_memory_policy, selected_visibility=selected_visibility, prompt_symbol_packet=prompt_symbol_packet, strategy_memory=strategy_memory, strategy_visibility=strategy_visibility, facade=_r3_sys.modules[__name__])

    active_layers, priority_order, read_model_daily_summary_present, read_model_recent_trade_count, read_model_symbol_pattern_count, read_model_symbols, reporter_confidence, reporter_dominant_patterns, reporter_gate_reason, reporter_insight_summary, reporter_recommendation_count, reporter_recommendations, reporter_source_reports, reporter_status, reporter_trade_report_analysis, usage_notes = memory_status_active_layers_priority_order(read_model_facts=read_model_facts, read_model_visibility=read_model_visibility, reporter_feedback=reporter_feedback, reporter_visibility=reporter_visibility, commander_memory_policy=commander_memory_policy, policy_visibility=policy_visibility, strategy_present=strategy_present, strategy_requested_day=strategy_requested_day, strategy_resolved_day=strategy_resolved_day, best_playbooks=best_playbooks, worst_playbooks=worst_playbooks, recent_failures=recent_failures, daily_packet=daily_packet, weekly_packet=weekly_packet, monthly_packet=monthly_packet, symbol_packet=symbol_packet, packets_visibility=packets_visibility, facade=_r3_sys.modules[__name__])

    if selected_present:
        selected_parts = [f"{symbol or '해당 종목'} 종목 메모리가 들어왔습니다"]
        if selected_trade_count:
            selected_parts.append(f"과거 거래 {selected_trade_count}건")
        if selected_win_rate is not None:
            selected_parts.append(f"승률 {selected_win_rate * 100.0:.1f}%")
        if selected_playbook:
            selected_parts.append(f"우세 playbook {selected_playbook}")
        if selected_blocker:
            selected_parts.append(f"주요 blocker {selected_blocker}")
        usage_notes.append(", ".join(selected_parts) + "입니다.")
    else:
        usage_notes.append(f"{symbol or '해당 종목'} 종목 메모리는 비어 있었고, 종목별 과거 이력 제약은 직접 반영되지 않았습니다.")

    if reporter_available or reporter_consumed:
        usage_notes.append(
            f"same-day reporter feedback은 상태 {reporter_status or 'ok'} / 신뢰도 {reporter_confidence or '-'}로 전략가에 반영됐습니다."
        )
    elif reporter_present:
        usage_notes.append(
            f"same-day reporter feedback은 {reporter_status or '미사용'} 상태였고 gate 사유는 {reporter_gate_reason or '확인되지 않음'}이었습니다."
        )
    else:
        usage_notes.append("same-day reporter feedback은 이번 리포트 입력에 없었습니다.")

    if read_model_present:
        daily_summary_text = "있음" if read_model_daily_summary_present else "없음"
        usage_notes.append(
            f"read_model_facts는 최근 거래 {read_model_recent_trade_count}건, 종목 패턴 {read_model_symbol_pattern_count}건, 일일 요약 {daily_summary_text} 기준으로 들어갔습니다."
        )
        if read_model_symbols:
            usage_notes.append(
                f"read_model_facts 종목 패턴 표본은 {_join_text(read_model_symbols, max_items=5, max_len=24) or '없음'}입니다."
            )
    else:
        usage_notes.append("read_model_facts는 이번 리포트 입력에서 직접 확인되지 않았습니다.")

    if playbook or monitor_guidance or scanner_bias:
        usage_notes.append(
            f"전략가 출력에는 playbook={playbook or '-'}, monitor_guidance={monitor_guidance or '-'}, scanner_bias={scanner_bias or '-'}가 남았습니다."
        )

    return memory_status_value_result(strategy_present=strategy_present, selected_present=selected_present, read_model_present=read_model_present, strategy_status=strategy_status, strategy_requested_day=strategy_requested_day, strategy_resolved_day=strategy_resolved_day, symbol=symbol, selected_trade_count=selected_trade_count, selected_win_rate=selected_win_rate, selected_playbook=selected_playbook, selected_blocker=selected_blocker, reporter_present=reporter_present, reporter_available=reporter_available, reporter_consumed=reporter_consumed, reporter_status=reporter_status, reporter_gate_reason=reporter_gate_reason, reporter_confidence=reporter_confidence, reporter_recommendation_count=reporter_recommendation_count, reporter_insight_summary=reporter_insight_summary, read_model_recent_trade_count=read_model_recent_trade_count, read_model_symbol_pattern_count=read_model_symbol_pattern_count, read_model_daily_summary_present=read_model_daily_summary_present, playbook=playbook, monitor_guidance=monitor_guidance, scanner_bias=scanner_bias, best_playbooks=best_playbooks, worst_playbooks=worst_playbooks, recent_failures=recent_failures, recent_success_patterns=recent_success_patterns, active_layers=active_layers, priority_order=priority_order, read_model_symbols=read_model_symbols, prompt_strategy_present=prompt_strategy_present, prompt_selected_present=prompt_selected_present, prompt_reporter_present=prompt_reporter_present, prompt_reporter_available=prompt_reporter_available, prompt_reporter_consumed=prompt_reporter_consumed, prompt_read_model_present=prompt_read_model_present, prompt_strategy_status=prompt_strategy_status, prompt_strategy_requested_day=prompt_strategy_requested_day, prompt_strategy_resolved_day=prompt_strategy_resolved_day, prompt_symbol=prompt_symbol, prompt_selected_trade_count=prompt_selected_trade_count, prompt_selected_win_rate=prompt_selected_win_rate, prompt_selected_playbook=prompt_selected_playbook, prompt_selected_blocker=prompt_selected_blocker, prompt_reporter_status=prompt_reporter_status, prompt_reporter_gate_reason=prompt_reporter_gate_reason, prompt_reporter_confidence=prompt_reporter_confidence, prompt_reporter_insight_summary=prompt_reporter_insight_summary, prompt_read_model_recent_trade_count=prompt_read_model_recent_trade_count, prompt_read_model_symbol_pattern_count=prompt_read_model_symbol_pattern_count, prompt_read_model_daily_summary_present=prompt_read_model_daily_summary_present, selected_symbol_memory_rebuilt=selected_symbol_memory_rebuilt, reporter_feedback_rebuilt=reporter_feedback_rebuilt, memory_packets_rebuilt=memory_packets_rebuilt, commander_memory_policy_rebuilt=commander_memory_policy_rebuilt, reconstructed_notes=reconstructed_notes, usage_notes=usage_notes, commander_memory_policy=commander_memory_policy, prompt_best_playbooks=prompt_best_playbooks, prompt_worst_playbooks=prompt_worst_playbooks, prompt_recent_failures=prompt_recent_failures, prompt_recent_success_patterns=prompt_recent_success_patterns, prompt_active_layers=prompt_active_layers, prompt_priority_order=prompt_priority_order, prompt_read_model_symbols=prompt_read_model_symbols, daily_packet=daily_packet, weekly_packet=weekly_packet, monthly_packet=monthly_packet, symbol_packet=symbol_packet, reporter_dominant_patterns=reporter_dominant_patterns, reporter_recommendations=reporter_recommendations, recent_feedback_visibility=recent_feedback_visibility, prompt_memory_packets=prompt_memory_packets, packets_visibility=packets_visibility, prompt_commander_memory_policy=prompt_commander_memory_policy, policy_visibility=policy_visibility, reporter_source_reports=reporter_source_reports, reporter_trade_report_analysis=reporter_trade_report_analysis, prompt_daily_packet=prompt_daily_packet, prompt_weekly_packet=prompt_weekly_packet, prompt_monthly_packet=prompt_monthly_packet, prompt_symbol_packet=prompt_symbol_packet, prompt_reporter_dominant_patterns=prompt_reporter_dominant_patterns, prompt_reporter_recommendations=prompt_reporter_recommendations, prompt_reporter_source_reports=prompt_reporter_source_reports, prompt_reporter_trade_report_analysis=prompt_reporter_trade_report_analysis, facade=_r3_sys.modules[__name__])


__all__ = ["build_trade_report_memory_surface"]
