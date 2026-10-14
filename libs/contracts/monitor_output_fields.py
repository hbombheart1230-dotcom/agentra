"""Monitor output artifact: cycle identity, position snapshot and decision fields (key order unchanged).

T3.5 (P1.5 Third Pass): contiguous statement runs / dict item ranges of `libs/contracts/agent_outputs.py::build_monitor_output_artifact` moved verbatim into
contract-owned projection stages. Locals enter as explicit parameters and leave as the returned record or dict; value
helpers are imported from `libs.contracts.agent_output_values`; remaining module globals of the public facade are
resolved at use time as `facade.NAME`. Final artifact assembly and `validate_artifact` stay in the public builder.
"""
from __future__ import annotations

from libs.contracts.agent_output_values import (
    _clip,
    _dict,
    _dict_list,
    _listify,
    _safe_int,
)


def monitor_artifact_decision_fields(decision_action, decision_phase, decision_status, decision_summary, exit_info, exit_vs_strategy_intent, monitor_output, open_position_count, primary_reason_code, secondary_reason_codes, state, symbol, thresholds):
    return {
            "cycle_id": _clip(state.get("cycle_id"), max_len=80),
            "session_id": _clip(state.get("session_id"), max_len=80),
            "trade_id": _clip(state.get("trade_id") or state.get("story_id"), max_len=120),
            "position_snapshot": {
                "open_position_count": open_position_count,
                "symbol": symbol,
                "qty": _safe_int(exit_info.get("qty")),
                "exit_qty": _safe_int(exit_info.get("exit_qty") or exit_info.get("qty")),
                "avg_price": exit_info.get("avg_price"),
                "current_price": exit_info.get("price"),
                "peak_price": exit_info.get("peak_price"),
            },
            "thresholds_guards_used": {
                "thresholds": thresholds,
                "min_hold_sec": _safe_int(exit_info.get("min_hold_sec")),
                "sell_cooldown_sec": _safe_int(exit_info.get("sell_cooldown_sec")),
                "exit_confirm_ticks": _safe_int(exit_info.get("exit_confirm_ticks")),
                "exit_confirm_count": _safe_int(exit_info.get("exit_confirm_count")),
            },
            "evaluation_summary": _clip(exit_info.get("monitor_reason") or exit_info.get("reason") or monitor_output.get("entry_exit_reason"), max_len=220),
            "decision": str(monitor_output.get("intent_side") or "NOOP").strip().upper(),
            "decision_phase": decision_phase,
            "decision_action": decision_action,
            "decision_status": decision_status,
            "decision_summary": decision_summary,
            "exit_vs_strategy_intent": dict(exit_vs_strategy_intent),
            "primary_reason_code": primary_reason_code,
            "primary_reason_text": _clip(primary_reason_code.replace("_", " "), max_len=220),
            "secondary_reason_codes": secondary_reason_codes
    }


def monitor_artifact_no_trade_fields(monitor_no_trade_surface):
    return {
            "no_trade_surface": dict(monitor_no_trade_surface),
            "decision_outcome": _clip(monitor_no_trade_surface.get("decision_outcome"), max_len=16),
            "pre_intent_decision": _clip(monitor_no_trade_surface.get("pre_intent_decision"), max_len=16),
            "no_trade_stage": _clip(monitor_no_trade_surface.get("no_trade_stage"), max_len=32),
            "no_trade_reason_code": _clip(monitor_no_trade_surface.get("no_trade_reason_code"), max_len=120),
            "no_trade_reason_summary": _clip(monitor_no_trade_surface.get("no_trade_reason_summary"), max_len=220),
            "dominant_blocker": _clip(monitor_no_trade_surface.get("dominant_blocker"), max_len=120),
            "blocker_family": _clip(monitor_no_trade_surface.get("blocker_family"), max_len=80),
            "blocker_metrics": _dict(monitor_no_trade_surface.get("blocker_metrics")),
            "distance_to_ready": _dict(monitor_no_trade_surface.get("distance_to_ready")),
            "near_ready_flag": bool(monitor_no_trade_surface.get("near_ready_flag")),
            "required_checks_failed": _listify(monitor_no_trade_surface.get("required_checks_failed"), limit=8, max_len=120),
            "preferred_checks_failed": _listify(monitor_no_trade_surface.get("preferred_checks_failed"), limit=8, max_len=120),
            "relaxable_checks_failed": _listify(monitor_no_trade_surface.get("relaxable_checks_failed"), limit=8, max_len=120),
            "evidence_snapshot": _dict(monitor_no_trade_surface.get("evidence_snapshot"))
    }


def monitor_artifact_handoff_focus_fields(entry_blocker_surface, entry_candidate_cascade, monitor_focus_context, scanner_monitor_handoff, threshold_snapshot):
    return {
            "entry_blocker_surface": dict(entry_blocker_surface),
            "scanner_monitor_handoff": dict(scanner_monitor_handoff),
            "scanner_selected_symbol": _clip(scanner_monitor_handoff.get("scanner_selected_symbol"), max_len=24),
            "scanner_rank": _safe_int(scanner_monitor_handoff.get("scanner_rank")),
            "scanner_score_total": scanner_monitor_handoff.get("scanner_score_total"),
            "scanner_score_breakdown": _dict(scanner_monitor_handoff.get("scanner_score_breakdown")),
            "scanner_top_candidates": _dict_list(scanner_monitor_handoff.get("scanner_top_candidates"), limit=3),
            "scanner_vs_monitor_alignment": _clip(scanner_monitor_handoff.get("scanner_vs_monitor_alignment"), max_len=80),
            "monitor_rejection_after_top_pick": bool(scanner_monitor_handoff.get("monitor_rejection_after_top_pick")),
            "monitor_rejection_reason_code": _clip(scanner_monitor_handoff.get("monitor_rejection_reason_code"), max_len=120),
            "monitor_rejection_reason_summary": _clip(scanner_monitor_handoff.get("monitor_rejection_reason_summary"), max_len=220),
            "handoff_trace": _listify(scanner_monitor_handoff.get("handoff_trace"), limit=6, max_len=120),
            "entry_candidate_cascade": dict(entry_candidate_cascade),
            "monitor_focus_context": dict(monitor_focus_context),
            "entry_candidate_symbol": _clip(monitor_focus_context.get("entry_candidate_symbol"), max_len=24),
            "entry_final_symbol": _clip(monitor_focus_context.get("entry_final_symbol"), max_len=24),
            "position_focus_symbol": _clip(monitor_focus_context.get("position_focus_symbol"), max_len=24),
            "monitor_output_symbol": _clip(monitor_focus_context.get("monitor_output_symbol"), max_len=24),
            "monitor_focus_mode": _clip(monitor_focus_context.get("focus_mode"), max_len=80),
            "threshold_snapshot": threshold_snapshot
    }
