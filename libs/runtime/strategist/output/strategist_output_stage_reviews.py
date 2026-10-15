"""Strategist: stage review and decision fields from AI overrides.

T4-C (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/strategist_node.py::strategist_node` moved verbatim into a
Strategist Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging, persistence, the frame LLM
call and provider IO stay in the orchestrator at their original boundaries.
"""
from __future__ import annotations


def fill_strategist_output_stage_reviews(ai_overrides, strategist_output):
    for stage_output_key in (
        "selected_symbol_tactical_review",
        "stale_intraday_hold_review",
        "end_of_day_carry_review",
    ):
        if isinstance(ai_overrides.get(stage_output_key), dict):
            strategist_output[stage_output_key] = dict(ai_overrides.get(stage_output_key) or {})
    if ai_overrides.get("selected_symbol_decision") not in (None, ""):
        strategist_output["selected_symbol_decision"] = str(ai_overrides.get("selected_symbol_decision") or "")
        strategist_output["target_symbol"] = str(ai_overrides.get("target_symbol") or "")
        strategist_output["target_rank"] = int(ai_overrides.get("target_rank") or 0)
        strategist_output["runner_up_order"] = list(ai_overrides.get("runner_up_order") or [])
        strategist_output["monitor_instruction"] = dict(ai_overrides.get("monitor_instruction") or {})
        strategist_output["entry_policy_delta"] = dict(ai_overrides.get("entry_policy_delta") or {})
        strategist_output["memory_usage"] = dict(ai_overrides.get("memory_usage") or {})
        strategist_output["market_regime_rail"] = str(
            ai_overrides.get("market_regime_rail") or strategist_output.get("market_regime_rail") or ""
        )
        strategist_output["news_quality"] = (
            dict(ai_overrides.get("news_quality") or {})
            if isinstance(ai_overrides.get("news_quality"), dict)
            else dict(strategist_output.get("news_quality") or {})
        )
        strategist_output["risk_off_exception_conditions"] = list(
            ai_overrides.get("risk_off_exception_conditions")
            or strategist_output.get("risk_off_exception_conditions")
            or []
        )
        strategist_output["commander_actionability"] = str(ai_overrides.get("commander_actionability") or "")
    if ai_overrides.get("hold_review_decision") not in (None, ""):
        strategist_output["hold_review_decision"] = str(ai_overrides.get("hold_review_decision") or "")
    if ai_overrides.get("portfolio_level_decision") not in (None, ""):
        strategist_output["carry_review"] = list(ai_overrides.get("carry_review") or [])
        strategist_output["portfolio_level_decision"] = str(ai_overrides.get("portfolio_level_decision") or "")
    return None
