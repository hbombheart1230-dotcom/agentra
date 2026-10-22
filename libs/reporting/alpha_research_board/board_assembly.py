"""Pure board assembly for the alpha research board (P1.5 DEV-A).

Attention ordering, the in-place sensitivity and final-offline-review adjustments of candidate rows, the two rows that
are derived from other reviews (strong-bull BTC, short alpha), the missing-source list and the legacy board payload. No
I/O or clock (``generated_at`` is passed in): ``libs.reporting.alpha_research_board.builder`` runs every builder and
reader in the original order and then calls these. Helpers and contract constants are read on the injected ``facade``
at call time.
"""
from __future__ import annotations

from typing import Any, Mapping


def _attention_order_impl(candidates: list[dict[str, Any]], *, facade: Any) -> list[str]:
    order = {
        "RUNTIME_VALIDATION_NEXT": 0,
        "BACKGROUND_RUNTIME_REQUIRED": 1,
        "ACTION_REVIEW": 2,
        "OBSERVE_FIXED": 3,
        "DATA_REPAIR_BOUNDARY": 4,
        "CLOSED_AFTER_SENSITIVITY_REVIEW": 5,
        "CLOSED_NEGATIVE_PROSPECTIVE": 6,
        "CLOSED": 7,
    }
    return [
        row["candidate_id"]
        for row in sorted(
            candidates,
            key=lambda row: (order.get(str(row.get("board_bucket")), 9), row["candidate_id"]),
        )
    ]


def apply_sensitivity_review(candidates: list[dict[str, Any]], risk_high_sensitivity: Mapping[str, Any]) -> None:
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


def strong_btc_candidate_impl(
    remaining_reviews: Mapping[str, Any],
    payloads: Mapping[str, Any],
    *,
    facade: Any,
) -> dict[str, Any]:
    broad_btc_review = next(
        (
            facade.mapping(row)
            for row in remaining_reviews.get("reviews") or []
            if facade.mapping(row).get("candidate_id") == "BTC_WOORI_V2_ONLY_LOCAL_CONFIRMATION"
        ),
        {},
    )
    strong_btc_history = next(
        (
            facade.mapping(row)
            for row in broad_btc_review.get("by_btc_regime") or []
            if facade.mapping(row).get("btc_regime") == "strong_bull"
        ),
        {},
    )
    return facade._candidate(
        candidate_id="BTC_STRONG_BULL_LOCAL_CONFIRMATION_V1",
        track_id="BTC_WOORI",
        discriminator="BTC 60m >= 1.0% or 24h >= 3.0%, plus Woori local confirmation",
        target_horizon="+30m",
        source_status="PROSPECTIVE_SHADOW_FROM_2026_08_25",
        board_bucket="BACKGROUND_RUNTIME_REQUIRED",
        owner="BTC_WOORI_BASELINE",
        historical=facade.metric_snapshot(strong_btc_history),
        prospective=facade._q12_hypothesis_metric(
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


def short_alpha_candidate_impl(short_alpha_review: Mapping[str, Any], *, facade: Any) -> dict[str, Any]:
    short_cohort_review = facade.mapping(short_alpha_review.get("cohort_review"))
    short_historical = facade.mapping(short_cohort_review.get("historical_reference"))
    short_prospective = facade.mapping(short_cohort_review.get("prospective"))
    historical_5m = facade.mapping(facade.mapping(short_historical.get("horizons")).get("+5m"))
    prospective_5m = facade.mapping(facade.mapping(short_prospective.get("horizons")).get("+5m"))
    return facade._candidate(
        candidate_id="HIGH_COMMON_SHORT_ALPHA_V1",
        track_id="OPENING_CONDITIONAL",
        discriminator="risk HIGH + common stock short-horizon alpha",
        target_horizon="+5m",
        source_status="PROSPECTIVE_SHADOW_FROM_2026_08_25",
        board_bucket="BACKGROUND_RUNTIME_REQUIRED",
        owner="SCANNER_OR_HORIZON_REVIEW",
        historical=facade.metric_snapshot(historical_5m),
        prospective=facade.metric_snapshot(prospective_5m),
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


def apply_final_offline_reviews(
    candidates: list[dict[str, Any]],
    remaining_reviews: Mapping[str, Any],
    *,
    facade: Any,
) -> None:
    reviews_by_id = {
        str(row.get("candidate_id")): facade.mapping(row)
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


def find_missing_sources(sources: Mapping[str, Mapping[str, Any]]) -> list[str]:
    return [
        key for key, source in sources.items() if not source.get("available") or source.get("error")
    ]


def legacy_board_payload_impl(
    *,
    generated_at: str,
    through_day: str,
    candidates: list[dict[str, Any]],
    risk_high_sensitivity: Mapping[str, Any],
    remaining_reviews: Mapping[str, Any],
    runtime_validation: Mapping[str, Any],
    short_alpha_review: Mapping[str, Any],
    missing_sources: list[str],
    sources: Mapping[str, Any],
    facade: Any,
) -> dict[str, Any]:
    return {
        "schema_version": facade.SCHEMA_VERSION,
        "behavior_effect": "evaluation_only",
        "generated_at": generated_at,
        "through_day": through_day,
        "cost_authority": {
            "live_equity_round_trip_pct": facade.LIVE_RESEARCH_COST_PCT,
            "rule": "Gross, live-research net, and broker mock net must not be mixed.",
        },
        "purpose": "Consolidate existing evidence; do not rerun broad historical mining.",
        "tracks": facade.TRACKS,
        "candidate_count": len(candidates),
        "attention_order": facade._attention_order(candidates),
        "candidates": candidates,
        "sensitivity_reviews": [risk_high_sensitivity],
        "remaining_candidate_reviews": remaining_reviews,
        "runtime_validation": runtime_validation,
        "short_alpha_discriminator": short_alpha_review,
        "settled_findings": facade.SETTLED_FINDINGS,
        "integrity": {
            "status": "PASS" if not missing_sources else "PASS_WITH_MISSING_SOURCES",
            "missing_or_invalid_sources": missing_sources,
        },
        "sources": sources,
        "behavior_change_authorized": False,
    }
