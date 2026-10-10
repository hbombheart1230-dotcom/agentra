"""Pure Markdown report headline cleanup, symbol matching and display labels.

Old mutable facade helpers are supplied per-call; no trading authority.
"""
from __future__ import annotations
from typing import Any, List


def _strip_html_tags_impl(text: Any, *, html, re, _clip) -> str:
    raw = html.unescape(_clip(text, 300))
    if not raw:
        return ""
    raw = re.sub(r"<[^>]+>", "", raw)
    raw = raw.replace("NewsItem(title='", "")
    raw = raw.split("', url='", 1)[0]
    return re.sub(r"\s+", " ", raw).strip()



def _clean_news_title_impl(text: Any, *, _strip_html_tags) -> str:
    return _strip_html_tags(text).rstrip(".")



def _sample_news_titles_impl(values: Any, limit: int = 2, *, _listify, _clean_news_title) -> List[str]:
    out: List[str] = []
    seen = set()
    for raw in _listify(values):
        cleaned = _clean_news_title(raw)
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        out.append(cleaned)
        if len(out) >= limit:
            break
    return out



def _normalize_news_symbol_impl(value: Any, *, re) -> str:
    if value is None:
        return ""
    match = re.search(r"\b(\d{6})\b", str(value))
    return match.group(1) if match else ""



def _news_symbol_from_item_impl(value: Any, *, re, _normalize_news_symbol) -> str:
    if isinstance(value, dict):
        for key in ("symbol", "code", "stock_code", "ticker"):
            symbol = _normalize_news_symbol(value.get(key))
            if symbol:
                return symbol
        return ""
    raw = str(value or "")
    match = re.match(r"\s*(\d{6})\s*:", raw)
    if match:
        return match.group(1)
    match = re.search(r"\bsymbol=['\"]?(\d{6})['\"]?", raw)
    return match.group(1) if match else ""



def _sample_news_titles_for_symbol_impl(symbol: Any, *sources: Any, limit: int = 2, _normalize_news_symbol, _listify, _sample_news_titles, _news_symbol_from_item) -> List[str]:
    target = _normalize_news_symbol(symbol)
    untagged_fallback: List[Any] = []
    for source in sources:
        rows = _listify(source)
        if not rows:
            continue
        if not target:
            return _sample_news_titles(rows, limit=limit)
        matched: List[Any] = []
        has_detectable_symbol = False
        for row in rows:
            row_symbol = _news_symbol_from_item(row)
            if row_symbol:
                has_detectable_symbol = True
            if row_symbol == target:
                matched.append(row)
        if matched:
            return _sample_news_titles(matched, limit=limit)
        if not has_detectable_symbol and not untagged_fallback:
            # Curated symbol-only headline lists may omit the code prefix.
            untagged_fallback = rows
    if untagged_fallback:
        return _sample_news_titles(untagged_fallback, limit=limit)
    return []



def _mismatched_symbol_news_bullet_impl(text: Any, symbol: Any, *, re, _normalize_news_symbol) -> bool:
    target = _normalize_news_symbol(symbol)
    if not target:
        return False
    raw = str(text or "")
    if "대표 종목/섹터 뉴스" not in raw and "종목 뉴스" not in raw:
        return False
    symbols = set(re.findall(r"\b(\d{6})\s*:", raw))
    return bool(symbols and target not in symbols)



def _news_linkage_strength_label_impl(value: Any, *, _clip, _metadata_value) -> str:
    lowered = _clip(value, 40).lower()
    return {
        "weak": "약한 편이었습니다",
        "moderate": "보통 수준이었습니다",
        "strong": "강한 편이었습니다",
    }.get(lowered, _metadata_value(value) or "-")

