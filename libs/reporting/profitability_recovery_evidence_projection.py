"""profitability_recovery_day1 projections (moved verbatim from profitability_recovery_day1).

Module globals and helpers are resolved on ``facade`` (the profitability_recovery_day1 module) at call time; this module never imports it.
"""
from __future__ import annotations

from typing import Any, Dict, List


def _execution_missing_fields(execution_details: Dict[str, Any], *, facade: Any) -> List[str]:
    execution_details = execution_details if isinstance(execution_details, dict) else {}
    missing: List[str] = []
    for key in facade.REQUIRED_EXECUTION_FIELDS:
        if key not in execution_details or execution_details.get(key) in (None, "", []):
            missing.append(str(key))
    return missing



def _bundle_artifacts(lifecycle_bundle: Dict[str, Any]) -> Dict[str, Any]:
    artifacts = lifecycle_bundle.get("artifacts")
    return artifacts if isinstance(artifacts, dict) else {}



def _section_provenance(lifecycle_bundle: Dict[str, Any]) -> Dict[str, Any]:
    section_provenance = lifecycle_bundle.get("section_provenance")
    return section_provenance if isinstance(section_provenance, dict) else {}
