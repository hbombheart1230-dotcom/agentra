"""post_exit_shadow_recap projections (moved verbatim from post_exit_shadow_recap).

Module globals and helpers are resolved on ``facade`` (the post_exit_shadow_recap module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, List


def resolve_post_exit_state_path(reports_root: Path, state_path: Path | None = None, *, facade: Any) -> Path | None:
    candidates: List[facade.Path] = []
    if state_path is not None and str(state_path).strip():
        candidates.append(facade.Path(state_path))
    for key in ("STATE_STORE_PATH", "MOCK_EXAM_STATE_PATH"):
        raw = str(facade.os.getenv(key) or "").strip()
        if raw:
            candidates.append(facade.Path(raw))

    reports_root_path = facade.Path(reports_root)
    candidates.append(reports_root_path.parent / "data" / "state.json")
    candidates.append(facade.Path("data/state.json"))

    for candidate in candidates:
        path = candidate
        if not path.is_absolute():
            path = (facade.Path.cwd() / path).resolve()
        if path.exists():
            return path
    return None
