"""Strategist: risk-off/risk-on policy adjustment from the global sentiment score.

T4-C (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/strategist_node.py::strategist_node` moved verbatim into a
Strategist Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging, persistence, the frame LLM
call and provider IO stay in the orchestrator at their original boundaries.
"""
from __future__ import annotations


def adjust_policy_for_global_sentiment(gs, policy):
    base_max_risk = float(policy.get("max_risk", 0.7))
    base_min_conf = float(policy.get("min_confidence", 0.6))
    off_th = float(policy.get("candidate_risk_off_threshold", -0.5))
    on_th = float(policy.get("candidate_risk_on_threshold", 0.5))

    if gs <= off_th:
        policy["max_risk"] = max(0.05, base_max_risk - 0.1)
        policy["min_confidence"] = min(0.99, base_min_conf + 0.1)
    elif gs >= on_th:
        policy["max_risk"] = min(1.0, base_max_risk + 0.1)
        policy["min_confidence"] = max(0.01, base_min_conf - 0.1)
    else:
        policy["max_risk"] = base_max_risk
        policy["min_confidence"] = base_min_conf
    return None
