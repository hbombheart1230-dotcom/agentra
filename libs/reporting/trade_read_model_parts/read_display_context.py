"""Display/context assembly of the trade read model result.

Second Pass (P1.5) intra-function extraction from `libs/reporting/trade_read_model.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def read_display_context(report_data, _trim_text, _clean_str_list, entry_obj, scanner_reason_human, monitor_reason_human, filters_human, market_context_human, bundle, lifecycle, holding_obj, monitor_exit_trigger, thresholds_snapshot, stop_policy_trace, blocker_trace, same_day_status, same_day_reason, data_source_quality, _clip, playbook_value, strategy_policy_source_value, execution_label_value, watch_axes, scanner_art, executor_art, monitor_art, *, facade):
    report_section_seeds = {
        "market_context_at_entry": facade.normalize_trade_report_section(
            report_data,
            "market_context_at_entry",
            (
                (entry_obj.get("strategist_context") or {}).get("market_context_summary")
                if isinstance(entry_obj.get("strategist_context"), dict)
                else market_context_human.get("summary") or ""
            ),
            trim_text=_trim_text,
            clean_str_list=_clean_str_list,
        ),
        "why_this_symbol_was_chosen": facade.normalize_trade_report_section(
            report_data,
            "why_this_symbol_was_chosen",
            entry_obj.get("reason_human") or scanner_reason_human.get("summary") or "",
            trim_text=_trim_text,
            clean_str_list=_clean_str_list,
        ),
        "strategist_summary": facade.normalize_trade_report_section(
            report_data,
            "strategist_summary",
            (
                (entry_obj.get("strategist_context") or {}).get("market_context_summary")
                if isinstance(entry_obj.get("strategist_context"), dict)
                else market_context_human.get("summary") or ""
            ),
            trim_text=_trim_text,
            clean_str_list=_clean_str_list,
        ),
        "entry_decision": facade.normalize_trade_report_section(
            report_data,
            "entry_decision",
            entry_obj.get("reason_human") or scanner_reason_human.get("summary") or "",
            trim_text=_trim_text,
            clean_str_list=_clean_str_list,
        ),
        "holding_monitoring_story": facade.normalize_trade_report_section(
            report_data,
            "holding_monitoring_story",
            monitor_reason_human.get("summary")
            or (
                f"Holding phase captured {len(list(holding_obj.get('run_ids') or []))} runs."
                if list(holding_obj.get("run_ids") or [])
                else ""
            ),
            trim_text=_trim_text,
            clean_str_list=_clean_str_list,
        ),
        "exit_decision": facade.normalize_trade_report_section(
            report_data,
            "exit_decision",
            (lifecycle.get("exit", {}).get("reason_human") if isinstance(lifecycle.get("exit"), dict) else "")
            or (
                bundle.get("execution_outcome_human").get("summary")
                if isinstance(bundle.get("execution_outcome_human"), dict)
                else ""
            )
            or monitor_reason_human.get("summary")
            or (
                "Position is still open; no closing SELL execution has been captured yet."
                if str(lifecycle.get("status") or "").lower() == "open"
                else ""
            ),
            trim_text=_trim_text,
            clean_str_list=_clean_str_list,
        ),
        "scanner_filters": facade.normalize_trade_report_section(
            report_data,
            "scanner_filters",
            filters_human.get("summary") or "",
            trim_text=_trim_text,
            clean_str_list=_clean_str_list,
        ),
        "execution_quality": facade.normalize_trade_report_section(
            report_data,
            "execution_quality",
            (
                bundle.get("execution_outcome_human").get("summary")
                if isinstance(bundle.get("execution_outcome_human"), dict)
                else ""
            ),
            trim_text=_trim_text,
            clean_str_list=_clean_str_list,
        ),
        "guard_approval_result": facade.normalize_trade_report_section(
            report_data,
            "guard_approval_result",
            (
                bundle.get("guard_reason_human").get("summary")
                if isinstance(bundle.get("guard_reason_human"), dict)
                else ""
            ),
            trim_text=_trim_text,
            clean_str_list=_clean_str_list,
        ),
        "reporter_evaluation": facade.normalize_trade_report_section(
            report_data,
            "reporter_evaluation",
            (
                bundle.get("reporter_status_human").get("summary")
                if isinstance(bundle.get("reporter_status_human"), dict)
                else ""
            ),
            trim_text=_trim_text,
            clean_str_list=_clean_str_list,
        ),
        "final_operator_conclusion": facade.normalize_trade_report_section(
            report_data,
            "final_operator_conclusion",
            (
                bundle.get("operator_conclusion_human").get("summary")
                if isinstance(bundle.get("operator_conclusion_human"), dict)
                else ""
            ),
            trim_text=_trim_text,
            clean_str_list=_clean_str_list,
        ),
    }

    context = {
        "scanner_selection_summary": _clip(
            scanner_art.get("summary")
            or scanner_art.get("selection_reason")
            or scanner_art.get("comparison")
        ),
        "scanner_score_drivers": (
            scanner_art.get("selected_symbol_score_drivers")
            if isinstance(scanner_art.get("selected_symbol_score_drivers"), dict)
            else {}
        ),
        "scanner_top_candidates": (
            list(scanner_art.get("top_candidates") or [])[:5]
            if isinstance(scanner_art.get("top_candidates"), list)
            else (list(scanner_art.get("ranked_candidates") or [])[:5] if isinstance(scanner_art.get("ranked_candidates"), list) else [])
        ),
        "monitor_entry_reason": _clip(
            monitor_art.get("summary")
            or monitor_art.get("decision_summary")
            or monitor_art.get("monitor_reason_human")
        ),
        "monitor_primary_blocker": _clip(
            monitor_art.get("primary_reason_code")
            or monitor_art.get("dominant_blocker")
            or monitor_art.get("no_trade_code")
        ),
        "monitor_exit_trigger": monitor_exit_trigger,
        "thresholds_snapshot": thresholds_snapshot,
        "watch_axes": list(watch_axes)[:8],
        "monitor_stop_policy_trace": stop_policy_trace,
        "monitor_blocker_trace": blocker_trace,
        "executor_execution_details": executor_art.get("execution_details")
        if isinstance(executor_art.get("execution_details"), dict)
        else {},
        "same_day_reporter_status": same_day_status,
        "same_day_reporter_linkage_status": same_day_status,
        "same_day_reporter_linkage_reason": same_day_reason,
        "data_source_quality": data_source_quality,
        "report_section_seeds": report_section_seeds,
        "scanner": {
            "summary": _clip(
                scanner_art.get("summary")
                or scanner_art.get("selection_reason")
                or scanner_art.get("comparison")
            ),
            "score_drivers": (
                scanner_art.get("selected_symbol_score_drivers")
                if isinstance(scanner_art.get("selected_symbol_score_drivers"), dict)
                else {}
            ),
            "top_candidates": (
                list(scanner_art.get("top_candidates") or [])[:5]
                if isinstance(scanner_art.get("top_candidates"), list)
                else (list(scanner_art.get("ranked_candidates") or [])[:5] if isinstance(scanner_art.get("ranked_candidates"), list) else [])
            ),
        },
        "monitor": {
            "entry_reason": _clip(
                monitor_art.get("summary")
                or monitor_art.get("decision_summary")
                or monitor_art.get("monitor_reason_human")
            ),
            "exit_trigger": monitor_exit_trigger,
            "primary_blocker": _clip(
                monitor_art.get("primary_reason_code")
                or monitor_art.get("dominant_blocker")
                or monitor_art.get("no_trade_code")
            ),
            "stop_policy_trace": stop_policy_trace,
            "blocker_trace": blocker_trace,
            "thresholds_snapshot": thresholds_snapshot,
            "watch_axes": list(watch_axes)[:8],
        },
        "strategist": {
            "playbook": playbook_value,
            "policy_source": strategy_policy_source_value,
            "themes": (
                (entry_obj.get("strategist_context") if isinstance(entry_obj.get("strategist_context"), dict) else {}).get("themes")
                if isinstance((entry_obj.get("strategist_context") if isinstance(entry_obj.get("strategist_context"), dict) else {}).get("themes"), list)
                else []
            ),
            "market_context_summary": _clip(
                (entry_obj.get("strategist_context") if isinstance(entry_obj.get("strategist_context"), dict) else {}).get("market_context_summary")
            ),
        },
        "executor": {
            "execution_label": execution_label_value,
            "execution_details": executor_art.get("execution_details")
            if isinstance(executor_art.get("execution_details"), dict)
            else {},
        },
    }
    return (context,)
