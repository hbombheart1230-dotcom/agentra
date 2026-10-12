"""Markdown-clean memory/policy/scanner/monitor phase lines and reconstructed memory surface (read-only text composition).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _memory_layer_label_r3_impl(value, *, facade):
    raw = facade._clip(value, 80).lower()
    mapping = {
        "daily": "당일",
        "weekly": "주간",
        "monthly": "월간",
        "symbol": "종목",
    }
    return mapping.get(raw, facade._metadata_value(value) or "-")


def _memory_status_label_r3_impl(value, *, facade):
    raw = facade._clip(value, 80).lower()
    mapping = {
        "ok": "정상 기록",
        "not_recorded": "미기록",
        "missing": "미기록",
        "empty": "비어 있음",
        "auto_ignored": "자동 제외",
        "error": "오류",
    }
    return mapping.get(raw, facade._metadata_value(value) or "-")


def _memory_layers_text_r3_impl(values, *, arrow, humanize, facade):
    items = [str(x).strip() for x in facade._listify(values) if str(x).strip()]
    if not items:
        return "-"
    if humanize:
        items = [facade._memory_layer_label(x) for x in items]
    return " -> ".join(items) if arrow else ", ".join(items)


def _memory_packet_state_line_r3_impl(name, packet, *, facade):
    status = facade._memory_status_label(packet.get("status") or "not_recorded")
    parts = [status]
    sample_day_count = packet.get("sample_day_count")
    if name in {"weekly", "monthly"} and sample_day_count not in (None, ""):
        parts.append(f"{sample_day_count}days")
    parts.append("활성" if packet.get("active") else "보조 참고")
    return f"{facade._memory_layer_label(name)}=" + ", ".join(parts)


def _policy_phase_line_r3_impl(label, policy, *, facade):
    active_layers = facade._memory_layers_text(policy.get("active_layers"))
    priority_order = facade._memory_layers_text(policy.get("priority_order"), arrow=True)
    scanner_bias = facade._on_off_label(policy.get("scanner_bias_enabled"))
    monitor_bias = facade._on_off_label(policy.get("monitor_bias_enabled"))
    symbol_override = facade._on_off_label(policy.get("symbol_memory_override_enabled"))
    application_mode = facade._metadata_value(policy.get("application_mode") or "-")
    return (
        f"- [{label}] 활성 레이어={active_layers}; 우선순위={priority_order}; "
        f"scanner bias={scanner_bias}; monitor bias={monitor_bias}; "
        f"symbol override={symbol_override}; 적용 모드={application_mode}."
    )


def _same_policy_snapshot_r3_impl(left, right, *, facade):
    keys = (
        "active_layers",
        "priority_order",
        "scanner_bias_enabled",
        "monitor_bias_enabled",
        "symbol_memory_override_enabled",
        "application_mode",
    )
    return all(left.get(key) == right.get(key) for key in keys)


def _scanner_phase_line_r3_impl(scanner, *, facade):
    source = facade._metadata_value(scanner.get("source") or "-")
    active_layers = facade._memory_layers_text(scanner.get("active_layers"))
    not_applied = facade._metadata_value(scanner.get("not_applied_reason") or "")
    suffix = f"; 미적용 사유={not_applied}" if not_applied else ""
    return (
        f"- [스캐너 적용 시점] captured={facade._on_off_label(scanner.get('captured'))}; "
        f"enabled={facade._on_off_label(scanner.get('enabled'))}; "
        f"applied={facade._applied_label(scanner.get('applied'))}; "
        f"active_layers={active_layers}; source={source}{suffix}."
    )


def _monitor_phase_line_r3_impl(monitor, *, facade):
    source = facade._metadata_value(monitor.get("source") or "-")
    active_layers = facade._memory_layers_text(monitor.get("active_layers"))
    not_applied = facade._metadata_value(monitor.get("not_applied_reason") or "")
    suffix = f"; 미적용 사유={not_applied}" if not_applied else ""
    return (
        f"- [모니터 적용 시점] captured={facade._on_off_label(monitor.get('captured'))}; "
        f"enabled={facade._on_off_label(monitor.get('enabled'))}; "
        f"entry={facade._applied_label(monitor.get('applied'))}; "
        f"hold={facade._applied_label(monitor.get('hold_applied'))}; "
        f"exit={facade._applied_label(monitor.get('exit_applied'))}; "
        f"active_layers={active_layers}; source={source}{suffix}."
    )


def _resolve_reconstructed_memory_surface_r3_impl(memory, *, facade):
    reconstructed = facade._as_dict(memory.get("reconstructed_trade_context"))
    if reconstructed:
        return reconstructed
    return {
        "status": {
            "selected_symbol_memory_rebuilt": False,
            "reporter_feedback_rebuilt": False,
            "memory_packets_rebuilt": False,
            "commander_memory_policy_rebuilt": False,
        },
        "selected_symbol_memory": dict(facade._as_dict(memory.get("selected_symbol_memory")), rebuilt=False, source="prompt_proven"),
        "reporter_feedback_packet": dict(facade._as_dict(memory.get("reporter_feedback_packet")), rebuilt=False, source="prompt_proven"),
        "memory_packets": {"rebuilt": False, "source": "prompt_proven"},
        "commander_memory_policy": dict(facade._as_dict(memory.get("commander_memory_policy")), rebuilt=False, source="prompt_proven"),
        "notes": [],
    }


def _build_generation_info_r3_impl(report, *, facade):
    generation = facade._as_dict(report.get("generation"))
    lines = [
        f"- 생성 상태: {facade._metadata_value(generation.get('status') or '-')}",
        f"- 생성 방식: {facade._metadata_value(generation.get('mode') or '-')}",
        f"- 사용 모델: {facade._metadata_value(generation.get('model') or '-')}",
    ]
    if report.get("generated_at"):
        lines.append(f"- 생성 시각: {facade._clip(report.get('generated_at'), 80)}")
    reason = facade._metadata_value(generation.get("reason"))
    if reason:
        lines.append(f"- 생성 사유: {reason}")
    return lines


def _is_closed_trade_context_r3_impl(report, *, facade):
    status = facade._clip(report.get("status"), 20).lower()
    if status == "closed":
        return True
    shared = facade._as_dict(report.get("shared_facts"))
    monitor = facade._as_dict(report.get("monitor_snapshot"))
    action = facade._clip(shared.get("action") or report.get("action"), 20).upper()
    if action == "SELL" and monitor.get("trigger_type"):
        return True
    return False


def _strategy_output_layer_bits_r3_impl(layer_decisions, *, facade):
    decisions = facade._as_dict(layer_decisions)
    bits: List[str] = []
    for layer, row in list(decisions.items())[:4]:
        item = facade._as_dict(row)
        used = "used" if bool(item.get("used")) else "not_used"
        gate = facade._strategy_output_text(
            item.get("gate_reason") or item.get("reason") or item.get("status"),
            max_len=80,
        )
        bits.append(f"{layer}={used}" + (f"/{gate}" if gate else ""))
    return ", ".join(bits)
