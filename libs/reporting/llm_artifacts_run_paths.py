"""LLM artifacts run artifact paths (moved verbatim from llm_artifacts).

Helpers are resolved on ``facade`` (the llm_artifacts module) at call time; this module never imports it.
Path construction only (read-only existence check inside the finder).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def llm_artifact_paths(reports_root: Path, day: str, run_id: str, component: str, *, facade: Any) -> Dict[str, Path]:
    run_base = facade.find_llm_run_dir(Path(reports_root), str(day or "").strip(), str(run_id or "").strip())
    base = run_base / str(component or "").strip()
    return {
        "base_dir": base,
        "prompt_json": base / "prompt.json",
        "response_json": base / "response.json",
        "meta_json": base / "meta.json",
    }
