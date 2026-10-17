"""Reporter read-model owner (decomposed from libs/reporting/trade_report_symbol_metadata.py; bodies verbatim). Symbol-name plausibility and text inference."""
from __future__ import annotations

import re
from typing import Any, Callable, Dict

from libs.agents.reporter.read_models.symbol_metadata_sources import iter_trade_symbol_metadata_sources
from libs.agents.reporter.read_models.symbol_metadata_text import clip_text, listify


def looks_like_symbol_name(candidate: str, symbol: str) -> bool:
    text = str(candidate or "").strip()
    if not text or text == str(symbol or "").strip() or re.fullmatch(r"\d{6}", text):
        return False
    lowered = text.lower()
    if re.fullmatch(r"[a-z][a-z0-9_]{8,}", lowered) and any(
        token in lowered
        for token in (
            "_entry",
            "_pullback",
            "_structure",
            "_confirmation",
            "_breakout",
            "_reclaim",
            "_vwap",
            "_volume",
            "_reason",
            "_ready",
        )
    ):
        return False
    if any(
        token in lowered
        for token in (
            "runner_up",
            "runner-up",
            "score",
            "rank",
            "fallback",
            "selected",
            "candidate",
            "trigger",
            "reason",
            "highest",
            "best score",
            "total score",
            "composite score",
            "structure_above_vwap",
            "volume_confirmation",
            "entry_reason",
        )
    ):
        return False
    if any(token in text for token in ("스코어", "점수", "순위", "후보", "선택", "사유", "최고", "종합")):
        return False
    return True


def infer_symbol_name_from_report_text(report: Dict[str, Any], symbol: str, *, metadata_value: Callable[[Any], str], translate_text: Callable[[Any], str]) -> str:
    target = str(symbol or "").strip()
    if not target:
        return ""
    text_candidates: List[tuple[str, Any]] = []
    for source in iter_trade_symbol_metadata_sources(report):
        for key in ("symbol_news_titles", "strategist_symbol_headlines", "candidate_headlines_used"):
            text_candidates.extend(("headline", item) for item in listify(source.get(key)))
        text_candidates.extend(("narrative", item) for item in listify(source.get("bullets")))
        text_candidates.append(("narrative", source.get("summary")))
    for candidate_kind, raw in text_candidates:
        text = metadata_value(translate_text(raw))
        if not text or target not in text:
            continue
        paren_match = re.search(rf"([A-Za-z가-힣0-9&._\-\s]+)\(\s*{re.escape(target)}\s*\)", text)
        if paren_match:
            name = re.sub(r"\s+", " ", paren_match.group(1)).strip(" ,;:-")
            if looks_like_symbol_name(name, target):
                return clip_text(name.split()[-1], 80)
        prefix = re.search(rf"{re.escape(target)}\s*:\s*(.+)", text)
        if not prefix:
            continue
        if candidate_kind == "headline":
            continue
        headline = str(prefix.group(1) or "").strip()
        name_prefix = re.split(r"[,·/]|[↑↓▲▼]", headline)[0]
        name_prefix = re.sub(r"\s+", " ", name_prefix).strip(" ,;:-")
        if looks_like_symbol_name(name_prefix, target):
            return clip_text(name_prefix, 80)
        if "…" in headline:
            headline = headline.rsplit("…", 1)[-1]
        elif "..." in headline:
            headline = headline.rsplit("...", 1)[-1]
        headline = re.sub(r"\[[^\]]+\]", " ", headline)
        headline = re.split(r"[·,/]|[↑↓▲▼]", headline)[0]
        name = re.sub(r"\s+", " ", headline).strip(" ,;:-")
        if looks_like_symbol_name(name, target) and not any(token in name for token in ("뉴스", "상승", "하락", "강세", "약세")):
            return clip_text(name, 80)
    return ""
