"""Operator brief renderer: pure narrative/summary/compaction helper closures.

T4-A (P1.5 Third Pass): contiguous statement run / value expression of `apps/operator_ui/data_access_core.py::_render_operator_brief_markdown` moved verbatim into a
scanner projection Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
Scanner node are resolved at use time as `facade.NAME`. State writes, event emission, logging and persistence stay in the
orchestrator at their original boundaries.
"""
from __future__ import annotations


def operator_brief_narrative_helpers(_narrative_text, *, facade):
    def _usable_narrative_text(text: facade.Any) -> str:
        cleaned = _narrative_text(text)
        return cleaned if facade._count_hangul_chars(cleaned) >= 4 else ""

    def _summary_text(section: facade.Dict[str, facade.Any], *extra: facade.Any) -> str:
        candidates: facade.List[facade.Any] = [section.get("summary")] if isinstance(section, dict) else []
        candidates.extend(extra)
        for candidate in candidates:
            text = _usable_narrative_text(candidate) or _narrative_text(candidate)
            if text:
                return text
        return ""

    def _compact_items(values: facade.Any, *, limit: int = 3, max_len: int = 180) -> facade.List[str]:
        items = facade._clean_str_list(values, limit=limit, max_len=max_len)
        out: facade.List[str] = []
        for item in items:
            text = facade._sanitize_operator_brief_text(item)
            if text:
                out.append(text)
        return out
    return (_compact_items, _summary_text, _usable_narrative_text)
