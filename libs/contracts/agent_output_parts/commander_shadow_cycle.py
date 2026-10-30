from typing import Any, Dict


def end_of_cycle_summary(*, no_trade_reason_code: str, reason_summary: str, actual_runtime: Dict[str, Any], next_action_recommendation: str, recommendation_gap: str, facade) -> Dict[str, Any]:
    return {"no_trade_reason_code": no_trade_reason_code, "reason_summary": reason_summary, "actual_runtime": actual_runtime, "next_action_recommendation": next_action_recommendation, "recommendation_gap": recommendation_gap}
