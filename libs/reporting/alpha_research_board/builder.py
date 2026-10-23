from __future__ import annotations

import json
import sys as _sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from libs.reporting.alpha_research_board.candidate_rows import (  # noqa: F401 - facade ABI re-exports
    _broad_opening_impl,
    _btc_woori_impl,
    _candidate_impl,
    _feature_candidates_impl,
    _fresh_change_impl,
    _latent_impl,
    _opening_rows_impl,
    _q12_hypothesis_metric_impl,
)
from libs.reporting.alpha_research_board.board_assembly import (  # noqa: F401 - facade ABI re-exports
    _attention_order_impl,
    apply_final_offline_reviews,
    apply_sensitivity_review,
    find_missing_sources,
    legacy_board_payload_impl,
    short_alpha_candidate_impl,
    strong_btc_candidate_impl,
)
from .contracts import (
    LIVE_RESEARCH_COST_PCT,
    SCHEMA_VERSION,
    SETTLED_FINDINGS,
    SOURCE_PATHS,
    TRACKS,
)
from .canonical import canonicalize_board
from .loaders import find_by_id, find_horizon, load_json, mapping, metric_snapshot
from .large_cap_review import build_large_cap_daily_review
from .report import render_alpha_research_board
from .remaining_reviews import (
    build_remaining_candidate_reviews,
    render_remaining_candidate_reviews,
)
from .runtime_validation import (
    build_immediate_opening_runtime_validation,
    render_immediate_opening_runtime_validation,
)
from .sensitivity import build_risk_high_sensitivity, render_risk_high_sensitivity
from ..short_alpha_discriminator import build_short_alpha_discriminator
from ..short_alpha_discriminator.report import render_short_alpha_discriminator


def _candidate(
    *,
    candidate_id: str,
    track_id: str,
    discriminator: str,
    target_horizon: str,
    source_status: str,
    board_bucket: str,
    owner: str,
    historical: Mapping[str, Any] | None = None,
    validation: Mapping[str, Any] | None = None,
    prospective: Mapping[str, Any] | None = None,
    concentration: Mapping[str, Any] | None = None,
    evidence_note: str,
    next_action: str,
    source_keys: list[str],
) -> dict[str, Any]:
    return _candidate_impl(candidate_id=candidate_id, track_id=track_id, discriminator=discriminator, target_horizon=target_horizon, source_status=source_status, board_bucket=board_bucket, owner=owner, historical=historical, validation=validation, prospective=prospective, concentration=concentration, evidence_note=evidence_note, next_action=next_action, source_keys=source_keys, facade=_sys.modules[__name__])


def _q12_hypothesis_metric(
    payload: Mapping[str, Any],
    *,
    phase: str,
    path_value: str = "FAST_BUY_ALL_PASS",
    entry_method: str = "09:05",
    horizon: str = "+30m",
) -> dict[str, Any]:
    return _q12_hypothesis_metric_impl(payload, phase=phase, path_value=path_value, entry_method=entry_method, horizon=horizon, facade=_sys.modules[__name__])


def _feature_candidates(
    feature_payload: Mapping[str, Any],
    prospective_payload: Mapping[str, Any],
    concentrations: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return _feature_candidates_impl(feature_payload, prospective_payload, concentrations, facade=_sys.modules[__name__])


def _prospective_concentrations(
    *, reports_root: Path, first_day: str, through_day: str
) -> dict[str, dict[str, Any]]:
    daily_root = (
        reports_root
        / "evaluation"
        / "feature_mart"
        / "opening_rank1"
        / "prospective"
    )
    day_symbols: dict[str, set[tuple[str, str]]] = {}
    for path in sorted(daily_root.glob("20??-??-??/rank1_candidate_shadow_daily.json")):
        day = path.parent.name
        if day < first_day or day > through_day:
            continue
        payload, source = load_json(path)
        if source.get("error"):
            continue
        for value in payload.get("observations") or []:
            row = mapping(value)
            if not row.get("matched"):
                continue
            candidate_id = str(row.get("candidate_id") or "")
            symbol = str(row.get("symbol") or "")
            row_day = str(row.get("day") or day)
            if candidate_id and symbol:
                day_symbols.setdefault(candidate_id, set()).add((row_day, symbol))

    def _largest_key(counts: Counter[str]) -> str | None:
        """Return a reproducible mode: count descending, key ascending.

        ``Counter.most_common(1)`` preserves first-seen order for ties.  The
        source population above is accumulated in sets, whose iteration order
        intentionally varies between Python hash seeds, so it cannot define
        daily authority identity.
        """
        if not counts:
            return None
        return min(counts, key=lambda key: (-counts[key], key))

    result: dict[str, dict[str, Any]] = {}
    for candidate_id, pairs in day_symbols.items():
        days = Counter(day for day, _symbol in pairs)
        symbols = Counter(symbol for _day, symbol in pairs)
        count = len(pairs)
        result[candidate_id] = {
            "independent_day_symbol_count": count,
            "observed_day_count": len(days),
            "largest_day_share": round(max(days.values()) / count, 4) if count else None,
            "largest_symbol_share": round(max(symbols.values()) / count, 4) if count else None,
            "largest_day": _largest_key(days),
            "largest_symbol": _largest_key(symbols),
        }
    return result


def _fresh_change(payload: Mapping[str, Any]) -> dict[str, Any]:
    return _fresh_change_impl(payload, facade=_sys.modules[__name__])


def _opening_rows(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    return _opening_rows_impl(payload, facade=_sys.modules[__name__])


def _broad_opening(payload: Mapping[str, Any]) -> dict[str, Any]:
    return _broad_opening_impl(payload, facade=_sys.modules[__name__])


def _latent(payload: Mapping[str, Any]) -> dict[str, Any]:
    return _latent_impl(payload, facade=_sys.modules[__name__])


def _btc_woori(payload: Mapping[str, Any]) -> dict[str, Any]:
    return _btc_woori_impl(payload, facade=_sys.modules[__name__])


def _large_cap_candidate(reports_root: Path, through_day: str) -> tuple[dict[str, Any], dict[str, Any]]:
    review = build_large_cap_daily_review(
        reports_root=reports_root, through_day=through_day
    )
    live_net = metric_snapshot(review.get("base"))
    live_net["window_count"] = int(mapping(review.get("base")).get("window_count") or 0)
    row = _candidate(
        candidate_id="SAMSUNG_HYNIX_FIXED_UNIVERSE_TOP1",
        track_id="LARGE_CAP_TWO_SYMBOL",
        discriminator="momentum + volume confirmation within fixed two-symbol universe",
        target_horizon="+180m",
        source_status=str(review.get("decision") or "RUNTIME_DATA_REQUIRED"),
        board_bucket="BACKGROUND_RUNTIME_REQUIRED",
        owner="SAMSUNG_HYNIX_BASELINE",
        prospective=live_net,
        evidence_note="정합성 수정 이후 하루만 비교 가능하며 반복 window는 독립 거래가 아님.",
        next_action="과거 시점 오류 자료를 섞지 않고 수정 이후 day-level episode만 누적.",
        source_keys=["large_cap_daily"],
    )
    return row, {
        "path": "multiple_daily_artifacts",
        "available": bool(review.get("source_count")),
        "error": "INVALID_DAILY_ARTIFACT" if review.get("invalid_sources") else None,
        "through_day": through_day,
        "source_count": review.get("source_count"),
    }


def _attention_order(candidates: list[dict[str, Any]]) -> list[str]:
    return _attention_order_impl(candidates, facade=_sys.modules[__name__])


def build_alpha_research_board(
    *, reports_root: Path, through_day: str
) -> dict[str, Any]:
    sources: dict[str, dict[str, Any]] = {}
    payloads: dict[str, dict[str, Any]] = {}
    for key, relative_path in SOURCE_PATHS.items():
        payloads[key], sources[key] = load_json(reports_root / relative_path)
    q12_hypothesis_path = (
        reports_root
        / "evaluation"
        / "baseline_btc_woori_tech"
        / "hypothesis_validation"
        / "q12_btc_woori_hypothesis_cumulative.json"
    )
    if q12_hypothesis_path.exists():
        payloads["btc_woori_hypothesis"], sources["btc_woori_hypothesis"] = load_json(
            q12_hypothesis_path
        )

    contract = mapping(payloads.get("prospective_contract"))
    concentrations = _prospective_concentrations(
        reports_root=reports_root,
        first_day=str(contract.get("first_eligible_day") or "0000-00-00"),
        through_day=through_day,
    )
    candidates = _feature_candidates(
        payloads["feature_candidates"],
        payloads["prospective_candidates"],
        concentrations,
    )
    risk_high_sensitivity = build_risk_high_sensitivity(
        reports_root=reports_root,
        first_day=str(contract.get("first_eligible_day") or "0000-00-00"),
        through_day=through_day,
    )
    apply_sensitivity_review(candidates, risk_high_sensitivity)
    candidates.extend(_opening_rows(payloads["opening_cumulative"]))
    candidates.extend(
        [
            _broad_opening(payloads["opening_cumulative"]),
            _fresh_change(payloads["fresh_change"]),
            _latent(payloads["latent_reactivation"]),
            _btc_woori(payloads["btc_woori_history"]),
        ]
    )
    large_cap, large_cap_source = _large_cap_candidate(reports_root, through_day)
    candidates.append(large_cap)
    sources["large_cap_daily"] = large_cap_source
    remaining_reviews = build_remaining_candidate_reviews(
        reports_root=reports_root, through_day=through_day
    )
    candidates.append(strong_btc_candidate_impl(remaining_reviews, payloads, facade=_sys.modules[__name__]))
    short_alpha_review = build_short_alpha_discriminator(
        reports_root=reports_root,
        through_day=through_day,
    )
    candidates.append(short_alpha_candidate_impl(short_alpha_review, facade=_sys.modules[__name__]))
    runtime_validation = build_immediate_opening_runtime_validation(
        reports_root=reports_root, through_day=through_day
    )
    apply_final_offline_reviews(candidates, remaining_reviews, facade=_sys.modules[__name__])

    missing_sources = find_missing_sources(sources)
    legacy_payload = legacy_board_payload_impl(
        generated_at=datetime.now(timezone.utc).isoformat(),
        through_day=through_day,
        candidates=candidates,
        risk_high_sensitivity=risk_high_sensitivity,
        remaining_reviews=remaining_reviews,
        runtime_validation=runtime_validation,
        short_alpha_review=short_alpha_review,
        missing_sources=missing_sources,
        sources=sources,
        facade=_sys.modules[__name__],
    )
    return canonicalize_board(
        legacy_payload,
        reports_root=reports_root,
        through_day=through_day,
    )


def write_alpha_research_board(
    *, reports_root: Path, through_day: str, output_dir: Path
) -> dict[str, Any]:
    payload = build_alpha_research_board(
        reports_root=reports_root, through_day=through_day
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "alpha_research_board.json"
    markdown_path = output_dir / "alpha_research_board.md"
    sensitivity_json_path = output_dir / "risk_high_30m_sensitivity.json"
    sensitivity_markdown_path = output_dir / "risk_high_30m_sensitivity.md"
    remaining_json_path = output_dir / "remaining_candidate_reviews.json"
    remaining_markdown_path = output_dir / "remaining_candidate_reviews.md"
    runtime_json_path = output_dir / "immediate_opening_runtime_validation.json"
    runtime_markdown_path = output_dir / "immediate_opening_runtime_validation.md"
    short_alpha_json_path = output_dir / "short_alpha_discriminator.json"
    short_alpha_markdown_path = output_dir / "short_alpha_discriminator.md"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    markdown = render_alpha_research_board(payload)
    markdown_path.write_text(markdown, encoding="utf-8")
    latest_dir = output_dir.parent
    latest_json_path = latest_dir / "latest.json"
    latest_markdown_path = latest_dir / "latest.md"
    latest_json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    latest_markdown_path.write_text(markdown, encoding="utf-8")
    # Canonicalization intentionally keeps the board schema small. Diagnostic
    # companions are rebuilt from their authoritative builders instead of
    # attempting to read legacy-only keys from the canonical payload.
    contract = mapping(payload.get("prospective_contract"))
    sensitivity = build_risk_high_sensitivity(
        reports_root=reports_root,
        first_day=str(contract.get("first_eligible_day") or "0000-00-00"),
        through_day=through_day,
    )
    sensitivity_json_path.write_text(
        json.dumps(sensitivity, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    sensitivity_markdown_path.write_text(
        render_risk_high_sensitivity(sensitivity), encoding="utf-8"
    )
    remaining = build_remaining_candidate_reviews(
        reports_root=reports_root,
        through_day=through_day,
    )
    remaining_json_path.write_text(
        json.dumps(remaining, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    remaining_markdown_path.write_text(
        render_remaining_candidate_reviews(remaining), encoding="utf-8"
    )
    runtime_validation = build_immediate_opening_runtime_validation(
        reports_root=reports_root,
        through_day=through_day,
    )
    runtime_json_path.write_text(
        json.dumps(runtime_validation, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    runtime_markdown_path.write_text(
        render_immediate_opening_runtime_validation(runtime_validation), encoding="utf-8"
    )
    short_alpha = build_short_alpha_discriminator(
        reports_root=reports_root,
        through_day=through_day,
    )
    short_alpha_json_path.write_text(
        json.dumps(short_alpha, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    short_alpha_markdown_path.write_text(
        render_short_alpha_discriminator(short_alpha), encoding="utf-8"
    )
    return {
        "json_path": str(json_path),
        "markdown_path": str(markdown_path),
        "latest_json_path": str(latest_json_path),
        "latest_markdown_path": str(latest_markdown_path),
        "sensitivity_json_path": str(sensitivity_json_path),
        "sensitivity_markdown_path": str(sensitivity_markdown_path),
        "remaining_json_path": str(remaining_json_path),
        "remaining_markdown_path": str(remaining_markdown_path),
        "runtime_json_path": str(runtime_json_path),
        "runtime_markdown_path": str(runtime_markdown_path),
        "short_alpha_json_path": str(short_alpha_json_path),
        "short_alpha_markdown_path": str(short_alpha_markdown_path),
        "candidate_count": payload["candidate_count"],
        "integrity_status": mapping(payload.get("integrity")).get("status"),
    }
