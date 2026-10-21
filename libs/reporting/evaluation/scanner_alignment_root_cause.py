from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from . import fast08_scanner_attribution as _sa


ROOT_CAUSES = (
    "Scanner Ranking Failure",
    "Rank Drift",
    "Strategist Override",
    "Candidate Filtering",
    "Symbol Mapping",
    "Missing Evidence",
    "Aligned / No Alignment Issue",
)

OUTCOME_CONDITIONED_CAUSES = {
    "Scanner Ranking Failure",
    "Aligned / No Alignment Issue",
}

EVIDENCE_GAP_CAUSES = {"Missing Evidence"}


_mapping = _sa.mapping


def _rows(value: Any) -> list[Mapping[str, Any]]:
    return [row for row in (value or []) if isinstance(row, Mapping)]


_num = _sa.number
_symbol = _sa.symbol_of


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


_selected_rank = _sa.selected_rank
_score_gap = _sa.score_gap
_outcome_return = _sa.outcome_return


def classify_scanner_alignment_root_cause(
    *,
    row: Mapping[str, Any],
    model: Mapping[str, Any],
    net_return_pct: float | None,
) -> dict[str, Any]:
    raw = str(row.get("raw_scanner_top1") or "")
    post = str(row.get("post_strategy_top1") or "")
    selected = str(row.get("selected_symbol") or "")
    executed = str(row.get("executed_symbol") or "")
    rank = _selected_rank(model)
    score_gap = _score_gap(model)
    reasons: list[str] = []

    if not raw or not post or not selected or not executed:
        return {
            "root_cause": "Missing Evidence",
            "confidence": "high",
            "reasons": ["raw/post/selected/executed symbol missing"],
            "selected_rank": rank,
            "score_gap": score_gap,
        }

    if (
        row.get("final_to_executed_changed") is True
        or row.get("monitor_to_commander_changed") is True
        or row.get("selected_to_monitor_changed") is True
    ):
        return {
            "root_cause": "Symbol Mapping",
            "confidence": "high",
            "reasons": ["symbol changed after selection path"],
            "selected_rank": rank,
            "score_gap": score_gap,
        }

    if selected != post and rank is not None and rank > 1:
        reasons.append("selected candidate is below post-strategy top1")
        reasons.append(f"selected_rank={rank}")
        if score_gap is not None:
            reasons.append(f"score_gap={score_gap}")
        return {
            "root_cause": "Candidate Filtering",
            "confidence": "high",
            "reasons": reasons,
            "selected_rank": rank,
            "score_gap": score_gap,
        }

    if raw != post and selected == post:
        return {
            "root_cause": "Strategist Override",
            "confidence": "medium",
            "reasons": ["post-strategy top1 differs from raw top1 and final selection followed post-strategy top1"],
            "selected_rank": rank,
            "score_gap": score_gap,
        }

    if raw != post or (rank is not None and rank > 1):
        reasons.append("top candidate changed or selected rank drifted")
        if raw != post:
            reasons.append("raw_top1_differs_from_post_strategy_top1")
        if rank is not None and rank > 1:
            reasons.append(f"selected_rank={rank}")
        return {
            "root_cause": "Rank Drift",
            "confidence": "medium",
            "reasons": reasons,
            "selected_rank": rank,
            "score_gap": score_gap,
        }

    if net_return_pct is not None and net_return_pct < 0:
        return {
            "root_cause": "Scanner Ranking Failure",
            "confidence": "medium",
            "reasons": ["top-ranked selected candidate produced negative realized return"],
            "selected_rank": rank,
            "score_gap": score_gap,
        }

    return {
        "root_cause": "Aligned / No Alignment Issue",
        "confidence": "medium",
        "reasons": ["raw/post/selected/executed symbols are aligned"],
        "selected_rank": rank,
        "score_gap": score_gap,
    }


_impact_score = _sa.impact_score


def _diagnostic_kind(cause: str) -> str:
    if cause in OUTCOME_CONDITIONED_CAUSES:
        return "outcome_conditioned"
    if cause in EVIDENCE_GAP_CAUSES:
        return "evidence_gap"
    return "structural"


_largest_cause = _sa.largest_cause


def _patch_candidate(cause: str) -> str:
    if cause == "Candidate Filtering":
        return "Tighten runner-up/candidate filtering evidence before selecting below post-strategy top1."
    if cause == "Strategist Override":
        return "Audit strategy-context rank adjustments before allowing post-strategy top1 to replace raw top1."
    if cause == "Rank Drift":
        return "Require explicit rank-drift reason and score-gap evidence when Top1 changes."
    if cause == "Scanner Ranking Failure":
        return "Decompose scanner raw score components for aligned losing Top1 trades."
    if cause == "Symbol Mapping":
        return "Fix symbol propagation before any trading behavior patch."
    if cause == "Missing Evidence":
        return "Fix missing selection evidence before interpreting scanner alignment."
    return "No scanner-alignment behavior patch candidate from aligned rows."


def _largest_causes(cause_summary: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return _sa.largest_causes(
        cause_summary,
        behavior_excluded={"Missing Evidence", "Aligned / No Alignment Issue"},
        structural_excluded=OUTCOME_CONDITIONED_CAUSES | EVIDENCE_GAP_CAUSES,
    )


def build_scanner_alignment_root_cause_report(
    *,
    day: str,
    models: Sequence[Mapping[str, Any]],
    evaluations: Sequence[Mapping[str, Any]],
    selection_authority: Mapping[str, Any],
) -> dict[str, Any]:
    model_by_trade = {str(model.get("trade_id") or ""): model for model in models}
    evaluation_by_trade = {str(row.get("trade_id") or ""): row for row in evaluations}
    rows: list[dict[str, Any]] = []
    for row in _rows(selection_authority.get("rows")):
        trade_id = str(row.get("trade_id") or "")
        model = _mapping(model_by_trade.get(trade_id))
        evaluation = _mapping(evaluation_by_trade.get(trade_id))
        net_return = _outcome_return(evaluation, model)
        classification = classify_scanner_alignment_root_cause(
            row=row,
            model=model,
            net_return_pct=net_return,
        )
        rows.append(
            _sa.root_cause_row(
                row,
                trade_id=trade_id,
                net_return=net_return,
                classification=classification,
                kind=_diagnostic_kind(classification["root_cause"]),
            )
        )

    cause_summary = _sa.root_cause_summary(rows, ROOT_CAUSES, kind_of=_diagnostic_kind)
    largest = _largest_causes(cause_summary)
    largest_structural = largest["largest_structural_root_cause"]
    patch_candidate = _patch_candidate(str(largest_structural.get("root_cause") or ""))

    return {
        "schema_version": "scanner_alignment_root_cause.v1",
        "measurement_contract_version": "q14_structural_causality.v2",
        "evaluation_program_id": "Q14_SCANNER_ALIGNMENT_ROOT_CAUSE",
        "behavior_effect": "observation_only",
        "day": day,
        "trade_count": len(rows),
        "cause_summary": cause_summary,
        **largest,
        "outcome_conditioned_causes": sorted(OUTCOME_CONDITIONED_CAUSES),
        "q15_behavior_patch_candidate": patch_candidate,
        "rows": rows,
        "interpretation_rule": (
            "Q14 explains why scanner_alignment_score is low. It does not authorize behavior changes. "
            "Scanner Ranking Failure and Aligned / No Alignment Issue are outcome-conditioned labels, "
            "not independent causal proof. Structural behavior candidates must use "
            "largest_structural_root_cause plus Q9 forward evidence."
        ),
    }


render_scanner_alignment_root_cause_report = _sa.render_scanner_alignment_root_cause_report


def _load_day_models_and_evaluations(reports_root: Path, day: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    root = reports_root / "evaluation" / "trades" / day
    models: list[dict[str, Any]] = []
    evaluations: list[dict[str, Any]] = []
    if not root.exists():
        return models, evaluations
    for trade_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        model = _read_json(trade_dir / "trade_read_model.json")
        evaluation = _read_json(trade_dir / "trade_evaluation.json")
        if model:
            models.append(model)
        if evaluation:
            evaluations.append(evaluation)
    return models, evaluations


def build_scanner_alignment_root_cause_range(
    *,
    reports_root: Path = Path("reports"),
    start: str,
    end: str,
) -> dict[str, Any]:
    from datetime import date, timedelta

    reports_root = Path(reports_root)
    cursor = date.fromisoformat(start)
    final = date.fromisoformat(end)
    daily_payloads: list[dict[str, Any]] = []
    while cursor <= final:
        day = cursor.isoformat()
        selection_authority = _read_json(
            reports_root / "evaluation" / "daily" / day / "selection_authority_audit.json"
        )
        models, evaluations = _load_day_models_and_evaluations(reports_root, day)
        if selection_authority or models or evaluations:
            daily_payloads.append(
                build_scanner_alignment_root_cause_report(
                    day=day,
                    models=models,
                    evaluations=evaluations,
                    selection_authority=selection_authority,
                )
            )
        cursor += timedelta(days=1)

    all_rows = [row for payload in daily_payloads for row in payload.get("rows") or []]
    cause_summary = _sa.root_cause_summary(all_rows, ROOT_CAUSES, kind_of=_diagnostic_kind)
    largest = _largest_causes(cause_summary)
    largest_structural = largest["largest_structural_root_cause"]
    return {
        "schema_version": "scanner_alignment_root_cause_range.v1",
        "evaluation_program_id": "Q14_SCANNER_ALIGNMENT_ROOT_CAUSE_RANGE",
        "behavior_effect": "observation_only",
        "start": start,
        "end": end,
        "day_count": len(daily_payloads),
        "trade_count": len(all_rows),
        "cause_summary": cause_summary,
        **largest,
        "outcome_conditioned_causes": sorted(OUTCOME_CONDITIONED_CAUSES),
        "measurement_contract_version": "q14_structural_causality.v2",
        "q15_behavior_patch_candidate": _patch_candidate(str(largest_structural.get("root_cause") or "")),
        "daily_rows": [
            {
                "day": payload.get("day"),
                "trade_count": payload.get("trade_count"),
                "largest_root_cause": _mapping(payload.get("largest_root_cause")).get("root_cause") or "",
            }
            for payload in daily_payloads
        ],
        "rows": all_rows,
        "interpretation_rule": (
            "Range aggregate for Q14. Outcome-conditioned labels are descriptive only. "
            "Use largest_structural_root_cause and independent Q9 forward evidence before "
            "choosing a behavior candidate."
        ),
    }


def write_scanner_alignment_root_cause_range(
    *,
    reports_root: Path = Path("reports"),
    start: str,
    end: str,
) -> dict[str, str]:
    reports_root = Path(reports_root)
    payload = build_scanner_alignment_root_cause_range(
        reports_root=reports_root,
        start=start,
        end=end,
    )
    out_dir = reports_root / "evaluation" / "range" / f"{start}_{end}"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "scanner_alignment_root_cause_report.json"
    md_path = out_dir / "scanner_alignment_root_cause_report.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_scanner_alignment_root_cause_report(payload), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


__all__ = [
    "build_scanner_alignment_root_cause_report",
    "render_scanner_alignment_root_cause_report",
    "build_scanner_alignment_root_cause_range",
    "write_scanner_alignment_root_cause_range",
]
