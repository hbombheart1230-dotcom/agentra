from __future__ import annotations

import sys as _sys
import libs.agents.commander.projections.cache_refresh_read_model as _pure_read_model

import os
from typing import Any, Dict

from libs.runtime.commander.policy_readers import coerce_int
from libs.runtime.commander.strategist_cache_decision import (
    portfolio_open_position_count,
    runtime_now_epoch,
    strategist_cache_payload,
)


def runtime_float(value: Any, default: float = 0.0) -> float:
    return _pure_read_model.runtime_float(value, default, facade=_sys.modules[__name__])


def shadow_float(value: Any) -> float | None:
    return _pure_read_model.shadow_float(value, facade=_sys.modules[__name__])


def shadow_text(value: Any, *, max_len: int = 120) -> str:
    return _pure_read_model.shadow_text(value, max_len=max_len, facade=_sys.modules[__name__])


def portfolio_open_position_symbols(state: Dict[str, Any]) -> list[str]:
    snapshot = state.get("portfolio_snapshot") if isinstance(state.get("portfolio_snapshot"), dict) else {}
    positions = snapshot.get("positions")
    if isinstance(positions, dict):
        rows = list(positions.values())
    elif isinstance(positions, list):
        rows = positions
    else:
        rows = []
    seen: set[str] = set()
    symbols: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if coerce_int(row.get("qty"), 0) <= 0:
            continue
        symbol = str(row.get("symbol") or "").strip().upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        symbols.append(symbol)
    return symbols


def post_scanner_selected_symbol(state: Dict[str, Any]) -> str:
    return _pure_read_model.post_scanner_selected_symbol(state, facade=_sys.modules[__name__])


def score_bucket(value: Any, *, step: float = 0.10) -> str:
    return _pure_read_model.score_bucket(value, step=step, facade=_sys.modules[__name__])


def rank_bucket(value: Any) -> str:
    return _pure_read_model.rank_bucket(value, facade=_sys.modules[__name__])


def entry_gate_bucket(state: Dict[str, Any]) -> str:
    return _pure_read_model.entry_gate_bucket(state, facade=_sys.modules[__name__])


def candidate_theme_tokens(row: Dict[str, Any]) -> list[str]:
    return _pure_read_model.candidate_theme_tokens(row, facade=_sys.modules[__name__])


def candidate_chart_fit_value(row: Dict[str, Any]) -> Any:
    return _pure_read_model.candidate_chart_fit_value(row, facade=_sys.modules[__name__])


def candidate_edge_bucket(row: Dict[str, Any], state: Dict[str, Any]) -> str:
    return _pure_read_model.candidate_edge_bucket(row, state, facade=_sys.modules[__name__])


def compact_post_scanner_candidate_row(row: Dict[str, Any], *, fallback_rank: int = 0) -> Dict[str, Any]:
    return _pure_read_model.compact_post_scanner_candidate_row(row, fallback_rank=fallback_rank, facade=_sys.modules[__name__])


def post_scanner_context_quality(
    *,
    selected_candidate: Dict[str, Any],
    scanner_rank1_candidate: Dict[str, Any],
    runner_ups: list[Dict[str, Any]],
) -> Dict[str, Any]:
    reasons: list[str] = []
    if not str(selected_candidate.get("symbol") or "").strip():
        reasons.append("selected_candidate_missing")
    if coerce_int(selected_candidate.get("rank"), 0) <= 0:
        reasons.append("selected_rank_missing")
    if selected_candidate.get("score") is None and selected_candidate.get("score_total") is None:
        reasons.append("selected_score_missing")
    if not str(scanner_rank1_candidate.get("symbol") or "").strip():
        reasons.append("scanner_rank1_missing")
    if not runner_ups:
        reasons.append("runner_ups_missing")
    quality = "complete"
    if reasons:
        quality = "partial"
    if "selected_candidate_missing" in reasons or "scanner_rank1_missing" in reasons:
        quality = "weak"
    return {"quality": quality, "reasons": reasons}


def post_scanner_candidate_snapshot(state: Dict[str, Any], selected_symbol: str) -> Dict[str, Any]:
    scanner_output = state.get("scanner_output") if isinstance(state.get("scanner_output"), dict) else {}
    raw_rows: list[Any] = []
    for source in (
        state.get("ranked_candidates"),
        scanner_output.get("ranked_candidates"),
        scanner_output.get("candidate_ranking_table", {}).get("rows")
        if isinstance(scanner_output.get("candidate_ranking_table"), dict)
        else [],
        scanner_output.get("runner_ups"),
    ):
        if isinstance(source, list):
            raw_rows.extend(source)
    rows: list[Dict[str, Any]] = []
    seen: set[str] = set()
    for idx, raw in enumerate(raw_rows, start=1):
        if not isinstance(raw, dict):
            continue
        row = compact_post_scanner_candidate_row(raw, fallback_rank=idx)
        symbol = str(row.get("symbol") or "")
        if not symbol or symbol in seen:
            continue
        rows.append(row)
        seen.add(symbol)
        if len(rows) >= 8:
            break
    scanner_rank1_candidate = {}
    for row in rows:
        if coerce_int(row.get("rank"), 0) == 1:
            scanner_rank1_candidate = dict(row)
            break
    if not scanner_rank1_candidate and rows:
        scanner_rank1_candidate = dict(rows[0])
    selected_candidate = {}
    for row in rows:
        if str(row.get("symbol") or "").strip().upper() == selected_symbol:
            selected_candidate = dict(row)
            break
    if selected_symbol and not selected_candidate:
        selected = state.get("selected") if isinstance(state.get("selected"), dict) else {}
        fallback_raw = dict(selected)
        fallback_raw["symbol"] = selected_symbol
        fallback_raw.setdefault("source", "selected")
        selected_candidate = compact_post_scanner_candidate_row(
            fallback_raw,
            fallback_rank=coerce_int(fallback_raw.get("rank") or fallback_raw.get("selected_rank"), 0),
        )
        if not selected_candidate:
            selected_candidate = {
                "symbol": selected_symbol,
                "rank": 0,
                "score": None,
                "score_total": None,
                "reason": "",
                "source": "selected_missing_from_scanner_rows",
            }
        if selected_symbol not in seen:
            rows.append(dict(selected_candidate))
            seen.add(selected_symbol)
    primary = dict(selected_candidate or scanner_rank1_candidate)
    runner_ups = [
        dict(row)
        for row in rows
        if str(row.get("symbol") or "").strip().upper() != selected_symbol
    ][:4]
    quality = post_scanner_context_quality(
        selected_candidate=selected_candidate,
        scanner_rank1_candidate=scanner_rank1_candidate,
        runner_ups=runner_ups,
    )
    return {
        "primary": primary,
        "selected_candidate": dict(selected_candidate),
        "scanner_rank1_candidate": dict(scanner_rank1_candidate),
        "runner_ups": runner_ups,
        "rows": rows[:5],
        "selected_symbol_was_rank1": bool(
            selected_symbol
            and str((scanner_rank1_candidate or {}).get("symbol") or "").strip().upper() == selected_symbol
        ),
        "stage2_context_quality": quality["quality"],
        "stage2_context_quality_reasons": list(quality["reasons"]),
    }


def build_strategist_input_fingerprint(state: Dict[str, Any]) -> Dict[str, Any]:
    selected_symbol = post_scanner_selected_symbol(state)
    snapshot = post_scanner_candidate_snapshot(state, selected_symbol) if selected_symbol else {}
    rows = [dict(row) for row in list(snapshot.get("rows") or []) if isinstance(row, dict)]
    if not rows:
        scanner_output = state.get("scanner_output") if isinstance(state.get("scanner_output"), dict) else {}
        for key in ("candidates", "top_candidates", "ranked_candidates", "pool"):
            raw_rows = scanner_output.get(key)
            if isinstance(raw_rows, list):
                rows = [
                    compact_post_scanner_candidate_row(row, fallback_rank=idx)
                    for idx, row in enumerate(raw_rows[:10], start=1)
                    if isinstance(row, dict)
                ]
                rows = [row for row in rows if row]
                break
    selected_candidate = dict(snapshot.get("selected_candidate") or snapshot.get("primary") or {})
    if not selected_candidate and selected_symbol:
        selected_candidate = next((dict(row) for row in rows if str(row.get("symbol") or "").upper() == selected_symbol), {})
    if not selected_symbol:
        selected_symbol = str(selected_candidate.get("symbol") or "").strip().upper()
    market_context = state.get("market_context") if isinstance(state.get("market_context"), dict) else {}
    open_symbols = portfolio_open_position_symbols(state)
    themes: list[str] = []
    for row in rows[:5]:
        for token in candidate_theme_tokens(row):
            if token not in themes:
                themes.append(token)
    top_symbols = [str(row.get("symbol") or "").strip().upper() for row in rows[:5] if str(row.get("symbol") or "").strip()]
    selected_score = selected_candidate.get("score_total") if selected_candidate.get("score_total") is not None else selected_candidate.get("score")
    return {
        "schema_version": "strategist_input_fingerprint.v1",
        "selected_symbol": selected_symbol,
        "selected_rank_bucket": rank_bucket(selected_candidate.get("rank")),
        "selected_score_bucket": score_bucket(selected_score),
        "selected_chart_fit_bucket": score_bucket(candidate_chart_fit_value(selected_candidate)),
        "selected_edge_bucket": candidate_edge_bucket(selected_candidate, state),
        "entry_gate_bucket": entry_gate_bucket(state),
        "top_symbols": top_symbols[:5],
        "top3_symbols": top_symbols[:3],
        "top_themes": themes[:5],
        "market_regime": str(
            state.get("market_regime")
            or market_context.get("regime")
            or market_context.get("market_regime")
            or ""
        ).strip().lower()[:80],
        "open_position_count": int(portfolio_open_position_count(state)),
        "open_symbols": sorted(open_symbols),
    }


def jaccard_distance(left: list[str], right: list[str]) -> float:
    left_set = {str(x or "").strip() for x in left if str(x or "").strip()}
    right_set = {str(x or "").strip() for x in right if str(x or "").strip()}
    if not left_set and not right_set:
        return 0.0
    if not left_set or not right_set:
        return 1.0
    return float(1.0 - (len(left_set & right_set) / len(left_set | right_set)))


def assess_strategist_fingerprint_drift(
    previous: Dict[str, Any],
    current: Dict[str, Any],
    *,
    threshold: float | None = None,
) -> Dict[str, Any]:
    prev = dict(previous or {}) if isinstance(previous, dict) else {}
    cur = dict(current or {}) if isinstance(current, dict) else {}
    effective_threshold = (
        float(threshold)
        if threshold is not None
        else float(runtime_float(os.getenv("COMMANDER_STRATEGIST_INPUT_DRIFT_THRESHOLD", "0.45"), 0.45))
    )
    reasons: list[str] = []
    if not prev or not cur:
        return {
            "comparable": False,
            "material_change": True,
            "change_score": 1.0,
            "threshold": float(effective_threshold),
            "reasons": ["fingerprint_missing"],
            "previous": prev,
            "current": cur,
        }
    score = 0.0
    if str(prev.get("selected_symbol") or "") != str(cur.get("selected_symbol") or ""):
        score += 0.30
        reasons.append("selected_symbol_changed")
    top_distance = jaccard_distance(list(prev.get("top_symbols") or []), list(cur.get("top_symbols") or []))
    if top_distance > 0.0:
        score += 0.25 * top_distance
        reasons.append("top_symbols_changed")
    theme_distance = jaccard_distance(list(prev.get("top_themes") or []), list(cur.get("top_themes") or []))
    if theme_distance > 0.0:
        score += 0.10 * theme_distance
        reasons.append("top_themes_changed")
    for key, weight, reason in (
        ("selected_rank_bucket", 0.08, "selected_rank_bucket_changed"),
        ("selected_chart_fit_bucket", 0.12, "selected_chart_fit_bucket_changed"),
        ("selected_edge_bucket", 0.12, "selected_edge_bucket_changed"),
        ("entry_gate_bucket", 0.10, "entry_gate_changed"),
        ("market_regime", 0.10, "market_regime_changed"),
    ):
        if str(prev.get(key) or "") != str(cur.get(key) or ""):
            score += weight
            reasons.append(reason)
    if int(prev.get("open_position_count") or 0) != int(cur.get("open_position_count") or 0):
        score += 0.15
        reasons.append("open_position_count_changed")
    if sorted(list(prev.get("open_symbols") or [])) != sorted(list(cur.get("open_symbols") or [])):
        score += 0.12
        reasons.append("open_symbols_changed")
    score = min(1.0, float(score))
    return {
        "comparable": True,
        "material_change": bool(score >= effective_threshold),
        "change_score": round(score, 6),
        "threshold": float(effective_threshold),
        "reasons": reasons,
        "previous": prev,
        "current": cur,
    }


def assess_cached_strategist_input_drift(state: Dict[str, Any]) -> Dict[str, Any]:
    cache_payload = strategist_cache_payload(state)
    previous = cache_payload.get("input_fingerprint") if isinstance(cache_payload.get("input_fingerprint"), dict) else {}
    current = build_strategist_input_fingerprint(state)
    out = assess_strategist_fingerprint_drift(previous, current)
    out["cache_source"] = str(cache_payload.get("source") or "")
    out["cache_age_sec"] = (
        max(0, runtime_now_epoch(state) - coerce_int(cache_payload.get("generated_epoch"), 0))
        if coerce_int(cache_payload.get("generated_epoch"), 0) > 0
        else None
    )
    return out
