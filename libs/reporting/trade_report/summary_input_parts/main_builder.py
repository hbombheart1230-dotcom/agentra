from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Mapping


def build_trade_summary_input_impl(
    report: Dict[str, Any], *, deps: Mapping[str, Any],
    collect_deterministic_summary_findings: Any,
    build_broker_alignment: Any, build_market_and_strategy: Any, build_decision_flow: Any,
) -> Dict[str, Any]:
    _RECOVERED_PARTIAL_ENTRY_NOTE = deps["RECOVERED_PARTIAL_ENTRY_NOTE"]
    _RECOVERED_PARTIAL_EXIT_NOTE = deps["RECOVERED_PARTIAL_EXIT_NOTE"]
    _action_label = deps["action_label"]
    _as_dict = deps["as_dict"]
    _authoritative_final_operator_summary = deps["authoritative_final_operator_summary"]
    _authoritative_hold_duration_seconds = deps["authoritative_hold_duration_seconds"]
    _authoritative_holding_duration_label = deps["authoritative_holding_duration_label"]
    _build_trade_cost_analysis = deps["build_trade_cost_analysis"]
    _carryover_context = deps["carryover_context"]
    _clip = deps["clip"]
    _compact_post_exit_shadow = deps["compact_post_exit_shadow"]
    _enrich_exit_signal_snapshot_from_monitor = deps["enrich_exit_signal_snapshot_from_monitor"]
    _entry_confidence_for_operator_summary = deps["entry_confidence_for_operator_summary"]
    _entry_reason_line = deps["entry_reason_line"]
    _entry_watch_execution_lines = deps["entry_watch_execution_lines"]
    _execution_mode_label = deps["execution_mode_label"]
    _extract_exit_signal_snapshot = deps["extract_exit_signal_snapshot"]
    _fmt_pct = deps["fmt_pct"]
    _get_truth_surface = deps["get_truth_surface"]
    _is_not_captured = deps["is_not_captured"]
    _is_recovered_partial_exit_report = deps["is_recovered_partial_exit_report"]
    _listify = deps["listify"]
    _metadata_value = deps["metadata_value"]
    _normalize_exit_trigger_label = deps["normalize_exit_trigger_label"]
    _num_opt = deps["num_opt"]
    _operator_pnl_pct = deps["operator_pnl_pct"]
    _playbook_label = deps["playbook_label"]
    _post_exit_shadow_surface = deps["post_exit_shadow_surface"]
    _quant_tactic_surface_impl = deps["quant_tactic_surface_impl"]
    _resolve_entry_execution_visibility = deps["resolve_entry_execution_visibility"]
    _resolve_entry_signal_snapshot = deps["resolve_entry_signal_snapshot"]
    _resolve_market_context = deps["resolve_market_context"]
    _resolve_trade_symbol_metadata = deps["resolve_trade_symbol_metadata"]
    _risk_mode_label = deps["risk_mode_label"]
    _same_day_current_result = deps["same_day_current_result"]
    _same_day_summary_from_texts = deps["same_day_summary_from_texts"]
    _sample_news_titles = deps["sample_news_titles"]
    _sample_news_titles_for_symbol = deps["sample_news_titles_for_symbol"]
    _selection_fallback_context = deps["selection_fallback_context"]
    _status_label = deps["status_label"]
    _story_type_label = deps["story_type_label"]
    _strategy_horizon_report_surface = deps["strategy_horizon_report_surface"]
    _theme_label = deps["theme_label"]
    _translate_text = deps["translate_text"]
    _translated_metadata = deps["translated_metadata"]
    _truth_source_label = deps["truth_source_label"]
    """Build the compact deterministic input that a summary LLM may evaluate."""

    def _pick(*values: Any) -> Any:
        for value in values:
            if value not in (None, ""):
                return value
        return ""

    def _section_texts(*sections: Dict[str, Any]) -> List[str]:
        texts: List[str] = []
        for section in sections:
            if not isinstance(section, dict):
                continue
            summary = _translate_text(section.get("summary")).strip()
            if summary:
                texts.append(summary)
            texts.extend(_translate_text(item).strip() for item in _listify(section.get("bullets")) if str(item or "").strip())
        return texts

    def _same_day_summary(section: Dict[str, Any]) -> str:
        return _same_day_summary_from_texts(
            _section_texts(section),
            current_result=_same_day_current_result(report),
        )

    def _first_matching_line(values: Iterable[Any], needles: Iterable[str]) -> str:
        lowered_needles = [needle.lower() for needle in needles]
        for raw in values:
            text = _translate_text(raw).strip()
            if not text:
                continue
            lowered = text.lower()
            if any(needle in lowered for needle in lowered_needles):
                return text.rstrip(".")
        return ""

    def _policy_deltas(memory_bias: Dict[str, Any]) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for row in _listify(memory_bias.get("applied_deltas")) + _listify(memory_bias.get("exit_deltas")):
            row_obj = _as_dict(row)
            field = str(row_obj.get("field") or "").strip()
            if not field:
                continue
            rows.append(
                {
                    "field": field,
                    "from": row_obj.get("from"),
                    "to": row_obj.get("to"),
                    "delta": row_obj.get("delta"),
                }
            )
        return rows[:8]

    def _compact_section(section: Dict[str, Any], *, limit: int = 5) -> Dict[str, Any]:
        return {
            "summary": _translate_text(section.get("summary")).strip(),
            "bullets": [_translate_text(item).strip() for item in _listify(section.get("bullets"))[:limit] if str(item or "").strip()],
        }

    shared = _as_dict(report.get("shared_facts"))
    truth = _get_truth_surface(report)
    truth_price = _as_dict(truth.get("price"))
    truth_pnl = _as_dict(truth.get("pnl"))
    market = _resolve_market_context(report)
    strategist = _as_dict(report.get("strategist_summary"))
    trace_summary = _as_dict(report.get("strategist_trace_summary"))
    selection = _as_dict(report.get("why_this_symbol_was_chosen"))
    entry = _as_dict(report.get("entry_decision"))
    holding = _as_dict(report.get("holding_monitoring_story"))
    exit_decision = _as_dict(report.get("exit_decision"))
    reporter_eval = _as_dict(report.get("reporter_evaluation"))
    memory_app = _as_dict(report.get("memory_application_surface"))
    monitor = _as_dict(report.get("monitor_snapshot"))
    scanner_memory = _as_dict(memory_app.get("scanner_memory_bias"))
    monitor_memory = _as_dict(memory_app.get("monitor_memory_bias"))
    final = _as_dict(report.get("final_operator_conclusion"))
    trade_id = _clip(report.get("trade_id") or report.get("story_id"), 80)
    symbol = _clip(_pick(report.get("symbol"), shared.get("symbol")), 32)
    symbol_metadata = _resolve_trade_symbol_metadata(report, symbol)
    action_label = _action_label(_pick(final.get("current_action"), report.get("action"), shared.get("action")))
    recovered_partial_exit = _is_recovered_partial_exit_report(report)
    carryover_context = _carryover_context(report)
    carryover_exit = bool(carryover_context.get("is_carryover_exit"))
    exit_only_report = recovered_partial_exit or carryover_exit
    day = _clip(report.get("day") or shared.get("day"), 32)
    if not day:
        match = re.search(r"TRD_(\d{4})(\d{2})(\d{2})", trade_id)
        if match:
            day = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

    pnl = _pick(truth_pnl.get("value"), shared.get("pnl"))
    pnl_pct, pnl_pct_is_observation = _operator_pnl_pct(truth_pnl, shared)
    pnl_num = _num_opt(pnl)
    pnl_label_basis = pnl_num if pnl_num is not None else _num_opt(pnl_pct)
    result_label = "breakeven"
    if pnl_label_basis is not None and pnl_label_basis > 0:
        result_label = "profit"
    elif pnl_label_basis is not None and pnl_label_basis < 0:
        result_label = "loss"
    truth_source_value = _pick(truth_pnl.get("pnl_truth_source"), shared.get("pnl_truth_source"))
    if pnl_num is None and pnl_pct_is_observation:
        truth_source_value = _pick(
            truth_price.get("price_truth_source"),
            shared.get("price_truth_source"),
            truth_source_value,
        )

    selection_trace = _as_dict(selection.get("scanner_selection_trace"))
    scanner_chart_fit = _as_dict(selection.get("scanner_chart_fit")) or _as_dict(selection_trace.get("scanner_chart_fit"))
    selection_fallback = _selection_fallback_context(selection, _clip(_pick(report.get("symbol"), shared.get("symbol")), 32))
    entry_signal_snapshot = _resolve_entry_signal_snapshot(report)
    selection_rank = _pick(selection.get("selected_rank"), selection_trace.get("selected_rank"), selection.get("scanner_rank"))
    selection_score = _pick(selection.get("score_total"), selection.get("selected_score"))
    if selection_score in (None, "") and selection_fallback.get("used"):
        selection_score = _pick(selection_trace.get("selected_score"), _as_dict(selection_trace.get("news_scanner_contribution")).get("selected_score_total"))
    if exit_only_report:
        selection_rank = None
        selection_score = ""
    selection_texts = _section_texts(selection)
    entry_texts = _section_texts(entry)
    exit_texts = _section_texts(exit_decision)
    exit_signal_snapshot = _extract_exit_signal_snapshot(exit_texts + _section_texts(holding))
    exit_signal_snapshot = _enrich_exit_signal_snapshot_from_monitor(exit_signal_snapshot, monitor)
    post_exit_shadow_summary = _compact_post_exit_shadow(_post_exit_shadow_surface(report))
    strategy_horizon_summary = _strategy_horizon_report_surface(report)
    authoritative_hold_sec = _authoritative_hold_duration_seconds(report)
    authoritative_hold_label = _authoritative_holding_duration_label(report)
    if authoritative_hold_sec is not None:
        strategy_horizon_summary = dict(strategy_horizon_summary)
        strategy_horizon_summary["actual_hold_sec"] = authoritative_hold_sec
        strategy_horizon_summary["actual_hold_label"] = authoritative_hold_label
        strategy_horizon_summary["actual_hold_source"] = "entry_exit_execution_timestamps"
    exit_trigger = _first_matching_line(
        _listify(exit_decision.get("bullets")),
        ["촉발", "트리거", "청산 사유", "peak_drawdown", "고점 대비"],
    )
    if not exit_trigger:
        exit_trigger = _first_matching_line(exit_texts, ["촉발", "트리거", "청산", "peak_drawdown", "고점 대비"])
    exit_trigger_label = _normalize_exit_trigger_label(
        exit_signal_snapshot.get("trigger") or exit_trigger,
        shared.get("exit_reason"),
    )
    reporter_texts = _section_texts(reporter_eval)
    combined_texts = _section_texts(market, strategist, selection, entry, holding, exit_decision, reporter_eval)
    combined_blob = "\n".join(combined_texts).lower()
    entry_execution_visibility = _resolve_entry_execution_visibility(report)
    entry_watch_lines = _entry_watch_execution_lines(
        report,
        require_trade_symbol_match=bool(selection_fallback.get("used")) or bool(exit_only_report),
    )
    broker_alignment = _as_dict(report.get("broker_alignment"))
    broker_alignment_summary = _as_dict(broker_alignment.get("summary"))
    broker_account_snapshot = _as_dict(broker_alignment.get("account_snapshot"))

    (
        deterministic_positives, deterministic_problems,
        root_cause_candidates, validation_questions,
    ) = collect_deterministic_summary_findings(
        truth_price=truth_price, truth_pnl=truth_pnl,
        strategist=strategist, selection=selection, entry=entry,
        exit_decision=exit_decision, memory_app=memory_app,
        carryover_exit=carryover_exit, recovered_partial_exit=recovered_partial_exit,
        combined_blob=combined_blob, selection_rank=selection_rank,
        scanner_chart_fit=scanner_chart_fit, monitor_memory=monitor_memory,
        deps=deps,
    )

    return {
        "schema_version": "ai_trade_summary_input.v1",
        "artifact_type": "ai_trade_summary_input",
        "source_artifact": "ai_trade_report.json",
        "trade": {
            "trade_id": trade_id,
            "day": day,
            "symbol": _clip(_pick(report.get("symbol"), shared.get("symbol")), 32),
            "symbol_name": str(symbol_metadata.get("symbol_name") or ""),
            "theme": str(symbol_metadata.get("theme") or ""),
            "themes": list(symbol_metadata.get("themes") or []),
            "status": _status_label(_pick(report.get("status"), shared.get("status"))),
            "story_type": _story_type_label(report.get("story_type")),
            "execution_mode": _execution_mode_label(report.get("execution_mode_label")),
            "action": action_label,
            "recovered_partial_exit": recovered_partial_exit,
            "carryover_exit": carryover_exit,
            "carryover_context": carryover_context,
            "entry_assessment_scope": (
                "excluded_carryover_exit"
                if carryover_exit
                else ("excluded_recovered_partial" if recovered_partial_exit else "normal")
            ),
        },
        "truth_surface": {
            "result_label": result_label,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "pnl_pct_text": _fmt_pct(pnl_pct),
            "buy_price": _pick(truth_price.get("broker_buy_price"), shared.get("broker_buy_price")),
            "sell_price": _pick(truth_price.get("broker_fill_price"), shared.get("broker_fill_price")),
            "monitor_sell_reference_price": _pick(
                truth_price.get("monitor_mark_price"),
                shared.get("monitor_mark_price"),
                exit_signal_snapshot.get("monitor_current_price"),
            ),
            "fee": _pick(shared.get("broker_fee"), truth_pnl.get("broker_fee")),
            "tax": _pick(shared.get("broker_tax"), truth_pnl.get("broker_tax")),
            "cost_analysis": _build_trade_cost_analysis(report),
            "truth_source": _truth_source_label(truth_source_value),
        },
        "same_day_context": {
            "summary": _same_day_summary(reporter_eval),
            "label": "당일 성과(리포트 생성 시점 기준)",
            "basis": "report_generation_time",
            "reporter_evaluation": _compact_section(reporter_eval, limit=6),
        },
        "broker_alignment": build_broker_alignment(
            _metadata_value=_metadata_value, broker_account_snapshot=broker_account_snapshot, broker_alignment=broker_alignment, broker_alignment_summary=broker_alignment_summary,
        ),
        "market_and_strategy": build_market_and_strategy(
            _is_not_captured=_is_not_captured, _listify=_listify, _metadata_value=_metadata_value, _pick=_pick,
            _playbook_label=_playbook_label, _risk_mode_label=_risk_mode_label, _sample_news_titles=_sample_news_titles, _sample_news_titles_for_symbol=_sample_news_titles_for_symbol,
            _theme_label=_theme_label, _translate_text=_translate_text, market=market, report=report,
            symbol=symbol, trace_summary=trace_summary,
        ),
        "decision_flow": build_decision_flow(
            _RECOVERED_PARTIAL_ENTRY_NOTE=_RECOVERED_PARTIAL_ENTRY_NOTE, _RECOVERED_PARTIAL_EXIT_NOTE=_RECOVERED_PARTIAL_EXIT_NOTE, _authoritative_final_operator_summary=_authoritative_final_operator_summary, _entry_confidence_for_operator_summary=_entry_confidence_for_operator_summary,
            _entry_reason_line=_entry_reason_line, _first_matching_line=_first_matching_line, _metadata_value=_metadata_value, _num_opt=_num_opt,
            _pick=_pick, _translate_text=_translate_text, _translated_metadata=_translated_metadata, action_label=action_label,
            authoritative_hold_label=authoritative_hold_label, carryover_context=carryover_context, carryover_exit=carryover_exit, entry_execution_visibility=entry_execution_visibility,
            entry_signal_snapshot=entry_signal_snapshot, entry_texts=entry_texts, entry_watch_lines=entry_watch_lines, exit_only_report=exit_only_report,
            exit_signal_snapshot=exit_signal_snapshot, exit_trigger_label=exit_trigger_label, final=final, pnl_pct=pnl_pct,
            recovered_partial_exit=recovered_partial_exit, report=report, scanner_chart_fit=scanner_chart_fit, selection=selection,
            selection_fallback=selection_fallback, selection_rank=selection_rank, selection_score=selection_score, selection_texts=selection_texts,
            selection_trace=selection_trace, shared=shared, truth_price=truth_price,
        ),
        "strategy_horizon": strategy_horizon_summary,
        "post_exit_shadow": post_exit_shadow_summary,
        "quant_tactic": _quant_tactic_surface_impl(report),
        "memory_and_policy": {
            "scanner_memory_applied": bool(scanner_memory.get("applied")),
            "monitor_memory_applied": bool(monitor_memory.get("applied")),
            "monitor_active_layers": list(monitor_memory.get("active_layers") or []),
            "monitor_policy_deltas": _policy_deltas(monitor_memory),
        },
        "deterministic_findings": {
            "positives": deterministic_positives,
            "problems": deterministic_problems,
            "root_cause_candidates": root_cause_candidates,
            "validation_questions": validation_questions,
            "raw_reporter_pattern_lines": [_translate_text(line).strip() for line in reporter_texts[:6] if line],
        },
        "llm_task": {
            "purpose": "Fill only the interpretation fields for ai_trade_summary evaluation.",
            "allowed_output_fields": [
                "conclusion",
                "root_cause",
                "priority_actions",
                "risk_notes",
                "validation_questions",
            ],
            "hard_constraints": [
                "Do not invent or modify prices, pnl, fees, taxes, timestamps, or order facts.",
                "Use truth_surface as immutable fact.",
                "Treat decision_flow.exit_observation as monitor_signal_snapshot only, not as broker fill or realized pnl.",
                "Treat strategy_horizon as strategy intent and observation-only report visibility; do not treat it as forced hold unless allow_behavior_change is true.",
                "Treat post_exit_shadow as observation-only evidence, not as a live behavior-change rule.",
                "If trade.carryover_exit is true, separate the original carry/overnight date basis from the current-day exit context.",
                "If evidence is weak, state that validation is required instead of asserting causality.",
                "Keep output operator-facing and concise.",
            ],
        },
    }
