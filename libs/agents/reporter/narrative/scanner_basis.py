"""Reporter story-scanner narrative owner (decomposed) (scanner_basis; definitions copied verbatim from libs/reporting/trade_story_pipeline_scanner.py)."""
from __future__ import annotations
from typing import Any, Dict, List, Mapping


def _korea_indices_bullet(korea_indices: Any) -> str:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    packet = korea_indices if isinstance(korea_indices, dict) else {}
    indices = packet.get("indices") if isinstance(packet.get("indices"), dict) else {}
    parts: List[str] = []
    for name in ("KOSPI", "KOSDAQ"):
        row = indices.get(name) if isinstance(indices.get(name), dict) else {}
        if not row:
            continue
        parts.append(
            f"{name} current={_facade.format_pct(row.get('current'))} "
            f"previous_close={_facade.format_pct(row.get('previous_close'))} "
            f"change={_facade.format_pct(row.get('change_pct'))}%"
        )
    return "; ".join(parts)


def _top_numeric_drivers(values: Any, *, limit: int = 4) -> Dict[str, float]:
    if not isinstance(values, dict):
        return {}
    scored: List[tuple[float, str, float]] = []
    for key, value in values.items():
        try:
            numeric = float(value)
        except Exception:
            continue
        if numeric == 0.0:
            continue
        scored.append((abs(numeric), str(key), numeric))
    scored.sort(key=lambda row: (-row[0], row[1]))
    out: Dict[str, float] = {}
    for _, key, numeric in scored[: max(1, int(limit))]:
        out[key] = numeric
    return out


def _scanner_chart_fit_payload(row: Mapping[str, Any] | None) -> Dict[str, Any]:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    obj = dict(row or {}) if isinstance(row, Mapping) else {}
    score = obj.get("scanner_chart_fit_score")
    authority = str(obj.get("scanner_chart_fit_authority") or "").strip()
    components = obj.get("scanner_chart_fit_components") if isinstance(obj.get("scanner_chart_fit_components"), dict) else {}
    if score in (None, "") and not authority and not components:
        return {}
    return {
        "score": _facade.safe_float(score, 0.0) if score not in (None, "") else None,
        "authority": authority,
        "components": dict(components or {}),
    }


def _scanner_macro_chart_fit_payload(row: Mapping[str, Any] | None) -> Dict[str, Any]:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    obj = dict(row or {}) if isinstance(row, Mapping) else {}
    score = obj.get("scanner_macro_chart_fit_score")
    authority = str(obj.get("scanner_macro_chart_fit_authority") or "").strip()
    components = (
        obj.get("scanner_macro_chart_fit_components")
        if isinstance(obj.get("scanner_macro_chart_fit_components"), dict)
        else {}
    )
    bias = obj.get("scanner_macro_chart_fit_bias")
    if score in (None, "") and bias in (None, "") and not authority and not components:
        return {}
    return {
        "score": _facade.safe_float(score, 0.0) if score not in (None, "") else None,
        "bias": _facade.safe_float(bias, 0.0) if bias not in (None, "") else None,
        "authority": authority,
        "components": dict(components or {}),
    }


def _candidate_sources_from_score_breakdown(score_breakdown: Mapping[str, Any] | None) -> List[str]:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    scores = dict(score_breakdown or {})
    sources: List[str] = []
    if _facade.safe_float(scores.get("trading_value"), 0.0) > 0.0:
        sources.append("top_value")
    if _facade.safe_float(scores.get("volume_surge"), 0.0) > 0.0:
        sources.append("top_volume")
    if _facade.safe_float(scores.get("theme_boost"), 0.0) > 0.0:
        sources.append("sector_theme")
    if _facade.safe_float(scores.get("sentiment"), 0.0) > 0.0:
        sources.append("sentiment")
    return sources


def _selection_basis_from_scores(
    score_breakdown: Mapping[str, Any] | None,
    sources: List[str],
) -> List[str]:
    # Resolve through the compatibility façade to retain call-time patched helpers.
    from libs.reporting import trade_story_pipeline as _facade
    scores = dict(score_breakdown or {})
    basis: List[str] = []
    if _facade.safe_float(scores.get("trading_value"), 0.0) > 0.0 or "top_value" in sources:
        basis.append("trading value")
    if _facade.safe_float(scores.get("volume_surge"), 0.0) > 0.0 or "top_volume" in sources:
        basis.append("turnover and volume")
    if _facade.safe_float(scores.get("theme_boost"), 0.0) > 0.0 or "sector_theme" in sources:
        basis.append("theme and sector alignment")
    if _facade.safe_float(scores.get("sentiment"), 0.0) > 0.0 or "sentiment" in sources:
        basis.append("sentiment support")
    if not basis and _facade.safe_float(scores.get("momentum"), 0.0) > 0.0:
        basis.append("momentum")
    if not basis and _facade.safe_float(scores.get("trend"), 0.0) > 0.0:
        basis.append("trend")
    if not basis:
        basis.append("combined scanner ranking score")
    return basis
