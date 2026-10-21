from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .artifact_inventory import read_json
from .counterfactuals import build_selection_attribution
from . import fast08_evidence_inventory as _ev
from .trade_evaluator import evaluate_trade
from .trade_read_model import build_q9_trade_read_model


DEFAULT_BEFORE_DAY = "2026-06-29"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _day_from_trade_dir(trade_dir: Path) -> str:
    parts = list(trade_dir.parts)
    for index, part in enumerate(parts):
        if part == "trades" and index + 1 < len(parts):
            return parts[index + 1]
    return ""


def iter_historical_trade_dirs(
    reports_root: Path,
    *,
    from_day: str = "",
    before_day: str = DEFAULT_BEFORE_DAY,
) -> list[Path]:
    trades_root = Path(reports_root) / "trades"
    if not trades_root.exists():
        return []
    rows: list[Path] = []
    for path in sorted({item.parent for item in trades_root.rglob("lifecycle_bundle.json")}):
        day = _day_from_trade_dir(path)
        if not day:
            continue
        if from_day and day < from_day:
            continue
        if before_day and day >= before_day:
            continue
        rows.append(path)
    return rows


_net_return = _ev.evaluation_net_return
_rank_bucket = _ev.prior_rank_bucket
_group_metrics = _ev.group_metrics


def summarize_historical_prior(
    *,
    models: list[dict[str, Any]],
    evaluations: list[dict[str, Any]],
    attributions: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    from_day: str,
    before_day: str,
) -> dict[str, Any]:
    return _ev.historical_prior_summary(
        models=models,
        evaluations=evaluations,
        attributions=attributions,
        errors=errors,
        from_day=from_day,
        before_day=before_day,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


render_historical_prior_markdown = _ev.render_historical_prior_markdown


def build_historical_q9_prior(
    reports_root: Path,
    *,
    from_day: str = "",
    before_day: str = DEFAULT_BEFORE_DAY,
) -> dict[str, Any]:
    reports_root = Path(reports_root)
    output_root = reports_root / "evaluation" / "historical_q9_prior"
    trade_dirs = iter_historical_trade_dirs(reports_root, from_day=from_day, before_day=before_day)
    models: list[dict[str, Any]] = []
    evaluations: list[dict[str, Any]] = []
    attributions: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for trade_dir in trade_dirs:
        try:
            model = build_q9_trade_read_model(trade_dir)
            evaluation = evaluate_trade(model)
            attribution = build_selection_attribution(model)
        except Exception as exc:
            errors.append({
                "trade_dir": str(trade_dir),
                "day": _day_from_trade_dir(trade_dir),
                "error": f"{type(exc).__name__}: {exc}",
            })
            continue
        models.append(model)
        evaluations.append(evaluation)
        attributions.append(attribution)

    summary = summarize_historical_prior(
        models=models,
        evaluations=evaluations,
        attributions=attributions,
        errors=errors,
        from_day=from_day,
        before_day=before_day,
    )
    _write_json(output_root / "historical_q9_trade_read_models.json", {
        "schema_version": "historical_q9_trade_read_models.v1",
        "behavior_effect": "read_only_historical_prior",
        "rows": models,
    })
    _write_json(output_root / "historical_q9_trade_evaluations.json", {
        "schema_version": "historical_q9_trade_evaluations.v1",
        "behavior_effect": "read_only_historical_prior",
        "rows": evaluations,
    })
    _write_json(output_root / "historical_q9_selection_attributions.json", {
        "schema_version": "historical_q9_selection_attributions.v1",
        "behavior_effect": "read_only_historical_prior",
        "rows": attributions,
    })
    _write_json(output_root / "historical_q9_prior_summary.json", summary)
    _write_text(output_root / "historical_q9_prior_report.md", render_historical_prior_markdown(summary))
    return {
        "ok": True,
        "trade_count": len(models),
        "error_count": len(errors),
        "output_dir": str(output_root),
        "summary": str(output_root / "historical_q9_prior_summary.json"),
        "report": str(output_root / "historical_q9_prior_report.md"),
    }


__all__ = [
    "DEFAULT_BEFORE_DAY",
    "build_historical_q9_prior",
    "iter_historical_trade_dirs",
    "render_historical_prior_markdown",
    "summarize_historical_prior",
]
