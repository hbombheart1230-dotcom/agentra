"""Strategist: theme hints, candidate symbol list and theme strength ordering.

T4-C (P1.5 Third Pass): contiguous statement run / value expression of `graphs/nodes/strategist_node.py::strategist_node` moved verbatim into a
Strategist Owner. Locals enter as explicit parameters and leave as the returned record; module globals of the
source module are resolved at use time as `facade.NAME`. State writes, event emission, logging, persistence, the frame LLM
call and provider IO stay in the orchestrator at their original boundaries.
"""
from __future__ import annotations

from typing import Any, NamedTuple


class ThemeCandidateInputs(NamedTuple):
    """Result of `project_theme_candidate_inputs` (positional order = sorted output names)."""

    candidate_symbols: Any
    theme_strength: Any
    themes: Any

def project_theme_candidate_inputs(candidates, policy, state, theme_hints, *, facade):
    themes = list(theme_hints)
    pre_ai_overrides = facade._extract_ai_overrides(state, policy)
    themes = facade._merge_override_text_list(themes, pre_ai_overrides.get("themes"), limit=5)
    candidate_symbols = [str(c.get("symbol") or "") for c in candidates if str(c.get("symbol") or "").strip()]
    theme_index = facade._extract_theme_symbol_index(state, policy)
    theme_scores = state.get("theme_scores") if isinstance(state.get("theme_scores"), dict) else {}
    theme_strength = facade._theme_strength_map(
        themes=list(themes),
        candidates=list(candidates),
        theme_scores=theme_scores,
        theme_index=theme_index,
    )
    if theme_strength:
        ranked_theme_names = [k for k, _v in sorted(theme_strength.items(), key=lambda kv: kv[1], reverse=True)]
        themes = facade._merge_override_text_list(ranked_theme_names, themes, limit=5)
    return ThemeCandidateInputs(candidate_symbols, theme_strength, themes)
