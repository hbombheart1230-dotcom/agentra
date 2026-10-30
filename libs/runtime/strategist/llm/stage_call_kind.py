"""Pure resolver for the Strategist stage call kind."""
from __future__ import annotations


def resolve_strategist_llm_call_kind(payload):
    compact = payload if isinstance(payload, dict) else {}
    context = compact.get("commander_refresh_context") if isinstance(compact.get("commander_refresh_context"), dict) else {}
    if bool(context.get("requested")):
        scope = str(context.get("refresh_scope") or "").strip().lower()
        reason = str(context.get("reason") or "").strip().lower()
        carry_state = str(context.get("carry_state") or "").strip().lower()
        if ("closeout" in scope or "closeout" in reason or "end_of_day" in scope or "end_of_day" in reason or "eod" in scope or "eod" in reason or "overnight_review" in scope or "overnight_review" in reason or "overnight" in reason or reason in {"end_of_day_carry_review", "session_closeout_carry_review"}):
            return "end_of_day_carry_review"
        if ("open_position" in scope or "hold" in scope or "position" in scope or "hold" in reason or "loss_threshold" in reason or "preopen_carry" in reason or carry_state):
            return "stale_intraday_hold_review"
        return "selected_symbol_tactical_refresh"
    explicit = str(compact.get("resolved_call_kind") or compact.get("call_kind") or "").strip().lower()
    if explicit in {"selected_symbol_tactical_refresh", "stale_intraday_hold_review", "end_of_day_carry_review", "market_strategy_frame"}:
        return explicit
    return "market_strategy_frame"
