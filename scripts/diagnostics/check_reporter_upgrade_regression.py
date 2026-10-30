from __future__ import annotations

# Direct execution from the deeper scripts package retains repository imports.
import sys as _migration_sys
from pathlib import Path as _MigrationPath
_migration_root = _MigrationPath(__file__).resolve().parents[2]
if str(_migration_root) not in _migration_sys.path:
    _migration_sys.path.insert(0, str(_migration_root))

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


CANONICAL_ARTIFACT_KEYS: Tuple[str, ...] = (
    "canonical_commander_json",
    "canonical_strategist_json",
    "canonical_scanner_json",
    "canonical_monitor_json",
    "canonical_supervisor_json",
    "canonical_executor_json",
)


def _read_json(path: Path) -> Dict[str, Any]:
    from scripts.diagnostics.reporter_upgrade_read_projection import _read_json as owner
    return owner(path, facade=_migration_sys.modules[__name__])


def _trade_dirs_for_day(reports_root: Path, day: str) -> List[Path]:
    from scripts.diagnostics.reporter_upgrade_read_projection import _trade_dirs_for_day as owner
    return owner(reports_root, day, facade=_migration_sys.modules[__name__])


def _is_closed_trade(bundle: Dict[str, Any]) -> bool:
    from scripts.diagnostics.reporter_upgrade_state_projection import _is_closed_trade as owner
    return owner(bundle, facade=_migration_sys.modules[__name__])


def _section_provenance_all_fallback(report: Dict[str, Any]) -> bool:
    from scripts.diagnostics.reporter_upgrade_provenance_projection import _section_provenance_all_fallback as owner
    return owner(report, facade=_migration_sys.modules[__name__])


def _reporter_section_fallback(report: Dict[str, Any]) -> bool:
    from scripts.diagnostics.reporter_upgrade_state_projection import _reporter_section_fallback as owner
    return owner(report, facade=_migration_sys.modules[__name__])


def _missing_canonical_paths(bundle: Dict[str, Any]) -> bool:
    from scripts.diagnostics.reporter_upgrade_state_projection import _missing_canonical_paths as owner
    return owner(bundle, facade=_migration_sys.modules[__name__])


def _thin_trace(bundle: Dict[str, Any]) -> bool:
    from scripts.diagnostics.reporter_upgrade_trace_projection import _thin_trace as owner
    return owner(bundle, facade=_migration_sys.modules[__name__])
def analyze_day(reports_root: Path, day: str) -> Dict[str, Any]:
    from scripts.diagnostics.reporter_upgrade_analysis_projection import analyze_day as owner
    return owner(reports_root, day, facade=_migration_sys.modules[__name__])
def compare_days(base: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, Any]:
    from scripts.diagnostics.reporter_upgrade_comparison_projection import compare_days as owner
    return owner(base, target, facade=_migration_sys.modules[__name__])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check reporter upgrade regression metrics for trade artifacts.")
    parser.add_argument("--reports-root", default="reports", help="reports root directory (default: reports)")
    parser.add_argument("--day", action="append", required=True, help="target day (YYYY-MM-DD). can be repeated.")
    parser.add_argument("--json", action="store_true", help="print raw JSON output only")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    reports_root = Path(str(args.reports_root))
    days = [str(day).strip() for day in args.day if str(day).strip()]
    outputs = [analyze_day(reports_root, day) for day in days]
    payload: Dict[str, Any] = {"days": outputs}
    if len(outputs) >= 2:
        payload["comparison"] = compare_days(outputs[0], outputs[-1])

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    for item in outputs:
        print(f"[day={item['day']}] total={item['total_trades']} closed={item['closed_trades']}")
        print(
            "  closed_reports: "
            f"exists={item['closed_trade_ai_report_exists']} missing={item['closed_trade_ai_report_missing']}"
        )
        print(
            "  fallback: "
            f"all_sections={item['all_fallback_section_count']} reporter={item['reporter_fallback_count']}"
        )
        print(
            "  quality: "
            f"missing_canonical={item['missing_canonical_path_count']} thin_trace={item['thin_trace_count']}"
        )

    if "comparison" in payload:
        cmp = payload["comparison"]
        print(f"[comparison] base={cmp['base_day']} target={cmp['target_day']}")
        for key, delta in (cmp.get("deltas") or {}).items():
            sign = "+" if int(delta) > 0 else ""
            print(f"  {key}: {sign}{delta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
