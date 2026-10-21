"""Pure Scanner / selection attribution read-models (P1.5 FAST08 A8.2).

Selection-path symbol deltas, Q14 root-cause row/summary assembly (shared by the
daily and range reports), episode de-duplication, score-component correlation,
Scanner top-K / source forward performance and the Markdown renderers. Root-cause
classification, patch candidates, readiness/eligibility thresholds, forward
attachment and artifact reads stay in ``scanner_alignment_root_cause``,
``episode_scanner_review``, ``scanner_quality`` and ``selection_authority_audit``.
No Scanner rank or selection policy is computed here.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from math import sqrt
from typing import Any, Callable, Mapping, Sequence

from .metrics import performance_metrics


def mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def number(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def symbol_of(value: Any) -> str:
    if isinstance(value, Mapping):
        return str(value.get("symbol") or "").strip()
    return str(value or "").strip()


def observed_return(row: Mapping[str, Any], horizon: str) -> float | None:
    checkpoint = mapping(mapping(mapping(row.get("shadow_forward_outcome")).get("checkpoints")).get(horizon))
    if str(checkpoint.get("status") or "") != "observed":
        return None
    return number(checkpoint.get("return_pct"))


# --- A8.2a: selection authority path ----------------------------------------------


SELECTION_CHANGE_KEYS = (
    "raw_to_post_changed",
    "post_to_selected_changed",
    "selected_to_monitor_changed",
    "monitor_to_commander_changed",
    "final_to_executed_changed",
)


def changed(a: str, b: str) -> bool | None:
    if not a or not b:
        return None
    return a != b


def selection_path_row(model: Mapping[str, Any]) -> dict[str, Any]:
    selection = mapping(model.get("selection"))
    monitor = mapping(model.get("monitor"))
    commander = mapping(selection.get("commander_final"))
    raw_top1 = symbol_of(selection.get("raw_scanner_top1"))
    post_top1 = symbol_of(selection.get("scanner_top1"))
    selected = symbol_of(selection.get("selected_symbol"))
    monitor_symbol = symbol_of(monitor.get("selected_symbol") or mapping(monitor.get("entry_context")).get("selected_symbol"))
    commander_candidate = symbol_of(commander.get("candidate_symbol"))
    commander_selected = symbol_of(commander.get("selected_symbol"))
    executed = symbol_of(model.get("symbol"))
    return {
        "trade_id": model.get("trade_id"),
        "symbol": executed,
        "raw_scanner_top1": raw_top1,
        "post_strategy_top1": post_top1,
        "selected_symbol": selected,
        "monitor_symbol": monitor_symbol,
        "commander_candidate_symbol": commander_candidate,
        "commander_selected_symbol": commander_selected,
        "executed_symbol": executed,
        "raw_to_post_changed": changed(raw_top1, post_top1),
        "post_to_selected_changed": changed(post_top1, selected),
        "selected_to_monitor_changed": changed(selected, monitor_symbol),
        "monitor_to_commander_changed": changed(monitor_symbol or selected, commander_candidate or commander_selected),
        "final_to_executed_changed": changed(commander_selected or commander_candidate or selected, executed),
        "commander_authority_scope": str(commander.get("authority_scope") or ""),
        "commander_decision": str(commander.get("decision") or ""),
        "selection_mismatch": mapping(selection.get("selection_mismatch")),
    }


def count_selection_changes(counters: Counter[str], row: Mapping[str, Any]) -> None:
    for key in SELECTION_CHANGE_KEYS:
        value = row[key]
        counters[f"{key}:unavailable" if value is None else f"{key}:{bool(value)}"] += 1


def render_selection_authority_audit(payload: Mapping[str, Any]) -> str:
    lines = [
        "# Selection Authority Audit",
        "",
        f"- Behavior effect: `{payload.get('behavior_effect', '')}`",
        f"- Trades: {payload.get('trade_count', 0)}",
        "",
        "## Summary",
        "",
    ]
    summary = mapping(payload.get("summary"))
    if summary:
        for key in sorted(summary):
            lines.append(f"- `{key}`: {summary[key]}")
    else:
        lines.append("- No rows.")
    lines.extend([
        "",
        "## Rows",
        "",
        "| Trade | Raw Top1 | Post-Strategy Top1 | Selected | Monitor | Commander Candidate | Commander Selected | Executed |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ])
    for row in payload.get("rows") or []:
        if not isinstance(row, Mapping):
            continue
        lines.append(
            "| "
            + " | ".join(
                str(row.get(key) or "-")
                for key in (
                    "trade_id",
                    "raw_scanner_top1",
                    "post_strategy_top1",
                    "selected_symbol",
                    "monitor_symbol",
                    "commander_candidate_symbol",
                    "commander_selected_symbol",
                    "executed_symbol",
                )
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


# --- A8.2b: Q14 scanner alignment root cause -----------------------------------------


def selected_rank(model: Mapping[str, Any]) -> int | None:
    selection = mapping(model.get("selection"))
    value = number(selection.get("selected_rank") or mapping(selection.get("selected_candidate")).get("rank"))
    return int(value) if value is not None else None


def score_gap(model: Mapping[str, Any]) -> float | None:
    selection = mapping(model.get("selection"))
    top_score = number(mapping(selection.get("scanner_top1")).get("score_total"))
    selected_score = number(mapping(selection.get("selected_candidate")).get("score_total"))
    if top_score is None or selected_score is None:
        return None
    return round(top_score - selected_score, 6)


def outcome_return(evaluation: Mapping[str, Any], model: Mapping[str, Any]) -> float | None:
    value = number(mapping(evaluation.get("realized_outcome")).get("net_return_pct"))
    if value is not None:
        return value
    return number(mapping(model.get("outcome")).get("net_return_pct"))


def impact_score(returns: list[float]) -> float:
    return round(sum(value for value in returns if value < 0), 4)


def root_cause_row(
    row: Mapping[str, Any],
    *,
    trade_id: str,
    net_return: float | None,
    classification: Mapping[str, Any],
    kind: str,
) -> dict[str, Any]:
    return {
        "trade_id": trade_id,
        "symbol": row.get("executed_symbol") or row.get("symbol"),
        "raw_scanner_top1": row.get("raw_scanner_top1"),
        "post_strategy_top1": row.get("post_strategy_top1"),
        "selected_symbol": row.get("selected_symbol"),
        "executed_symbol": row.get("executed_symbol"),
        "net_return_pct": net_return,
        "root_cause": classification["root_cause"],
        "diagnostic_kind": kind,
        "causal_eligible": kind == "structural",
        "confidence": classification["confidence"],
        "selected_rank": classification["selected_rank"],
        "score_gap": classification["score_gap"],
        "reasons": classification["reasons"],
    }


def root_cause_summary(
    rows: Sequence[Mapping[str, Any]],
    causes: Sequence[str],
    *,
    kind_of: Callable[[str], str],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("root_cause") or "Missing Evidence")].append(row)
    out: list[dict[str, Any]] = []
    for cause in causes:
        cause_rows = grouped.get(cause, [])
        returns = [float(row["net_return_pct"]) for row in cause_rows if row.get("net_return_pct") is not None]
        metrics = performance_metrics(returns)
        out.append(
            {
                "root_cause": cause,
                "diagnostic_kind": kind_of(cause),
                "causal_eligible": kind_of(cause) == "structural",
                "trade_count": len(cause_rows),
                "return_observation_count": len(returns),
                "win_rate": metrics["win_rate"],
                "avg_return_pct": metrics["average_return_pct"],
                "profit_factor": metrics["profit_factor"],
                "max_drawdown_pct": metrics["maximum_drawdown_pct"],
                "negative_impact_pct": impact_score(returns),
            }
        )
    return out


def largest_cause(cause_summary: Sequence[Mapping[str, Any]], *, excluded: set[str] | None = None) -> dict[str, Any]:
    excluded = excluded or set()
    observed = [
        row
        for row in cause_summary
        if int(row.get("trade_count") or 0) > 0 and str(row.get("root_cause") or "") not in excluded
    ]
    return dict(
        max(
            observed,
            key=lambda row: (int(row.get("trade_count") or 0), abs(float(row.get("negative_impact_pct") or 0.0))),
            default={},
        )
    )


def largest_causes(
    cause_summary: Sequence[Mapping[str, Any]],
    *,
    behavior_excluded: set[str],
    structural_excluded: set[str],
) -> dict[str, Any]:
    largest = largest_cause(cause_summary)
    return {
        "largest_root_cause": largest,
        "largest_observed_root_cause": largest,
        "largest_behavior_root_cause": largest_cause(cause_summary, excluded=behavior_excluded),
        "largest_structural_root_cause": largest_cause(cause_summary, excluded=structural_excluded),
    }


def render_scanner_alignment_root_cause_report(payload: Mapping[str, Any]) -> str:
    lines = [
        f"# Q14 Scanner Alignment Root Cause - {payload.get('day', '')}",
        "",
        f"- Behavior effect: `{payload.get('behavior_effect', '')}`",
        f"- Trades: {payload.get('trade_count', 0)}",
        f"- Largest observed root cause: `{mapping(payload.get('largest_observed_root_cause') or payload.get('largest_root_cause')).get('root_cause') or '-'}`",
        f"- Largest behavior root cause: `{mapping(payload.get('largest_behavior_root_cause')).get('root_cause') or '-'}`",
        f"- Largest structural root cause: `{mapping(payload.get('largest_structural_root_cause')).get('root_cause') or '-'}`",
        "- Outcome-conditioned labels are descriptive and are not independent causal proof.",
        f"- Q15 candidate: {payload.get('q15_behavior_patch_candidate') or '-'}",
        "",
        "## Root Cause Summary",
        "",
        "| Root Cause | Kind | Causal | Trades | Return Obs | Win Rate | Avg Return | Profit Factor | MDD | Negative Impact |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload.get("cause_summary") or []:
        if not isinstance(row, Mapping):
            continue
        lines.append(
            f"| {row.get('root_cause')} | {row.get('diagnostic_kind') or '-'} | "
            f"{bool(row.get('causal_eligible'))} | {row.get('trade_count')} | "
            f"{row.get('return_observation_count')} | {float(row.get('win_rate') or 0):.1%} | "
            f"{float(row.get('avg_return_pct') or 0):.4f}% | {row.get('profit_factor')} | "
            f"{float(row.get('max_drawdown_pct') or 0):.4f}% | "
            f"{float(row.get('negative_impact_pct') or 0):.4f}% |"
        )
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Trade | Symbol | Raw Top1 | Post Top1 | Selected | Rank | Return | Root Cause | Reasons |",
            "| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |",
        ]
    )
    for row in payload.get("rows") or []:
        if not isinstance(row, Mapping):
            continue
        reasons = ", ".join(str(reason) for reason in row.get("reasons") or []) or "-"
        value = row.get("net_return_pct")
        lines.append(
            f"| {row.get('trade_id')} | {row.get('symbol') or '-'} | "
            f"{row.get('raw_scanner_top1') or '-'} | {row.get('post_strategy_top1') or '-'} | "
            f"{row.get('selected_symbol') or '-'} | {row.get('selected_rank') or '-'} | "
            f"{'-' if value is None else f'{float(value):.4f}%'} | "
            f"{row.get('root_cause')} | {reasons} |"
        )
    lines.extend(["", "## Interpretation", "", f"- {payload.get('interpretation_rule', '')}", ""])
    return "\n".join(lines)


# --- A8.2c: Scanner top-K and candidate-source forward performance --------------------


def topk_forward_rows(
    rows: list[dict[str, Any]],
    *,
    horizons: Sequence[str],
    top_k_values: Sequence[int],
    cost_pct: float,
    slippage_pct: float,
    day_of: Callable[[Mapping[str, Any]], str],
) -> tuple[int, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        decision_id = str(row.get("q9_decision_id") or "")
        if decision_id:
            grouped[decision_id].append(row)
    output: list[dict[str, Any]] = []
    total_drag = float(cost_pct) + float(slippage_pct)
    for horizon in horizons:
        for top_k in top_k_values:
            gross_values: list[float] = []
            net_values: list[float] = []
            days: set[str] = set()
            candidate_observations = 0
            for decision_rows in grouped.values():
                ranked = sorted(decision_rows, key=lambda row: int(number(row.get("rank")) or 999))
                observed = [value for row in ranked[:top_k] for value in [observed_return(row, horizon)] if value is not None]
                if not observed:
                    continue
                window_return = sum(observed) / len(observed)
                gross_values.append(window_return)
                net_values.append(window_return - total_drag)
                candidate_observations += len(observed)
                day = next((day_of(row) for row in ranked[:top_k] if day_of(row)), "")
                if day:
                    days.add(day)
            output.append(
                {
                    "top_k": top_k,
                    "horizon": horizon,
                    "window_count": len(gross_values),
                    "candidate_observation_count": candidate_observations,
                    "observed_day_count": len(days),
                    "cost_pct": round(float(cost_pct), 6),
                    "slippage_pct": round(float(slippage_pct), 6),
                    "gross": performance_metrics(gross_values),
                    "net": performance_metrics(net_values),
                }
            )
    return len(grouped), output


def source_forward_rows(
    rows: list[dict[str, Any]],
    *,
    horizons: Sequence[str],
    cost_pct: float,
    slippage_pct: float,
    day_of: Callable[[Mapping[str, Any]], str],
) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, str], list[float]] = defaultdict(list)
    days: dict[tuple[str, str], set[str]] = defaultdict(set)
    total_drag = float(cost_pct) + float(slippage_pct)
    for row in rows:
        sources = [
            str(value or "") for value in row.get("q9_candidate_sources") or row.get("sources") or [] if str(value or "")
        ] or ["unknown"]
        for horizon in horizons:
            value = observed_return(row, horizon)
            if value is None:
                continue
            for source in sources:
                key = (source, horizon)
                buckets[key].append(value - total_drag)
                day = day_of(row)
                if day:
                    days[key].add(day)
    return [
        {
            "source": source,
            "horizon": horizon,
            "observed_day_count": len(days[(source, horizon)]),
            "cost_pct": round(float(cost_pct), 6),
            "slippage_pct": round(float(slippage_pct), 6),
            **performance_metrics(values),
        }
        for (source, horizon), values in sorted(buckets.items())
    ]


# --- A8.2d: episode de-duplication and score components ---------------------------------


def baseline_epoch(row: Mapping[str, Any]) -> int:
    return int(number(mapping(row.get("shadow_forward_base")).get("baseline_epoch")) or 0)


def setup_key(row: Mapping[str, Any]) -> str:
    lane = mapping(row.get("entry_lane_observation"))
    return str(lane.get("subtype_v2") or lane.get("subtype") or lane.get("primary_lane") or row.get("reason") or "unknown")


def compact_day(row: Mapping[str, Any], day_of: Callable[[Mapping[str, Any]], str]) -> str:
    value = (day_of(row) or str(row.get("day") or "")).replace("-", "")
    return value if len(value) == 8 and value.isdigit() else ""


def episode_rank_bucket(rank: int) -> str:
    if rank == 1:
        return "rank1"
    if 2 <= rank <= 3:
        return "rank2_3"
    if rank >= 4:
        return "rank4_plus"
    return "unknown"


def episode_representatives(
    rows: Sequence[Mapping[str, Any]],
    *,
    episode_gap_sec: int,
    horizons: Sequence[str],
    day_of: Callable[[Mapping[str, Any]], str],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        day = compact_day(row, day_of)
        symbol = str(row.get("symbol") or "")
        if not day or not symbol:
            continue
        grouped[(day, symbol, setup_key(row))].append(row)
    episodes: list[dict[str, Any]] = []
    for (day, symbol, setup), candidates in sorted(grouped.items()):
        previous_epoch: int | None = None
        episode_index = 0
        for row in sorted(candidates, key=lambda item: (baseline_epoch(item), int(number(item.get("rank")) or 999))):
            current_epoch = baseline_epoch(row)
            if (
                previous_epoch is None
                or current_epoch <= 0
                or previous_epoch <= 0
                or current_epoch - previous_epoch > episode_gap_sec
            ):
                episode_index += 1
                rank = int(number(row.get("rank")) or 0)
                episodes.append(
                    {
                        "episode_id": f"{day}:{symbol}:{setup}:{episode_index}",
                        "day": day,
                        "symbol": symbol,
                        "setup": setup,
                        "baseline_epoch": current_epoch or None,
                        "rank": rank or None,
                        "rank_bucket": episode_rank_bucket(rank),
                        "score_breakdown": dict(mapping(row.get("score_breakdown"))),
                        "sources": [str(value) for value in row.get("q9_candidate_sources") or row.get("sources") or [] if str(value)],
                        "returns": {horizon: observed_return(row, horizon) for horizon in horizons},
                    }
                )
            previous_epoch = current_epoch
    return episodes


def rank_horizon_rows(
    episodes: Sequence[Mapping[str, Any]],
    *,
    buckets: Sequence[str],
    horizons: Sequence[str],
    mock_drag_pct: float,
    live_drag_pct: float,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for bucket in buckets:
        bucket_rows = [row for row in episodes if row["rank_bucket"] == bucket]
        for horizon in horizons:
            gross = [float(row["returns"][horizon]) for row in bucket_rows if row["returns"].get(horizon) is not None]
            output.append(
                {
                    "rank_bucket": bucket,
                    "horizon": horizon,
                    "episode_count": len(bucket_rows),
                    "observed_count": len(gross),
                    "observed_day_count": len({row["day"] for row in bucket_rows if row["returns"].get(horizon) is not None}),
                    "gross": performance_metrics(gross),
                    "live_net": performance_metrics([value - float(live_drag_pct) for value in gross]),
                    "mock_net": performance_metrics([value - float(mock_drag_pct) for value in gross]),
                }
            )
    return output


def score_component_rows(
    covered: Sequence[Mapping[str, Any]],
    *,
    live_drag_pct: float,
) -> list[dict[str, Any]]:
    component_values: dict[str, list[tuple[float, float, str]]] = defaultdict(list)
    for row in covered:
        outcome = float(row["returns"]["+30m"])
        for key, raw in row["score_breakdown"].items():
            value = number(raw)
            if value is not None:
                component_values[str(key)].append((value, outcome, row["day"]))
    rows: list[dict[str, Any]] = []
    for component, values in component_values.items():
        xs = [value for value, _, _ in values]
        ys = [outcome for _, outcome, _ in values]
        x_mean = sum(xs) / len(xs)
        y_mean = sum(ys) / len(ys)
        covariance = sum((value - x_mean) * (outcome - y_mean) for value, outcome, _ in values)
        x_scale = sqrt(sum((value - x_mean) ** 2 for value in xs))
        y_scale = sqrt(sum((outcome - y_mean) ** 2 for outcome in ys))
        correlation = covariance / (x_scale * y_scale) if x_scale and y_scale else None
        rows.append(
            {
                "component": component,
                "observed_count": len(values),
                "observed_day_count": len({day for _, _, day in values}),
                "avg_score_contribution": round(x_mean, 6),
                "avg_gross_return_30m_pct": round(y_mean, 4),
                "avg_live_net_return_30m_pct": round(y_mean - float(live_drag_pct), 4),
                "score_return_correlation": round(correlation, 4) if correlation is not None else None,
            }
        )
    rows.sort(key=lambda row: (int(row["observed_count"]), abs(float(row["score_return_correlation"] or 0.0))), reverse=True)
    return rows


def bucket_expectancy(rows: Sequence[Mapping[str, Any]], bucket: str, horizon: str) -> float | None:
    row = next((r for r in rows if r["rank_bucket"] == bucket and r["horizon"] == horizon), {})
    return number(mapping(row.get("gross")).get("expectancy_pct"))


def reentry_series(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """First vs repeat same-day same-symbol entries, split by the prior entry's outcome."""
    unique: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        trade_id = str(row.get("trade_id") or "")
        if trade_id:
            unique[trade_id] = row
    grouped: dict[tuple[str, str], list[tuple[int, float, str]]] = defaultdict(list)
    for trade_id, row in unique.items():
        parts = trade_id.split("_")
        if len(parts) < 4 or not parts[1].isdigit():
            continue
        value = number(row.get("net_return_pct"))
        symbol = str(row.get("symbol") or "")
        if value is None or not symbol:
            continue
        try:
            sequence = int(parts[-1])
        except ValueError:
            sequence = 0
        grouped[(parts[1], symbol)].append((sequence, value, trade_id))
    first: list[float] = []
    repeat: list[float] = []
    after_loss: list[float] = []
    after_non_loss: list[float] = []
    repeated_groups = 0
    for values in grouped.values():
        ordered = sorted(values)
        first.append(ordered[0][1])
        for index, (_, value, _) in enumerate(ordered[1:], start=1):
            repeat.append(value)
            (after_loss if ordered[index - 1][1] < 0.0 else after_non_loss).append(value)
        if len(ordered) > 1:
            repeated_groups += 1
    return {
        "group_count": len(grouped),
        "repeated_group_count": repeated_groups,
        "first": first,
        "repeat": repeat,
        "after_loss": after_loss,
        "after_non_loss": after_non_loss,
    }
