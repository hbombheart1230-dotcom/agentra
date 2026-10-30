from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
def analyze_day(reports_root: Path, day: str, *, facade: Any) -> Dict[str, Any]:
    trade_dirs=facade._trade_dirs_for_day(reports_root,day); metrics={"day":day,"total_trades":0,"closed_trades":0,"closed_trade_ai_report_exists":0,"closed_trade_ai_report_missing":0,"all_fallback_section_count":0,"reporter_fallback_count":0,"missing_canonical_path_count":0,"thin_trace_count":0}
    for trade_dir in trade_dirs:
        metrics["total_trades"]+=1; bundle=facade._read_json(trade_dir/"lifecycle_bundle.json"); report=facade._read_json(trade_dir/"reports"/"ai_trade_report.json")
        if facade._missing_canonical_paths(bundle): metrics["missing_canonical_path_count"]+=1
        if facade._thin_trace(bundle): metrics["thin_trace_count"]+=1
        if not facade._is_closed_trade(bundle): continue
        metrics["closed_trades"]+=1
        if report:
            metrics["closed_trade_ai_report_exists"]+=1
            if facade._section_provenance_all_fallback(report): metrics["all_fallback_section_count"]+=1
            if facade._reporter_section_fallback(report): metrics["reporter_fallback_count"]+=1
        else: metrics["closed_trade_ai_report_missing"]+=1
    closed=max(1,int(metrics["closed_trades"])); metrics["ratios"]={"closed_trade_ai_report_exists_ratio":float(metrics["closed_trade_ai_report_exists"])/float(closed),"all_fallback_section_ratio":float(metrics["all_fallback_section_count"])/float(closed),"reporter_fallback_ratio":float(metrics["reporter_fallback_count"])/float(closed)}
    return metrics
