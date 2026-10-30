"""Strategist LLM summary inline JSON projection (moved verbatim from strategist_llm_summary).

Pure function; no IO.
"""
from __future__ import annotations

import json
from typing import Any


def json_inline(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(value)
