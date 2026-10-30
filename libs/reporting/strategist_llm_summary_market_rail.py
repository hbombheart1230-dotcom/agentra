"""Strategist LLM summary market rail projection (moved verbatim from strategist_llm_summary).

Helpers are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
Pure function; no IO.
"""
from __future__ import annotations

from typing import Any, Dict


def _market_rail_from_canonical(canonical: Dict[str, Any], *, facade: Any) -> Dict[str, Any]:
    global_signal = facade._as_dict(canonical.get("global_sentiment_signal"))
    if not global_signal:
        global_signal = facade._as_dict(facade._as_dict(canonical.get("market_context")).get("global_signal"))
    packet = {
        "generated_at": facade._text(canonical.get("generated_at") or canonical.get("saved_at"), ""),
        "global_sentiment": {
            "score": global_signal.get("score"),
            "status": global_signal.get("status"),
            "source": global_signal.get("source"),
        },
        "index_moves": facade._as_dict(global_signal.get("index_moves")),
        "korea_indices": facade._as_dict(global_signal.get("korea_indices")),
        "macro_moves": facade._as_dict(global_signal.get("macro_moves")),
    }
    return facade.classify_market_regime_rail(packet)
