from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .contracts import (
    LIVE_RESEARCH_COST_PCT,
    SCHEMA_VERSION,
    SETTLED_FINDINGS,
    SOURCE_PATHS,
    TRACKS,
)
from .canonical import canonicalize_board
from . import builder_prospective_concentrations as _builder_prospective_concentrations_owner
from . import builder_large_cap_candidate as _builder_large_cap_candidate_owner
from . import builder_q12_hypothesis_metric as _builder_q12_hypothesis_metric_owner
from . import builder_feature_candidates as _builder_feature_candidates_owner
from . import builder_btc_woori as _builder_btc_woori_owner
from . import builder_opening_rows as _builder_opening_rows_owner
from . import builder_broad_opening as _builder_broad_opening_owner
from . import builder_latent as _builder_latent_owner
from . import builder_fresh_change as _builder_fresh_change_owner
from . import builder_attention_order as _builder_attention_order_owner
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
    return {
        "candidate_id": candidate_id,
        "track_id": track_id,
        "discriminator": discriminator,
        "target_horizon": target_horizon,
        "source_status": source_status,
        "board_bucket": board_bucket,
        "responsibility_if_proven": owner,
        "historical": dict(historical or {}),
        "validation": dict(validation or {}),
        "prospective": dict(prospective or {}),
        "concentration": dict(concentration or {}),
        "evidence_note": evidence_note,
        "next_action": next_action,
        "source_keys": source_keys,
    }


def _q12_hypothesis_metric(
    payload: Mapping[str, Any],
    *,
    phase: str,
    path_value: str = "FAST_BUY_ALL_PASS",
    entry_method: str = "09:05",
    horizon: str = "+30m",
) -> dict[str, Any]:
    return _builder_q12_hypothesis_metric_owner._q12_hypothesis_metric(payload, phase=phase, path_value=path_value, entry_method=entry_method, horizon=horizon, facade=sys.modules[__name__])


def _feature_candidates(
    feature_payload: Mapping[str, Any],
    prospective_payload: Mapping[str, Any],
    concentrations: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return _builder_feature_candidates_owner._feature_candidates(feature_payload, prospective_payload, concentrations, facade=sys.modules[__name__])


def _prospective_concentrations(
    *, reports_root: Path, first_day: str, through_day: str
) -> dict[str, dict[str, Any]]:
    return _builder_prospective_concentrations_owner.prospective_concentrations(reports_root=reports_root, first_day=first_day, through_day=through_day, facade=sys.modules[__name__])


def _fresh_change(payload: Mapping[str, Any]) -> dict[str, Any]:
    return _builder_fresh_change_owner._fresh_change(payload, facade=sys.modules[__name__])


def _opening_rows(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    return _builder_opening_rows_owner._opening_rows(payload, facade=sys.modules[__name__])


def _broad_opening(payload: Mapping[str, Any]) -> dict[str, Any]:
    return _builder_broad_opening_owner._broad_opening(payload, facade=sys.modules[__name__])


def _latent(payload: Mapping[str, Any]) -> dict[str, Any]:
    return _builder_latent_owner._latent(payload, facade=sys.modules[__name__])


def _btc_woori(payload: Mapping[str, Any]) -> dict[str, Any]:
    return _builder_btc_woori_owner._btc_woori(payload, facade=sys.modules[__name__])


def _large_cap_candidate(reports_root: Path, through_day: str) -> tuple[dict[str, Any], dict[str, Any]]:
    return _builder_large_cap_candidate_owner.large_cap_candidate(reports_root, through_day, facade=sys.modules[__name__])


def _attention_order(candidates: list[dict[str, Any]]) -> list[str]:
    return _builder_attention_order_owner._attention_order(candidates)


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
    for row in candidates:
        if row.get("candidate_id") != "R1_SCANNER_RISK_HIGH_30M_V1":
            continue
        row["sensitivity_review"] = {
            "decision": risk_high_sensitivity.get("decision"),
            "rationale": risk_high_sensitivity.get("rationale"),
        }
        if risk_high_sensitivity.get("decision") != "PROMOTION_REVIEW_PASS":
            row["board_bucket"] = "CLOSED_AFTER_SENSITIVITY_REVIEW"
            row["evidence_note"] = (
                "과거·검증·prospective 평균은 양수였지만 수익 기여 종목 leave-one-out에서 PF 기준이 무너짐."
            )
            row["next_action"] = (
                "일반 risk-band 구분자로는 기각. 결과를 보고 threshold를 재튜닝하지 않음."
            )
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
    broad_btc_review = next(
        (
            mapping(row)
            for row in remaining_reviews.get("reviews") or []
            if mapping(row).get("candidate_id") == "BTC_WOORI_V2_ONLY_LOCAL_CONFIRMATION"
        ),
        {},
    )
    strong_btc_history = next(
        (
            mapping(row)
            for row in broad_btc_review.get("by_btc_regime") or []
            if mapping(row).get("btc_regime") == "strong_bull"
        ),
        {},
    )
    candidates.append(
        _candidate(
            candidate_id="BTC_STRONG_BULL_LOCAL_CONFIRMATION_V1",
            track_id="BTC_WOORI",
            discriminator="BTC 60m >= 1.0% or 24h >= 3.0%, plus Woori local confirmation",
            target_horizon="+30m",
            source_status="PROSPECTIVE_SHADOW_FROM_2026_08_25",
            board_bucket="BACKGROUND_RUNTIME_REQUIRED",
            owner="BTC_WOORI_BASELINE",
            historical=metric_snapshot(strong_btc_history),
            prospective=_q12_hypothesis_metric(
                payloads.get("btc_woori_hypothesis") or {},
                phase="PROSPECTIVE",
            ),
            evidence_note=(
                "The historical strong-bull subgroup is hypothesis-generating only; "
                "the rejected broad BTC rule remains closed."
            ),
            next_action=(
                "Collect only the fixed additive shadow variant from the next full session."
            ),
            source_keys=[
                "btc_woori_history",
                *(
                    ["btc_woori_hypothesis"]
                    if payloads.get("btc_woori_hypothesis")
                    else []
                ),
            ],
        )
    )
    short_alpha_review = build_short_alpha_discriminator(
        reports_root=reports_root,
        through_day=through_day,
    )
    short_cohort_review = mapping(short_alpha_review.get("cohort_review"))
    short_historical = mapping(short_cohort_review.get("historical_reference"))
    short_prospective = mapping(short_cohort_review.get("prospective"))
    historical_5m = mapping(mapping(short_historical.get("horizons")).get("+5m"))
    prospective_5m = mapping(mapping(short_prospective.get("horizons")).get("+5m"))
    candidates.append(
        _candidate(
            candidate_id="HIGH_COMMON_SHORT_ALPHA_V1",
            track_id="OPENING_CONDITIONAL",
            discriminator="risk HIGH + common stock short-horizon alpha",
            target_horizon="+5m",
            source_status="PROSPECTIVE_SHADOW_FROM_2026_08_25",
            board_bucket="BACKGROUND_RUNTIME_REQUIRED",
            owner="SCANNER_OR_HORIZON_REVIEW",
            historical=metric_snapshot(historical_5m),
            prospective=metric_snapshot(prospective_5m),
            concentration={
                "historical_day_count": short_historical.get("day_count"),
                "historical_largest_day_share": short_historical.get("largest_day_share"),
                "historical_largest_symbol_share": short_historical.get("largest_symbol_share"),
            },
            evidence_note=(
                "Post-hoc historical discriminator. Historical and prospective "
                "episodes are kept separate and no behavior is changed."
            ),
            next_action=(
                "Collect the frozen HIGH common-stock cohort at +5m/+15m/+30m/EOD."
            ),
            source_keys=["short_alpha_discriminator"],
        )
    )
    runtime_validation = build_immediate_opening_runtime_validation(
        reports_root=reports_root, through_day=through_day
    )
    reviews_by_id = {
        str(row.get("candidate_id")): mapping(row)
        for row in remaining_reviews.get("reviews") or []
    }
    for row in candidates:
        review = reviews_by_id.get(str(row.get("candidate_id")))
        if not review:
            continue
        row["final_offline_review"] = {
            "decision": review.get("decision"),
            "rationale": review.get("rationale"),
        }
        decision = str(review.get("decision") or "")
        if decision == "READY_FOR_FIXED_RUNTIME_VALIDATION":
            row["board_bucket"] = "RUNTIME_VALIDATION_NEXT"
            row["next_action"] = "기존 observer로 고정된 5거래일 prospective 런 검증 수행."
        elif decision == "RUNTIME_DATA_REQUIRED":
            row["board_bucket"] = "BACKGROUND_RUNTIME_REQUIRED"
            row["next_action"] = "행동 변경 없이 기존 artifact로 필요한 독립 표본만 수집."
        elif decision.startswith("REJECT"):
            row["board_bucket"] = "CLOSED_AFTER_SENSITIVITY_REVIEW"
            row["evidence_note"] = str(review.get("rationale") or row.get("evidence_note"))
            row["next_action"] = "오프라인 판정 종료. 재튜닝하거나 이름을 바꿔 재개하지 않음."

    missing_sources = [
        key for key, source in sources.items() if not source.get("available") or source.get("error")
    ]
    legacy_payload = {
        "schema_version": SCHEMA_VERSION,
        "behavior_effect": "evaluation_only",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "through_day": through_day,
        "cost_authority": {
            "live_equity_round_trip_pct": LIVE_RESEARCH_COST_PCT,
            "rule": "Gross, live-research net, and broker mock net must not be mixed.",
        },
        "purpose": "Consolidate existing evidence; do not rerun broad historical mining.",
        "tracks": TRACKS,
        "candidate_count": len(candidates),
        "attention_order": _attention_order(candidates),
        "candidates": candidates,
        "sensitivity_reviews": [risk_high_sensitivity],
        "remaining_candidate_reviews": remaining_reviews,
        "runtime_validation": runtime_validation,
        "short_alpha_discriminator": short_alpha_review,
        "settled_findings": SETTLED_FINDINGS,
        "integrity": {
            "status": "PASS" if not missing_sources else "PASS_WITH_MISSING_SOURCES",
            "missing_or_invalid_sources": missing_sources,
        },
        "sources": sources,
        "behavior_change_authorized": False,
    }
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
