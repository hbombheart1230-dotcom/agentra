"""Strategist LLM summary canonical-strategist path projection (moved verbatim from strategist_llm_summary).

Pure function; no IO.
"""
from __future__ import annotations

from pathlib import Path


def canonical_strategist_path_for_response(source_path: Path) -> Path | None:
    if source_path.name != "response.json":
        return None
    artifact_dir = source_path.parent
    run_dir = artifact_dir.parent
    day_dir = run_dir.parent
    llm_dir = day_dir.parent
    if llm_dir.name != "llm":
        category_dir = run_dir.parent
        day_dir = category_dir.parent
        llm_dir = day_dir.parent
        if llm_dir.name != "llm":
            return None
    reports_root = llm_dir.parent
    return reports_root / "canonical" / day_dir.name / run_dir.name / "strategist.json"


def trade_strategist_input_path_for_response(source_path: Path) -> Path | None:
    if source_path.parent.name != "reports":
        return None
    candidate = source_path.parent.parent / "strategist_input.json"
    return candidate if candidate.exists() else None
