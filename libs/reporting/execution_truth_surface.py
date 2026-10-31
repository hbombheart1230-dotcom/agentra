from __future__ import annotations

import sys
from typing import Any, Dict, List

from libs.reporting.truth_source_labels import (
    pnl_truth_source_label,
    price_truth_source_label,
    with_ro_particle,
)
from libs.reporting import execution_truth_scalar_projection as _scalar_owner
from libs.reporting import execution_truth_bullet_projection as _bullet_owner


def _clip(value: Any, *, max_len: int = 120) -> str:
    return _scalar_owner._clip(value, max_len=max_len)


def _fmt_price(value: Any) -> str:
    return _scalar_owner._fmt_price(value)


def _fmt_pct(value: Any) -> str:
    return _scalar_owner._fmt_pct(value)


def _is_available(value: Any) -> bool:
    return _scalar_owner._is_available(value)


def build_execution_truth_bullets(
    *,
    execution_details: Dict[str, Any] | None = None,
    shared_facts: Dict[str, Any] | None = None,
) -> List[str]:
    return _bullet_owner.build_execution_truth_bullets(execution_details=execution_details, shared_facts=shared_facts, facade=sys.modules[__name__])
