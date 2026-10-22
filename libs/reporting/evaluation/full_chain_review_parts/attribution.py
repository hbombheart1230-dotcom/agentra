"""Pure role-metric and decision-window attribution for the Q9 full-chain component review (P1.5 DEV-A).

Per-role metrics, paired role deltas, selection availability and the decision-window attribution over candidate rows.
No direct I/O: rows reach ``_decision_window_attribution`` through the facade's ``_q9_decision_candidate_rows``, which
keeps the forward-outcome attachment. Helpers and constants are read on the injected ``facade`` at call time.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping


def _role_metrics_impl(
    candidates: list[dict[str, Any]],
    *,
    role: str,
    horizon: str,
    cost_pct: float,
    facade: Any,
) -> dict[str, Any]:
    values: list[float] = []
    days: set[str] = set()
    for row in candidates:
        if str(row.get("shadow_role") or "") != role:
            continue
        value = facade._checkpoint_return(row, horizon)
        if value is None:
            continue
        values.append(value - cost_pct)
        day = facade.candidate_day(row)
        if day:
            days.add(day)
    return {
        "role": role,
        "horizon": horizon,
        "evidence_class": "TRUSTED_SHADOW",
        "observed_count": len(values),
        "observed_day_count": len(days),
        "cost_adjusted": True,
        **facade.performance_metrics(values),
    }


def _paired_role_deltas_impl(
    candidates: list[dict[str, Any]],
    *,
    horizon: str,
    facade: Any,
) -> dict[str, Any]:
    windows: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    window_days: dict[str, str] = {}
    for row in candidates:
        role = str(row.get("shadow_role") or "")
        if role not in {"top_pick", "runner_up_evaluated"}:
            continue
        value = facade._checkpoint_return(row, horizon)
        if value is None:
            continue
        window = str(row.get("_payload_generated_at") or "")
        if not window:
            continue
        windows[window][role].append(value)
        window_days[window] = facade.candidate_day(row) or ""
    deltas: list[float] = []
    days: set[str] = set()
    for window, roles in windows.items():
        top = roles.get("top_pick") or []
        runner = roles.get("runner_up_evaluated") or []
        if not top or not runner:
            continue
        deltas.append((sum(top) / len(top)) - (sum(runner) / len(runner)))
        if window_days.get(window):
            days.add(window_days[window])
    return {
        "horizon": horizon,
        "comparison": "top_pick_minus_runner_up_evaluated",
        "evidence_class": "TRUSTED_SHADOW",
        "paired_window_count": len(deltas),
        "observed_day_count": len(days),
        "average_delta_pct": round(sum(deltas) / len(deltas), 4) if deltas else None,
        "positive_delta_rate": round(sum(value > 0 for value in deltas) / len(deltas), 4) if deltas else None,
        "delta_distribution": facade.performance_metrics(deltas),
    }


def _selection_availability_impl(models: list[dict[str, Any]], *, facade: Any) -> dict[str, Any]:
    raw_controls = 0
    strategist_snapshots = 0
    commander_snapshots = 0
    comparable_strategist = 0
    comparable_commander = 0
    missing: dict[str, int] = defaultdict(int)
    for model in models:
        selection = model.get("selection") if isinstance(model.get("selection"), Mapping) else {}
        raw_rows = selection.get("raw_scanner_top10")
        raw_control = bool(
            selection.get("raw_scanner_snapshot_source")
            in {"control_snapshot", "scanner_intrinsic_control_snapshot"}
            and isinstance(raw_rows, list)
            and raw_rows
        )
        strategist = bool(
            selection.get("strategist_run_id")
            and isinstance(selection.get("post_strategist_top10"), list)
            and selection.get("post_strategist_top10")
        )
        commander = bool(selection.get("commander_final_explicit"))
        raw_controls += int(raw_control)
        strategist_snapshots += int(strategist)
        commander_snapshots += int(commander)
        comparable_strategist += int(raw_control and strategist)
        comparable_commander += int(strategist and commander)
        if not raw_control:
            missing["trusted_raw_scanner_top10"] += 1
        if not strategist:
            missing["strategist_run_and_post_ranking"] += 1
        if not commander:
            missing["explicit_commander_selection_or_veto"] += 1
    return {
        "trade_model_count": len(models),
        "raw_scanner_control_count": raw_controls,
        "strategist_snapshot_count": strategist_snapshots,
        "commander_snapshot_count": commander_snapshots,
        "scanner_vs_strategist_comparable_count": comparable_strategist,
        "strategist_vs_commander_comparable_count": comparable_commander,
        "missing_fields": dict(sorted(missing.items())),
    }


def _q9_role_row_impl(
    roles: Mapping[str, list[dict[str, Any]]],
    role: str,
    *, facade: Any,
) -> dict[str, Any]:
    rows = roles.get(role) or []
    if role == "B_STRATEGIST_RANKED":
        selected = next((row for row in rows if row.get("q9_selected")), None)
        if selected:
            return selected
    return min(
        rows,
        key=lambda row: int(float(row.get("rank") or 999)),
        default={},
    )


def _decision_window_attribution_impl(
    payloads: list[dict[str, Any]],
    *,
    cost_pct: float,
    facade: Any,
) -> dict[str, Any]:
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in facade._q9_decision_candidate_rows(payloads):
        decision_id = str(row.get("q9_decision_id") or "")
        role = str(row.get("q9_decision_role") or "")
        if decision_id and role:
            grouped[decision_id][role].append(row)
    by_horizon: list[dict[str, Any]] = []
    for horizon in facade.HORIZONS:
        strategist_deltas: list[float] = []
        refresh_deltas: list[float] = []
        commander_deltas: list[float] = []
        strategist_days: set[str] = set()
        refresh_days: set[str] = set()
        commander_days: set[str] = set()
        for roles in grouped.values():
            a_row = facade._q9_role_row(roles, "A_SCANNER_CONTROL")
            b_row = facade._q9_role_row(roles, "B_STRATEGIST_RANKED")
            r1_row = facade._q9_role_row(roles, "R1_PRE_REFRESH_SCANNER")
            r2_row = facade._q9_role_row(roles, "R2_POST_REFRESH_SCANNER")
            c_row = facade._q9_role_row(roles, "C_COMMANDER_FINAL")
            a_value = facade._checkpoint_return(a_row, horizon) if a_row else None
            b_value = facade._checkpoint_return(b_row, horizon) if b_row else None
            if a_value is not None and b_value is not None:
                strategist_deltas.append(b_value - a_value)
                day = facade.candidate_day(b_row)
                if day:
                    strategist_days.add(day)
            r1_value = facade._checkpoint_return(r1_row, horizon) if r1_row else None
            r2_value = facade._checkpoint_return(r2_row, horizon) if r2_row else None
            if r1_value is not None and r2_value is not None:
                refresh_deltas.append(r2_value - r1_value)
                day = facade.candidate_day(r2_row)
                if day:
                    refresh_days.add(day)
            if b_value is None or not c_row:
                continue
            if c_row.get("q9_commander_no_trade"):
                c_net = 0.0
            else:
                c_value = facade._checkpoint_return(c_row, horizon)
                if c_value is None:
                    continue
                c_net = c_value - cost_pct
            b_net = b_value - cost_pct
            commander_deltas.append(c_net - b_net)
            day = facade.candidate_day(c_row)
            if day:
                commander_days.add(day)
        by_horizon.append(
            {
                "horizon": horizon,
                "strategist_comparison_count": len(strategist_deltas),
                "strategist_day_count": len(strategist_days),
                "average_strategist_delta_pct": (
                    round(sum(strategist_deltas) / len(strategist_deltas), 4)
                    if strategist_deltas
                    else None
                ),
                "strategist_positive_delta_rate": (
                    round(sum(value > 0 for value in strategist_deltas) / len(strategist_deltas), 4)
                    if strategist_deltas
                    else None
                ),
                "strategy_ranking_overlay_comparison_count": len(strategist_deltas),
                "strategy_ranking_overlay_day_count": len(strategist_days),
                "average_strategy_ranking_overlay_delta_pct": (
                    round(sum(strategist_deltas) / len(strategist_deltas), 4)
                    if strategist_deltas
                    else None
                ),
                "strategy_ranking_overlay_positive_delta_rate": (
                    round(sum(value > 0 for value in strategist_deltas) / len(strategist_deltas), 4)
                    if strategist_deltas
                    else None
                ),
                "post_scanner_refresh_comparison_count": len(refresh_deltas),
                "post_scanner_refresh_day_count": len(refresh_days),
                "average_post_scanner_refresh_delta_pct": (
                    round(sum(refresh_deltas) / len(refresh_deltas), 4)
                    if refresh_deltas
                    else None
                ),
                "post_scanner_refresh_positive_delta_rate": (
                    round(sum(value > 0 for value in refresh_deltas) / len(refresh_deltas), 4)
                    if refresh_deltas
                    else None
                ),
                "commander_comparison_count": len(commander_deltas),
                "commander_day_count": len(commander_days),
                "average_commander_delta_pct": (
                    round(sum(commander_deltas) / len(commander_deltas), 4)
                    if commander_deltas
                    else None
                ),
                "commander_positive_delta_rate": (
                    round(sum(value > 0 for value in commander_deltas) / len(commander_deltas), 4)
                    if commander_deltas
                    else None
                ),
            }
        )
    return {
        "schema_version": "q9_decision_window_attribution.v1",
        "role_semantics": {
            "A_SCANNER_CONTROL": "same-universe intrinsic Scanner ranking; not a full pre-Strategist control",
            "B_STRATEGIST_RANKED": "strategy-weighted Scanner ranking",
            "R1_PRE_REFRESH_SCANNER": "first Scanner result before optional tactical refresh",
            "R2_POST_REFRESH_SCANNER": "Scanner result after optional tactical refresh",
            "C_COMMANDER_FINAL": "Commander final approval or veto",
        },
        "full_strategist_contribution_status": "NOT_MEASURABLE",
        "full_strategist_missing_control": "strategy-neutral candidate sourcing and ranking shadow",
        "decision_window_count": len(grouped),
        "candidate_row_count": sum(
            len(rows) for roles in grouped.values() for rows in roles.values()
        ),
        "by_horizon": by_horizon,
    }
