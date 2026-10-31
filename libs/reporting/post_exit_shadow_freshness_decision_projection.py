"""post_exit_shadow_recap projections (moved verbatim from post_exit_shadow_recap).

Module globals and helpers are resolved on ``facade`` (the post_exit_shadow_recap module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping


def _post_exit_shadow_needs_fresh_minutes(shadow: Mapping[str, Any], rows: List[Dict[str, Any]], *, facade: Any) -> bool:
    target_epoch = facade._shadow_latest_required_epoch(shadow)
    now_epoch = facade.datetime.now(facade.timezone.utc).timestamp()
    if target_epoch is not None:
        if now_epoch + 30.0 < target_epoch:
            return False
        if not facade._rows_reach_epoch(rows, target_epoch):
            return True

    now_kst = facade.datetime.now(facade.timezone.utc).astimezone(facade.KST)
    checkpoints = facade._as_dict(shadow.get("checkpoints"))
    eod = facade._as_dict(checkpoints.get("EOD"))
    eod_pending = str(eod.get("status") or "").strip().lower() != "observed"
    if eod_pending and now_kst.strftime("%H%M%S") >= "153500":
        return not facade._rows_reach_regular_close(rows)
    return False
