from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from libs.reporting.quant_shadow_candidate_evaluation import (
    Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN,
    load_quant_shadow_candidate_payloads_for_range,
)
from libs.reporting.q9_forward_candles import (
    FORWARD_DATA_SOURCE,
    load_q9_forward_candles,
)
from libs.runtime.broker_cost_profile import load_broker_cost_profile

from . import fast08_qwindow_projection as _qw
from .scanner_quality import (
    build_scanner_quality_review,
    extract_pre_strategist_candidate_rows,
)


DEFAULT_EVALUATION_SLIPPAGE_PCT = 0.05
LIVE_BUY_FEE_RATE = 0.00015
LIVE_SELL_FEE_RATE = 0.00015
LIVE_EQUITY_SELL_TAX_RATE_2026 = 0.002


def _pct(value: float) -> float:
    return round(float(value) * 100.0, 6)


def build_evaluation_cost_bases(
    profile: Mapping[str, Any] | None,
    *,
    slippage_pct: float = DEFAULT_EVALUATION_SLIPPAGE_PCT,
) -> dict[str, Any]:
    observed = dict(profile or {})
    mock_ratio = float(
        observed.get("conservative_round_trip_cost_pct")
        or observed.get("ema_round_trip_cost_pct")
        or 0.009
    )
    live_ratio = LIVE_BUY_FEE_RATE + LIVE_SELL_FEE_RATE + LIVE_EQUITY_SELL_TAX_RATE_2026
    return {
        "schema_version": "evaluation_cost_bases.v1",
        "primary_interpretation": "show_both_no_automatic_policy_change",
        "slippage_pct": round(float(slippage_pct), 6),
        "mock_observed": {
            "purpose": "mock_broker_pnl_and_mock_cash_truth",
            "source": str(observed.get("source") or "fallback"),
            "sample_count": int(observed.get("sample_count") or 0),
            "round_trip_cost_pct": _pct(mock_ratio),
            "total_drag_with_slippage_pct": round(_pct(mock_ratio) + float(slippage_pct), 6),
        },
        "live_deployment_equity": {
            "purpose": "real_account_strategy_evaluation",
            "source": "kiwoom_openapi_standard_equity_assumption_2026",
            "buy_fee_pct": _pct(LIVE_BUY_FEE_RATE),
            "sell_fee_pct": _pct(LIVE_SELL_FEE_RATE),
            "sell_tax_pct": _pct(LIVE_EQUITY_SELL_TAX_RATE_2026),
            "round_trip_cost_pct": _pct(live_ratio),
            "total_drag_with_slippage_pct": round(_pct(live_ratio) + float(slippage_pct), 6),
            "scope": "KRX listed equities; ETF/ETN tax treatment must be resolved by instrument type",
        },
    }


_topk_rows = _qw.topk_rows_by_key


def build_cost_basis_comparison(
    *,
    reports_root: Path,
    start: str,
    end: str,
    cost_profile_path: Path | None = None,
    slippage_pct: float = DEFAULT_EVALUATION_SLIPPAGE_PCT,
) -> dict[str, Any]:
    payloads = load_quant_shadow_candidate_payloads_for_range(
        reports_root=Path(reports_root),
        start=start,
        end=end,
        drop_q9_row_keys=Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN,  # only pre-strategist rows' forward outcomes are read
    )
    profile = load_broker_cost_profile(cost_profile_path)
    bases = build_evaluation_cost_bases(profile, slippage_pct=slippage_pct)
    pre_strategist_rows = extract_pre_strategist_candidate_rows(payloads)
    forward_candles = load_q9_forward_candles(
        pre_strategist_rows,
        allow_fresh_fetch=start[:10] == end[:10],
        run_id_prefix="q9_cost_basis_forward_recovery",
    )
    mock_cost = float(bases["mock_observed"]["round_trip_cost_pct"])
    live_cost = float(bases["live_deployment_equity"]["round_trip_cost_pct"])
    mock_review = build_scanner_quality_review(
        payloads,
        cost_pct=mock_cost,
        slippage_pct=slippage_pct,
        minute_rows_by_symbol=forward_candles,
    )
    live_review = build_scanner_quality_review(
        payloads,
        cost_pct=live_cost,
        slippage_pct=slippage_pct,
        minute_rows_by_symbol=forward_candles,
    )
    rows = _qw.cost_comparison_rows(mock_review, live_review)
    return {
        "schema_version": "q9_cost_basis_comparison.v1",
        "behavior_effect": "evaluation_only",
        "cohort_scope": "all_pre_strategist_windows_with_observed_horizon",
        "forward_data_source": FORWARD_DATA_SOURCE,
        "range": {"start": start[:10], "end": end[:10]},
        "cost_bases": bases,
        "pre_strategist_universe_available": bool(
            mock_review.get("pre_strategist_universe_available")
        ),
        "rows": rows,
        "interpretation": {
            "mock_net": "Can the signal overcome Kiwoom mock-account friction?",
            "live_net": "Could the signal overcome the stated real-account equity assumptions?",
            "policy_change_authorized": False,
        },
    }


render_cost_basis_comparison = _qw.render_cost_basis_comparison


def write_cost_basis_comparison(
    *,
    reports_root: Path,
    start: str,
    end: str,
    output_dir: Path,
    cost_profile_path: Path | None = None,
) -> dict[str, str]:
    payload = build_cost_basis_comparison(
        reports_root=reports_root,
        start=start,
        end=end,
        cost_profile_path=cost_profile_path,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "cost_basis_comparison.json"
    markdown_path = output_dir / "cost_basis_comparison.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_cost_basis_comparison(payload), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path)}


__all__ = [
    "build_cost_basis_comparison",
    "build_evaluation_cost_bases",
    "render_cost_basis_comparison",
    "write_cost_basis_comparison",
]
