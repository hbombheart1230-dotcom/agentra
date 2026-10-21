"""Pure Q9 evidence classification and readouts (P1.5 FAST08 A8.1).

Window/forward-outcome classification, session-coverage derivation, inventory
coverage, day-validity check readout, trade-evaluation evidence blocks and the
historical-prior summary/markdown. File reads, shadow/window streaming, forward
outcome attachment, the wall clock and every validity/eligibility threshold stay
in ``artifact_inventory``, ``day_validity``, ``trade_evaluator`` and
``historical_prior``.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Iterable, Mapping
from zoneinfo import ZoneInfo

from .metrics import performance_metrics


Q9_DECISION_SCHEMA = "q9_decision_windows.v1"
KRX_SYMBOL_RE = re.compile(r"^\d{6}$")
_SYMBOL_KEYS = {"symbol", "ticker", "selected_symbol", "top1_symbol", "candidate_symbol"}
_UNAVAILABLE_REASONS = {"baseline_or_minute_rows_unavailable", "baseline_unavailable", "minute_rows_unavailable"}


# --- A8.1a: window and forward-outcome classification --------------------------


def parse_window_kst(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=ZoneInfo("UTC"))
    return parsed.astimezone(ZoneInfo("Asia/Seoul"))


def synthetic_identity(row: dict[str, Any]) -> bool:
    identity = " ".join(
        str(row.get(key) or "").lower() for key in ("decision_id", "q9_decision_id", "run_id", "candidate_pool_id")
    )
    if any(marker in identity for marker in ("test", "fixture", "synthetic")):
        return True
    symbols: list[str] = []

    def collect(value: Any, *, path: tuple[str, ...] = ()) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                child_path = (*path, str(key))
                if key in _SYMBOL_KEYS and not any(
                    part == "layer_packet_ids" or part.endswith("_packet_ids") for part in path
                ):
                    text = str(child or "").strip()
                    if text:
                        symbols.append(text)
                elif isinstance(child, (dict, list)):
                    collect(child, path=child_path)
        elif isinstance(value, list):
            for child in value:
                collect(child, path=path)

    collect(row)
    return any(not KRX_SYMBOL_RE.fullmatch(symbol) for symbol in symbols)


def regular_session_window(row: dict[str, Any]) -> bool:
    parsed = parse_window_kst(row.get("generated_at"))
    if parsed is None:
        return True
    return (9, 0) <= (parsed.hour, parsed.minute) <= (15, 30)


class Q9WindowTally:
    """Streaming classification of ``q9_decision_windows`` rows (synthetic / post-session / trusted)."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.window_count = self.synthetic_count = self.post_session_count = self.trusted_count = 0
        self.abc_count = self.pabc_count = self.pre_universe_count = self.missing_selected_count = 0
        self.trusted_window_times: list[Any] = []

    def add(self, row: Any) -> None:
        if not isinstance(row, dict):
            return
        self.window_count += 1
        if not isinstance(row.get("scanner_control"), dict):
            return
        if synthetic_identity(row):
            self.synthetic_count += 1
            return
        if not regular_session_window(row):
            self.post_session_count += 1
            return
        self.trusted_count += 1
        parsed_time = parse_window_kst(row.get("generated_at"))
        if parsed_time is not None:
            self.trusted_window_times.append(parsed_time)
        strategist = row.get("strategist_selection")
        commander = row.get("commander_final")
        universe = row.get("scanner_pre_strategist_universe")
        if isinstance(strategist, dict) and isinstance(commander, dict):
            self.abc_count += 1
            if isinstance(universe, dict):
                self.pabc_count += 1
        if isinstance(universe, dict) and bool(universe.get("intrinsic_ranked_top20")):
            self.pre_universe_count += 1
        if bool((strategist or {}).get("post_strategist_top10")) and not str((strategist or {}).get("selected_symbol") or ""):
            self.missing_selected_count += 1


def forward_outcome_tally(observed_rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """observed / pending / unavailable / invalid split of forward outcomes (missing never counts as observed)."""
    rows = list(observed_rows)
    observed = sum(1 for row in rows if bool((row.get("shadow_forward_outcome") or {}).get("available")))
    pending = unavailable = invalid = 0
    reasons: Counter[str] = Counter()
    signatures: Counter[str] = Counter()
    for row in rows:
        outcome = row.get("shadow_forward_outcome")
        outcome = outcome if isinstance(outcome, dict) else {}
        if outcome.get("available"):
            continue
        reason = str(outcome.get("reason") or "")
        reasons[reason or "checkpoint_status_only"] += 1
        checkpoints = outcome.get("checkpoints")
        checkpoints = checkpoints if isinstance(checkpoints, dict) else {}
        statuses = {str(checkpoint.get("status") or "") for checkpoint in checkpoints.values() if isinstance(checkpoint, dict)}
        signatures["+".join(sorted(statuses)) or "NO_CHECKPOINT_STATUS"] += 1
        if reason in {"", "forward_window_pending"} and statuses <= {"", "pending"}:
            pending += 1
        elif reason in _UNAVAILABLE_REASONS:
            unavailable += 1
        else:
            invalid += 1
    return {
        "observed": observed,
        "pending": pending,
        "unavailable": unavailable,
        "invalid": invalid,
        "reason_counts": dict(reasons),
        "signature_counts": dict(signatures),
    }


def session_coverage(
    *,
    window_times: list[Any],
    shadow_times: list[Any],
    closeout: Mapping[str, Any],
) -> dict[str, Any]:
    first_window = min(window_times) if window_times else None
    last_window = max(window_times) if window_times else None
    last_runtime_evidence = max(window_times + shadow_times) if (window_times or shadow_times) else None
    closeout_steps = closeout.get("steps") if isinstance(closeout.get("steps"), dict) else {}
    residual = closeout_steps.get("closeout_residual_position_reconciliation")
    residual = residual if isinstance(residual, dict) else {}
    account_snapshot = closeout_steps.get("account_snapshot")
    account_snapshot = account_snapshot if isinstance(account_snapshot, dict) else {}
    post_close_account_ok = bool(
        closeout.get("ok")
        and account_snapshot.get("ok")
        and residual.get("ok")
        and not residual.get("requires_next_open_flatten")
    )
    late_session = bool(last_runtime_evidence and (last_runtime_evidence.hour, last_runtime_evidence.minute) >= (15, 10))
    trigger = str(closeout.get("trigger") or "")
    trigger_ok = bool(trigger.startswith("kiwoom_market_status_") or (trigger and post_close_account_ok and late_session))
    early_open = bool(first_window and (first_window.hour, first_window.minute) <= (9, 10))
    time_coverage_ok = bool(early_open and last_runtime_evidence and late_session)
    post_close_override = bool(early_open and post_close_account_ok and trigger_ok)
    return {
        "first_window": first_window,
        "last_window": last_window,
        "last_runtime_evidence": last_runtime_evidence,
        "post_close_account_ok": post_close_account_ok,
        "late_session_runtime_evidence": late_session,
        "closeout_trigger": trigger,
        "time_coverage_ok": time_coverage_ok,
        "post_close_override": post_close_override,
    }


def q9_diagnostics_fields(
    record: Mapping[str, Any],
    *,
    tally: Q9WindowTally,
    coverage: Mapping[str, Any],
    shadow_payload_count: int,
    pre_row_count: int,
    forward: Mapping[str, Any],
    recovery_artifact_used: bool,
) -> dict[str, Any]:
    first_window = coverage["first_window"]
    last_window = coverage["last_window"]
    last_runtime = coverage["last_runtime_evidence"]
    return {
        "expected_schema_version": Q9_DECISION_SCHEMA,
        "schema_match": bool(record.get("schema_version") == Q9_DECISION_SCHEMA),
        "window_count": tally.window_count,
        "scanner_selection_window_count": tally.trusted_count,
        "complete_abc_window_count": tally.abc_count,
        "complete_pabc_window_count": tally.pabc_count,
        "pre_strategist_universe_window_count": tally.pre_universe_count,
        "missing_selected_candidate_count": tally.missing_selected_count,
        "synthetic_window_count": tally.synthetic_count,
        "post_session_window_count": tally.post_session_count,
        "first_scanner_window_kst": first_window.isoformat() if first_window else "",
        "last_scanner_window_kst": last_window.isoformat() if last_window else "",
        "last_q9_runtime_evidence_kst": last_runtime.isoformat() if last_runtime else "",
        "session_coverage_source": (
            "post_close_account_snapshot_override"
            if coverage["post_close_override"] and not coverage["time_coverage_ok"]
            else "scanner_selection_plus_q9_shadow_runtime"
            if last_runtime and last_runtime != last_window
            else "scanner_selection"
        ),
        "full_session_coverage": bool(coverage["time_coverage_ok"] or coverage["post_close_override"]),
        "post_close_account_snapshot_coverage": bool(coverage["post_close_override"]),
        "post_close_account_snapshot_ok": bool(coverage["post_close_account_ok"]),
        "post_close_trigger": coverage["closeout_trigger"],
        "late_session_runtime_evidence": bool(coverage["late_session_runtime_evidence"]),
        "shadow_payload_count": shadow_payload_count,
        "pre_strategist_forward_candidate_count": pre_row_count,
        "forward_observed_candidate_count": forward["observed"],
        "forward_missing_candidate_count": max(0, pre_row_count - forward["observed"]),
        "forward_pending_candidate_count": forward["pending"],
        "forward_unavailable_candidate_count": forward["unavailable"],
        "forward_invalid_candidate_count": forward["invalid"],
        "forward_outcome_reason_counts": dict(forward["reason_counts"]),
        "forward_outcome_status_signature_counts": dict(forward["signature_counts"]),
        "forward_recovery_artifact_used": bool(recovery_artifact_used),
    }


def inventory_summary(day: str, trades: list[dict[str, Any]], daily: dict[str, Any]) -> dict[str, Any]:
    required_count = sum(1 for trade in trades for row in trade["artifacts"].values() if row["required"]) + sum(
        1 for row in daily.values() if row["required"]
    )
    present = sum(1 for trade in trades for row in trade["artifacts"].values() if row["required"] and row["exists"]) + sum(
        1 for row in daily.values() if row["required"] and row["exists"]
    )
    return {
        "schema_version": "artifact_inventory.v1",
        "day": day,
        "trade_count": len(trades),
        "required_artifact_count": required_count,
        "present_required_artifact_count": present,
        "required_coverage": round(present / required_count, 4) if required_count else 0.0,
        "trades": trades,
        "daily_artifacts": daily,
    }


def trade_inventory(trade_dir: str, trade_id: str, artifacts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    missing_required = [name for name, row in artifacts.items() if row["required"] and not row["exists"]]
    return {
        "trade_dir": trade_dir,
        "trade_id": trade_id,
        "artifacts": artifacts,
        "missing_required": missing_required,
        "complete": not missing_required,
    }


# --- A8.1b: day validity readout ----------------------------------------------------


def q9_day_signals(inventory: Mapping[str, Any]) -> dict[str, Any]:
    """Counts the validity rule reads off the Q9 inventory record (absent counts read as 0)."""
    daily = inventory.get("daily_artifacts")
    daily = daily if isinstance(daily, dict) else {}
    decision = daily.get("q9_decision_windows")
    decision = decision if isinstance(decision, dict) else {}
    comparison = daily.get("q9_vs_samsung_hynix_comparison")
    comparison = comparison if isinstance(comparison, dict) else {}
    window_count = int(decision.get("scanner_selection_window_count") or 0)
    complete_count = int(decision.get("complete_pabc_window_count") or decision.get("complete_abc_window_count") or 0)
    observed = int(decision.get("forward_observed_candidate_count") or 0)
    pending = int(decision.get("forward_pending_candidate_count") or 0)
    total = int(decision.get("pre_strategist_forward_candidate_count") or 0)
    return {
        "decision": decision,
        "comparison": comparison,
        "window_count": window_count,
        "complete_count": complete_count,
        "linkage_ratio": complete_count / window_count if window_count else 0.0,
        "synthetic_count": int(decision.get("synthetic_window_count") or 0),
        "missing_selected": int(decision.get("missing_selected_candidate_count") or 0),
        "invalid_forward": int(decision.get("forward_invalid_candidate_count") or 0),
        "unavailable_forward": int(decision.get("forward_unavailable_candidate_count") or 0),
        "pending_forward": pending,
        "observed_forward": observed,
        "forward_total": total,
        "forward_coverage": (observed + pending) / total if total else 0.0,
        "comparison_complete": (
            bool(comparison.get("exists"))
            and str(comparison.get("schema_version") or "") == "q9_baseline_unified_comparison.v1"
            and str(comparison.get("evidence_status") or "").upper() == "COMPLETE"
            and bool(comparison.get("forward_windows_complete"))
        ),
    }


def q9_day_checks(signals: Mapping[str, Any]) -> dict[str, Any]:
    decision = signals["decision"]
    comparison = signals["comparison"]
    return {
        "artifact_exists": bool(decision.get("exists")),
        "schema_match": bool(decision.get("schema_match", True)),
        "complete_pabc_window_count": signals["complete_count"],
        "scanner_selection_window_count": signals["window_count"],
        "pabc_linkage_ratio": round(signals["linkage_ratio"], 4),
        "full_session_coverage": bool(decision.get("full_session_coverage")),
        "first_window_kst": decision.get("first_scanner_window_kst"),
        "last_window_kst": decision.get("last_scanner_window_kst"),
        "last_runtime_evidence_kst": decision.get("last_q9_runtime_evidence_kst"),
        "session_coverage_source": decision.get("session_coverage_source"),
        "synthetic_window_count": signals["synthetic_count"],
        "post_session_window_count": int(decision.get("post_session_window_count") or 0),
        "missing_selected_candidate_count": signals["missing_selected"],
        "forward_candidate_count": signals["forward_total"],
        "forward_observed_candidate_count": signals["observed_forward"],
        "forward_pending_candidate_count": signals["pending_forward"],
        "forward_unavailable_candidate_count": signals["unavailable_forward"],
        "forward_invalid_candidate_count": signals["invalid_forward"],
        "forward_usable_coverage": round(signals["forward_coverage"], 4),
        "forward_outcome_reason_counts": dict(decision.get("forward_outcome_reason_counts") or {}),
        "forward_outcome_status_signature_counts": dict(decision.get("forward_outcome_status_signature_counts") or {}),
        "unified_comparison_exists": bool(comparison.get("exists")),
        "unified_comparison_evidence_status": str(comparison.get("evidence_status") or ""),
        "unified_comparison_forward_complete": bool(comparison.get("forward_windows_complete")),
        "unified_comparison_complete_override": bool(signals["comparison_complete"]),
    }


# --- A8.1c: trade evaluation evidence blocks -----------------------------------------


def observed_post_exit(model: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    post_exit = (model.get("monitor") or {}).get("post_exit")
    post_exit = post_exit if isinstance(post_exit, dict) else {}
    checkpoints = post_exit.get("checkpoints") if isinstance(post_exit.get("checkpoints"), dict) else {}
    observed = {
        key: value
        for key, value in checkpoints.items()
        if isinstance(value, dict) and str(value.get("status") or "") == "observed"
    }
    return post_exit, observed


def exit_quality_block(
    *, exit_metric_excluded: bool, exit_reason: str, post_exit: Mapping[str, Any], observed: Mapping[str, Any]
) -> dict[str, Any]:
    return {
        "status": "excluded_runtime_incident" if exit_metric_excluded else "observed" if observed else "diagnostic_only",
        "reason": exit_reason,
        "label": "ambiguous",
        "post_exit_comparison": "available" if observed else "unavailable",
        "observed_checkpoints": dict(observed),
        "best_exit_offset": post_exit.get("best_exit_offset"),
        "best_exit_price": post_exit.get("best_exit_price"),
        "max_post_exit_upside_pct": post_exit.get("max_post_exit_upside_pct"),
        "max_post_exit_drawdown_pct": post_exit.get("max_post_exit_drawdown_pct"),
    }


# --- A8.1d: historical prior summary --------------------------------------------------


def evaluation_net_return(evaluation: Mapping[str, Any]) -> float | None:
    value = (evaluation.get("realized_outcome") or {}).get("net_return_pct")
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def prior_rank_bucket(value: Any) -> str:
    try:
        rank = int(float(value))
    except (TypeError, ValueError):
        return "unknown"
    if rank <= 1:
        return "rank1"
    if rank <= 3:
        return "rank2-3"
    if rank <= 10:
        return "rank4-10"
    return "rank11_plus"


def group_metrics(rows: Iterable[tuple[str, float]]) -> dict[str, Any]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for key, value in rows:
        grouped[str(key or "unknown")].append(float(value))
    return {key: performance_metrics(values) for key, values in sorted(grouped.items())}


def historical_prior_summary(
    *,
    models: list[dict[str, Any]],
    evaluations: list[dict[str, Any]],
    attributions: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    from_day: str,
    before_day: str,
    generated_at: str,
) -> dict[str, Any]:
    eligible = [row for row in evaluations if bool((row.get("integrity") or {}).get("promotion_metric_eligible"))]
    returns = [value for value in (evaluation_net_return(row) for row in eligible) if value is not None]
    all_returns = [value for value in (evaluation_net_return(row) for row in evaluations) if value is not None]
    integrity_counts = Counter(str((row.get("integrity") or {}).get("status") or "unknown") for row in evaluations)
    watch_counts = Counter(item for row in evaluations for item in list((row.get("integrity") or {}).get("watch_items") or []))
    defect_counts = Counter(item for row in evaluations for item in list((row.get("integrity") or {}).get("defects") or []))
    rank_rows: list[tuple[str, float]] = []
    playbook_rows: list[tuple[str, float]] = []
    symbol_rows: list[tuple[str, float]] = []
    horizon_rows: list[tuple[str, float]] = []
    source_days = sorted({str(row.get("day") or "") for row in evaluations if str(row.get("day") or "")})
    for model, evaluation in zip(models, evaluations):
        value = evaluation_net_return(evaluation)
        if value is None:
            continue
        selection = model.get("selection") if isinstance(model.get("selection"), dict) else {}
        horizon = evaluation.get("horizon_alignment") if isinstance(evaluation.get("horizon_alignment"), dict) else {}
        rank_rows.append((prior_rank_bucket(selection.get("selected_rank")), value))
        playbook_rows.append((selection.get("strategist_playbook") or "unknown", value))
        symbol_rows.append((model.get("symbol") or "unknown", value))
        horizon_rows.append((horizon.get("bucket") or "unknown", value))
    comparable = [row for row in attributions if (row.get("deltas") or {}).get("strategist_delta_pct") is not None]
    return {
        "schema_version": "historical_q9_prior_summary.v1",
        "behavior_effect": "read_only_historical_prior",
        "generated_at": generated_at,
        "scope": {
            "from_day": from_day,
            "before_day": before_day,
            "source": "reports/trades lifecycle_bundle artifacts",
            "official_q9_freeze_sample": False,
            "usage": "prior_evidence_only",
        },
        "coverage": {
            "source_day_count": len(source_days),
            "source_days": source_days,
            "trade_count": len(evaluations),
            "eligible_trade_count": len(eligible),
            "build_error_count": len(errors),
            "integrity_status_counts": dict(integrity_counts),
            "top_watch_items": dict(watch_counts.most_common(20)),
            "top_defects": dict(defect_counts.most_common(20)),
        },
        "performance": {
            "eligible": performance_metrics(returns),
            "all_realized": performance_metrics(all_returns),
        },
        "breakdowns": {
            "selected_rank_bucket": group_metrics(rank_rows),
            "strategist_playbook": group_metrics(playbook_rows),
            "symbol": group_metrics(symbol_rows),
            "horizon_bucket": group_metrics(horizon_rows),
        },
        "selection_attribution": {
            "comparison_count": len(comparable),
            "unavailable_count": len(attributions) - len(comparable),
            "note": "Historical artifacts often lack Q9-native A/B/C forward controls; use as prior only.",
        },
        "interpretation_guardrails": [
            "Do not merge these rows into the frozen Q9 five-day validation sample.",
            "Do not promote a new tactic from historical_prior alone.",
            "Use this report to decide whether Q9 freeze findings agree with older evidence.",
        ],
        "errors": errors[:50],
    }


def render_historical_prior_markdown(payload: dict[str, Any]) -> str:
    coverage = payload.get("coverage") or {}
    performance = payload.get("performance") or {}
    eligible = performance.get("eligible") or {}
    all_realized = performance.get("all_realized") or {}
    scope = payload.get("scope") or {}
    breakdowns = payload.get("breakdowns") or {}
    lines = [
        "# Historical Q9 Prior",
        "",
        f"- Scope: `{scope.get('from_day') or 'beginning'}` to before `{scope.get('before_day')}`",
        "- Behavior effect: read-only historical prior",
        "- Official Q9 freeze sample: **False**",
        "- Usage: prior evidence only, not promotion evidence by itself",
        "",
        "## Coverage",
        "",
        f"- Source days: {coverage.get('source_day_count', 0)}",
        f"- Trades: {coverage.get('trade_count', 0)} total / {coverage.get('eligible_trade_count', 0)} eligible",
        f"- Build errors: {coverage.get('build_error_count', 0)}",
        f"- Integrity counts: {coverage.get('integrity_status_counts', {})}",
        "",
        "## Performance",
        "",
        f"- Eligible count: {eligible.get('count', 0)}",
        f"- Eligible win rate: {float(eligible.get('win_rate') or 0) * 100:.1f}%",
        f"- Eligible average return: {float(eligible.get('average_return_pct') or 0):.4f}%",
        f"- Eligible profit factor: {eligible.get('profit_factor', 0)}",
        f"- Eligible maximum drawdown: {float(eligible.get('maximum_drawdown_pct') or 0):.4f}%",
        f"- All-realized count: {all_realized.get('count', 0)}",
        f"- All-realized average return: {float(all_realized.get('average_return_pct') or 0):.4f}%",
        "",
        "## Key Breakdowns",
        "",
    ]
    for name in ("selected_rank_bucket", "strategist_playbook", "horizon_bucket"):
        lines.append(f"### {name}")
        rows = breakdowns.get(name) if isinstance(breakdowns.get(name), dict) else {}
        if not rows:
            lines.append("- No comparable rows")
            lines.append("")
            continue
        for key, metrics in rows.items():
            lines.append(
                f"- {key}: count {metrics.get('count', 0)}, "
                f"win {float(metrics.get('win_rate') or 0) * 100:.1f}%, "
                f"avg {float(metrics.get('average_return_pct') or 0):.4f}%, "
                f"PF {metrics.get('profit_factor', 0)}"
            )
        lines.append("")
    lines.extend([
        "## Guardrails",
        "",
        "- This does not reopen Q8.",
        "- This does not extend the Q9 five-valid-day freeze.",
        "- Monday Q9 close remains the authoritative decision point; this report is a tie-breaker and root-cause prior.",
        "",
    ])
    return "\n".join(lines)
