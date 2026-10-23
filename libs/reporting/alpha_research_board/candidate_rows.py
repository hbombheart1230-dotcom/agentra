"""Pure candidate-row shaping for the alpha research board (P1.5 DEV-A).

Builds the board's candidate rows from already loaded evidence payloads: the common row factory, the Q12 hypothesis
metric lookup and the feature / fresh-change / opening / broad-opening / latent-reactivation / BTC-Woori rows. No I/O,
clock or loaders: ``libs.reporting.alpha_research_board.builder`` loads every payload and keeps the order of effects.
Every helper (``mapping``, ``metric_snapshot``, ``find_by_id``, ``find_horizon``, ``_candidate``) is read on the injected
``facade`` at call time, so patching a facade attribute behaves as before the move. Labels, notes and next actions are
byte-for-byte the originals.
"""
from __future__ import annotations

from typing import Any, Mapping


def _candidate_impl(
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
    facade: Any,
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


def _q12_hypothesis_metric_impl(
    payload: Mapping[str, Any],
    *,
    phase: str,
    path_value: str = "FAST_BUY_ALL_PASS",
    entry_method: str = "09:05",
    horizon: str = "+30m",
    facade: Any,
) -> dict[str, Any]:
    for raw in payload.get("rows") or []:
        row = facade.mapping(raw)
        if (
            row.get("evidence_phase") == phase
            and row.get("axis") == "hypothesis_path"
            and row.get("value") == path_value
            and row.get("entry_method") == entry_method
            and row.get("horizon") == horizon
        ):
            return facade.metric_snapshot(row.get("metrics"))
    return facade.metric_snapshot({})


def _feature_candidates_impl(
    feature_payload: Mapping[str, Any],
    prospective_payload: Mapping[str, Any],
    concentrations: Mapping[str, Mapping[str, Any]],
    *, facade: Any,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    prospective_rows = prospective_payload.get("candidate_summaries") or []
    specs = [
        (
            "R1_SCANNER_RISK_HIGH_30M_V1",
            "scanner.risk_band == HIGH",
            "+30m",
            "SCANNER",
        ),
        (
            "R1_ENTRY_DAILY_MA5_20_EXTENDED_15M_V1",
            "chart.daily_ma5_20_cross_state == POST_CROSS_EXTENDED",
            "+15m",
            "MONITOR_ENTRY",
        ),
    ]
    selected = feature_payload.get("prospective_shadow_candidates") or []
    for candidate_id, label, horizon, owner in specs:
        prospective = facade.find_by_id(prospective_rows, "candidate_id", candidate_id)
        candidate_meta = facade.mapping(prospective.get("candidate"))
        expected = candidate_meta.get("expected_value")
        feature_path = candidate_meta.get("feature_path")
        historical_row = next(
            (
                facade.mapping(row)
                for row in selected
                if facade.mapping(row).get("feature") == feature_path
                and facade.mapping(row).get("category") == expected
            ),
            {},
        )
        decision = facade.mapping(prospective.get("decision"))
        source_status = str(
            decision.get("status")
            or historical_row.get("decision")
            or "INSUFFICIENT_EVIDENCE"
        )
        bucket = (
            "ACTION_REVIEW"
            if source_status == "SINGLE_BEHAVIOR_PATCH_REVIEW_ELIGIBLE"
            else "OBSERVE_FIXED"
        )
        branch = facade.metric_snapshot(prospective.get("branch"))
        rows.append(
            facade._candidate(
                candidate_id=candidate_id,
                track_id="OPENING_CONDITIONAL",
                discriminator=label,
                target_horizon=horizon,
                source_status=source_status,
                board_bucket=bucket,
                owner=owner,
                historical=facade.metric_snapshot(historical_row.get("train")),
                validation=facade.metric_snapshot(historical_row.get("validation")),
                prospective=branch,
                concentration=concentrations.get(candidate_id),
                evidence_note=(
                    "Prospective에서도 비교군을 이겼지만 날짜·종목 집중도 민감도 검토가 필요함."
                    if bucket == "ACTION_REVIEW"
                    else "과거 방향성이 prospective에서 유지되지 못함."
                ),
                next_action=(
                    "집중 종목·최대 일자를 제외한 민감도 검토 후 승격 또는 기각. 다른 영역은 변경하지 않음."
                    if bucket == "ACTION_REVIEW"
                    else "관측만 유지하고 과거 성과만으로 승격하지 않음."
                ),
                source_keys=["feature_candidates", "prospective_candidates"],
            )
        )
    return rows


def _fresh_change_impl(payload: Mapping[str, Any], *, facade: Any) -> dict[str, Any]:
    reference = facade.mapping(payload.get("historical_reference"))
    historical = facade.mapping(reference.get("branch"))
    historical_metric = facade.mapping(facade.mapping(historical.get("horizons")).get("+30m"))
    prospective_metric = facade.mapping(facade.mapping(facade.mapping(payload.get("branch")).get("horizons")).get("+30m"))
    source_status = str(facade.mapping(payload.get("decision")).get("status") or "INSUFFICIENT_EVIDENCE")
    return facade._candidate(
        candidate_id="R1_FRESH_CHANGE_ACTIVATION_V1",
        track_id="OPENING_CONDITIONAL",
        discriminator="fresh top-change activation",
        target_horizon="+30m",
        source_status=source_status,
        board_bucket="CLOSED_NEGATIVE_PROSPECTIVE",
        owner="SCANNER",
        historical=facade.metric_snapshot(historical_metric),
        prospective=facade.metric_snapshot(prospective_metric),
        evidence_note="과거 양수 결과가 prospective에서 음수로 뒤집힘.",
        next_action="승격 후보에서 기각하고 과거 참고자료로만 보존.",
        source_keys=["fresh_change"],
    )


def _opening_rows_impl(payload: Mapping[str, Any], *, facade: Any) -> list[dict[str, Any]]:
    summary = facade.mapping(payload.get("summary"))
    lanes = facade.mapping(summary.get("conditional_lane_summaries"))
    rows: list[dict[str, Any]] = []
    for lane_id, horizon, note in [
        (
            "IMMEDIATE_OPENING_PROBE",
            "+5m",
            "즉시 반응은 초반이 가장 강하고 EOD로 갈수록 약해짐.",
        ),
        (
            "CONFIRMED_RECURRENT_RANK",
            "+30m",
            "방향은 강하지만 독립 표본이 지나치게 작음.",
        ),
        (
            "DISLOCATION_REBOUND",
            "+60m",
            "5분보다 30~60분 반등 근거가 강함.",
        ),
    ]:
        lane = facade.mapping(lanes.get(lane_id))
        horizon_row = facade.mapping(facade.mapping(lane.get("horizons")).get(horizon))
        rows.append(
            facade._candidate(
                candidate_id=lane_id,
                track_id="OPENING_CONDITIONAL",
                discriminator=lane_id.lower(),
                target_horizon=horizon,
                source_status="COLLECTING",
                board_bucket="OBSERVE_FIXED",
                owner="SCANNER_OR_HORIZON_REVIEW",
                prospective=facade.metric_snapshot(horizon_row.get("live_net")),
                evidence_note=note,
                next_action="기존 고정 observer만 지속하고 새 lane은 만들지 않음.",
                source_keys=["opening_cumulative"],
            )
        )
    return rows


def _broad_opening_impl(payload: Mapping[str, Any], *, facade: Any) -> dict[str, Any]:
    decision = facade.mapping(payload.get("promotion_decision"))
    values = facade.mapping(decision.get("values"))
    return facade._candidate(
        candidate_id="OPEN_0_20_RANK1_30M",
        track_id="OPENING_CONDITIONAL",
        discriminator="all opening Rank-1 candidates",
        target_horizon="+30m",
        source_status=str(decision.get("status") or "INSUFFICIENT_EVIDENCE"),
        board_bucket="CLOSED",
        owner="NONE",
        prospective={
            "sample_count": values.get("observed_count", 0),
            "window_count": values.get("observed_count", 0),
            "win_rate": values.get("win_rate"),
            "avg_net_return_pct": values.get("average_net_return_pct"),
            "profit_factor": values.get("profit_factor"),
            "coverage": values.get("coverage"),
        },
        concentration={
            "largest_day_share": values.get("largest_day_share"),
            "largest_symbol_share": values.get("largest_symbol_share"),
        },
        evidence_note="평균은 양수지만 고정된 종목 집중도 gate를 통과하지 못함.",
        next_action="종료. Rank-1 전부 진입 근거로 재해석하지 않음.",
        source_keys=["opening_cumulative"],
    )


def _latent_impl(payload: Mapping[str, Any], *, facade: Any) -> dict[str, Any]:
    summary = facade.mapping(payload.get("summary"))
    horizon = facade.mapping(facade.mapping(summary.get("horizons")).get("+30m"))
    return facade._candidate(
        candidate_id="LATENT_REACTIVATION_FRESH_TRIGGER",
        track_id="SCANNER_REACTIVATION_HORIZON",
        discriminator="fresh D+1-D+5 trigger after prior Rank-1 discovery",
        target_horizon="+30m",
        source_status=str(summary.get("status") or "INSUFFICIENT_EVIDENCE"),
        board_bucket="CLOSED",
        owner="NONE",
        prospective=facade.metric_snapshot(horizon.get("live_net")),
        concentration={
            "largest_day_share": summary.get("largest_day_share"),
            "largest_symbol_share": summary.get("largest_symbol_share"),
            "positive_day_ratio": summary.get("positive_day_ratio"),
        },
        evidence_note="수익률은 양수지만 날짜·종목 집중도와 양수 일자 gate를 통과하지 못함.",
        next_action="고정 계약은 기각하고 30~60분 방향성만 연구 힌트로 보존.",
        source_keys=["latent_reactivation"],
    )


def _btc_woori_impl(payload: Mapping[str, Any], *, facade: Any) -> dict[str, Any]:
    horizon = facade.find_horizon(payload.get("episode_horizons"), "+30m")
    return facade._candidate(
        candidate_id="BTC_WOORI_V2_ONLY_LOCAL_CONFIRMATION",
        track_id="BTC_WOORI",
        discriminator="BTC multi-horizon momentum + Woori local price/volume confirmation",
        target_horizon="+30m",
        source_status=str(payload.get("conclusion") or "INSUFFICIENT_EVIDENCE"),
        board_bucket="OBSERVE_FIXED",
        owner="BTC_WOORI_BASELINE",
        historical=facade.metric_snapshot(horizon.get("real_net")),
        evidence_note="BTC 단독과 광범위 v2는 약하고, 독립 v2-only +30분 하위군만 양수임.",
        next_action="고정된 현지 확인 하위군만 prospective로 수집.",
        source_keys=["btc_woori_history"],
    )
