from __future__ import annotations

from typing import Any


def build_decision_flow(
    *,
    _RECOVERED_PARTIAL_ENTRY_NOTE: Any, _RECOVERED_PARTIAL_EXIT_NOTE: Any, _authoritative_final_operator_summary: Any, _entry_confidence_for_operator_summary: Any,
    _entry_reason_line: Any, _first_matching_line: Any, _metadata_value: Any, _num_opt: Any,
    _pick: Any, _translate_text: Any, _translated_metadata: Any, action_label: Any,
    authoritative_hold_label: Any, carryover_context: Any, carryover_exit: Any, entry_execution_visibility: Any,
    entry_signal_snapshot: Any, entry_texts: Any, entry_watch_lines: Any, exit_only_report: Any,
    exit_signal_snapshot: Any, exit_trigger_label: Any, final: Any, pnl_pct: Any,
    recovered_partial_exit: Any, report: Any, scanner_chart_fit: Any, selection: Any,
    selection_fallback: Any, selection_rank: Any, selection_score: Any, selection_texts: Any,
    selection_trace: Any, shared: Any, truth_price: Any,
) -> dict:
    """Preserve the canonical decision_flow input contract and value evaluation order."""
    return {
            "scanner_rank": selection_rank,
            "scanner_score": selection_score,
            "scanner_chart_fit": scanner_chart_fit,
            "scanner_chart_fit_score": scanner_chart_fit.get("score") if scanner_chart_fit else None,
            "scanner_chart_fit_authority": scanner_chart_fit.get("authority") if scanner_chart_fit else "",
            "scanner_rank_basis": (
                "carryover_exit_no_same_day_entry"
                if carryover_exit
                else "recovered_partial_no_entry_evidence"
                if recovered_partial_exit
                else ("monitor_fallback_reassessment" if selection_fallback.get("used") else "scanner_rank")
            ),
            "selection_path": (
                "carryover_exit"
                if carryover_exit
                else "recovered_partial_exit"
                if recovered_partial_exit
                else selection_fallback.get("selection_path") or _metadata_value(selection_trace.get("selection_path"))
            ),
            "scanner_top_pick_symbol": selection_fallback.get("scanner_top_pick_symbol"),
            "monitor_fallback_reason": selection_fallback.get("reason"),
            "selection_basis": (
                "오버나이트/주말 이월 포지션 청산"
                if carryover_exit
                else ("보유/회수 포지션 청산" if recovered_partial_exit else _translated_metadata(selection.get("basis")))
            ),
            "selection_blocker": (
                ""
                if exit_only_report
                else (
                f"스캐너 상위 후보 {selection_fallback.get('scanner_top_pick_symbol')} 보류 후 재평가"
                if selection_fallback.get("used")
                else _first_matching_line(selection_texts + entry_texts, ["1순위", "top pick", "blocked", "막혔"])
                )
            ),
            "entry_reason": (
                "오늘 신규 진입 판단이 아니라 전일/주말 이월 포지션입니다."
                if carryover_exit
                else (_RECOVERED_PARTIAL_ENTRY_NOTE if recovered_partial_exit else _entry_reason_line(entry_texts))
            ),
            "entry_confidence": _entry_confidence_for_operator_summary(
                entry_texts,
                action=action_label,
                buy_price=_pick(truth_price.get("broker_buy_price"), shared.get("broker_buy_price")),
            )
            if not exit_only_report
            else "",
            "entry_observation": entry_signal_snapshot,
            "holding_duration": authoritative_hold_label or _pick(
                shared.get("holding_duration"),
                report.get("hold_duration"),
                carryover_context.get("duration_label"),
            ),
            "exit_reason": exit_trigger_label,
            "exit_trigger": exit_trigger_label,
            "exit_trigger_basis": "monitor_signal_snapshot_not_realized_result",
            "exit_result_note": (
                "모니터 신호명과 별개로 Truth Surface 기준 실현 결과는 이익입니다."
                if recovered_partial_exit and (_num_opt(pnl_pct) or 0.0) > 0.0
                else ""
            ),
            "entry_execution_visibility": entry_execution_visibility,
            "entry_watch_summary_lines": entry_watch_lines,
            "recovered_partial_note": _RECOVERED_PARTIAL_EXIT_NOTE if recovered_partial_exit else "",
            "carryover_note": "오버나이트/주말 이월 포지션 청산은 당일 신규 스캐너 선정 평가에서 제외합니다." if carryover_exit else "",
            "carryover_context": carryover_context,
            "exit_observation": exit_signal_snapshot,
            "final_operator_summary": _authoritative_final_operator_summary(
                report,
                action=action_label,
                fallback=_translate_text(final.get("summary")).strip(),
            ),
        }
