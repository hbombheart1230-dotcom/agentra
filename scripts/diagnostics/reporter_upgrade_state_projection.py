from __future__ import annotations
from typing import Any, Dict
def _is_closed_trade(bundle: Dict[str, Any], *, facade: Any) -> bool:
    lifecycle=bundle.get("lifecycle") if isinstance(bundle.get("lifecycle"),dict) else {}; exit_payload=lifecycle.get("exit") if isinstance(lifecycle.get("exit"),dict) else {}
    if exit_payload: return True
    status=str(bundle.get("trade_lifecycle_status") or lifecycle.get("status") or bundle.get("status") or "").strip().lower()
    if status in {"closed","exited","sell"}: return True
    top_exit=bundle.get("exit") if isinstance(bundle.get("exit"),dict) else {}; return bool(top_exit.get("available"))
def _reporter_section_fallback(report: Dict[str, Any], *, facade: Any) -> bool:
    provenance=report.get("section_provenance") if isinstance(report.get("section_provenance"),dict) else {}
    for key in ("reporter_evaluation","errors_weaknesses_improvement_points"):
        item=provenance.get(key) if isinstance(provenance.get(key),dict) else {}
        if str(item.get("source") or "").strip().lower() in {"fallback","unknown","missing"}: return True
    return False
def _missing_canonical_paths(bundle: Dict[str, Any], *, facade: Any) -> bool:
    artifacts=bundle.get("artifacts") if isinstance(bundle.get("artifacts"),dict) else {}
    return any(not str(artifacts.get(key) or bundle.get(key) or "").strip() for key in facade.CANONICAL_ARTIFACT_KEYS)
