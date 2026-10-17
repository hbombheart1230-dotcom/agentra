"""Reporter read-model owner (decomposed from libs/reporting/trade_report_symbol_metadata.py; bodies verbatim). Report source and component-theme traversal."""
from __future__ import annotations

from typing import Any, Callable, Dict, Iterable

from libs.agents.reporter.read_models.symbol_metadata_text import append_unique_text, as_dict, listify


def iter_trade_symbol_metadata_sources(report: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    shared = as_dict(report.get("shared_facts"))
    yield report
    yield shared
    yield as_dict(shared.get("resolved_trade_facts"))
    for key in (
        "executive_summary",
        "market_context_at_entry",
        "strategist_summary",
        "why_this_symbol_was_chosen",
        "scanner_filters",
        "entry_decision",
        "monitor_snapshot",
        "fact_payload",
    ):
        section = as_dict(report.get(key))
        if section:
            yield section
        for nested_key in (
            "selected_candidate",
            "selected_row",
            "candidate",
            "scanner_selection_trace",
            "selection_trace",
            "theme_alignment_trace",
            "theme_strength_packet",
            "selected_symbol_detail",
            "trade",
        ):
            nested = as_dict(section.get(nested_key))
            if nested:
                yield nested


def symbol_in_theme_components(symbol: str, components: Any) -> bool:
    target = str(symbol or "").strip()
    if not target:
        return False
    for item in listify(components):
        if isinstance(item, dict):
            candidate = str(
                item.get("symbol")
                or item.get("code")
                or item.get("stk_cd")
                or item.get("ticker")
                or ""
            ).strip()
        else:
            candidate = str(item or "").strip()
        if candidate == target:
            return True
    return False


def iter_nested_dicts(value: Any, *, max_depth: int = 8) -> Iterable[Dict[str, Any]]:
    if max_depth < 0:
        return
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_nested_dicts(child, max_depth=max_depth - 1)
    elif isinstance(value, list):
        for child in value:
            yield from iter_nested_dicts(child, max_depth=max_depth - 1)


def component_themes_for_symbol(
    report: Dict[str, Any],
    symbol: str,
    *,
    metadata_value: Callable[[Any], str],
    translate_text: Callable[[Any], str],
) -> List[str]:
    themes: List[str] = []
    for source in iter_nested_dicts(report):
        for map_key in ("component_symbols_by_theme", "theme_map", "symbol_theme_map"):
            component_map = as_dict(source.get(map_key))
            if not component_map:
                continue
            for raw_theme, components in component_map.items():
                if symbol_in_theme_components(symbol, components):
                    append_unique_text(
                        themes,
                        raw_theme,
                        metadata_value=metadata_value,
                        translate_text=translate_text,
                    )
    return themes
