"""post_exit_shadow_recap projections (moved verbatim from post_exit_shadow_recap).

Module globals and helpers are resolved on ``facade`` (the post_exit_shadow_recap module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def _fresh_minute_fetch_enabled(*, facade: Any) -> bool:
    raw = str(facade.os.getenv("POST_EXIT_SHADOW_RECAP_FETCH_FRESH_MINUTES", "1")).strip().lower()
    return raw not in {"0", "false", "no", "off"}
