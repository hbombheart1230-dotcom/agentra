"""Reporter story-news narrative owner (decomposed) (news_text; definitions copied verbatim from libs/reporting/trade_story_pipeline_news.py)."""
from __future__ import annotations
import html
import re
from typing import Any, Dict


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
