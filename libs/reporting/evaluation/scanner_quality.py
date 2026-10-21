from __future__ import annotations

from typing import Any, Mapping

from libs.reporting.q8_evaluation_contract import candidate_day
from libs.reporting.quant_shadow_forward_outcomes import attach_forward_outcomes

from . import fast08_scanner_attribution as _sa


TOP_K_VALUES = (1, 3, 5, 10)
SCANNER_HORIZONS = ("+5m", "+15m", "+30m", "EOD")


_number = _sa.number
_checkpoint_return = _sa.observed_return


def extract_pre_strategist_candidate_rows(
    payloads: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, int]] = set()
    for payload in payloads:
        generated_at = str(payload.get("generated_at") or "")
        for raw in payload.get("q9_decision_candidates") or []:
            if not isinstance(raw, Mapping):
                continue
            if str(raw.get("q9_decision_role") or "") != "P_SCANNER_PRE_STRATEGIST_UNIVERSE":
                continue
            row = dict(raw)
            decision_id = str(row.get("q9_decision_id") or "")
            symbol = str(row.get("symbol") or "")
            rank = int(_number(row.get("rank")) or 0)
            key = (decision_id, symbol, rank)
            if not decision_id or not symbol or rank <= 0 or key in seen:
                continue
            seen.add(key)
            row.setdefault("_payload_generated_at", generated_at)
            rows.append(row)
    return rows


def pre_strategist_candidate_rows(
    payloads: list[dict[str, Any]],
    *,
    minute_rows_by_symbol: Mapping[str, list[Mapping[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    rows = extract_pre_strategist_candidate_rows(payloads)
    if minute_rows_by_symbol is None:
        return attach_forward_outcomes(rows)
    return attach_forward_outcomes(
        rows,
        minute_rows_by_symbol=minute_rows_by_symbol,
    )


def build_scanner_topk_forward_performance(
    rows: list[dict[str, Any]],
    *,
    cost_pct: float,
    slippage_pct: float,
) -> dict[str, Any]:
    window_count, output = _sa.topk_forward_rows(
        rows,
        horizons=SCANNER_HORIZONS,
        top_k_values=TOP_K_VALUES,
        cost_pct=cost_pct,
        slippage_pct=slippage_pct,
        day_of=candidate_day,
    )
    return {
        "schema_version": "q9_scanner_topk_forward_performance.v1",
        "behavior_effect": "evaluation_only",
        "decision_window_count": window_count,
        "candidate_row_count": len(rows),
        "top_k_values": list(TOP_K_VALUES),
        "horizons": list(SCANNER_HORIZONS),
        "rows": output,
    }


def build_scanner_source_performance(
    rows: list[dict[str, Any]],
    *,
    cost_pct: float,
    slippage_pct: float,
) -> dict[str, Any]:
    return {
        "schema_version": "q9_scanner_source_performance.v1",
        "behavior_effect": "evaluation_only",
        "rows": _sa.source_forward_rows(
            rows,
            horizons=SCANNER_HORIZONS,
            cost_pct=cost_pct,
            slippage_pct=slippage_pct,
            day_of=candidate_day,
        ),
    }


def build_scanner_quality_review(
    payloads: list[dict[str, Any]],
    *,
    cost_pct: float,
    slippage_pct: float,
    minute_rows_by_symbol: Mapping[str, list[Mapping[str, Any]]] | None = None,
) -> dict[str, Any]:
    rows = pre_strategist_candidate_rows(
        payloads,
        minute_rows_by_symbol=minute_rows_by_symbol,
    )
    return {
        "schema_version": "q9_scanner_quality_review.v1",
        "behavior_effect": "evaluation_only",
        "pre_strategist_universe_available": bool(rows),
        "topk_forward_performance": build_scanner_topk_forward_performance(
            rows,
            cost_pct=cost_pct,
            slippage_pct=slippage_pct,
        ),
        "source_performance": build_scanner_source_performance(
            rows,
            cost_pct=cost_pct,
            slippage_pct=slippage_pct,
        ),
    }


__all__ = [
    "SCANNER_HORIZONS",
    "TOP_K_VALUES",
    "build_scanner_quality_review",
    "build_scanner_source_performance",
    "build_scanner_topk_forward_performance",
    "pre_strategist_candidate_rows",
]
