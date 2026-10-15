"""Strategist: regime score, sentiment score and labels.

T4-C (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/strategist_node.py::strategist_node` moved verbatim into a
Strategist Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging, persistence, the frame LLM
call and provider IO stay in the orchestrator at their original boundaries.
"""
from __future__ import annotations

from typing import Any, NamedTuple


class RegimeSentimentScores(NamedTuple):
    """Result of `score_market_regime_and_sentiment` (positional order = sorted output names)."""

    market_regime: Any
    market_sentiment: Any
    regime_score: Any
    sentiment_score: Any

def score_market_regime_and_sentiment(gs, market_context_inputs, news_avg_score, news_ctx, *, facade):
    regime_score = facade._compose_regime_score(
        global_score=gs,
        news_score=news_avg_score,
        market_context_inputs=market_context_inputs,
    )
    sentiment_score = float(
        facade._clamp(
            (0.60 * gs)
            + (0.30 * facade._to_float(news_ctx.get("avg_score"), 0.0))
            + (0.10 * facade._to_float(market_context_inputs.get("index_trend"), 0.0)),
            -1.0,
            1.0,
        )
    )
    market_regime = facade._risk_regime_label(regime_score)
    market_sentiment = facade._market_sentiment_label(sentiment_score)
    return RegimeSentimentScores(market_regime, market_sentiment, regime_score, sentiment_score)
