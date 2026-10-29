"""``_existing_trade_run_ids`` moved verbatim from live_execution_bundle_runner.py.

Helpers are resolved on ``facade`` (the source module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, List


def _existing_trade_run_ids(trade_dir: Path, *, facade: Any) -> List[str]:
    lifecycle_path = trade_dir / "lifecycle_bundle.json"
    if not lifecycle_path.exists():
        return []
    payload = facade._read_json_if_exists(lifecycle_path)
    run_ids: List[str] = [str(x or "").strip() for x in list(payload.get("linked_run_ids") or []) if str(x or "").strip()]
    entry = payload.get("entry") if isinstance(payload.get("entry"), dict) else {}
    exit_ctx = payload.get("exit") if isinstance(payload.get("exit"), dict) else {}
    lifecycle = payload.get("lifecycle") if isinstance(payload.get("lifecycle"), dict) else {}
    holding = lifecycle.get("holding") if isinstance(lifecycle.get("holding"), dict) else {}
    for item in (
        entry.get("run_id"),
        exit_ctx.get("run_id"),
    ):
        rid = str(item or "").strip()
        if rid and rid not in run_ids:
            run_ids.append(rid)
    for item in list(holding.get("run_ids") or []):
        rid = str(item or "").strip()
        if rid and rid not in run_ids:
            run_ids.append(rid)
    return run_ids
