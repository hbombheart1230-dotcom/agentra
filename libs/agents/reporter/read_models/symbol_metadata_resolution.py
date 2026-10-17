"""Reporter read-model owner (decomposed from libs/reporting/trade_report_symbol_metadata.py; bodies verbatim). Composed symbol metadata resolution."""
from __future__ import annotations

from typing import Any, Callable, Dict, List

from libs.agents.reporter.read_models.symbol_metadata_fallbacks import SYMBOL_NAME_FALLBACKS, SYMBOL_THEME_FALLBACKS
from libs.agents.reporter.read_models.symbol_metadata_name_inference import infer_symbol_name_from_report_text, looks_like_symbol_name
from libs.agents.reporter.read_models.symbol_metadata_sources import component_themes_for_symbol, iter_trade_symbol_metadata_sources
from libs.agents.reporter.read_models.symbol_metadata_text import append_theme_values, clip_text


def resolve_trade_symbol_metadata(report: Dict[str, Any], symbol: str, *, metadata_value: Callable[[Any], str], translate_text: Callable[[Any], str]) -> Dict[str, Any]:
    name_keys = (
        "symbol_name",
        "stock_name",
        "stock_nm",
        "stk_nm",
        "isu_nm",
        "corp_name",
        "company_name",
        "name_kr",
    )
    exact_theme_keys = (
        "symbol_theme",
        "symbol_themes",
        "symbol_theme_name",
        "matched_symbol_theme",
        "matched_symbol_themes",
        "matched_themes",
    )
    symbol_row_theme_keys = (
        "theme",
        "theme_name",
        "themes",
    )
    symbol_text = str(symbol or "").strip()
    symbol_name = ""
    component_themes = component_themes_for_symbol(
        report,
        symbol_text,
        metadata_value=metadata_value,
        translate_text=translate_text,
    )
    themes: List[str] = list(component_themes)
    for source in iter_trade_symbol_metadata_sources(report):
        source_symbol = str(
            source.get("symbol")
            or source.get("selected_symbol")
            or source.get("entry_final_symbol")
            or source.get("monitor_output_symbol")
            or ""
        ).strip()
        source_matches_symbol = not source_symbol or not symbol_text or source_symbol == symbol_text
        if source_matches_symbol and not symbol_name:
            for key in name_keys:
                candidate = metadata_value(translate_text(source.get(key))).strip()
                if looks_like_symbol_name(candidate, symbol_text):
                    symbol_name = clip_text(candidate, 80)
                    break
        if not component_themes:
            for key in exact_theme_keys:
                append_theme_values(
                    themes,
                    source.get(key),
                    metadata_value=metadata_value,
                    translate_text=translate_text,
                )
                if len(themes) >= 4:
                    break
        if not component_themes and source_symbol and source_matches_symbol:
            for key in symbol_row_theme_keys:
                append_theme_values(
                    themes,
                    source.get(key),
                    metadata_value=metadata_value,
                    translate_text=translate_text,
                )
                if len(themes) >= 4:
                    break
        if symbol_name and len(themes) >= 4:
            break
    if not symbol_name:
        symbol_name = SYMBOL_NAME_FALLBACKS.get(symbol_text, "")
    if not symbol_name:
        symbol_name = infer_symbol_name_from_report_text(report, symbol_text, metadata_value=metadata_value, translate_text=translate_text)
    if not themes:
        themes = list(SYMBOL_THEME_FALLBACKS.get(symbol_text, []))
    return {
        "symbol": symbol_text,
        "symbol_name": symbol_name,
        "themes": themes[:4],
        "theme": ", ".join(themes[:4]),
    }
