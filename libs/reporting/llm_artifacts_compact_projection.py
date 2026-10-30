"""LLM artifacts: Compact input artifact payload builder (moved verbatim from llm_artifacts).

Helpers are resolved on ``facade`` (the llm_artifacts module) at call time where needed; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict


def build_compact_input_artifact(
    *,
    component: str,
    run_id: Any,
    trade_id: Any = "",
    story_id: Any = "",
    day: Any = "",
    source_artifact_path: Any = "",
    source_input: Any = None,
    compact_input: Any = None,
    facade: Any,
) -> Dict[str, Any]:
    source_payload = source_input if isinstance(source_input, (dict, list)) else {}
    compact_payload = compact_input if isinstance(compact_input, (dict, list)) else {}
    source_text = facade.json.dumps(source_payload, ensure_ascii=False)
    compact_text = facade.json.dumps(compact_payload, ensure_ascii=False)
    source_char_count = len(source_text)
    compact_char_count = len(compact_text)
    reduction_ratio = 0.0
    if source_char_count > 0:
        reduction_ratio = max(0.0, 1.0 - (compact_char_count / float(source_char_count)))
    return {
        "schema_version": "llm_compact_input.v1",
        "component": str(component or "").strip(),
        "role": str(component or "").strip(),
        "run_id": str(run_id or ""),
        "trade_id": str(trade_id or ""),
        "story_id": str(story_id or trade_id or ""),
        "day": str(day or ""),
        "saved_at": facade.utc_now_iso(),
        "input_variant": "llm_compact_input",
        "source_artifact_path": str(source_artifact_path or ""),
        "source_char_count": source_char_count,
        "compact_input_char_count": compact_char_count,
        "reduction_ratio": reduction_ratio,
        "compact_input": compact_payload,
    }
