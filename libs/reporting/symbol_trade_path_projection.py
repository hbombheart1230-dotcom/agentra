"""Symbol trade report summary input path projection (moved verbatim from symbol_trade_report).

``Path`` is resolved on ``facade`` (the symbol_trade_report module) at call time; this module never imports it.
Pure path construction; no filesystem access.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def _summary_input_path_for_report(report_path: Path, *, facade: Any) -> Path:
    return facade.Path(report_path).with_name("ai_trade_summary_input.json")
