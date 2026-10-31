from typing import Any, Dict


def _build_markdown(out: Dict[str, Any]) -> str:
    lines = [f"# Incident Timeline Reconstruction ({out.get('day')})", "", f"- ok: **{bool(out.get('ok'))}**", f"- events: **{int(out.get('events') or 0)}**", f"- runs: **{int(out.get('runs') or 0)}**", f"- incident_total: **{int(out.get('incident_total') or 0)}**", f"- recovered_incident_total: **{int(out.get('recovered_incident_total') or 0)}**", f"- unresolved_incident_total: **{int(out.get('unresolved_incident_total') or 0)}**", "", "## Trigger Totals", ""]
    trigger_total = out.get("trigger_total") if isinstance(out.get("trigger_total"), dict) else {}
    lines.extend([f"- {k}: {int(v)}" for k, v in sorted(trigger_total.items())] if trigger_total else ["- (none)"])
    lines += ["", "## Recovery Totals", ""]
    recovery_total = out.get("recovery_total") if isinstance(out.get("recovery_total"), dict) else {}
    lines.extend([f"- {k}: {int(v)}" for k, v in sorted(recovery_total.items())] if recovery_total else ["- (none)"])
    ttr = out.get("ttr_sec") if isinstance(out.get("ttr_sec"), dict) else {}
    lines += ["", "## Time To Recovery (sec)", "", f"- count: {int(float(ttr.get('count') or 0.0))}", f"- avg: {float(ttr.get('avg') or 0.0):.3f}", f"- p50: {float(ttr.get('p50') or 0.0):.3f}", f"- p95: {float(ttr.get('p95') or 0.0):.3f}", f"- max: {float(ttr.get('max') or 0.0):.3f}", "", "## Failures", ""]
    failures = out.get("failures") if isinstance(out.get("failures"), list) else []
    lines.extend([f"- {msg}" for msg in failures] if failures else ["- (none)"])
    lines.append("")
    return "\n".join(lines)
