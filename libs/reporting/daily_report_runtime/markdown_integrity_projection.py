"""Daily report markdown trade report integrity section (moved verbatim from daily_report_runtime.markdown).

``json`` is resolved on ``facade`` (the markdown module) at call time; this module never imports it.
Pure formatting; no IO.
"""
from __future__ import annotations

from typing import Any, Dict, List


def render_trade_report_integrity(payload: Dict[str, Any], *, facade: Any) -> List[str]:
    integrity = payload.get("trade_report_integrity") if isinstance(payload.get("trade_report_integrity"), dict) else {}
    if not integrity:
        return []
    missing = integrity.get("missing") if isinstance(integrity.get("missing"), list) else []
    broker_closed_report_open = (
        integrity.get("broker_closed_report_open")
        if isinstance(integrity.get("broker_closed_report_open"), list)
        else []
    )
    lines = [
        "",
        "## Trade Report Integrity",
        "",
        f"- status: **{str(integrity.get('status') or 'unknown').upper()}**",
        f"- expected_trade_count: **{int(integrity.get('expected_trade_count') or 0)}**",
        f"- summary_md_count: **{int(integrity.get('summary_md_count') or 0)}**",
        f"- summary_json_count: **{int(integrity.get('summary_json_count') or 0)}**",
        f"- summary_input_count: **{int(integrity.get('summary_input_count') or 0)}**",
        f"- missing_count: **{int(integrity.get('missing_count') or 0)}**",
        f"- broker_closed_report_open_count: **{int(integrity.get('broker_closed_report_open_count') or 0)}**",
    ]
    for row in broker_closed_report_open[:10]:
        if not isinstance(row, dict):
            continue
        lines.append(
            f"- broker closed but report open `{row.get('trade_id') or '-'}` {row.get('symbol') or ''}: "
            f"status=`{row.get('lifecycle_status') or 'unknown'}`"
        )
    for row in missing[:10]:
        if not isinstance(row, dict):
            continue
        lines.append(
            f"- missing `{row.get('trade_id') or '-'}` {row.get('symbol') or ''}: "
            f"`{facade.json.dumps(row.get('missing') or [], ensure_ascii=False)}`"
        )
    return lines
