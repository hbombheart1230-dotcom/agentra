from __future__ import annotations
from typing import Any, Dict
def _thin_trace(bundle: Dict[str, Any], *, facade: Any) -> bool:
    scanner_trace=bundle.get("scanner_selection_trace") if isinstance(bundle.get("scanner_selection_trace"),dict) else {}
    if not scanner_trace:
        reason=bundle.get("scanner_reason_human") if isinstance(bundle.get("scanner_reason_human"),dict) else {}; scanner_trace=reason.get("scanner_selection_trace") if isinstance(reason.get("scanner_selection_trace"),dict) else {}
    ranked=scanner_trace.get("ranked_candidates") if isinstance(scanner_trace.get("ranked_candidates"),list) else []
    if not ranked:
        reason=bundle.get("scanner_reason_human") if isinstance(bundle.get("scanner_reason_human"),dict) else {}; ranked=reason.get("ranked_candidates") if isinstance(reason.get("ranked_candidates"),list) else []
    monitor_trace=bundle.get("monitor_stop_policy_trace") if isinstance(bundle.get("monitor_stop_policy_trace"),dict) else {}
    if not monitor_trace:
        reason=bundle.get("monitor_reason_human") if isinstance(bundle.get("monitor_reason_human"),dict) else {}; monitor_trace=reason.get("monitor_stop_policy_trace") if isinstance(reason.get("monitor_stop_policy_trace"),dict) else {}
    return len(ranked)==0 or len(monitor_trace)==0
