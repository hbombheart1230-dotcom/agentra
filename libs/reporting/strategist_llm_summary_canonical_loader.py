"""Strategist LLM summary canonical strategist loader (moved verbatim from strategist_llm_summary).

Helpers are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
Read-only; no writes.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple


def _load_canonical_strategist(source_path: Path, *, facade: Any) -> Tuple[Path | None, Dict[str, Any]]:
    canonical_path = facade._canonical_strategist_path_for_response(source_path)
    if canonical_path is not None and canonical_path.exists():
        try:
            raw = facade.json.loads(canonical_path.read_text(encoding="utf-8"))
        except Exception:
            raw = {}
        if isinstance(raw, dict) and raw:
            return canonical_path, dict(raw)

    input_path = facade._trade_strategist_input_path_for_response(source_path)
    if input_path is None:
        return canonical_path, {}
    try:
        raw_input = facade.json.loads(input_path.read_text(encoding="utf-8"))
    except Exception:
        return input_path, {}
    if not isinstance(raw_input, dict):
        return input_path, {}
    source_input = facade._as_dict(raw_input.get("source_input"))
    if not source_input:
        return input_path, {}
    canonical = dict(source_input)
    canonical.setdefault("generated_at", raw_input.get("saved_at"))
    canonical.setdefault("run_id", raw_input.get("run_id"))
    return input_path, canonical
