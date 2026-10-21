from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import fast07_chain_render_projection as _render


SCHEMA_VERSION = "operator_summary_mining.v1"


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        return {"__error__": str(exc)}


_dict = _render.mining_dict
_list = _render.mining_list
_safe_int = _render.mining_safe_int
_safe_float = _render.mining_safe_float
_avg = _render.mining_avg


@dataclass(frozen=True)
class DailyArtifacts:
    day: str
    daily_summary: dict[str, Any]
    operator_summary: dict[str, Any]
    q8_review: dict[str, Any]
    q9_windows: dict[str, Any]
    closeout: dict[str, Any]
    trade_index: list[Any]
    daily_report: dict[str, Any]
    errors: list[str]


def _daily_artifacts(day_dir: Path) -> DailyArtifacts:
    errors: list[str] = []

    def load(name: str) -> Any:
        payload = _load_json(day_dir / name)
        if isinstance(payload, dict) and "__error__" in payload:
            errors.append(f"{name}: {payload['__error__']}")
        return payload

    return DailyArtifacts(
        day=day_dir.name,
        daily_summary=_dict(load("daily_summary.json")),
        operator_summary=_dict(load("operator_summary.json")),
        q8_review=_dict(load("q8_shadow_blocker_review.json")),
        q9_windows=_dict(load("q9_decision_windows.json")),
        closeout=_dict(load("closeout_maintenance.json")),
        trade_index=_list(load("trade_index.json")),
        daily_report=_dict(load("daily_report.json")),
        errors=errors,
    )


_presence_report = _render.mining_presence_report
_daily_quality = _render.mining_daily_quality


def _weekly_quality(root: Path) -> dict[str, Any]:
    weekly_root = root / "weekly"
    weeks = [p for p in sorted(weekly_root.glob("*")) if p.is_dir()] if weekly_root.exists() else []
    return _render.mining_weekly_quality(
        [_render.mining_weekly_row(week_dir.name, _dict(_load_json(week_dir / "weekly_summary.json"))) for week_dir in weeks]
    )


def _symbol_quality(root: Path) -> dict[str, Any]:
    symbol_root = root / "symbols"
    symbols = [p for p in sorted(symbol_root.glob("*")) if p.is_dir()] if symbol_root.exists() else []
    return _render.mining_symbol_quality(
        [
            _render.mining_symbol_row(
                symbol_dir.name,
                _dict(_load_json(symbol_dir / "symbol_summary.json")),
                _dict(_load_json(symbol_dir / "symbol_memory.json")),
            )
            for symbol_dir in symbols
        ]
    )


_q9_overlap = _render.mining_q9_overlap


def _readiness(payload: dict[str, Any]) -> dict[str, Any]:
    presence = _dict(payload.get("daily_presence"))
    daily = _dict(payload.get("daily_quality"))
    weekly = _dict(payload.get("weekly_quality"))
    symbols = _dict(payload.get("symbol_quality"))
    q9 = _dict(payload.get("q9_overlap"))
    issues: list[str] = []
    strengths: list[str] = []
    if _safe_int(presence.get("daily_count")) >= 40:
        strengths.append("daily operator summaries cover enough history for operational mining")
    if _safe_int(weekly.get("usable_week_count")) >= 4:
        strengths.append("weekly summaries contain tactic/shadow evidence across multiple weeks")
    if _safe_int(symbols.get("symbols_with_trade_count_ge_5")) >= 10:
        strengths.append("symbol summaries have enough repeated names for symbol-level diagnostics")
    if _safe_int(q9.get("q9_window_count_total")) >= 1000:
        strengths.append("Q9 decision windows are dense enough for attribution diagnostics")
    if daily.get("missing_runtime_surface_days"):
        issues.append("some recent days have daily_summary trades but missing daily_report/trade_index surface")
    if daily.get("trade_index_mismatch_examples"):
        issues.append("some recent trade_index counts differ from daily_summary trade counts")
    if _safe_int(q9.get("q9_operator_summary_day_count")) < 5:
        issues.append("Q9-linked operator_summary history is still short")
    status = "USABLE_WITH_GAPS" if strengths else "WEAK"
    if issues and not strengths:
        status = "NEEDS_REPAIR"
    elif not issues and strengths:
        status = "USABLE"
    return {
        "status": status,
        "strengths": strengths,
        "issues": issues,
        "recommended_use": [
            "use operator_summary as Q9 support evidence, not as the single source of truth",
            "mine weekly and symbol summaries for recurring failure/success patterns",
            "keep execution behavior frozen; use this report for observability only",
        ],
    }


def build_operator_summary_mining(reports_root: Path | str = "reports") -> dict[str, Any]:
    reports_root = Path(reports_root)
    operator_root = reports_root / "operator_summary"
    daily_root = operator_root / "daily"
    day_dirs = [p for p in sorted(daily_root.glob("*")) if p.is_dir()] if daily_root.exists() else []
    days = [_daily_artifacts(path) for path in day_dirs]
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "behavior_effect": "observation_only",
        "source": str(operator_root),
        "daily_presence": _presence_report(days),
        "daily_quality": _daily_quality(days),
        "weekly_quality": _weekly_quality(operator_root),
        "symbol_quality": _symbol_quality(operator_root),
        "q9_overlap": _q9_overlap(days),
    }
    payload["readiness"] = _readiness(payload)
    return payload


_fmt = _render.mining_fmt
render_operator_summary_mining_markdown = _render.render_operator_summary_mining_markdown


def write_operator_summary_mining(
    reports_root: Path | str = "reports",
    *,
    output_dir: Path | str | None = None,
) -> dict[str, str]:
    reports_root = Path(reports_root)
    payload = build_operator_summary_mining(reports_root)
    target = Path(output_dir) if output_dir else reports_root / "evaluation" / "operator_summary_mining"
    target.mkdir(parents=True, exist_ok=True)
    json_path = target / "operator_summary_mining.json"
    md_path = target / "operator_summary_mining.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_operator_summary_mining_markdown(payload), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


__all__ = [
    "build_operator_summary_mining",
    "render_operator_summary_mining_markdown",
    "write_operator_summary_mining",
]
