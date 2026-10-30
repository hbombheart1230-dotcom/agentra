from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List, Mapping, Sequence

import sys as _p15_sys
from libs.reporting import strategist_llm_evaluation_build as _build_owner
from libs.reporting import strategist_llm_evaluation_extra_projection as _extra_owner
from libs.reporting import strategist_llm_evaluation_formatting as _formatting_owner
from libs.reporting import strategist_llm_evaluation_projection as projection
from libs.reporting import strategist_llm_evaluation_rows as _rows_owner
from libs.reporting import strategist_llm_evaluation_scalar as _scalar_owner


def _text(value: Any) -> str:
    return _scalar_owner._text(value)


def _float(value: Any, default: float = 0.0) -> float:
    return _scalar_owner._float(value, default)


def _bool(value: Any) -> bool:
    return _extra_owner._bool(value)


def _row_closed(row: Mapping[str, Any]) -> bool:
    return _extra_owner._row_closed(row)


def _result_pct(row: Mapping[str, Any]) -> float:
    return _extra_owner._result_pct(row, facade=_p15_sys.modules[__name__])


def _tactic(row: Mapping[str, Any]) -> str:
    return _extra_owner._tactic(row, facade=_p15_sys.modules[__name__])


def _shape_from_reason(reason: str, axis: str = "") -> str:
    return _rows_owner._shape_from_reason(reason, axis, facade=_p15_sys.modules[__name__])


def _shape_from_tactic(tactic: str) -> str:
    return _rows_owner._shape_from_tactic(tactic, facade=_p15_sys.modules[__name__])


def _top_counter(counter: Counter[str], *, limit: int = 6) -> List[Dict[str, Any]]:
    return _rows_owner._top_counter(counter, limit=limit)


def _closed_rows(rows: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    return _rows_owner._closed_rows(rows, facade=_p15_sys.modules[__name__])


def _shadow_rows(payloads: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    return _rows_owner._shadow_rows(payloads, facade=_p15_sys.modules[__name__])


def _tactic_performance(rows: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    return projection._tactic_performance(rows, facade=_p15_sys.modules[__name__])


def _shadow_shape_diagnostics(rows: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    return projection._shadow_shape_diagnostics(rows, facade=_p15_sys.modules[__name__])


def _quality_label(*, rows: Sequence[Mapping[str, Any]], primary_tactic: str, shadow: Dict[str, Any]) -> str:
    return _extra_owner._quality_label(rows=rows, primary_tactic=primary_tactic, shadow=shadow, facade=_p15_sys.modules[__name__])


def build_strategist_llm_evaluation(
    rows: Iterable[Mapping[str, Any]],
    shadow_payloads: Iterable[Mapping[str, Any]] = (),
) -> Dict[str, Any]:
    return _build_owner.build_strategist_llm_evaluation(rows, shadow_payloads, facade=_p15_sys.modules[__name__])


def _format_perf(rows: Sequence[Mapping[str, Any]], *, limit: int = 3) -> str:
    return _formatting_owner._format_perf(rows, limit=limit, facade=_p15_sys.modules[__name__])


def render_strategist_llm_evaluation_lines(payload: Mapping[str, Any] | None) -> List[str]:
    return _formatting_owner.render_strategist_llm_evaluation_lines(payload, facade=_p15_sys.modules[__name__])
