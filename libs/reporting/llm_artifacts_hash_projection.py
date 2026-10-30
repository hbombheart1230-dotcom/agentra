"""LLM artifacts: Stable JSON text and SHA-256 helpers (moved verbatim from llm_artifacts).

Helpers are resolved on ``facade`` (the llm_artifacts module) at call time where needed; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def json_stable_text(payload: Any, *, facade: Any) -> str:
    if isinstance(payload, (dict, list)):
        return facade.json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return str(payload or "")


def sha256_text(text: Any, *, facade: Any) -> str:
    return facade.hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()
