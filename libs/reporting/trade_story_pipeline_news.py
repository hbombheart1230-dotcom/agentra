from __future__ import annotations

import html
import re
from typing import Any, Dict, List, Mapping

from libs.core.symbols import normalize_symbol
from libs.reporting.trade_report_common import clip_text as clip, list_text as _list_text, safe_float


def _headline_text(row: Any) -> str:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    item = row if isinstance(row, dict) else {}
    for key in ("title", "headline", "summary", "description", "text", "news_title"):
        text = _facade.clip(item.get(key), max_len=180)
        if text:
            return text
    return ""


def _clean_news_fragment(value: Any, *, max_len: int = 180) -> str:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    text = html.unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return _facade.clip(text, max_len=max_len)


def _news_item_field(raw: Any, field: str) -> str:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    text = str(raw or "")
    for quote in ("'", '"'):
        marker = f"{field}={quote}"
        start = text.find(marker)
        if start < 0:
            continue
        start += len(marker)
        end = text.find(f"{quote}, ", start)
        if end < 0:
            end = text.find(quote, start)
        if end > start:
            return _facade._clean_news_fragment(text[start:end])
    return ""


def _news_sample_parts(raw: Any) -> Dict[str, str]:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    if isinstance(raw, dict):
        return {
            "title": _facade._clean_news_fragment(
                raw.get("title") or raw.get("headline") or raw.get("news_title")
            ),
            "summary": _facade._clean_news_fragment(
                raw.get("summary") or raw.get("description") or raw.get("text"),
                max_len=260,
            ),
            "symbol": _facade._norm_symbol_text(raw.get("symbol") or raw.get("code") or raw.get("ticker")),
        }
    return {
        "title": _facade._news_item_field(raw, "title") or _facade._clean_news_fragment(raw),
        "summary": _facade._news_item_field(raw, "summary"),
        "symbol": _facade._norm_symbol_text(_facade._news_item_field(raw, "symbol")),
    }


def _norm_symbol_text(value: Any) -> str:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    return _facade.normalize_symbol(value, allow_test_symbols=True).strip().upper()


def _symbol_name_from_text(text: Any, symbol: str) -> str:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    target = _facade._norm_symbol_text(symbol)
    if not target:
        return ""
    cleaned = _facade._clean_news_fragment(text, max_len=320)
    pattern = rf"([A-Za-z0-9가-힣&·.\-\s]{{1,40}})\(\s*{re.escape(target)}\s*\)"
    match = re.search(pattern, cleaned)
    if not match:
        return ""
    name = re.sub(r"\s+", " ", str(match.group(1) or "")).strip(" ,;:·-")
    if not name:
        return ""
    # Keep the nearest token phrase; news snippets often have a long prefix.
    pieces = re.split(r"[,\s]+", name)
    return pieces[-1].strip() if pieces else name


def _sample_title_directly_matches_symbol(parts: Dict[str, str], symbol: str) -> bool:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    target = _facade._norm_symbol_text(symbol)
    title = str(parts.get("title") or "")
    if not target or not title:
        return False
    if target in title:
        return True
    symbol_name = _facade._symbol_name_from_text(parts.get("summary"), target)
    return bool(symbol_name and symbol_name in title)


def _format_symbol_news_headline(symbol: str, title: str, *, indirect: bool = False) -> str:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    target = _facade._norm_symbol_text(symbol)
    cleaned = _facade._clean_news_fragment(title)
    if not cleaned:
        return ""
    if re.match(r"\s*\d{6}\s*:", cleaned):
        return cleaned
    if indirect:
        return f"{target}: 관련 테마 뉴스 - {cleaned}" if target else f"관련 테마 뉴스 - {cleaned}"
    return f"{target}: {cleaned}" if target else cleaned


def _collect_symbol_headlines_from_ranked_rows(rows: Any, *, symbol: str, limit: int = 3) -> List[str]:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    if not isinstance(rows, list):
        return []
    target = _facade._norm_symbol_text(symbol)
    if not target:
        return []
    direct: List[str] = []
    indirect: List[str] = []
    for row in rows:
        item = row if isinstance(row, dict) else {}
        row_target = _facade._norm_symbol_text(
            item.get("target")
            or item.get("symbol")
            or item.get("code")
            or item.get("ticker")
        )
        if row_target and row_target != target:
            continue
        samples = item.get("sample_titles") or item.get("sample") or item.get("headlines") or []
        if not isinstance(samples, list):
            samples = [samples]
        if not samples:
            samples = [item]
        for sample in samples:
            parts = _facade._news_sample_parts(sample)
            title = parts.get("title") or ""
            if not title:
                continue
            sample_symbol = _facade._norm_symbol_text(parts.get("symbol"))
            summary_has_target = bool(target in str(parts.get("summary") or ""))
            title_is_direct = _facade._sample_title_directly_matches_symbol(parts, target)
            if sample_symbol and sample_symbol != target and not summary_has_target:
                continue
            bucket = direct if title_is_direct else indirect
            headline = _facade._format_symbol_news_headline(target, title, indirect=not title_is_direct)
            if headline and headline not in bucket:
                bucket.append(headline)
    picked = direct if direct else indirect
    return picked[: max(1, int(limit))]


def _headline_matches_symbol(row: Any, symbol: str) -> bool:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    item = row if isinstance(row, dict) else {}
    target = _facade._norm_symbol_text(symbol)
    if not target:
        return False
    scalar_candidates = [
        item.get("symbol"),
        item.get("code"),
        item.get("ticker"),
        item.get("query_target"),
        item.get("query"),
        item.get("news_query_target"),
    ]
    for candidate in scalar_candidates:
        if _facade._norm_symbol_text(candidate) == target:
            return True
    for key in ("symbols", "tickers", "related_symbols"):
        values = item.get(key)
        if not isinstance(values, list):
            continue
        for candidate in values:
            if _facade._norm_symbol_text(candidate) == target:
                return True
    joined = " ".join(
        [
            str(item.get("title") or ""),
            str(item.get("headline") or ""),
            str(item.get("summary") or ""),
            str(item.get("description") or ""),
            str(item.get("query_target") or ""),
        ]
    ).upper()
    return bool(target and target in joined)


def _collect_top_headlines(rows: Any, *, limit: int = 3, symbol: str = "") -> List[str]:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    if not isinstance(rows, list):
        return []
    filtered: List[str] = []
    fallback: List[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        text = _facade._headline_text(row)
        if not text:
            continue
        if text not in fallback:
            fallback.append(text)
        if symbol and _facade._headline_matches_symbol(row, symbol) and text not in filtered:
            filtered.append(text)
    picked = filtered if symbol else fallback
    return picked[: max(1, int(limit))]


def _title_prefixed_symbol(value: Any) -> str:
    match = re.match(r"\s*(\d{6})\s*:", str(value or ""))
    return match.group(1) if match else ""


def _list_text_for_symbol(values: Any, *, symbol: str, limit: int = 3, max_len: int = 180) -> List[str]:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    target = _facade._norm_symbol_text(symbol)
    rows = _facade._list_text(values, limit=50, max_len=max_len)
    if not target:
        return rows[: max(1, int(limit))]
    matched: List[str] = []
    untagged: List[str] = []
    has_detectable_symbol = False
    for row in rows:
        row_symbol = _facade._title_prefixed_symbol(row)
        if row_symbol:
            has_detectable_symbol = True
        if row_symbol == target and row not in matched:
            matched.append(row)
        elif not row_symbol and row not in untagged:
            untagged.append(row)
    if matched:
        return matched[: max(1, int(limit))]
    if not has_detectable_symbol:
        return untagged[: max(1, int(limit))]
    return []


def _optional_float(value: Any) -> Any:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    if value in (None, ""):
        return None
    return _facade.safe_float(value, 0.0)


def _build_news_scanner_contribution_trace(
    *,
    selected_symbol: str,
    selected_score: Any,
    selected_sources: List[str],
    score_breakdown: Dict[str, Any],
    component_snapshot: Dict[str, Any],
    strategist: Dict[str, Any],
) -> Dict[str, Any]:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    positive_total = sum(max(_facade.safe_float(value, 0.0), 0.0) for value in dict(score_breakdown or {}).values())
    key_rows: Dict[str, Dict[str, Any]] = {}
    for key in ("trading_value", "momentum", "trend", "theme_boost", "sentiment"):
        value = _facade.safe_float(score_breakdown.get(key), 0.0)
        key_rows[key] = {
            "value": value,
            "positive_share_pct": (100.0 * value / positive_total) if positive_total > 0 else 0.0,
        }

    ranked = strategist.get("news_evidence_ranked") if isinstance(strategist.get("news_evidence_ranked"), dict) else {}
    market_headlines = _facade._collect_top_headlines(list(ranked.get("market_news_ranked") or []), limit=3)
    symbol_headlines = _facade._collect_top_headlines(
        list(ranked.get("candidate_news_ranked") or []),
        limit=3,
        symbol=selected_symbol,
    )
    query_targets = _facade._list_text(
        strategist.get("news_query_targets")
        if strategist.get("news_query_targets") is not None
        else ranked.get("news_query_targets"),
        limit=8,
        max_len=80,
    )
    decision_frame = strategist.get("decision_frame") if isinstance(strategist.get("decision_frame"), dict) else {}
    theme_packet = strategist.get("theme_strength_packet") if isinstance(strategist.get("theme_strength_packet"), dict) else {}
    if not theme_packet and isinstance(decision_frame.get("theme_strength_packet"), dict):
        theme_packet = dict(decision_frame.get("theme_strength_packet") or {})
    theme_source = str(strategist.get("theme_source") or theme_packet.get("source") or "").strip()
    theme_status = str(strategist.get("theme_source_status") or theme_packet.get("status") or "").strip()
    theme_reason = str(strategist.get("theme_source_reason") or theme_packet.get("reason") or "").strip()

    return {
        "selected_score_total": _facade.safe_float(selected_score, 0.0),
        "positive_contribution_total": positive_total,
        "core_score_contributions": key_rows,
        "sentiment_inputs": {
            "news_sentiment_score": _facade._optional_float(component_snapshot.get("news_sentiment")),
            "global_sentiment_score": _facade._optional_float(component_snapshot.get("global_sentiment")),
            "blended_sentiment_component": _facade._optional_float(component_snapshot.get("sentiment_component")),
            "weighted_sentiment_score_contribution": _facade.safe_float(score_breakdown.get("sentiment"), 0.0),
        },
        "theme_alignment_trace": {
            "theme_boost_score_contribution": _facade.safe_float(score_breakdown.get("theme_boost"), 0.0),
            "theme_source_matched": ("sector_theme" in selected_sources) or _facade.safe_float(score_breakdown.get("theme_boost"), 0.0) > 0.0,
            "strategist_themes": _facade._list_text(strategist.get("themes"), limit=6, max_len=80),
            "theme_source": theme_source,
            "theme_source_status": theme_status,
            "theme_source_reason": theme_reason,
            "top_themes": _facade._list_text(theme_packet.get("top_themes"), limit=6, max_len=80),
            "theme_scores": dict(theme_packet.get("theme_scores") or {}) if isinstance(theme_packet.get("theme_scores"), dict) else {},
        },
        "news_linkage_trace": {
            "news_query_targets": query_targets,
            "symbol_headlines_used": symbol_headlines,
            "market_headlines_used": market_headlines,
            "symbol_headline_count": len(symbol_headlines),
            "market_headline_count": len(market_headlines),
        },
    }
