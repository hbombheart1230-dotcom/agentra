"""strategist_llm_summary generate_strategist_llm_summary (moved verbatim from strategist_llm_summary).

Module globals and helpers are resolved on ``facade`` (the strategist_llm_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple


def generate_strategist_llm_summary(response_json_path: Path, *, facade: Any) -> Tuple[Path, Path, Dict[str, Any]]:
    source_path = facade.Path(response_json_path)
    payload = facade.build_strategist_llm_summary_payload(source_path)
    md_path = source_path.with_name("strategist_summary.md")
    json_path = source_path.with_name("strategist_summary.json")
    json_path.write_text(facade.json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(facade.render_strategist_llm_summary_markdown(payload), encoding="utf-8-sig", newline="\n")
    return md_path, json_path, payload
