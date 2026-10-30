"""intraday_trade_reports projections (moved verbatim from intraday_trade_reports).

Module globals and helpers are resolved on ``facade`` (the intraday_trade_reports module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def _is_trueish(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _normalize_symbol(value: Any) -> str:
    return str(value or "").strip().upper()


def _stable_json_text(payload: Any, *, facade: Any) -> str:
    return facade.json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _payload_fingerprint(payload: Any, *, facade: Any) -> str:
    return facade.hashlib.sha256(facade._stable_json_text(payload).encode("utf-8")).hexdigest()
