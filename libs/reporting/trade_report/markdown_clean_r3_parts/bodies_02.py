"""Behavior-preserving R3 implementation bodies moved from the public facade.

Each function keeps its original body. Names it used as facade module globals are
read from the injected `facade` module at call entry (explicit names, no getattr
fallback), preserving monkeypatch semantics. Owner never imports the facade.
"""
from __future__ import annotations


def _selection_fallback_context_r3_impl(selection, traded_symbol, *, facade):
    _as_dict = facade._as_dict
    _metadata_value = facade._metadata_value
    _translate_reason_phrase = facade._translate_reason_phrase
    section = _as_dict(selection)
    trace = _as_dict(section.get("scanner_selection_trace"))
    selected_symbol = _metadata_value(
        traded_symbol
        or section.get("symbol")
        or trace.get("monitor_selected_symbol")
        or trace.get("selected_symbol")
    )
    top_pick = _metadata_value(section.get("scanner_top_pick_symbol") or trace.get("scanner_top_pick_symbol"))
    used = bool(section.get("monitor_fallback_used") or trace.get("monitor_fallback_used"))
    if not top_pick or top_pick == "-":
        used = False
    if top_pick and selected_symbol and top_pick == selected_symbol:
        used = False
    reason_raw = section.get("monitor_fallback_reason") or trace.get("monitor_fallback_reason") or trace.get("monitor_trigger_reason")
    reason = _translate_reason_phrase(str(reason_raw or "")) if reason_raw else ""
    return {
        "used": used,
        "selected_symbol": selected_symbol,
        "scanner_top_pick_symbol": top_pick if top_pick != "-" else "",
        "reason": reason,
        "selection_path": _metadata_value(section.get("selection_path") or trace.get("selection_path")),
    }


def _candidate_cascade_symbols_r3_impl(cascade, *, facade):
    _as_dict = facade._as_dict
    _display_candidate_symbol = facade._display_candidate_symbol
    _listify = facade._listify
    symbols: set[str] = set()

    def add(value: Any) -> None:
        symbol = _display_candidate_symbol(value)
        if symbol:
            symbols.add(symbol)

    for key in (
        "top_pick_symbol",
        "fallback_from_symbol",
        "fallback_to_symbol",
        "final_selected_symbol",
    ):
        add(cascade.get(key))
    for key in ("runner_up_symbols", "candidate_symbols"):
        for value in _listify(cascade.get(key)):
            add(value)
    for row in _listify(cascade.get("fallback_trace")):
        row_obj = _as_dict(row)
        add(row_obj.get("symbol"))
    return symbols


def _resolve_market_context_r3_impl(report, *, facade):
    _as_dict = facade._as_dict
    _has_payload = facade._has_payload
    _merge_preferred = facade._merge_preferred
    primary = _as_dict(report.get("market_context_at_entry"))
    fallback = _as_dict(report.get("market_context_human"))
    trace = _as_dict(report.get("strategist_trace_summary"))
    feedback = _as_dict(report.get("strategist_feedback_input"))
    merged = _merge_preferred(primary, fallback)

    for key in ("summary", "playbook", "themes", "headline_count", "news_query_count"):
        if not _has_payload(merged.get(key)) and _has_payload(trace.get(key)):
            merged[key] = trace.get(key)
    if not _has_payload(merged.get("regime")) and _has_payload(trace.get("market_regime")):
        merged["regime"] = trace.get("market_regime")
    if not _has_payload(merged.get("market_sentiment")) and _has_payload(trace.get("market_sentiment")):
        merged["market_sentiment"] = trace.get("market_sentiment")
    if not _has_payload(merged.get("global_sentiment_score")) and _has_payload(trace.get("global_sentiment_score")):
        merged["global_sentiment_score"] = trace.get("global_sentiment_score")
    if not _has_payload(merged.get("vix_level")) and _has_payload(trace.get("vix_level")):
        merged["vix_level"] = trace.get("vix_level")
    if not _has_payload(merged.get("korea_indices")) and _has_payload(trace.get("korea_indices")):
        merged["korea_indices"] = trace.get("korea_indices")
    if not _has_payload(merged.get("market_news_titles")) and _has_payload(merged.get("strategist_market_headlines")):
        merged["market_news_titles"] = merged.get("strategist_market_headlines")
    if not _has_payload(merged.get("candidate_news_titles")) and _has_payload(merged.get("strategist_symbol_headlines")):
        merged["candidate_news_titles"] = merged.get("strategist_symbol_headlines")
    if not _has_payload(merged.get("market_news_titles")) and _has_payload(report.get("strategist_market_headlines")):
        merged["market_news_titles"] = report.get("strategist_market_headlines")
    if not _has_payload(merged.get("candidate_news_titles")) and _has_payload(report.get("strategist_symbol_headlines")):
        merged["candidate_news_titles"] = report.get("strategist_symbol_headlines")
    if not _has_payload(merged.get("news_symbol_linkage")) and _has_payload(report.get("news_symbol_linkage")):
        merged["news_symbol_linkage"] = report.get("news_symbol_linkage")
    if not _has_payload(merged.get("news_query_targets")) and _has_payload(feedback.get("news_query_targets")):
        merged["news_query_targets"] = feedback.get("news_query_targets")
    if not _has_payload(merged.get("key_events")) and _has_payload(feedback.get("key_events")):
        merged["key_events"] = feedback.get("key_events")
    return merged


def _korea_index_lines_r3_impl(context, *, facade):
    _as_dict = facade._as_dict
    _num_opt = facade._num_opt
    packet = _as_dict(context.get("korea_indices"))
    indices = _as_dict(packet.get("indices"))
    lines: List[str] = []
    for name in ("KOSPI", "KOSDAQ"):
        row = _as_dict(indices.get(name))
        if not row:
            continue
        current = _num_opt(row.get("current"))
        previous = _num_opt(row.get("previous_close"))
        change_pct = _num_opt(row.get("change_pct"))
        if current is None and previous is None and change_pct is None:
            continue
        pieces = [name]
        if current is not None:
            pieces.append(f"현재 {current:,.2f}")
        if previous is not None:
            pieces.append(f"전일 {previous:,.2f}")
        if change_pct is not None:
            pieces.append(f"등락률 {change_pct:+.2f}%")
        lines.append(" ".join(pieces))
    return lines


def _normalize_exit_trigger_label_r3_impl(value, fallback, *, facade):
    _axis_label = facade._axis_label
    _translate_text = facade._translate_text
    re = facade.re
    text = _translate_text(value).strip().rstrip(".")
    if not text and fallback:
        text = _axis_label(fallback)
    text = re.sub(r"^Trigger type:\s*", "", text, flags=re.IGNORECASE).strip()
    patterns = [
        r"청산을 직접 촉발한 신호는\s*(.+?)(?:이었습니다|였습니다|입니다|\.|$)",
        r"핵심 청산 축은\s*(.+?)(?:,|\.|$)",
        r"우선 감시 축은\s*(.+?)(?:이었습니다|였습니다|입니다|\.|$)",
        r"청산 사유는\s*(.+?)(?:입니다|\.|$)",
        r"정규화된 청산 사유는\s*(.+?)(?:입니다|\.|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            text = match.group(1).strip()
            break
    text = text.replace("으로 청산", "").replace("로 청산", "").strip()
    if "고점 대비 하락폭" in text:
        return "고점 대비 하락폭 기준"
    label = _axis_label(text).strip().rstrip(".")
    fallback_label = _axis_label(fallback).strip().rstrip(".") if fallback else ""
    hold_labels = {"hold", "보유 유지", "보유 유지입니다", "현재 포지션 판단은 보유 유지입니다"}
    if label in hold_labels and fallback_label and fallback_label not in hold_labels:
        return fallback_label
    return label or _axis_label(fallback) or "-"


def _extract_exit_signal_snapshot_r3_impl(values, *, facade):
    _normalize_exit_trigger_label = facade._normalize_exit_trigger_label
    _number_from_text = facade._number_from_text
    _translate_text = facade._translate_text
    re = facade.re
    snapshot: Dict[str, Any] = {}

    def _set_number(key: str, raw: Any) -> None:
        if key in snapshot:
            return
        num = _number_from_text(raw)
        if num is not None:
            snapshot[key] = num

    for raw in values:
        text = _translate_text(raw).strip()
        if not text:
            continue

        if "trigger" not in snapshot and any(
            token in text for token in ("촉발", "Trigger type", "핵심 청산 축", "우선 감시 축", "청산 사유", "peak_drawdown", "고점 대비")
        ):
            trigger = _normalize_exit_trigger_label(text)
            if trigger and trigger != "-":
                snapshot["trigger"] = trigger

        if match := re.search(
            r"현재가,\s*평균가,\s*고점 기준 값은\s*([+-]?[0-9,.]+)\s*/\s*([+-]?[0-9,.]+)\s*/\s*([+-]?[0-9,.]+)",
            text,
        ):
            _set_number("monitor_current_price", match.group(1))
            _set_number("position_avg_price", match.group(2))
            _set_number("peak_price", match.group(3))

        if match := re.search(r"현재가(?:는|:)?\s*([+-]?[0-9,.]+)", text):
            _set_number("monitor_current_price", match.group(1))
        if match := re.search(r"평균가(?:는|:)?\s*([+-]?[0-9,.]+)", text):
            _set_number("position_avg_price", match.group(1))
        if match := re.search(r"고점(?:은|:)?\s*([+-]?[0-9,.]+)", text):
            _set_number("peak_price", match.group(1))
        if match := re.search(r"확인 조건(?:은|:)?\s*([0-9]+\s*/\s*[0-9]+)", text):
            snapshot.setdefault("confirm_state", re.sub(r"\s+", "", match.group(1)))
        if match := re.search(r"현재 손익 변동(?:은|:)?\s*([+-]?[0-9]+(?:\.[0-9]+)?)\s*%", text):
            snapshot.setdefault("monitor_drawdown_pct_text", f"{match.group(1)}%")

    if snapshot:
        snapshot.setdefault("basis", "monitor_signal_snapshot")
        snapshot.setdefault("truth_note", "체결가와 실현손익은 Truth Surface 기준입니다.")
    return snapshot


def _metadata_value_r3_impl(value, *, facade):
    _clip = facade._clip
    raw = _clip(value, 240)
    lowered = raw.lower()
    if not raw:
        return ""
    if lowered in {"unknown", "not available", "not_available", "unavailable"}:
        return "확인되지 않음"
    if lowered in {"not captured", "not_captured"}:
        return "기록되지 않음"
    if lowered in {"allowed", "allow"}:
        return "허용"
    if lowered in {"approve", "approved"}:
        return "승인"
    if lowered == "broad_market_leaders":
        return "시장 대표주"
    if lowered == "illiquid_microcap":
        return "유동성 낮은 초소형주"
    if lowered == "headline_only_momentum":
        return "헤드라인 추격형 모멘텀"
    if lowered == "high_gap_speculative":
        return "갭 과열 투기형"
    if lowered == "neutral":
        return "중립"
    if lowered == "bullish":
        return "강세"
    if lowered == "bearish":
        return "약세"
    if lowered == "strong":
        return "강함"
    if lowered == "weak":
        return "약함"
    if lowered == "high":
        return "높음"
    if lowered == "medium":
        return "보통"
    if lowered == "low":
        return "낮음"
    return raw
