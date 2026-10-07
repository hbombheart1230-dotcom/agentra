from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping


def same_day_summary_from_texts(
    texts: Iterable[Any],
    fallback: str = "",
    current_result: Dict[str, Any] | None = None,
    *,
    deps: Mapping[str, Any],
) -> str:
    _translate_text = deps["translate_text"]
    """Normalize same-day trade summary without treating unknown PnL as flat."""

    translated_texts: List[str] = []
    for raw in texts:
        text = _translate_text(raw).strip()
        if text:
            translated_texts.append(text)

    for text in translated_texts:
        closed_match = re.search(
            r"(?:closed trade|닫힌 거래|총 거래).*?(\d+)\s*(?:건|trades?)",
            text,
            flags=re.IGNORECASE,
        )
        if not closed_match:
            continue
        win_loss_match = None
        for pattern in (
            r"(?:승\s*/\s*패|승패|승률)\s*(\d+)\s*/\s*(\d+)",
            r"(\d+)\s*승\s*/\s*(\d+)\s*패",
            r"(\d+)\s*wins?\D+(\d+)\s*loss",
        ):
            win_loss_match = re.search(pattern, text, flags=re.IGNORECASE)
            if win_loss_match:
                break
        if not win_loss_match:
            continue

        avg_match = re.search(
            r"(확인분\s*)?평균(?:\s*손익률|\s*손익)?\s*([+-]?\d+(?:\.\d+)?)(%)?",
            text,
            flags=re.IGNORECASE,
        )
        avg_source_is_ratio = False
        if not avg_match:
            avg_match = re.search(
                r"(?:avg pnl pct|average same-day pnl pct)\s*([+-]?\d+(?:\.\d+)?)(%)?",
                text,
                flags=re.IGNORECASE,
            )
            avg_source_is_ratio = bool(avg_match and not avg_match.group(2))
        unknown_match = re.search(r"(?:손익\s*)?미확정\s*(\d+)\s*건", text) or re.search(
            r"(\d+)\s*unknown pnl",
            text,
            flags=re.IGNORECASE,
        )
        flat_match = re.search(r"보합\s*(\d+)\s*건", text) or re.search(
            r"(\d+)\s*flat",
            text,
            flags=re.IGNORECASE,
        )

        closed = int(closed_match.group(1))
        wins = int(win_loss_match.group(1))
        losses = int(win_loss_match.group(2))
        unknown = int(next(group for group in unknown_match.groups() if group)) if unknown_match else 0
        flat = int(next(group for group in flat_match.groups() if group)) if flat_match else 0
        avg_text = ""
        avg_confirmed = False
        if avg_match:
            if len(avg_match.groups()) > 2:
                avg_confirmed = bool(avg_match.group(1))
                avg_text = avg_match.group(2)
            else:
                avg_text = avg_match.group(1)

        avg_num = None
        if avg_text:
            try:
                avg_num = float(avg_text)
            except (TypeError, ValueError):
                avg_num = None
        if avg_source_is_ratio and avg_num is not None and abs(avg_num) <= 1.0:
            avg_num *= 100.0
            avg_text = f"{avg_num:.2f}"
            avg_confirmed = True
        if (
            unknown <= 0
            and closed > 0
            and wins == 0
            and losses == 0
            and flat == 0
            and avg_num == 0.0
        ):
            unknown = closed
            avg_text = ""
        current = dict(current_result or {})
        current_classification = current.get("classification")
        if (
            (unknown == closed or closed == 1)
            and current_classification in (-1, 0, 1)
        ):
            wins = 1 if current_classification > 0 else 0
            losses = 1 if current_classification < 0 else 0
            flat = 1 if current_classification == 0 else 0
            unknown = max(0, closed - wins - losses - flat)
            current_pct_text = str(current.get("pct_text") or "").strip()
            if current_pct_text:
                avg_text = current_pct_text
                avg_confirmed = True
        accounted = wins + losses + flat
        if accounted >= closed:
            flat = max(0, closed - wins - losses)
            unknown = 0
        else:
            unknown = max(0, min(unknown, closed - accounted))

        parts = [f"{closed}건 중 {wins}승 / {losses}패"]
        if flat > 0:
            parts.append(f"{flat}건 보합")
        if unknown > 0:
            parts.append(f"{unknown}건 손익 미확정")
        if avg_text:
            avg_label = "확인분 평균" if unknown > 0 or avg_confirmed else "평균"
            parts.append(f"{avg_label} {avg_text}%")
        return " / ".join(parts)

    for text in translated_texts:
        lowered = text.lower()
        if "closed trade" in lowered or "닫힌 거래" in text or "평균 손익" in text:
            return text.rstrip(".")
    return fallback


def build_summary_deterministic_diagnostics_section(
    summary_report: Dict[str, Any],
    *,
    report: Dict[str, Any] | None = None,
    deps: Mapping[str, Any],
) -> List[str]:
    _as_dict = deps["as_dict"]
    _listify = deps["listify"]
    _looks_like_symbol_name_impl = deps["looks_like_symbol_name_impl"]
    _metadata_value = deps["metadata_value"]
    _resolve_trade_symbol_metadata = deps["resolve_trade_symbol_metadata"]
    _strip_trailing_blanks = deps["strip_trailing_blanks"]
    _summary_decimal = deps["summary_decimal"]
    _summary_eval_sentence = deps["summary_eval_sentence"]
    _summary_fact_text = deps["summary_fact_text"]
    _summary_money = deps["summary_money"]
    _summary_problem_label = deps["summary_problem_label"]
    _summary_root_cause_label = deps["summary_root_cause_label"]
    payload = summary_report if isinstance(summary_report, dict) else {}
    trade = _as_dict(payload.get("trade"))
    truth = _as_dict(payload.get("truth_surface"))
    decision = _as_dict(payload.get("decision_flow"))
    broker_alignment = _as_dict(payload.get("broker_alignment"))
    findings = _as_dict(payload.get("deterministic_findings"))
    fallback_meta = _resolve_trade_symbol_metadata(report or {}, str(trade.get("symbol") or ""))

    facts: List[str] = []
    symbol = _metadata_value(trade.get("symbol"))
    raw_symbol_name = _metadata_value(trade.get("symbol_name"))
    symbol_name = raw_symbol_name if _looks_like_symbol_name_impl(raw_symbol_name, symbol) else ""
    if not symbol_name:
        symbol_name = _metadata_value(fallback_meta.get("symbol_name"))
    theme = _metadata_value(trade.get("theme") or fallback_meta.get("theme"))
    if symbol != "-":
        label = f"{symbol} ({symbol_name})" if symbol_name not in {"", "-"} else symbol
        facts.append(f"대상 종목: {label}")
    if theme not in {"", "-"}:
        facts.append(f"종목 해당 테마: {theme}")
    if truth.get("pnl") not in (None, "") or truth.get("pnl_pct_text") not in (None, ""):
        pnl_text = _summary_money(truth.get("pnl")) if truth.get("pnl") not in (None, "") else "-"
        facts.append(f"실현손익: {pnl_text} ({truth.get('pnl_pct_text') or '-'})")
    if broker_alignment:
        status = _metadata_value(broker_alignment.get("status"))
        local_total = broker_alignment.get("local_total")
        broker_total = broker_alignment.get("broker_total")
        missing_local = broker_alignment.get("missing_in_local_total")
        missing_broker = broker_alignment.get("missing_in_broker_total")
        facts.append(
            "브로커 주문 정합성: "
            f"{status or '-'} / local {local_total if local_total not in (None, '') else '-'}"
            f" / broker {broker_total if broker_total not in (None, '') else '-'}"
            f" / local누락 {missing_local if missing_local not in (None, '') else '-'}"
            f" / broker누락 {missing_broker if missing_broker not in (None, '') else '-'}"
        )
        snapshot_path = _metadata_value(broker_alignment.get("account_snapshot_path"))
        if snapshot_path not in {"", "-"}:
            facts.append(f"키움 계좌 스냅샷: {snapshot_path}")
    if decision.get("scanner_rank") not in (None, ""):
        score = _summary_decimal(decision.get("scanner_score"), 3)
        facts.append(f"스캐너 순위/점수: {decision.get('scanner_rank')}위 / {score}")
    chart_score = decision.get("scanner_chart_fit_score")
    if chart_score not in (None, ""):
        authority = _metadata_value(decision.get("scanner_chart_fit_authority"))
        facts.append(f"Scanner chart-fit: {_summary_decimal(chart_score, 3)} / {authority}")
    top_pick = _metadata_value(decision.get("scanner_top_pick_symbol"))
    fallback_reason = _summary_fact_text(decision.get("monitor_fallback_reason"))
    if top_pick != "-":
        facts.append(f"상위 후보 보류: {top_pick} ({fallback_reason or '-'})")
    entry_reason = _summary_fact_text(decision.get("entry_reason"))
    if entry_reason:
        facts.append(f"진입 근거: {entry_reason}")
    exit_reason = _summary_fact_text(decision.get("exit_reason"))
    if exit_reason:
        facts.append(f"청산 근거: {exit_reason}")

    problems = [_summary_problem_label(item) for item in _listify(findings.get("problems")) if str(item or "").strip()]
    causes = [_summary_root_cause_label(item) for item in _listify(findings.get("root_cause_candidates")) if str(item or "").strip()]
    questions = [_summary_eval_sentence(item) for item in _listify(findings.get("validation_questions")) if str(item or "").strip()]

    if not facts and not problems and not causes and not questions:
        return []

    lines: List[str] = ["## 🧾 확정 진단", ""]
    if facts:
        lines.append("### 확정 사실")
        lines.append("")
        lines.extend(f"* {item}" for item in facts[:10])
    if problems:
        lines.append("")
        lines.append("### 확정 문제 후보")
        lines.append("")
        lines.extend(f"* {item}" for item in problems[:8])
    if causes:
        lines.append("")
        lines.append("### 원인 후보")
        lines.append("")
        lines.extend(f"* {item}" for item in causes[:6])
    if questions:
        lines.append("")
        lines.append("### 검증 질문")
        lines.append("")
        lines.extend(f"* {item}" for item in questions[:6])
    return _strip_trailing_blanks(lines)


def build_summary_llm_evaluation_section(
    summary_report: Dict[str, Any],
    *,
    report: Dict[str, Any] | None = None,
    deps: Mapping[str, Any],
) -> List[str]:
    _action_label = deps["action_label"]
    _as_dict = deps["as_dict"]
    _authoritative_final_operator_summary = deps["authoritative_final_operator_summary"]
    _first_present_impl = deps["first_present_impl"]
    _listify = deps["listify"]
    _normalize_evaluation_hold_duration = deps["normalize_evaluation_hold_duration"]
    _strip_trailing_blanks = deps["strip_trailing_blanks"]
    _summary_eval_sentence = deps["summary_eval_sentence"]
    payload = summary_report if isinstance(summary_report, dict) else {}
    evaluation = _as_dict(payload.get("llm_evaluation"))
    generation = _as_dict(payload.get("generation"))
    status = str(generation.get("status") or payload.get("summary_status") or "").strip().lower()
    has_content = any(
        [
            str(evaluation.get("conclusion") or "").strip(),
            str(evaluation.get("root_cause") or "").strip(),
            _listify(evaluation.get("priority_actions")),
            _listify(evaluation.get("risk_notes")),
            _listify(evaluation.get("validation_questions")),
        ]
    )
    if not has_content:
        return []

    lines: List[str] = [
        "## 🤖 LLM 복기 초안",
        "",
        "* 성격: 아래 내용은 확정 사실이 아니라 문제 파악을 돕는 해석 초안입니다. 수치와 사실은 위 확정 진단과 Truth Surface를 우선합니다.",
    ]
    if status:
        lines.append(f"* 상태: {status}")
    action = _action_label(
        _first_present_impl(
            _as_dict((report or {}).get("final_operator_conclusion")).get("current_action"),
            (report or {}).get("action"),
            _as_dict((report or {}).get("shared_facts")).get("action"),
        )
    )
    conclusion = _summary_eval_sentence(evaluation.get("conclusion"))
    if report:
        conclusion = _authoritative_final_operator_summary(
            report,
            action=action,
            fallback=_normalize_evaluation_hold_duration(conclusion, report),
        )
    if conclusion:
        lines.append(f"* 결론: **{conclusion}**")
    root_cause = _normalize_evaluation_hold_duration(
        _summary_eval_sentence(evaluation.get("root_cause")),
        report or {},
    )
    trade = _as_dict(_as_dict((report or {}).get("fact_payload")).get("trade"))
    entry = _as_dict(trade.get("entry_summary"))
    opening_probe = entry.get("reason_human") == "opening_rank1_controlled_probe"
    if opening_probe:
        root_cause = (
            "Opening Alpha 예외 진입 거래입니다. 기존 진입 대기/차단 항목과 최종 레인 승인 결과는 구분해야 합니다. "
            "기존 blocker의 존재만으로 손실 원인이나 무단 우회를 단정할 수 없습니다. "
            "LLM 원문 해석은 검증되지 않았으며 원본 응답 파일에 보존합니다."
        )
    if root_cause:
        lines.append(f"* 원인 해석: {root_cause}")

    actions = [
        _normalize_evaluation_hold_duration(_summary_eval_sentence(item), report or {})
        for item in _listify(evaluation.get("priority_actions"))
        if str(item or "").strip()
    ]
    if opening_probe:
        actions = ["레인 승인 근거, 실제 체결 가격, 최종 청산 트리거를 대조해 원인을 검증합니다."]
    if actions:
        lines.append("")
        lines.append("### 우선 액션")
        lines.append("")
        lines.extend(f"{idx}. {item}" for idx, item in enumerate(actions[:4], 1))

    risks = [
        _normalize_evaluation_hold_duration(_summary_eval_sentence(item), report or {})
        for item in _listify(evaluation.get("risk_notes"))
        if str(item or "").strip()
    ]
    if risks:
        lines.append("")
        lines.append("### 리스크")
        lines.append("")
        lines.extend(f"* {item}" for item in risks[:4])

    questions = [_summary_eval_sentence(item) for item in _listify(evaluation.get("validation_questions")) if str(item or "").strip()]
    if questions:
        lines.append("")
        lines.append("### 검증 질문")
        lines.append("")
        lines.extend(f"* {item}" for item in questions[:4])

    return _strip_trailing_blanks(lines)


