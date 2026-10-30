"""Strategist LLM summary JSON read projection (moved verbatim from strategist_llm_summary).

``json`` is resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
Read-only; no writes.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def _read_json(path: Path, *, facade: Any) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = facade.json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return dict(payload) if isinstance(payload, dict) else {}
