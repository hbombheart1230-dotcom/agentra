from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from libs.reporting.llm_artifacts import iter_trade_dirs as _iter_trade_dirs_under_day


def _read_json(path: Path) -> Dict[str, Any]:
    from scripts.diagnostics.reports_trades_health_read_projection import _read_json as owner
    return owner(path, facade=sys.modules[__name__])


def _iter_trade_dirs(reports_root: Path, day: str = "") -> List[Path]:
    from scripts.diagnostics.reports_trades_health_read_projection import _iter_trade_dirs as owner
    return owner(reports_root, day, facade=sys.modules[__name__])


def _artifact_path(trade_dir: Path, *candidates: str) -> Path:
    from scripts.diagnostics.reports_trades_health_read_projection import _artifact_path as owner
    return owner(trade_dir, *candidates, facade=sys.modules[__name__])


def _issue(
    *,
    severity: str,
    trade_id: str,
    component: str,
    code: str,
    message: str,
    path: Path,
) -> Dict[str, Any]:
    from scripts.diagnostics.reports_trades_health_issue_projection import _issue as owner
    return owner(severity=severity, trade_id=trade_id, component=component, code=code, message=message, path=path, facade=sys.modules[__name__])


def _ai_trade_report_is_complete(trade_dir: Path) -> bool:
    from scripts.diagnostics.reports_trades_health_read_projection import _ai_trade_report_is_complete as owner
    return owner(trade_dir, facade=sys.modules[__name__])


def audit_reports_trades_health(reports_root: Path, *, day: str = "") -> Dict[str, Any]:
    from scripts.diagnostics.reports_trades_health_audit_projection import audit_reports_trades_health as owner
    return owner(reports_root, day=day, facade=sys.modules[__name__])
def _build_parser() -> argparse.ArgumentParser:
    from scripts.diagnostics.reports_trades_health_cli import _build_parser as owner
    return owner(facade=sys.modules[__name__])


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    reports_root = Path(str(args.reports_root).strip() or "reports")
    if not reports_root.is_absolute():
        reports_root = ROOT / reports_root
    out = audit_reports_trades_health(reports_root, day=str(args.day).strip())
    if bool(args.json):
        print(json.dumps(out, ensure_ascii=False))
    else:
        print(
            f"ok={out['ok']} trade_dir_count={out['trade_dir_count']} "
            f"issue_counts={json.dumps(out['issue_counts'], ensure_ascii=False)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
