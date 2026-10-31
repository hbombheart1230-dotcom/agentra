"""post_exit_shadow_recap projections (moved verbatim from post_exit_shadow_recap).

Module globals and helpers are resolved on ``facade`` (the post_exit_shadow_recap module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def _utc_now_iso(*, facade: Any) -> str:
    return facade.datetime.now(facade.timezone.utc).isoformat()
