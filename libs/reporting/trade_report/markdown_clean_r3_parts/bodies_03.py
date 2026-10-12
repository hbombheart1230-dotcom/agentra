"""Behavior-preserving R3 implementation bodies moved from the public facade.

Each function keeps its original body except that every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module, no getattr fallback,
no entry-time capture), so late/use-time lookup and monkeypatching match the original
module-level resolution. Owner never imports the facade.
"""
from __future__ import annotations


def _reason_tag_summary_r3_impl(tag, *, facade):
    raw = facade._clip(tag, 160)
    lower = raw.lower()
    mapping = {
        "daily_strategy_memory_available": "당일 전략 메모리를 사용할 수 있었습니다",
        "daily_prefers_pullback_or_defensive": "당일 메모리는 눌림목/방어형 접근을 선호했습니다",
        "scanner_bias_disabled": "메모리 bias가 비활성화되어 점수 조정에 쓰이지 않았습니다",
        "monitor_bias_disabled": "메모리 bias가 비활성화되어 진입/청산 정책 조정에 쓰이지 않았습니다",
        "commander_monitor_status:stable": "모니터 상태는 안정적이었습니다",
        "commander_focus:exit_quality": "지휘관은 청산 품질 점검을 우선했습니다",
        "commander_focus:guard_blocks": "지휘관은 가드 차단 패턴 점검을 우선했습니다",
        "commander_focus:scanner_fit": "지휘관은 스캐너 적합도 점검을 우선했습니다",
        "symbol_blocker:unknown": "종목별 반복 차단 패턴은 아직 뚜렷하지 않았습니다",
    }
    if lower in mapping:
        return mapping[lower]
    if lower.startswith("daily_best:"):
        return f"당일 메모리는 {facade._playbook_label(lower.split(':', 1)[1])} 전략 프레임을 우세 신호로 봤습니다"
    if lower.startswith("daily_failure:playbook:"):
        return f"당일 메모리에는 {facade._playbook_label(lower.split(':', 2)[2])} 전략 프레임 실패 흔적이 남았습니다"
    if lower.startswith("commander_risk_posture:"):
        return f"지휘관 위험 자세는 {facade._playbook_label(lower.split(':', 1)[1])}이었습니다"
    if lower.startswith("symbol_playbook:"):
        return f"종목 메모리는 {facade._playbook_label(lower.split(':', 1)[1])} 접근 이력을 보였습니다"
    return facade._metadata_value(tag) or "-"


def _resolve_prompt_proven_surface_r3_impl(memory, *, facade):
    prompt = facade._as_dict(memory.get("prompt_proven"))
    if prompt:
        return prompt
    strategy_memory = facade._as_dict(memory.get("strategy_memory"))
    memory_packets = facade._as_dict(memory.get("memory_packets"))
    commander_memory_policy = facade._as_dict(memory.get("commander_memory_policy"))
    selected_symbol_memory = facade._as_dict(memory.get("selected_symbol_memory"))
    reporter_feedback_packet = facade._as_dict(memory.get("reporter_feedback_packet"))
    read_model_facts = facade._as_dict(memory.get("read_model_facts"))
    selected_trade_count = facade._num_opt(selected_symbol_memory.get("trade_count"))
    recent_trade_count = facade._num_opt(read_model_facts.get("recent_trade_count"))
    symbol_pattern_count = facade._num_opt(read_model_facts.get("symbol_pattern_count"))

    strategy_memory_present = bool(
        strategy_memory.get("present")
        or strategy_memory.get("status")
        or facade._listify(strategy_memory.get("best_playbooks"))
        or facade._listify(strategy_memory.get("worst_playbooks"))
        or facade._listify(strategy_memory.get("recent_failures"))
    )
    commander_memory_policy_present = bool(
        commander_memory_policy.get("present")
        or facade._listify(commander_memory_policy.get("active_layers"))
        or facade._listify(commander_memory_policy.get("priority_order"))
        or commander_memory_policy.get("application_mode")
    )
    selected_symbol_memory_present = bool(
        selected_symbol_memory.get("present")
        or (selected_trade_count is not None and selected_trade_count > 0)
        or selected_symbol_memory.get("dominant_playbook")
        or selected_symbol_memory.get("dominant_monitor_blocker")
    )
    reporter_feedback_present = bool(
        reporter_feedback_packet.get("present")
        or reporter_feedback_packet.get("available")
        or reporter_feedback_packet.get("status")
        or reporter_feedback_packet.get("confidence")
        or facade._as_dict(reporter_feedback_packet.get("source_reports"))
        or facade._as_dict(reporter_feedback_packet.get("trade_report_analysis"))
        or facade._listify(reporter_feedback_packet.get("recommendation"))
    )
    read_model_facts_present = bool(
        read_model_facts.get("present")
        or (recent_trade_count is not None and recent_trade_count > 0)
        or (symbol_pattern_count is not None and symbol_pattern_count > 0)
        or read_model_facts.get("daily_summary_present")
        or facade._listify(read_model_facts.get("symbols"))
    )
    return {
        "status": {
            "strategy_memory_present": strategy_memory_present,
            "memory_packets_present": bool(memory_packets),
            "commander_memory_policy_present": commander_memory_policy_present,
            "selected_symbol_memory_present": selected_symbol_memory_present,
            "reporter_feedback_present": reporter_feedback_present,
            "reporter_feedback_available": bool(reporter_feedback_packet.get("available")),
            "reporter_feedback_consumed": bool(reporter_feedback_packet.get("consumed")),
            "read_model_facts_present": read_model_facts_present,
        },
        "strategy_memory": strategy_memory,
        "memory_packets": memory_packets,
        "commander_memory_policy": commander_memory_policy,
        "selected_symbol_memory": selected_symbol_memory,
        "reporter_feedback_packet": reporter_feedback_packet,
        "read_model_facts": read_model_facts,
    }


def _build_reconstructed_trade_memory_r3_impl(report, *, facade):
    memory = facade._as_dict(report.get("memory_surface"))
    if not memory:
        return []
    reconstructed = facade._resolve_reconstructed_memory_surface(memory)
    status = facade._as_dict(reconstructed.get("status"))
    selected = facade._as_dict(reconstructed.get("selected_symbol_memory"))
    reporter = facade._as_dict(reconstructed.get("reporter_feedback_packet"))
    policy = facade._as_dict(reconstructed.get("commander_memory_policy"))
    lines: List[str] = []
    symbol = facade._metadata_value(report.get("symbol") or selected.get("symbol") or "target_symbol")

    lines.append(f"- {facade._badge('사후 복원', '#7c3aed')} 실행 기록을 다시 읽어 {symbol} 거래 설명에 필요한 메모리만 보강했습니다.")

    if any(bool(status.get(key)) for key in status):
        lines.append(f"- 전략가 원본 프롬프트 밖의 거래 레벨 메모리를 기준으로 {symbol} 거래 문맥을 보강했습니다.")
    else:
        lines.append("- 이 거래는 전략가 프롬프트만으로 대부분 설명돼, 사후 메모리 복원은 크지 않았습니다.")

    if bool(status.get("selected_symbol_memory_rebuilt")) and selected.get("present"):
        trade_count = selected.get("trade_count") if selected.get("trade_count") not in (None, "") else "-"
        win_rate = selected.get("win_rate")
        lines.append(
            f"- {symbol} 종목 메모리는 저장된 종목 메모리에서 다시 읽었고, 과거 거래 {trade_count}건, 승률 {facade._fmt_pct(win_rate) if win_rate not in (None, '') else '-'}였습니다."
        )

    if bool(status.get("reporter_feedback_rebuilt")) and reporter.get("available"):
        source_label = facade._humanize_reporter_source_label(facade._as_dict(reporter.get("source_reports")))
        analysis = facade._as_dict(reporter.get("trade_report_analysis"))
        lines.append(
            f"- 당일 리포터 피드백은 {source_label}를 기준으로 다시 구성했고, 닫힌 거래 {analysis.get('closed_trade_count') if analysis.get('closed_trade_count') not in (None, '') else '-'}건 집계를 반영했습니다."
        )
        recommendation = ""
        for item in facade._listify(reporter.get("recommendation")):
            recommendation = facade._humanize_reporter_recommendation(item)
            if recommendation:
                break
        if recommendation:
            lines.append(f"- 사후 복원된 리포터 권고는 {facade._ensure_sentence(recommendation)}")

    if bool(status.get("memory_packets_rebuilt")):
        lines.append("- 전략가 원본 프롬프트에 메모리 묶음 세부 정보가 부족해, 실행 시점 메모리 묶음 문맥을 다시 구성했습니다.")
    if bool(status.get("commander_memory_policy_rebuilt")):
        lines.append(
            f"- 지휘관 메모리 정책도 실행 기록을 기준으로 다시 구성했고, 실제 반영 레이어는 {facade._memory_layers_text(policy.get('active_layers'))}으로 확인됐습니다."
        )

    if any(bool(status.get(key)) for key in status):
        lines.append("- 전략가 원본 프롬프트를 옮긴 내용이 아니라, 거래 설명용으로 사후 복원한 메모리 레이어입니다.")
    return lines


def _market_context_structured_lines_r3_impl(context, *, facade):
    lines: List[str] = []
    for raw in facade._listify(context.get("bullets")):
        raw_text = facade._clip(raw, 240)
        if not raw_text:
            continue
        lowered = raw_text.lower()
        if lowered.startswith("global sentiment "):
            value = raw_text.split(" ", 2)[-1].strip()
            lines.append(f"- 시장 심리 수치는 {value}입니다.")
            continue
        if lowered.startswith("global_sentiment score="):
            match = facade.re.search(r"score=([-+]?\\d+(?:\\.\\d+)?)", raw_text, facade.re.I)
            if match:
                lines.append(f"- 시장 심리 수치는 {match.group(1)}입니다.")
            continue
        if lowered.startswith("vix "):
            lines.append(f"- {raw_text}")
            continue
        if lowered.startswith("stress flags:"):
            flags = raw_text.split(":", 1)[1].strip()
            if flags:
                lines.append(f"- 스트레스 신호는 {flags}입니다.")
            continue
        if lowered.startswith("news input:"):
            match = facade.re.search(
                r"(\d+)\s+headlines were considered across\s+(\d+)\s+targets\s+\((\d+)\s+market\s*/\s*(\d+)\s+candidate signals\)\.?",
                raw_text,
                facade.re.I,
            )
            if match:
                lines.append(
                    f"- 뉴스 입력은 {match.group(2)}개 타깃에서 {match.group(1)}개 headline을 검토했고, 시장 {match.group(3)}건 / 후보 {match.group(4)}건 신호를 반영했습니다."
                )
            else:
                lines.append(f"- 뉴스 입력 요약: {raw_text.split(':', 1)[1].strip()}")
            continue
    return lines


def _resolve_strategist_output_surface_r3_impl(report, *, facade):
    direct = facade._as_dict(report.get("strategist_output") or report.get("strategist_output_surface"))
    if direct:
        return direct
    strategist = facade._as_dict(report.get("strategist_summary"))
    nested = facade._as_dict(strategist.get("strategist_output"))
    if nested:
        return nested
    visibility = facade._resolve_entry_execution_visibility(report)
    proposal = facade._as_dict(visibility.get("strategy_candidate_watch_proposal"))
    entry_control = facade._as_dict(visibility.get("commander_entry_control"))
    if not proposal and not entry_control:
        return {}

    strategy_detail: Dict[str, Any] = {}
    tactical = facade._metadata_value(proposal.get("tactical_strategy"))
    if tactical and tactical != "-":
        strategy_detail["tactical_strategy"] = tactical
    if proposal:
        strategy_detail["candidate_watch_policy"] = proposal

    thesis: Dict[str, Any] = {}
    playbook = facade._metadata_value(
        strategist.get("selected_playbook")
        or strategist.get("playbook")
        or facade._as_dict(report.get("market_context")).get("selected_playbook")
    )
    risk_tone = facade._metadata_value(
        strategist.get("risk_tone")
        or facade._as_dict(report.get("market_context")).get("risk_mode")
        or facade._as_dict(report.get("market_context")).get("risk_tone")
    )
    if playbook and playbook != "-":
        thesis["selected_playbook"] = playbook
    if risk_tone and risk_tone != "-":
        thesis["risk_tone"] = risk_tone

    out: Dict[str, Any] = {}
    if thesis:
        out["strategy_thesis"] = thesis
    if strategy_detail:
        out["strategy_detail"] = strategy_detail
    return out
