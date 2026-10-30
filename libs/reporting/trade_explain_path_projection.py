"""Trade explain output path projections (moved verbatim from trade_explain).

Globals are resolved on ``facade`` (the trade_explain module) at call time; this module never imports it.
Pure path construction; no filesystem access.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def official_trade_explain_report_dir(reports_root: Path, *, facade: Any) -> Path:
    return facade.Path(reports_root) / facade.OFFICIAL_TRADE_EXPLAIN_RELATIVE_DIR


def build_trade_explain_output_path_metadata(report_dir: Path, *, facade: Any) -> Dict[str, Any]:
    canonical_reports_root = facade._canonical_report_root(report_dir)
    requested_dir = facade.Path(report_dir)
    official_dir = facade.official_trade_explain_report_dir(canonical_reports_root)
    is_official = requested_dir == official_dir
    return {
        "official_report_dir": str(official_dir),
        "requested_report_dir": str(requested_dir),
        "path_status": "official" if is_official else "custom_nonofficial",
        "deprecated_note": ""
        if is_official
        else f"Official trade_explain path is `{official_dir}`; custom output path is supported but non-canonical.",
    }
