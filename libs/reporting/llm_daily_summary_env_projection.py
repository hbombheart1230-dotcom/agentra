"""LLM daily summary DRY_RUN environment projection (moved verbatim from llm_daily_summary).

``os`` is resolved on ``facade`` (the llm_daily_summary module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any


def _is_dry_run(*, facade: Any) -> bool:
    return str(facade.os.getenv("DRY_RUN", "0")).strip() in ("1", "true", "True")
