"""Strategist news sample/signal compaction and query-target building (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _compact_news_sample_for_llm_r3_impl(sample, *, max_symbols, max_titles, max_title_len, facade):
    out: Dict[str, Any] = {}
    if not isinstance(sample, dict):
        return out
    for symbol, value in list(sample.items())[:max_symbols]:
        if not isinstance(value, dict):
            continue
        rows = value.get("sample") if isinstance(value.get("sample"), list) else []
        titles: List[str] = []
        for row in rows[:max_titles]:
            if isinstance(row, dict):
                title = str(row.get("title") or "").strip()
            else:
                title = str(row or "").strip()
            if not title:
                continue
            if len(title) > max_title_len:
                title = title[: max_title_len - 3] + "..."
            titles.append(title)
        out[str(symbol)] = {
            "count": int(value.get("count") or len(rows)),
            "titles": titles,
        }
    return out


def _compact_global_signal_for_llm_r3_impl(signal, *, facade):
    src = signal if isinstance(signal, dict) else {}
    index_moves = src.get("index_moves") if isinstance(src.get("index_moves"), dict) else {}
    macro_moves = src.get("macro_moves") if isinstance(src.get("macro_moves"), dict) else {}
    fear_index = src.get("fear_index") if isinstance(src.get("fear_index"), dict) else {}
    korea_indices = src.get("korea_indices") if isinstance(src.get("korea_indices"), dict) else {}
    korea_rows = korea_indices.get("indices") if isinstance(korea_indices.get("indices"), dict) else {}
    krx_night_futures = (
        src.get("krx_night_futures") if isinstance(src.get("krx_night_futures"), dict) else {}
    )
    macro_indicators = src.get("macro_indicators") if isinstance(src.get("macro_indicators"), dict) else {}
    indicator_rows = macro_indicators.get("indicators") if isinstance(macro_indicators.get("indicators"), dict) else {}

    def _compact_korea_index(name: str) -> Dict[str, Any]:
        row = korea_rows.get(name) if isinstance(korea_rows.get(name), dict) else {}
        if not row:
            return {}
        return {
            "current": facade._round_optional(row.get("current"), 2),
            "previous_close": facade._round_optional(row.get("previous_close"), 2),
            "change_pct": facade._round_optional(row.get("change_pct"), 3),
            "change": facade._round_optional(row.get("change"), 2),
            "current_date": str(row.get("current_date") or ""),
            "previous_date": str(row.get("previous_date") or ""),
        }

    return {
        "score": facade._round_optional(src.get("score"), 4),
        "status": str(src.get("status") or ""),
        "source": str(src.get("source") or ""),
        "index_moves": {
            "sp500_pct": facade._round_optional(index_moves.get("sp500_pct"), 3),
            "nasdaq_pct": facade._round_optional(index_moves.get("nasdaq_pct"), 3),
            "dow_pct": facade._round_optional(index_moves.get("dow_pct"), 3),
            "kospi_pct": facade._round_optional(index_moves.get("kospi_pct"), 3),
            "kosdaq_pct": facade._round_optional(index_moves.get("kosdaq_pct"), 3),
            "kospi200_pct": facade._round_optional(index_moves.get("kospi200_pct"), 3),
            "krx_night_futures_pct": facade._round_optional(index_moves.get("krx_night_futures_pct"), 3),
        },
        "korea_indices": {
            "source": str(korea_indices.get("source") or ""),
            "status": str(korea_indices.get("status") or ""),
            "average_change_pct": facade._round_optional(korea_indices.get("average_change_pct"), 3),
            "breadth": facade._round_optional(korea_indices.get("breadth"), 3),
            "indices": {
                "KOSPI": _compact_korea_index("KOSPI"),
                "KOSDAQ": _compact_korea_index("KOSDAQ"),
                "KOSPI200": _compact_korea_index("KOSPI200"),
            },
        },
        "krx_night_futures": {
            "status": str(krx_night_futures.get("status") or ""),
            "source": str(krx_night_futures.get("source") or ""),
            "reason": str(krx_night_futures.get("reason") or ""),
            "current": facade._round_optional(krx_night_futures.get("current"), 3),
            "previous": facade._round_optional(krx_night_futures.get("previous"), 3),
            "change": facade._round_optional(krx_night_futures.get("change"), 3),
            "change_pct": facade._round_optional(krx_night_futures.get("change_pct"), 3),
            "basis": facade._round_optional(krx_night_futures.get("basis"), 3),
            "direction_pressure": str(krx_night_futures.get("direction_pressure") or ""),
            "behavior_effect": str(krx_night_futures.get("behavior_effect") or "observation_only"),
            "trading_action_allowed": bool(krx_night_futures.get("trading_action_allowed") is True),
        },
        "macro_moves": {
            "vix_pct": facade._round_optional(macro_moves.get("vix_pct"), 3),
            "vix_level": facade._round_optional(macro_moves.get("vix_level"), 2),
            "vix_level_pressure": facade._round_optional(macro_moves.get("vix_level_pressure"), 3),
            "dxy_pct": facade._round_optional(macro_moves.get("dxy_pct"), 3),
            "tnx_delta": facade._round_optional(macro_moves.get("tnx_delta"), 4),
        },
        "fear_index": {
            "level": facade._round_optional(fear_index.get("level"), 2),
            "change_pct": facade._round_optional(fear_index.get("change_pct"), 3),
            "level_pressure": facade._round_optional(fear_index.get("level_pressure"), 3),
        },
        "macro_indicators": {
            key: {
                "status": str((row or {}).get("status") or ""),
                "current": facade._round_optional((row or {}).get("current"), 4),
                "previous": facade._round_optional((row or {}).get("previous"), 4),
                "change_pct": facade._round_optional((row or {}).get("change_pct"), 4),
                "delta": facade._round_optional((row or {}).get("delta"), 5),
                "current_yield_pct": facade._round_optional((row or {}).get("current_yield_pct"), 5),
                "role": str((row or {}).get("role") or ""),
                "source": str((row or {}).get("source") or ""),
                "ticker": str((row or {}).get("ticker") or ""),
                "reason": str((row or {}).get("reason") or ""),
            }
            for key, row in indicator_rows.items()
            if isinstance(row, dict)
            and key
            in {
                "kr_3y_yield",
                "kr_10y_yield",
                "us_2y_yield",
                "us_10y_yield",
                "usdkrw",
                "dxy",
                "eurusd",
                "usdcny",
                "usdjpy",
                "kospi",
                "kospi200",
                "krx_night_futures",
                "sp500",
                "nasdaq",
            }
        },
    }


def _news_signal_label_r3_impl(score, *, facade):
    value = facade._to_float(score, 0.0)
    if value >= 0.25:
        return "positive"
    if value <= -0.25:
        return "negative"
    return "neutral"


def _news_item_title_for_llm_r3_impl(row, *, max_len, facade):
    if isinstance(row, dict):
        title = str(row.get("title") or row.get("headline") or "").strip()
    else:
        raw = str(row or "").strip()
        match = facade.re.search(r"title=['\"]([^'\"]+)['\"]", raw)
        title = match.group(1).strip() if match else raw
    title = facade.re.sub(r"<[^>]+>", "", title).strip()
    if len(title) > max_len:
        return title[: max_len - 3] + "..."
    return title


def _compact_news_signal_summary_for_llm_r3_impl(*, signal_map, sample, symbols, limit, facade):
    signals = signal_map if isinstance(signal_map, dict) else {}
    samples = sample if isinstance(sample, dict) else {}
    ordered_symbols: List[str] = []
    for symbol in list(symbols or []) + list(samples.keys()) + list(signals.keys()):
        text = str(symbol or "").strip()
        if text and text not in ordered_symbols:
            ordered_symbols.append(text)
    out: List[Dict[str, Any]] = []
    for symbol in ordered_symbols[:limit]:
        sig = signals.get(symbol) if isinstance(signals.get(symbol), dict) else {}
        score = facade._round_optional(sig.get("score"), 4)
        sample_row = samples.get(symbol) if isinstance(samples.get(symbol), dict) else {}
        rows = sample_row.get("sample") if isinstance(sample_row.get("sample"), list) else []
        evidence = [
            title
            for title in (facade._news_item_title_for_llm(row, max_len=120) for row in rows[:2])
            if title
        ]
        out.append(
            {
                "symbol": symbol,
                "score": score,
                "label": facade._news_signal_label(score),
                "status": str(sig.get("status") or ""),
                "headline_count": int(sample_row.get("count") or len(rows) or 0),
                "top_evidence": evidence,
            }
        )
    return out


def _selected_symbol_news_signal_for_llm_r3_impl(rows, selected_symbol, *, facade):
    symbol = str(selected_symbol or "").strip()
    if not symbol:
        return {}
    for row in rows:
        if str((row or {}).get("symbol") or "").strip() == symbol:
            return dict(row)
    return {"symbol": symbol, "score": None, "label": "unavailable", "status": "missing", "headline_count": 0, "top_evidence": []}


def _merge_news_collection_symbols_r3_impl(*, base_symbols, theme_symbols, limit, facade):
    out: List[str] = []
    seen: set[str] = set()
    for raw in [*list(base_symbols or []), *list(theme_symbols or [])]:
        symbol = str(raw or "").strip().upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        out.append(symbol)
        if len(out) >= max(1, int(limit)):
            break
    return out


def _build_market_news_query_targets_r3_impl(
    *,
    state,
    policy,
    global_signal,
    market_context_inputs,
    theme_hints,
    facade,
):
    limit = max(
        3,
        facade._to_int(
            policy.get("strategist_news_query_limit")
            if policy.get("strategist_news_query_limit") is not None
            else facade.os.getenv("STRATEGIST_NEWS_QUERY_LIMIT", "10"),
            10,
        ),
    )
    out: List[str] = []
    seen: set[str] = set()

    explicit_targets: List[Any] = []
    if isinstance(state.get("news_query_targets"), list):
        explicit_targets.extend(list(state.get("news_query_targets") or []))
    if isinstance(policy.get("news_query_targets"), list):
        explicit_targets.extend(list(policy.get("news_query_targets") or []))
    env_targets = str(facade.os.getenv("NEWS_QUERY_TARGETS", "") or "").strip()
    if env_targets:
        explicit_targets.extend([x.strip() for x in env_targets.split(",") if str(x).strip()])
    for raw in explicit_targets:
        facade._append_unique_text(out, seen, raw)

    global_score = facade._signal_score(global_signal)
    macro_risk = facade._to_float(market_context_inputs.get("macro_risk"), 0.0)
    index_trend = facade._to_float(market_context_inputs.get("index_trend"), 0.0)
    realized_volatility = facade._to_float(market_context_inputs.get("realized_volatility"), 0.0)
    market_breadth = facade._to_float(market_context_inputs.get("market_breadth"), 0.0)
    fear_index = global_signal.get("fear_index") if isinstance(global_signal.get("fear_index"), dict) else {}
    vix_level = facade._to_float(fear_index.get("level"), 0.0)
    vix_pressure = facade._to_float(fear_index.get("level_pressure"), 0.0)
    elevated_fear = vix_level >= 25.0 or vix_pressure >= 0.25
    theme_news_terms = facade._theme_news_query_terms(theme_hints, limit=4)
    for raw in theme_news_terms:
        facade._append_unique_text(out, seen, raw)
    if global_score <= -0.20 or macro_risk >= 0.65 or elevated_fear:
        base_queries = ["코스피", "미국 증시", "국제유가", "환율", "중동"]
    elif global_score >= 0.20 and index_trend >= -0.05:
        base_queries = ["코스피", "코스닥", "미국 증시", "위험선호", "주도주"]
    else:
        base_queries = ["코스피", "코스닥", "미국 증시", "증시 전망", "거시경제"]
    for raw in base_queries:
        facade._append_unique_text(out, seen, raw)

    if not theme_news_terms:
        for raw in list(theme_hints or [])[:5]:
            for q in facade._theme_to_news_queries(raw)[:2]:
                facade._append_unique_text(out, seen, q)

    if realized_volatility >= 0.03:
        facade._append_unique_text(out, seen, "변동성 확대")
    if market_breadth <= 0.40:
        for raw in ("하락 종목 수", "약세 업종"):
            facade._append_unique_text(out, seen, raw)
    elif market_breadth >= 0.60:
        for raw in ("상승 종목 수", "주도 섹터"):
            facade._append_unique_text(out, seen, raw)

    if macro_risk >= 0.65 or elevated_fear:
        for raw in ("국제유가", "환율", "달러", "중동", "방산", "금"):
            facade._append_unique_text(out, seen, raw)
    elif global_score <= -0.20:
        for raw in ("환율", "달러", "국채금리", "금", "방어주"):
            facade._append_unique_text(out, seen, raw)
    elif global_score >= 0.20 and index_trend >= 0.10:
        for raw in ("주도주", "실적주", "수출주"):
            facade._append_unique_text(out, seen, raw)

    for key in ("macro_events", "global_events", "major_events"):
        values = state.get(key)
        if not isinstance(values, list):
            continue
        for raw in list(values)[:3]:
            facade._append_unique_text(out, seen, raw)
        if values:
            break

    return out[:limit]
