"""Pure text fragments for stage-specific Strategist prompts."""
from __future__ import annotations


def stage_specific_role_boundary(call_kind):
    if call_kind == "selected_symbol_tactical_refresh":
        return ("You may recommend how to watch the Scanner-selected symbol and runner-ups, " "but you do not approve orders. Monitor calculates the final entry signal and Commander owns hard risk gates. ")
    if call_kind == "stale_intraday_hold_review":
        return ("You review an already-held intraday position for hold, tighter exit handling, or exit pressure, " "but you do not place or approve sell orders. Monitor and Commander retain hard exit authority. ")
    if call_kind == "end_of_day_carry_review":
        return ("You review held positions near the close for flatten/carry risk, " "but you do not bypass deterministic closeout, broker truth, weekend, or risk controls. ")
    return "Do not select final stock and do not produce order instructions. "


def stage_specific_task_requirement(call_kind):
    if call_kind == "selected_symbol_tactical_refresh":
        return ("Your role is to compare Scanner rank #1 with compressed runner-ups, use selected_symbol_memory only as bounded symbol-specific evidence when memory is enabled, " "and output selected_symbol_decision, target_symbol, target_rank, runner_up_order, monitor_instruction, entry_policy_delta, memory_usage, market_regime_rail, news_quality, risk_off_exception_conditions, news_event_intelligence_usage, commander_actionability, confidence, and reason. ")
    if call_kind == "stale_intraday_hold_review":
        return ("Your role is to review whether the held position thesis is still intact, whether exit pressure is rising, and whether the current operating horizon should be maintained, shortened, or extended for this symbol. " "Do not blindly preserve the entry horizon. Stage 3 may revise only same-session horizons; overnight carry remains a Stage 4 decision. " "Output hold_review_decision, horizon_action, current_horizon, proposed_horizon, revised_hold_window, exit_pressure, thesis_status, evidence_confidence, data_quality, monitor_adjustment, priority_exit_triggers, next_check_minutes, and reason. ")
    if call_kind == "end_of_day_carry_review":
        return ("Your role is to review each held position near session close for carry risk versus same-day flattening. " "Output carry_review, portfolio_level_decision, and risk_note. ")
    return ("Your role is to choose exactly ONE playbook, provide a short rationale, produce a realistic and bounded monitor_entry_policy, propose tactical strategy detail, propose candidate_watch_policy, and produce explicit strategy_adjustment_directives that indicate what should change, what should be maintained, and why. ")


def stage_specific_user_requirement(call_kind):
    if call_kind == "selected_symbol_tactical_refresh":
        return ("Decision requirements: return the Stage 2 selected-symbol tactical refresh contract only. " "Compare rank #1 and runner-ups in one call, decide whether to watch rank #1, avoid rank #1, tighten rank #1 gates, cascade to runner-ups, or no-trade. " "Always include market_regime_rail, news_quality, and risk_off_exception_conditions so Commander and reports can audit whether market/news context changed the recommendation. " "If news_event_intelligence exists, include news_event_intelligence_usage as observation-only evidence usage; it must not imply direct BUY/SELL or gate bypass. " "Do not output a direct BUY/SELL. ")
    if call_kind == "stale_intraday_hold_review":
        return ("Decision requirements: return the Stage 3 stale intraday hold review contract only. " "Decide hold, tighten_exit, exit_now, or wait_until_next_check using the held position thesis, net PnL, VWAP, drawdown, time decay, and market context. " "Explicitly decide whether the active same-session horizon should be maintained, shortened, or extended. Do not authorize overnight carry in Stage 3. " "Keep the reason tied to the held symbol under review and do not attribute unrelated candidate or market theme labels to that position. " "Do not output a direct SELL order. ")
    if call_kind == "end_of_day_carry_review":
        return ("Decision requirements: return the Stage 4 end-of-day carry review contract only. " "For each held position decide carry_overnight, flatten_today, or reduce_or_flatten, then provide a portfolio-level carry decision. " "Do not bypass hard closeout, weekend, broker-truth, or risk controls. ")
    return ("Decision requirements: choose exactly ONE playbook, provide a short but concrete rationale, produce tactical_strategy, strategy_scores, rejected_strategy_reasons, candidate_watch_policy, a realistic and bounded monitor_entry_policy, and strategy_adjustment_directives that clearly state whether to maintain, tighten, relax, rebalance, deprioritize, prefer, or switch, which fields, axes, or playbooks are affected, and why this action is justified by deterministic evidence. ")
