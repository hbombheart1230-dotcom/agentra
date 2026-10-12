"""Behavior-preserving R3 implementation bodies moved from the public facade.

Each function keeps its original body. Names it used as facade module globals are
read from the injected `facade` module at call entry (explicit names, no getattr
fallback), preserving monkeypatch semantics. Owner never imports the facade.
"""
from __future__ import annotations


def _build_strategist_refresh_trace_r3_impl(report, *, facade):
    _dedupe = facade._dedupe
    _listify = facade._listify
    _resolve_strategy_refresh_trace = facade._resolve_strategy_refresh_trace
    _strategy_output_list_text = facade._strategy_output_list_text
    _strategy_output_text = facade._strategy_output_text
    trace = _resolve_strategy_refresh_trace(report)
    if not trace:
        return []

    lines: List[str] = []
    summary = _strategy_output_text(trace.get("summary"), max_len=420)
    if summary:
        lines.append(summary)

    stage_rows = [row for row in _listify(trace.get("stages")) if isinstance(row, dict)]
    if stage_rows:
        for idx, row in enumerate(stage_rows[:4], start=1):
            label = _strategy_output_text(row.get("label"), max_len=80) or f"{idx}단계"
            stage_summary = _strategy_output_text(row.get("summary"), max_len=260)
            details: List[str] = []
            reason = _strategy_output_text(row.get("reason"), max_len=120)
            selected_symbol = _strategy_output_text(row.get("selected_symbol"), max_len=40)
            if row.get("requested") is not None:
                details.append(f"요청={bool(row.get('requested'))}")
            if row.get("evaluated") is not None:
                details.append(f"평가={bool(row.get('evaluated'))}")
            if row.get("effective") is not None:
                details.append(f"반영={bool(row.get('effective'))}")
            if selected_symbol:
                details.append(f"대상={selected_symbol}")
            if reason:
                details.append(f"사유={reason}")
            line = f"- [{label}] {stage_summary or '기록된 요약 없음'}"
            if details:
                line += f" ({'; '.join(details)})"
            lines.append(line)
    else:
        for raw in _listify(trace.get("bullets")):
            text = _strategy_output_text(raw, max_len=260)
            if text:
                lines.append(f"- {text}")

    delta_count = trace.get("policy_delta_count")
    delta_fields = _strategy_output_list_text(trace.get("policy_delta_fields"), limit=6)
    if delta_count is not None or delta_fields:
        delta_text = f"정책 delta count={delta_count if delta_count is not None else '-'}"
        if delta_fields:
            delta_text += f", fields={delta_fields}"
        lines.append(f"- [최종 정책 변화] {delta_text}")

    return _dedupe(lines)


def _build_execution_quality_r3_impl(report, *, facade):
    _as_dict = facade._as_dict
    _fmt_pct = facade._fmt_pct
    _fmt_price = facade._fmt_price
    _get_truth_surface = facade._get_truth_surface
    _metadata_value = facade._metadata_value
    _truth_source_label = facade._truth_source_label
    truth = _get_truth_surface(report)
    price = _as_dict(truth.get("price"))
    pnl = _as_dict(truth.get("pnl"))
    lines: List[str] = []
    sell_price = price.get("broker_fill_price")
    if sell_price not in (None, ""):
        lines.append(f"- 브로커 체결 기준 가격은 {_fmt_price(sell_price)}였습니다.")
    if pnl.get("value") not in (None, "", "unavailable") and pnl.get("pct") not in (None, ""):
        lines.append(f"- 브로커 실현 손익은 {pnl.get('value')} / {_fmt_pct(pnl.get('pct'))} 기준으로 정리했습니다.")
    if pnl.get("broker_fee") not in (None, "") or pnl.get("broker_tax") not in (None, ""):
        lines.append(
            f"- 브로커 수수료/세금은 {pnl.get('broker_fee') if pnl.get('broker_fee') not in (None, '') else '-'} / "
            f"{pnl.get('broker_tax') if pnl.get('broker_tax') not in (None, '') else '-'}였습니다."
        )
    if _as_dict(report.get("execution_details")).get("broker_truth_source"):
        lines.append(f"- 체결 truth 소스는 {_metadata_value(_as_dict(report.get('execution_details')).get('broker_truth_source'))}였습니다.")
    lines.append(f"- 가격 truth 소스는 {_truth_source_label(price.get('price_truth_source'))}으로 확인했습니다.")
    lines.append(f"- 손익 truth 소스는 {_truth_source_label(pnl.get('pnl_truth_source'))}으로 확인했습니다.")
    return lines


def _humanize_reporter_pattern_r3_impl(name, detail, value, *, facade):
    _clip = facade._clip
    _fmt_pct = facade._fmt_pct
    _num_opt = facade._num_opt
    _translate_text = facade._translate_text
    re = facade.re
    raw_name = _clip(name, 80)
    raw_detail = _clip(detail, 160)
    if raw_name == "freshness_status":
        return ""
    if raw_name == "closed_trade_count" or raw_detail.startswith("closed trade reports"):
        count = _num_opt(value)
        if count is None:
            match = re.search(r"(\d+)", raw_detail)
            count = float(match.group(1)) if match else None
        return f"당일 닫힌 거래는 {int(count)}건이었습니다." if count is not None else ""
    if raw_name == "avg_pnl_pct" or raw_detail.startswith("average same-day pnl pct"):
        pct = _num_opt(value)
        if pct is None:
            match = re.search(r"(-?\d+(?:\.\d+)?)", raw_detail)
            pct = float(match.group(1)) if match else None
        return f"당일 평균 손익률은 {_fmt_pct(pct)}였습니다." if pct is not None else ""
    if m := re.fullmatch(r"(monitor_only|cached_strategist|full_cycle)\s+(\d+)/(\d+)\s+runs", raw_detail, re.I):
        label = {
            "monitor_only": "모니터 단독 경로",
            "cached_strategist": "기존 전략가 재사용 경로",
            "full_cycle": "전체 재평가 경로",
        }.get(m.group(1).lower(), m.group(1))
        return f"{label}가 전체 {m.group(3)}회 중 {m.group(2)}회로 반복됐습니다."
    if m := re.fullmatch(r"(.+?)\s+(\d+)/(\d+)", raw_detail):
        return f"{m.group(1)} 패턴이 전체 {m.group(3)}회 중 {m.group(2)}회였습니다."
    if raw_detail:
        return _translate_text(raw_detail)
    return _translate_text(raw_name)


def _build_reporter_evaluation_r3_impl(report, *, facade):
    _as_dict = facade._as_dict
    _bullet_lines = facade._bullet_lines
    _dedupe = facade._dedupe
    _first_nonempty = facade._first_nonempty
    _fmt_pct = facade._fmt_pct
    _get_truth_surface = facade._get_truth_surface
    _humanize_reporter_pattern = facade._humanize_reporter_pattern
    _humanize_reporter_recommendation = facade._humanize_reporter_recommendation
    _humanize_reporter_source_label = facade._humanize_reporter_source_label
    _listify = facade._listify
    _num_opt = facade._num_opt
    _section_summary = facade._section_summary
    reporter_eval = _as_dict(report.get("reporter_evaluation"))
    memory = _as_dict(report.get("memory_surface"))
    packet = _as_dict(memory.get("reporter_feedback_packet"))
    lines: List[str] = []

    if packet.get("available"):
        truth = _get_truth_surface(report)
        pnl = _as_dict(truth.get("pnl"))
        pnl_value = _num_opt(pnl.get("value"))
        if pnl_value is not None:
            if pnl_value > 0:
                trade_result = "수익으로 마감한"
            elif pnl_value < 0:
                trade_result = "손실로 마감한"
            else:
                trade_result = "손익이 거의 없었던"
        else:
            trade_result = "손익을 직접 판단하기 어려운"

        analysis = _as_dict(packet.get("trade_report_analysis"))
        closed_count = analysis.get("closed_trade_count")
        win_count = analysis.get("win_count")
        loss_count = analysis.get("loss_count")
        avg_pnl_pct = analysis.get("avg_pnl_pct")
        source_label = _humanize_reporter_source_label(_as_dict(packet.get("source_reports")))
        lines.append(f"이번 거래는 {trade_result} 흐름이었고, 당일 리포터는 이를 같은 날 반복 패턴 속에서 보조 평가했습니다.")
        lines.append(
            f"- 리포터 소스는 {source_label}였고, 당일 닫힌 거래 {closed_count if closed_count not in (None, '') else '-'}건 중 "
            f"승리 {win_count if win_count not in (None, '') else '-'} / 손실 {loss_count if loss_count not in (None, '') else '-'}, "
            f"평균 손익률 {_fmt_pct(avg_pnl_pct)}였습니다."
        )
        pattern_rows: List[str] = []
        for item in _listify(packet.get("dominant_patterns"))[:3]:
            row = _as_dict(item)
            if row.get("name"):
                humanized = _humanize_reporter_pattern(row.get("name"), row.get("detail"), row.get("value"))
                if humanized:
                    pattern_rows.append(humanized.rstrip("."))
        if pattern_rows:
            lines.append(f"- 당일 반복 패턴 요약: {' / '.join(pattern_rows)}.")
        recommendation = _humanize_reporter_recommendation(_first_nonempty(_listify(packet.get("recommendation"))))
        if recommendation:
            lines.append(f"- 리포터 권고: {recommendation}")
        return lines

    summary = _section_summary(reporter_eval)
    if summary:
        lines.append(summary)
    for bullet in _bullet_lines(reporter_eval):
        lines.append(bullet)
    return _dedupe(lines)


def _build_weaknesses_r3_impl(report, *, facade):
    _as_dict = facade._as_dict
    _bullet_lines = facade._bullet_lines
    _dedupe = facade._dedupe
    _section_summary = facade._section_summary
    section = _as_dict(report.get("errors_weaknesses_improvement_points"))
    reporter_eval = _as_dict(report.get("reporter_evaluation"))
    memory = _as_dict(report.get("memory_surface"))
    reporter_packet = _as_dict(memory.get("reporter_feedback_packet"))
    reporter_ready = reporter_eval.get("status") == "ok" or reporter_packet.get("available")
    lines: List[str] = []
    summary = _section_summary(section)
    if summary:
        if summary == "Warnings and missing links were recorded for operator follow-up.":
            lines.append("운영자 후속 확인이 필요한 취약 지점을 정리했습니다.")
        else:
            lines.append(summary)
    for bullet in _bullet_lines(section):
        if reporter_ready and "동일 일자 리포터 분석이 아직 이 거래 생애주기에 연결되지 않았습니다." in bullet:
            continue
        lines.append(bullet)
    deduped = _dedupe(lines)
    if len(deduped) <= 3:
        return deduped
    compact = [deduped[0]]
    compact.extend(deduped[1:3])
    if len(deduped) > 3:
        compact.append("- 추가 취약 지점은 저장된 보완 사안 원문에 남겨 두었습니다.")
    return _dedupe(compact)


def _build_provenance_r3_impl(report, *, facade):
    _as_dict = facade._as_dict
    _clip = facade._clip
    _dedupe = facade._dedupe
    _extract_metadata_from_texts = facade._extract_metadata_from_texts
    _listify = facade._listify
    _metadata_value = facade._metadata_value
    lines: List[str] = []
    for section_name, row in _as_dict(report.get("section_provenance")).items():
        item = _as_dict(row)
        if item.get("source"):
            lines.append(f"- 데이터 출처: {_metadata_value(item.get('source'))}")
        if item.get("artifact_path"):
            lines.append(f"- 참조 경로: {item.get('artifact_path')}")
        if item.get("confidence"):
            lines.append(f"- 신뢰도: {_metadata_value(item.get('confidence'))}")
    texts: List[str] = []
    for key in ("market_context_at_entry", "strategist_summary", "why_this_symbol_was_chosen"):
        section = _as_dict(report.get(key))
        texts.extend([_clip(section.get("summary"), 400)])
        texts.extend(_listify(section.get("bullets")))
    lines.extend(_extract_metadata_from_texts(texts))
    generation = _as_dict(report.get("generation"))
    if generation.get("reason"):
        lines.append(f"- 생성 상태: {_metadata_value(generation.get('status') or '-')}")
        lines.append(f"- 생성 사유: {_metadata_value(generation.get('reason'))}")
    return _dedupe(lines)
