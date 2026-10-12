"""Behavior-preserving R3 implementation bodies moved from the public facade.

Each function keeps its original body. Names it used as facade module globals are
read from the injected `facade` module at call entry (explicit names, no getattr
fallback), preserving monkeypatch semantics. Owner never imports the facade.
"""
from __future__ import annotations


def _normalize_section_r3_impl(section, *, default_summary, bullet_key, facade):
    _clip = facade._clip
    _listify = facade._listify
    data = section if isinstance(section, dict) else {}
    out = {
        "summary": _clip(data.get("summary"), max_len=600) or _clip(default_summary, max_len=600),
        bullet_key: _listify(data.get(bullet_key), max_items=8, max_len=260),
    }
    for key in (
        "headline",
        "action",
        "confidence",
        "status",
        "grade",
        "current_action",
        "symbol",
        "story_type",
    ):
        value = _clip(data.get(key), max_len=120)
        if value:
            out[key] = value
    return out


def _actual_lifecycle_action_r3_impl(story_input, *, facade):
    _clip = facade._clip
    status_text = str(story_input.get("status") or "").strip().lower()
    exit_summary = story_input.get("exit_summary") if isinstance(story_input.get("exit_summary"), dict) else {}
    entry_summary = story_input.get("entry_summary") if isinstance(story_input.get("entry_summary"), dict) else {}
    operator_conclusion = story_input.get("operator_conclusion_human") if isinstance(story_input.get("operator_conclusion_human"), dict) else {}

    exit_action = _clip(exit_summary.get("action"), max_len=24).upper()
    entry_action = _clip(entry_summary.get("action"), max_len=24).upper()
    requested_action = _clip(story_input.get("action"), max_len=24).upper()
    conclusion_action = _clip(operator_conclusion.get("current_action"), max_len=24).upper()

    if exit_action in {"BUY", "SELL"}:
        return exit_action
    if status_text == "open":
        if conclusion_action in {"HOLD", "WAIT", "BUY"}:
            return conclusion_action
        return "HOLD"
    if requested_action in {"BUY", "SELL"}:
        return requested_action
    if conclusion_action in {"BUY", "SELL", "HOLD", "WAIT"}:
        return conclusion_action
    if entry_action in {"BUY", "SELL"}:
        return entry_action
    return "WAIT"


def _reporter_summary_is_placeholder_r3_impl(value, *, facade):
    text = str(value or "").strip()
    if not text:
        return False
    lowered = text.lower()
    exact_markers = {
        "same-day reporter analysis was not generated yet.",
        "a same-day reporter file exists, but this run was not linked to a run-specific evaluation yet.",
        "a same-day reporter analysis was linked to this run.",
        "당일 리포터 분석은 아직 생성되지 않았습니다.",
        "당일 리포터 파일은 있지만 이 run에 대한 개별 평가는 아직 연결되지 않았습니다.",
        "당일 리포터 분석이 이 run에 연결됐습니다.",
    }
    prefix_markers = (
        "reporter status:",
        "reporter reason:",
        "reporter grade:",
        "reporter summary:",
    )
    if lowered in {marker.lower() for marker in exact_markers}:
        return True
    return any(lowered.startswith(marker) for marker in prefix_markers)


def resolve_shared_trade_facts_r3_impl(story_input, *, facade):
    _as_action = facade._as_action
    _as_dict = facade._as_dict
    _as_status = facade._as_status
    _build_shared_summary_seed = facade._build_shared_summary_seed
    _clip = facade._clip
    shared_seed = _build_shared_summary_seed(story_input)
    resolved = _as_dict(shared_seed.get("resolved_trade_facts"))
    data_source = _as_dict(resolved.get("data_source"))
    return {
        "action": _as_action(resolved.get("action")) or "unavailable",
        "status": _as_status(resolved.get("status")) or "unavailable",
        "holding_duration": _clip(resolved.get("holding_duration"), max_len=80) or "unavailable",
        "exit_reason": _clip(resolved.get("exit_reason"), max_len=280) or "unavailable",
        "pnl": resolved.get("pnl", "unavailable"),
        "pnl_pct": resolved.get("pnl_pct", "unavailable"),
        "broker_fee": resolved.get("broker_fee"),
        "broker_tax": resolved.get("broker_tax"),
        "pnl_truth_source": _clip(resolved.get("pnl_truth_source"), max_len=80) or "unavailable",
        "broker_fill_price": resolved.get("broker_fill_price"),
        "broker_buy_price": resolved.get("broker_buy_price"),
        "account_mark_price": resolved.get("account_mark_price"),
        "monitor_mark_price": resolved.get("monitor_mark_price"),
        "price_truth_source": _clip(resolved.get("price_truth_source"), max_len=40) or "unavailable",
        "monitor_price_source": _clip(resolved.get("monitor_price_source"), max_len=120) or "unavailable",
        "data_source": data_source,
        "monitor_decision": _as_dict(shared_seed.get("monitor_decision")),
    }


def _extract_korea_indices_snapshot_r3_impl(section, *, facade):
    _listify = facade._listify
    re = facade.re
    data = section if isinstance(section, dict) else {}
    packet = data.get("korea_indices") if isinstance(data.get("korea_indices"), dict) else {}
    indices = packet.get("indices") if isinstance(packet.get("indices"), dict) else {}
    out: Dict[str, Dict[str, Any]] = {}
    for name in ("KOSPI", "KOSDAQ"):
        row = indices.get(name) if isinstance(indices.get(name), dict) else {}
        if row:
            out[name] = dict(row)
    if out:
        return out
    events = data.get("key_events") or data.get("key_events_hint")
    for row in _listify(events, max_items=8, max_len=260):
        text = str(row or "")
        match = re.search(
            r"kospi=([+-]?\d+(?:\.\d+)?)/prev=([+-]?\d+(?:\.\d+)?)/chg=([+-]?\d+(?:\.\d+)?)%.*?"
            r"kosdaq=([+-]?\d+(?:\.\d+)?)/prev=([+-]?\d+(?:\.\d+)?)/chg=([+-]?\d+(?:\.\d+)?)%",
            text,
            flags=re.IGNORECASE,
        )
        if not match:
            continue
        return {
            "KOSPI": {"current": float(match.group(1)), "previous_close": float(match.group(2)), "change_pct": float(match.group(3))},
            "KOSDAQ": {"current": float(match.group(4)), "previous_close": float(match.group(5)), "change_pct": float(match.group(6))},
        }
    return {}


def _format_korea_indices_sentence_r3_impl(indices, *, facade):
    _format_pct_points = facade._format_pct_points
    _num_opt = facade._num_opt
    parts: List[str] = []
    for name in ("KOSPI", "KOSDAQ"):
        row = indices.get(name) if isinstance(indices.get(name), dict) else {}
        if not row:
            continue
        current = _num_opt(row.get("current"))
        previous = _num_opt(row.get("previous_close"))
        change_pct = _num_opt(row.get("change_pct"))
        if current is None and previous is None and change_pct is None:
            continue
        bits = [name]
        if current is not None:
            bits.append(f"현재 {current:,.2f}")
        if previous is not None:
            bits.append(f"전일 {previous:,.2f}")
        if change_pct is not None:
            bits.append(f"등락률 {_format_pct_points(change_pct)}")
        parts.append(" ".join(bits))
    return "; ".join(parts)


def _scanner_selected_row_r3_impl(scanner_reason, *, facade):
    _clip = facade._clip
    _scanner_monitor_fallback_context = facade._scanner_monitor_fallback_context
    _scanner_ranked_candidates = facade._scanner_ranked_candidates
    selected_symbol = _clip(scanner_reason.get("selected_symbol"), max_len=24)
    ranked_rows = _scanner_ranked_candidates(scanner_reason)
    if selected_symbol:
        for row in ranked_rows:
            if _clip(row.get("symbol"), max_len=24) == selected_symbol:
                return dict(row)
    fallback_ctx = _scanner_monitor_fallback_context(scanner_reason)
    if fallback_ctx["used"] and selected_symbol:
        trace = scanner_reason.get("scanner_selection_trace") if isinstance(scanner_reason.get("scanner_selection_trace"), dict) else {}
        news = trace.get("news_scanner_contribution") if isinstance(trace.get("news_scanner_contribution"), dict) else {}
        row = {
            "symbol": selected_symbol,
            "rank": scanner_reason.get("selected_rank") or trace.get("selected_rank"),
            "score_total": scanner_reason.get("selected_score") or trace.get("selected_score") or news.get("selected_score_total"),
            "confidence": scanner_reason.get("confidence") or trace.get("confidence"),
            "risk_score": scanner_reason.get("risk_score") or trace.get("risk_score"),
        }
        return {key: value for key, value in row.items() if value not in (None, "")}
    return dict(ranked_rows[0]) if ranked_rows else {}


def _build_scanner_driver_summary_r3_impl(scanner_reason, *, facade):
    _num_opt = facade._num_opt
    _scanner_score_driver_label = facade._scanner_score_driver_label
    driver_source = (
        scanner_reason.get("selected_symbol_score_drivers")
        if isinstance(scanner_reason.get("selected_symbol_score_drivers"), dict)
        else {}
    )
    if not driver_source:
        trace = scanner_reason.get("scanner_selection_trace") if isinstance(scanner_reason.get("scanner_selection_trace"), dict) else {}
        driver_source = trace.get("selected_symbol_score_drivers") if isinstance(trace.get("selected_symbol_score_drivers"), dict) else {}
    driver_rows: List[tuple[str, float]] = []
    for key, value in dict(driver_source or {}).items():
        numeric = _num_opt(value)
        if numeric is None or numeric <= 0:
            continue
        driver_rows.append((_scanner_score_driver_label(key), numeric))
    if not driver_rows:
        return ""
    driver_rows.sort(key=lambda item: item[1], reverse=True)
    top_rows = [f"{label} {value:.3f}" for label, value in driver_rows[:3]]
    return ", ".join(top_rows)


def _build_runner_up_comparison_r3_impl(row, *, selected_symbol, selected_score, selected_risk, facade):
    _clip = facade._clip
    _num_opt = facade._num_opt
    _operatorize_report_text = facade._operatorize_report_text
    runner_symbol = _clip(row.get("symbol"), max_len=24)
    if not runner_symbol:
        return ""
    parts: List[str] = []
    runner_score = _num_opt(row.get("score_total"))
    runner_risk = _num_opt(row.get("risk_score"))
    if runner_score is not None and selected_score is not None:
        gap = selected_score - runner_score
        if gap >= 0:
            parts.append(
                f"종합 점수 {runner_score:.3f}로 {selected_symbol}({selected_score:.3f})보다 {gap:.3f} 낮았습니다"
            )
    if runner_risk is not None and selected_risk is not None and runner_risk > selected_risk:
        parts.append(
            f"리스크 점수 {runner_risk:.3f}로 {selected_symbol}({selected_risk:.3f})보다 높았습니다"
        )
    if not parts:
        why_text = _clip(row.get("why") or row.get("summary"), max_len=220)
        if why_text:
            parts.append(_operatorize_report_text(why_text))
    if not parts:
        return ""
    return f"{runner_symbol}은 " + ". ".join(parts) + "."
