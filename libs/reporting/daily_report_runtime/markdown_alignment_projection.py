"""Daily report markdown broker alignment section (moved verbatim from daily_report_runtime.markdown).

Pure formatting; no IO.
"""
from __future__ import annotations

from typing import Any, Dict, List


def render_broker_alignment(payload: Dict[str, Any]) -> List[str]:
    alignment = payload.get("broker_alignment") if isinstance(payload.get("broker_alignment"), dict) else {}
    if not alignment:
        return []
    summary = alignment.get("summary") if isinstance(alignment.get("summary"), dict) else {}
    status = str(alignment.get("status") or "unknown")
    lines = [
        "",
        "## Broker Alignment",
        "",
        f"- status: **{status.upper()}**",
        f"- generated_at: `{alignment.get('generated_at') or '-'}`",
        f"- local_total: **{int(summary.get('local_total') or 0)}**",
        f"- broker_total: **{int(summary.get('broker_total') or 0)}**",
        f"- matched_by_ord_no: **{int(summary.get('matched_by_ord_no') or 0)}**",
        f"- missing_in_local: **{int(summary.get('missing_in_local_total') or 0)}**",
        f"- missing_in_broker: **{int(summary.get('missing_in_broker_total') or 0)}**",
    ]
    if alignment.get("error"):
        lines.append(f"- error: `{alignment.get('error')}`")
    if alignment.get("report_json_path"):
        lines.append(f"- report_json: `{alignment.get('report_json_path')}`")
    snapshot = alignment.get("account_snapshot") if isinstance(alignment.get("account_snapshot"), dict) else {}
    if snapshot:
        closed_symbols = snapshot.get("day_trade_closed_symbols") if isinstance(snapshot.get("day_trade_closed_symbols"), list) else []
        lines.append(f"- account_snapshot_status: **{str(snapshot.get('status') or 'unknown').upper()}**")
        if snapshot.get("path"):
            lines.append(f"- account_snapshot_json: `{snapshot.get('path')}`")
        if snapshot.get("api_call_count") not in (None, ""):
            lines.append(
                f"- account_snapshot_calls: **{int(snapshot.get('ok_count') or 0)}"
                f"/{int(snapshot.get('api_call_count') or 0)} ok**"
            )
        lines.append(f"- day_trade_diary_count: **{int(snapshot.get('day_trade_diary_count') or 0)}**")
        if closed_symbols:
            lines.append(f"- day_trade_closed_symbols: `{', '.join(str(x) for x in closed_symbols)}`")
        if snapshot.get("error"):
            lines.append(f"- account_snapshot_error: `{snapshot.get('error')}`")
    for title, key in (("missing broker-only rows", "missing_in_local"), ("missing local-only rows", "missing_in_broker")):
        rows = summary.get(key) if isinstance(summary.get(key), list) else []
        if not rows:
            continue
        lines.append(f"- {title}:")
        for row in rows[:5]:
            if not isinstance(row, dict):
                continue
            lines.append(
                f"  - ord_no={row.get('ord_no') or '-'} symbol={row.get('symbol') or '-'} "
                f"side={row.get('side') or '-'} qty={row.get('filled_qty') or row.get('qty') or row.get('order_qty') or 0}"
            )
    return lines
