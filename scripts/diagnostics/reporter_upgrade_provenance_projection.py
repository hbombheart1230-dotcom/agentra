from __future__ import annotations

from typing import Any, Dict


def _section_provenance_all_fallback(report: Dict[str, Any], *, facade: Any) -> bool:
    provenance = report.get("section_provenance") if isinstance(report.get("section_provenance"), dict) else {}
    if not provenance:
        return False
    entries = [value for value in provenance.values() if isinstance(value, dict)]
    if not entries:
        return False
    fallback_tags = {"fallback", "unknown", "missing"}
    return all(str(entry.get("source") or "").strip().lower() in fallback_tags for entry in entries)
