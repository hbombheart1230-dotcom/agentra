"""AI report market-context sanitising, index snapshot and headline text helpers (deterministic, read-only).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _is_market_context_noise_bullet_r3_impl(value, *, facade):
    text = facade._clip(value, max_len=260).strip()
    if not text:
        return True
    lowered = text.lower()
    if lowered.startswith("news input:"):
        return True
    if lowered.startswith("news query targets:"):
        return True
    if "headlines were considered across" in lowered:
        return True
    if text.startswith("뉴스 입력 요약은"):
        return True
    if text.startswith("뉴스 조회 대상은"):
        return True
    if "관련 헤드라인" in text and "반영" in text:
        return True
    return False


def _sanitize_market_context_summary_r3_impl(value, *, facade):
    text = facade._clip(value, max_len=600).strip()
    if not text:
        return ""
    cleaned = facade.re.sub(
        r"[^.]*\b\d+\s*headlines were considered across \d+\s*targets[^.]*\.?\s*",
        " ",
        text,
        flags=facade.re.IGNORECASE,
    )
    cleaned = facade.re.sub(
        r"[^.]*관련 헤드라인\s*\d+건[^.]*\.?\s*",
        " ",
        cleaned,
    )
    cleaned = facade.re.sub(r"\s{2,}", " ", cleaned).strip(" .")
    return cleaned or text


def _extract_us_indices_snapshot_r3_impl(events, *, facade):
    for row in facade._listify(events, max_items=8, max_len=220):
        match = facade.re.search(
            r"sp500=([+-]?\d+(?:\.\d+)?)%\s+nasdaq=([+-]?\d+(?:\.\d+)?)%\s+dow=([+-]?\d+(?:\.\d+)?)%",
            str(row),
            flags=facade.re.IGNORECASE,
        )
        if not match:
            continue
        return {
            "sp500": float(match.group(1)),
            "nasdaq": float(match.group(2)),
            "dow": float(match.group(3)),
        }
    return {}


def _clean_news_title_r3_impl(value, *, max_len, facade):
    text = facade.html.unescape(facade._clip(value, max_len=max_len).strip())
    if not text:
        return ""
    text = facade.re.sub(r"<[^>]+>", "", text)
    text = facade.re.sub(r"\s+", " ", text).strip(" .;")
    return text


def _select_symbol_headline_r3_impl(headlines, symbol, *, facade):
    cleaned_rows = [facade._clean_news_title(row) for row in facade._listify(headlines, max_items=20, max_len=240)]
    cleaned_rows = [row for row in cleaned_rows if row]
    if not cleaned_rows:
        return ""
    symbol_token = str(symbol or "").strip()
    if symbol_token:
        for row in cleaned_rows:
            if row.startswith(f"{symbol_token}:"):
                return row
    return cleaned_rows[0]


def _num_opt_r3_impl(value, *, facade):
    try:
        if value in (None, ""):
            return None
        return float(value)
    except Exception:
        return None
