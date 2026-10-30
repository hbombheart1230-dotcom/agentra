from __future__ import annotations
from typing import Any, Dict
def compare_days(base: Dict[str, Any], target: Dict[str, Any], *, facade: Any) -> Dict[str, Any]:
    keys=("closed_trades","closed_trade_ai_report_exists","closed_trade_ai_report_missing","all_fallback_section_count","reporter_fallback_count","missing_canonical_path_count","thin_trace_count")
    return {"base_day":str(base.get("day") or ""),"target_day":str(target.get("day") or ""),"deltas":{key:int(target.get(key) or 0)-int(base.get(key) or 0) for key in keys}}
