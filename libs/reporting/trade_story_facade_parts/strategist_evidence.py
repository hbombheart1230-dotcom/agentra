from __future__ import annotations

from typing import Any, Dict


def _raw_strategist_evidence_impl(bundle_out: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(bundle_out.get("strategist_evidence"), dict):
        return dict(bundle_out.get("strategist_evidence") or {})
    evidence = bundle_out.get("evidence") if isinstance(bundle_out.get("evidence"), dict) else {}
    if isinstance(evidence.get("strategist"), dict):
        return dict(evidence.get("strategist") or {})
    return {}


def _strategist_trace_source_impl(
    canonical_strategist: Dict[str, Any],
    raw_strategist_evidence: Dict[str, Any],
) -> Dict[str, Any]:
    source = dict(canonical_strategist or {})
    raw = raw_strategist_evidence if isinstance(raw_strategist_evidence, dict) else {}
    # Raw evidence carries the structured news rows. Prefer those over stale
    # flattened market_context headlines when rebuilding reports.
    if raw.get("news_evidence_ranked") is not None:
        source["news_evidence_ranked"] = raw.get("news_evidence_ranked")
    if raw.get("market_context_snapshots") is not None and source.get("market_context_snapshots") is None:
        source["market_context_snapshots"] = raw.get("market_context_snapshots")
    return source


def _build_strategist_evidence_trace_impl(
    strategist: Dict[str, Any],
    *,
    selected_symbol: str = "",
    fallback_market_titles: Any = None,
    fallback_candidate_titles: Any = None,
    list_text: Any,
    collect_top_headlines: Any,
    collect_symbol_headlines_from_ranked_rows: Any,
    list_text_for_symbol: Any,
) -> Dict[str, Any]:
    _list_text = list_text
    _collect_top_headlines = collect_top_headlines
    _collect_symbol_headlines_from_ranked_rows = collect_symbol_headlines_from_ranked_rows
    _list_text_for_symbol = list_text_for_symbol
    data = strategist if isinstance(strategist, dict) else {}
    news_ranked_raw = data.get("news_evidence_ranked")
    news_ranked = news_ranked_raw if isinstance(news_ranked_raw, dict) else {}
    if not news_ranked and isinstance(news_ranked_raw, list):
        for event in news_ranked_raw:
            payload = event.get("payload") if isinstance(event, dict) else {}
            if isinstance(payload, dict) and (
                payload.get("candidate_news_ranked") is not None
                or payload.get("market_news_ranked") is not None
            ):
                news_ranked = dict(payload)
                break
    global_signal = data.get("global_sentiment_signal") if isinstance(data.get("global_sentiment_signal"), dict) else {}
    fear_index = data.get("fear_index") if isinstance(data.get("fear_index"), dict) else {}
    if not fear_index and isinstance(global_signal.get("fear_index"), dict):
        fear_index = dict(global_signal.get("fear_index") or {})
    market_rows = list(news_ranked.get("market_news_ranked") or [])
    candidate_rows = list(news_ranked.get("candidate_news_ranked") or [])
    market_headlines = _collect_top_headlines(market_rows, limit=3)
    symbol_headlines = _collect_symbol_headlines_from_ranked_rows(
        candidate_rows,
        symbol=selected_symbol,
        limit=3,
    ) or _collect_top_headlines(candidate_rows, limit=3, symbol=selected_symbol)
    if not market_headlines:
        market_headlines = _list_text(fallback_market_titles, limit=3, max_len=180)
    if not symbol_headlines:
        symbol_headlines = _list_text_for_symbol(
            fallback_candidate_titles,
            symbol=selected_symbol,
            limit=3,
            max_len=180,
        )
    candidate_hints = _list_text(
        data.get("candidate_symbols_hint"),
        limit=8,
        max_len=24,
    )
    key_events = _list_text(
        data.get("key_events") if data.get("key_events") is not None else data.get("key_events_hint"),
        limit=6,
        max_len=180,
    )
    return {
        "candidate_hints": candidate_hints,
        "news_query_targets": _list_text(
            data.get("news_query_targets")
            if data.get("news_query_targets") is not None
            else news_ranked.get("news_query_targets"),
            limit=8,
            max_len=80,
        ),
        "market_headlines": market_headlines,
        "symbol_headlines": symbol_headlines,
        "global_sentiment_signal": dict(global_signal or {}),
        "korea_indices": dict(global_signal.get("korea_indices") or {}) if isinstance(global_signal.get("korea_indices"), dict) else {},
        "fear_index": dict(fear_index or {}),
        "key_events": key_events,
    }
