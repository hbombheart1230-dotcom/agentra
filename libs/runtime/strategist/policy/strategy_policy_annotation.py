"""Strategist: market and scanner policy annotations on the strategy policy.

T4-C (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/strategist_node.py::strategist_node` moved verbatim into a
Strategist Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging, persistence, the frame LLM
call and provider IO stay in the orchestrator at their original boundaries.
"""
from __future__ import annotations

from typing import Any, NamedTuple


class HorizonMonitorPolicy(NamedTuple):
    """Result of `attach_horizon_to_monitor_policy_and_plan` (positional order = sorted output names)."""



def annotate_strategy_policy_market_scanner(candidate_watch_policy, llm_requested_playbook, playbook, pre_llm_playbook, rejected_strategy_reasons, requested_playbook, requested_playbook_source, strategy_policy, strategy_scores, tactical_strategy, tactical_subtype):
    market_policy = strategy_policy.get("market_policy") if isinstance(strategy_policy.get("market_policy"), dict) else {}
    market_policy["pre_llm_playbook"] = pre_llm_playbook
    market_policy["llm_requested_playbook"] = llm_requested_playbook
    market_policy["requested_playbook"] = requested_playbook
    market_policy["requested_playbook_source"] = requested_playbook_source
    market_policy["final_playbook"] = playbook
    market_policy["tactical_strategy"] = tactical_strategy
    market_policy["tactical_subtype"] = tactical_subtype
    market_policy["strategy_scores"] = dict(strategy_scores)
    market_policy["rejected_strategy_reasons"] = dict(rejected_strategy_reasons)
    strategy_policy["market_policy"] = dict(market_policy)
    scanner_policy = strategy_policy.get("scanner_policy") if isinstance(strategy_policy.get("scanner_policy"), dict) else {}
    scanner_policy["candidate_watch_policy"] = dict(candidate_watch_policy)
    strategy_policy["scanner_policy"] = dict(scanner_policy)
    return None

def attach_horizon_to_commander_context(commander_context, commander_horizon_policy, horizon_context, strategic_answers, strategist_refresh_context, strategy_policy):
    commander_context["strategist_refresh_context"] = strategist_refresh_context
    open_position_refresh_context = (
        dict(commander_context.get("open_position_refresh_context") or {})
        if isinstance(commander_context.get("open_position_refresh_context"), dict)
        else {}
    )
    if open_position_refresh_context:
        open_position_refresh_context["commander_horizon_policy"] = dict(commander_horizon_policy)
        open_position_refresh_context["horizon_context"] = dict(horizon_context)
        commander_context["open_position_refresh_context"] = open_position_refresh_context
    commander_context["commander_horizon_policy"] = dict(commander_horizon_policy)
    commander_context["horizon_context"] = dict(horizon_context)
    strategy_policy["commander_context"] = dict(commander_context)
    if isinstance((strategic_answers.get("q15_commander_refresh_context") or {}), dict):
        strategic_answers["q15_commander_refresh_context"] = {
            **dict(strategic_answers.get("q15_commander_refresh_context") or {}),
            "commander_horizon_policy": dict(commander_horizon_policy),
            "horizon_context": dict(horizon_context),
        }
    return None

def attach_horizon_to_monitor_policy_and_plan(commander_horizon_policy, strategist_horizon_proposal, strategist_plan, strategy_horizon_feedback, strategy_policy):
    strategy_monitor_policy = (
        dict(strategy_policy.get("monitor_policy") or {})
        if isinstance(strategy_policy.get("monitor_policy"), dict)
        else {}
    )
    strategy_monitor_policy["strategy_horizon_feedback"] = dict(strategy_horizon_feedback)
    strategy_monitor_policy["strategist_horizon_proposal"] = dict(strategist_horizon_proposal)
    strategy_monitor_policy["commander_horizon_policy"] = dict(commander_horizon_policy)
    strategy_monitor_policy["horizon_policy"] = dict(commander_horizon_policy)
    strategy_monitor_policy["strategy_horizon"] = str(strategy_horizon_feedback.get("strategy_horizon") or "")
    strategy_monitor_policy["expected_hold_window"] = dict(strategy_horizon_feedback.get("expected_hold_window") or {})
    strategy_monitor_policy["exit_guidance"] = dict(strategy_horizon_feedback.get("exit_guidance") or {})
    strategy_policy["monitor_policy"] = strategy_monitor_policy
    strategy_policy["commander_horizon_policy"] = dict(commander_horizon_policy)
    strategist_plan["strategy_horizon_feedback"] = dict(strategy_horizon_feedback)
    strategist_plan["strategist_horizon_proposal"] = dict(strategist_horizon_proposal)
    strategist_plan["commander_horizon_policy"] = dict(commander_horizon_policy)
    strategist_plan["strategy_horizon"] = str(strategy_horizon_feedback.get("strategy_horizon") or "")
    strategy_policy["strategist_plan"] = dict(strategist_plan)
    return None
