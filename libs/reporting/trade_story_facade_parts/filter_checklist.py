from __future__ import annotations

from typing import Any, Dict, List


def build_filters_human_impl(scanner: Dict[str, Any], strategist: Dict[str, Any], supervisor: Dict[str, Any], *, normalized_feature_coverage, safe_float) -> Dict[str, Any]:
    selected = scanner.get("selected_candidate") if isinstance(scanner.get("selected_candidate"), dict) else {}
    sources = [str(x or "") for x in list(selected.get("sources") or []) if str(x or "").strip()]
    score_breakdown = selected.get("score_breakdown") if isinstance(selected.get("score_breakdown"), dict) else {}
    components = selected.get("component_snapshot") if isinstance(selected.get("component_snapshot"), dict) else {}
    feature_snapshot = selected.get("feature_snapshot") if isinstance(selected.get("feature_snapshot"), dict) else {}
    coverage = normalized_feature_coverage(scanner, selected)
    checks: List[Dict[str, str]] = []

    def add_check(name: str, status: str, detail: str) -> None:
        checks.append({"name": name, "status": status, "detail": detail})

    liquidity_pass = "top_value" in sources or safe_float(components.get("trading_value_component"), 0.0) > 0
    turnover_pass = "top_volume" in sources or safe_float(score_breakdown.get("volume_surge"), 0.0) > 0
    theme_score = safe_float(score_breakdown.get("theme_boost"), 0.0)
    theme_pass = "sector_theme" in sources or theme_score > 0.0
    theme_detail = (
        f"selected candidate theme boost was {theme_score:+.3f} or sector_theme source matched"
        if theme_pass
        else f"selected candidate had no sector_theme source and theme boost was {theme_score:+.3f}"
    )
    if coverage["total"] <= 0:
        chart_status = "NOT_AVAILABLE"
    elif coverage["present"] >= 8:
        chart_status = "PASS"
    elif coverage["present"] >= 4:
        chart_status = "PARTIAL"
    else:
        chart_status = "FAIL"
    sentiment_gate = safe_float(components.get("sentiment_component"), 0.0) >= 0 or safe_float(
        strategist.get("global_sentiment_score"),
        0.0,
    ) > -0.35
    risk_gate = bool(supervisor.get("supervisor_allow")) and safe_float(selected.get("risk_score"), 0.0) <= 1.0
    spread_bps = selected.get("spread_bps")
    if spread_bps in (None, ""):
        spread_bps = feature_snapshot.get("quote_spread_bps")
    spread_bps = (safe_float(spread_bps, 0.0) if spread_bps not in (None, "") else None)
    spread_threshold_bps = 50.0
    spread_status = "NOT_AVAILABLE"
    spread_detail = "spread or slippage diagnostics were not captured in this run"
    if spread_bps is not None:
        spread_status = "PASS" if spread_bps <= spread_threshold_bps else "FAIL"
        spread_detail = f"scanner quote snapshot spread was {spread_bps:.1f} bps"

    add_check("liquidity filter", "PASS" if liquidity_pass else "FAIL", "top value or trading-value input supported the selection")
    add_check("turnover filter", "PASS" if turnover_pass else "FAIL", "top volume or turnover input supported the selection")
    add_check("sector/theme alignment", "PASS" if theme_pass else "FAIL", theme_detail)
    add_check("chart completeness filter", chart_status, f"{coverage['present']}/{coverage['total']} captured chart features")
    add_check("sentiment gate", "PASS" if sentiment_gate else "FAIL", f"news/global sentiment contribution was {safe_float(components.get('sentiment_component'), 0.0):.3f}")
    add_check("risk gate", "PASS" if risk_gate else "FAIL", f"risk score was {safe_float(selected.get('risk_score'), 0.0):.3f} and supervisor allow={bool(supervisor.get('supervisor_allow'))}")
    add_check("price anomaly filter", "NOT_AVAILABLE", "price anomaly check was not captured in this run")
    add_check("spread/slippage filter", spread_status, spread_detail)

    passed = sum(1 for row in checks if row["status"] == "PASS")
    bullets = [f"{row['name']}: {row['status']} - {row['detail']}" for row in checks]
    condition_status = str(scanner.get("condition_search_status") or "").strip()
    if condition_status:
        bullets.append(f"Condition search source: {condition_status} ({scanner.get('condition_search_reason') or 'no extra reason captured'})")
    coverage_quality = str(coverage.get("quality") or chart_status.lower()).strip().lower()
    return {
        "checks": checks,
        "summary": (
            f"Scanner and guard checks passed {passed} of {len(checks)} visible gates. "
            f"Chart completeness was {coverage_quality} with {coverage['present']}/{coverage['total']} captured features."
        ),
        "bullets": bullets,
    }
