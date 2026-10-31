"""quant_tactic_report projections (moved verbatim from quant_tactic_report).

Module globals and helpers are resolved on ``facade`` (the quant_tactic_report module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def _decision_label(value: Any) -> str:
    raw = str(value or "").strip()
    mapping = {
        "entry_ready": "진입 준비",
        "block_recommended": "진입 차단 권고",
        "wait": "대기",
        "hold_watch": "보유 관찰",
        "hard_exit": "즉시 청산 허용",
        "confirm_before_exit_recommended": "청산 전 확인 권고",
        "early_exit_warning": "조기 청산 경고",
        "exit_aligned": "청산 정합",
    }
    return mapping.get(raw, raw or "-")
