"""Daily report generator operator summary snapshot projection (moved verbatim from daily_report_generator).

Builders are resolved on ``facade`` (the daily_report_generator module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def _load_operator_summary_snapshot(events_path: Path, out_dir: Path, day: str, *, facade: Any) -> Dict[str, Any]:
    paths = facade.daily_artifact_paths(out_dir, day)
    payload = facade.build_operator_daily_summary_payload(
        events_path,
        out_dir,
        day=day,
        metrics_report_dir=out_dir / "metrics",
        m30_post_golive_dir=out_dir / "milestones" / "m30_post_golive",
        m30_golive_dir=out_dir / "milestones" / "m30_golive",
        m31_slo_incident_dir=out_dir / "m31_slo_incident",
    )
    snapshot = facade.build_operator_summary_snapshot_from_payload(payload)
    snapshot["report_json_path"] = str(paths["operator_summary_json"])
    snapshot["report_md_path"] = str(paths["operator_summary_md"])
    return snapshot
