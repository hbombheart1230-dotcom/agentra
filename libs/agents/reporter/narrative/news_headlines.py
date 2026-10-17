"""Reporter story-news narrative owner (decomposed) (news_headlines; definitions copied verbatim from libs/reporting/trade_story_pipeline_news.py)."""
from __future__ import annotations
import re
from typing import Any, List


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
