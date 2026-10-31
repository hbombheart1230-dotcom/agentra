"""profitability_recovery_day1 projections (moved verbatim from profitability_recovery_day1).

Module globals and helpers are resolved on ``facade`` (the profitability_recovery_day1 module) at call time; this module never imports it.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def _resolve_same_day_linkage(lifecycle_bundle: Dict[str, Any], trade_dir: Path, *, facade: Any) -> Dict[str, Any]:
    linkage = lifecycle_bundle.get("same_day_reporter_linkage")
    if isinstance(linkage, dict) and facade._linkage_surface_present(linkage):
        return dict(linkage)

    artifacts = facade._bundle_artifacts(lifecycle_bundle)
    section_provenance = facade._section_provenance(lifecycle_bundle)
    candidate_paths = [
        artifacts.get("reporter_analysis_json"),
        artifacts.get("reporter_analysis_md"),
        ((section_provenance.get("reporter_status_human") or {}) if isinstance(section_provenance.get("reporter_status_human"), dict) else {}).get("artifact_path"),
    ]
    for raw in candidate_paths:
        if not raw:
            continue
        candidate = facade.Path(str(raw))
        if not candidate.is_absolute():
            candidate = facade.Path.cwd() / candidate
        if candidate.exists():
            return {
                "status": "linked_day_fallback",
                "linkage_reason": "same_day_reporter_artifact_present",
                "artifact_path": str(candidate),
            }
    return linkage if isinstance(linkage, dict) else {}
