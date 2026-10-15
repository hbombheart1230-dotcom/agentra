"""Strategist: deterministic candidate rerank with the negative-news filter and risk-off cap.

T4-C (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/strategist_node.py::strategist_node` moved verbatim into a
Strategist Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging, persistence, the frame LLM
call and provider IO stay in the orchestrator at their original boundaries.
"""
from __future__ import annotations


def rerank_candidates_by_news_and_global(candidates, gs, k, news_sent, policy):
    w_news = float(policy.get("candidate_news_weight", 0.2))
    w_g = float(policy.get("candidate_global_weight", 0.1))
    neg_th = float(policy.get("candidate_negative_news_threshold", -0.7))

    # assign candidate_score
    scored = []
    candidate_meta = {str(c.get("symbol")): dict(c) for c in candidates if isinstance(c, dict)}
    for idx, c in enumerate(candidates):
        s = c["symbol"]
        rank_bias = (len(candidates) - idx) / max(len(candidates), 1) * 0.01  # small deterministic tie-break
        cs = rank_bias + (w_news * news_sent.get(s, 0.0)) + (w_g * gs)
        scored.append((s, cs, news_sent.get(s, 0.0), c.get("why") or ""))

    # filter overly negative news, but don't drop below 3 items if possible
    filtered = [t for t in scored if t[2] >= neg_th]
    if len(filtered) >= 3:
        scored = filtered

    scored.sort(key=lambda x: x[1], reverse=True)
    candidates = []
    for (s, cs, _ns, why) in scored:
        base = dict(candidate_meta.get(s) or {})
        base["symbol"] = s
        base["why"] = why
        base["rank_score"] = float(cs)
        candidates.append(base)

    # risk-off reduces count
    if gs <= float(policy.get("candidate_risk_off_threshold", -0.5)):
        max_cnt = int(policy.get("candidate_max_count_risk_off", 3))
        candidates = candidates[: max(1, max_cnt)]
    else:
        candidates = candidates[:k]
    return candidates
