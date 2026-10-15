"""Strategist: neutral fallback signals when news scoring raised.

T4-C (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/strategist_node.py::strategist_node` moved verbatim into a
Strategist Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging, persistence, the frame LLM
call and provider IO stay in the orchestrator at their original boundaries.
"""
from __future__ import annotations

from typing import Any, NamedTuple


class NewsFallbackSignals(NamedTuple):
    """Result of `news_exception_fallback_signals` (positional order = sorted output names)."""

    market_news_signal_map: Any
    news_signal_map: Any

class NewsDisabledSignals(NamedTuple):
    """Result of `news_disabled_signals` (positional order = sorted output names)."""

    market_news_signal_map: Any
    news_signal_map: Any

class NewsContextSummary(NamedTuple):
    """Result of `summarize_news_contexts` (positional order = sorted output names)."""

    candidate_news_ctx: Any
    market_news_ctx: Any
    news_avg_score: Any
    news_ctx: Any
    news_sent: Any

def news_exception_fallback_signals(news_collection_symbols, news_query_targets, now, *, facade):
    news_signal_map = {
        s: facade.make_signal(
            score=0.0,
            status=facade.SIGNAL_STATUS_FALLBACK,
            source="strategist_node",
            reason="news_sentiment_exception",
            ts=now,
        )
        for s in news_collection_symbols
    }
    market_news_signal_map = {
        q: facade.make_signal(
            score=0.0,
            status=facade.SIGNAL_STATUS_FALLBACK,
            source="strategist_node",
            reason="market_news_sentiment_exception",
            ts=now,
        )
        for q in news_query_targets
    }
    return NewsFallbackSignals(market_news_signal_map, news_signal_map)

def news_disabled_signals(news_collection_symbols, news_query_targets, now, *, facade):
    news_signal_map = {
        s: facade.make_signal(
            score=0.0,
            status=facade.SIGNAL_STATUS_FALLBACK,
            source="news_policy",
            reason="news_analysis_disabled",
            ts=now,
            )
            for s in news_collection_symbols
    }
    market_news_signal_map = {
        q: facade.make_signal(
            score=0.0,
            status=facade.SIGNAL_STATUS_FALLBACK,
            source="news_policy",
            reason="news_analysis_disabled",
            ts=now,
        )
        for q in news_query_targets
    }
    return NewsDisabledSignals(market_news_signal_map, news_signal_map)

def summarize_news_contexts(market_news_items_by_target, market_news_signal_map, news_collection_symbols, news_items_by_symbol, news_signal_map, *, facade):
    news_sent = {s: facade._signal_score(news_signal_map.get(s)) for s in news_collection_symbols}
    candidate_news_ctx = facade._news_context_summary(news_signal_map, news_items_by_symbol)
    market_news_ctx = facade._news_context_summary(market_news_signal_map, market_news_items_by_target)
    news_ctx = facade._merge_news_contexts(candidate_news_ctx, market_news_ctx)
    news_avg_score = facade._to_float(news_ctx.get("avg_score"), 0.0)
    return NewsContextSummary(candidate_news_ctx, market_news_ctx, news_avg_score, news_ctx, news_sent)
