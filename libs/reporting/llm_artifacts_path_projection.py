"""LLM artifacts operator-summary and trade-day path projections (moved verbatim from llm_artifacts).

Helpers are resolved on ``facade`` (the llm_artifacts module) at call time; this module never imports it.
Pure path construction except trade lookup, which only reads the filesystem through the facade.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def canonical_trade_day_root(reports_root: Path, day: str) -> Path:
    return Path(reports_root) / "trades" / str(day or "").strip()


def _repo_root_from_reports_root(reports_root: Path) -> Path:
    root = Path(reports_root)
    if root.name == "reports":
        return root.parent
    return root


def operator_summary_artifact_root(reports_root: Path) -> Path:
    """Canonical operator-facing report root.

    Passing either `reports` or `reports/operator_summary` should resolve to
    the same active operator-summary surface without double nesting.
    """
    root = Path(reports_root)
    if root.name == "operator_summary":
        return root
    if root.name in {"daily", "weekly", "monthly", "symbols"} and root.parent.name == "operator_summary":
        return root.parent
    return root / "operator_summary"


def daily_artifact_paths(reports_root: Path, day: str, *, facade: Any) -> Dict[str, Path]:
    """Canonical daily reporting paths under reports/operator_summary/daily/YYYY-MM-DD/."""
    normalized_day = str(day or "").strip()
    operator_root = facade.operator_summary_artifact_root(reports_root)
    daily_root = operator_root / "daily" / normalized_day
    return {
        "root_dir": daily_root,
        "daily_root": daily_root,
        "daily_report_json": daily_root / "daily_report.json",
        "daily_report_md": daily_root / "daily_report.md",
        "daily_summary_json": daily_root / "daily_summary.json",
        "daily_summary_md": daily_root / "daily_summary.md",
        "daily_report_llm_response_json": daily_root / "daily_report_llm_response.json",
        "operator_summary_json": daily_root / "operator_summary.json",
        "operator_summary_md": daily_root / "operator_summary.md",
        "trade_index_json": daily_root / "trade_index.json",
        "legacy_daily_json": operator_root / "daily" / f"daily_{normalized_day}.json",
        "legacy_daily_md": operator_root / "daily" / f"daily_{normalized_day}.md",
        "root_daily_json": operator_root / f"daily_{normalized_day}.json",
        "root_daily_md": operator_root / f"daily_{normalized_day}.md",
    }


def symbol_artifact_paths(reports_root: Path, symbol: str, *, facade: Any) -> Dict[str, Path]:
    """Canonical symbol-history reporting paths under reports/operator_summary/symbols/<SYMBOL>/."""
    normalized_symbol = str(symbol or "").strip().upper()
    symbol_root = facade.operator_summary_artifact_root(reports_root) / "symbols" / normalized_symbol
    return {
        "root_dir": symbol_root,
        "symbol_trade_report_json": symbol_root / "symbol_trade_report.json",
        "symbol_trade_report_md": symbol_root / "symbol_trade_report.md",
        "symbol_summary_json": symbol_root / "symbol_summary.json",
        "symbol_summary_md": symbol_root / "symbol_summary.md",
        "symbol_memory_json": symbol_root / "symbol_memory.json",
        "trade_history_json": symbol_root / "trade_history.json",
        "daily_index_json": symbol_root / "daily_index.json",
        "latest_snapshot_json": symbol_root / "latest_snapshot.json",
    }


def weekly_artifact_paths(reports_root: Path, week: str, *, facade: Any) -> Dict[str, Path]:
    """Canonical operator weekly summary paths under reports/operator_summary/weekly/YYYY-Www/."""
    normalized_week = str(week or "").strip()
    weekly_root = facade.operator_summary_artifact_root(reports_root) / "weekly" / normalized_week
    return {
        "root_dir": weekly_root,
        "weekly_root": weekly_root,
        "weekly_summary_json": weekly_root / "weekly_summary.json",
        "weekly_summary_md": weekly_root / "weekly_summary.md",
    }


def monthly_artifact_paths(reports_root: Path, month: str, *, facade: Any) -> Dict[str, Path]:
    """Canonical operator monthly summary paths under reports/operator_summary/monthly/YYYY-MM/."""
    normalized_month = str(month or "").strip()
    monthly_root = facade.operator_summary_artifact_root(reports_root) / "monthly" / normalized_month
    return {
        "root_dir": monthly_root,
        "monthly_root": monthly_root,
        "monthly_summary_json": monthly_root / "monthly_summary.json",
        "monthly_summary_md": monthly_root / "monthly_summary.md",
    }
