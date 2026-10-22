from __future__ import annotations

import json
import sys as _sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

from libs.reporting.evaluation.q8_shadow_readout_p15 import (  # noqa: F401 - facade ABI re-exports
    _counts_by_name_impl,
    _float,
    _forward_rows_impl,
    _int,
    _reason_summary_impl,
    _rows,
    _text,
    _verdict_impl,
    lane_decision_table_payload_impl,
)
from libs.reporting.q8_evaluation_contract import TRUSTED_FORWARD_MIN_COVERAGE
from libs.reporting.quant_shadow_candidate_evaluation import (
    build_quant_shadow_candidate_evaluation,
    load_quant_shadow_candidate_payloads,
)


def _forward_rows(evaluation: Mapping[str, Any]) -> List[Dict[str, Any]]:
    return _forward_rows_impl(evaluation, facade=_sys.modules[__name__])


def _counts_by_name(rows: Iterable[Mapping[str, Any]]) -> Dict[str, int]:
    return _counts_by_name_impl(rows, facade=_sys.modules[__name__])


def _reason_summary(evaluation: Mapping[str, Any], *, limit: int = 6) -> str:
    return _reason_summary_impl(evaluation, limit=limit, facade=_sys.modules[__name__])


def _verdict(row: Mapping[str, Any], *, promotion_allowed: bool) -> Dict[str, str]:
    return _verdict_impl(row, promotion_allowed=promotion_allowed, facade=_sys.modules[__name__])


def build_q8_lane_decision_table(
    *,
    reports_root: Path = Path("reports"),
    day: str,
) -> Dict[str, Any]:
    payloads = load_quant_shadow_candidate_payloads(reports_root=reports_root, days=[str(day)[:10]])
    evaluation = build_quant_shadow_candidate_evaluation(payloads)
    return lane_decision_table_payload_impl(evaluation, day=day, facade=_sys.modules[__name__])


def _fmt_pct(value: Any) -> str:
    if value in (None, ""):
        return "-"
    return f"{_float(value):.4f}%"


def render_q8_lane_decision_table_markdown(payload: Mapping[str, Any]) -> str:
    gate = payload.get("evaluation_trust_gate") if isinstance(payload.get("evaluation_trust_gate"), Mapping) else {}
    lines = [
        f"# Q8 Lane Decision Table - {payload.get('day')}",
        "",
        "## Summary",
        "",
        f"- payloads: {payload.get('payload_count')}",
        f"- candidates: {payload.get('candidate_count')}",
        f"- deduped candidates: {payload.get('deduped_candidate_count')}",
        f"- duplicates: {payload.get('duplicate_candidate_count')}",
        f"- dedupe_key: `{', '.join(list(payload.get('dedupe_key') or []))}`",
        f"- evaluated: {payload.get('evaluated_count')}",
        f"- forward observed: {payload.get('forward_outcome_available_count')} "
        f"({float(payload.get('forward_outcome_coverage') or 0.0):.1%})",
        f"- trust_gate: `{gate.get('status') or '-'}`",
        f"- promotion_allowed: `{bool(gate.get('promotion_allowed'))}`",
        f"- trust_block_reasons: `{', '.join(list(gate.get('block_reasons') or gate.get('reasons') or [])) or '-'}`",
        f"- would-enter: {payload.get('would_enter_count')}",
        f"- top reasons: {payload.get('reason_summary') or '-'}",
        "",
        "## Lane Verdicts",
        "",
        "| Lane | Verdict | Decision | n | obs | +5m | +15m | +30m | MFE5 | MAE5 | Rationale |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in _rows(payload.get("rows")):
        lines.append(
            "| "
            + " | ".join(
                [
                    _text(row.get("lane")) or "-",
                    _text(row.get("verdict")) or "-",
                    _text(row.get("decision")) or "-",
                    str(row.get("candidate_count") or 0),
                    str(row.get("observed_count") or 0),
                    _fmt_pct(row.get("avg_return_5m_pct")),
                    _fmt_pct(row.get("avg_return_15m_pct")),
                    _fmt_pct(row.get("avg_return_30m_pct")),
                    _fmt_pct(row.get("avg_mfe_5m_pct")),
                    _fmt_pct(row.get("avg_mae_5m_pct")),
                    _text(row.get("rationale")) or "-",
                ]
            )
            + " |"
        )
    lines += [
        "",
        "## Operating Interpretation",
        "",
        "- `TRUST_GATE_BLOCKED`: lane signal is visible, but Q8 evidence is not eligible for policy promotion.",
        "- `MISSED_OPPORTUNITY`: blocked candidates rose afterward. This is a review target, not direct permission to buy.",
        "- `GOOD_BLOCK`: blocked candidates underperformed after the block. Keep the gate under observation.",
        "- `DATA_INCOMPLETE`: sample or coverage is insufficient for a policy conclusion.",
        "",
        "## Current Action",
        "",
        "No new behavior patch is implied by this table unless the Q8 trust gate allows promotion review.",
        "",
    ]
    return "\n".join(lines)


def write_q8_lane_decision_table(
    *,
    reports_root: Path = Path("reports"),
    docs_root: Path = Path("docs/tactics"),
    day: str,
) -> Dict[str, Any]:
    payload = build_q8_lane_decision_table(reports_root=reports_root, day=day)
    docs_root.mkdir(parents=True, exist_ok=True)
    md_path = docs_root / f"q8_lane_decision_table_{str(day)[:10]}.md"
    json_dir = reports_root / "dev" / "analysis" / "q8_lane_decision_table"
    json_dir.mkdir(parents=True, exist_ok=True)
    json_path = json_dir / f"q8_lane_decision_table_{str(day)[:10]}.json"
    md_path.write_text(render_q8_lane_decision_table_markdown(payload), encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return {"ok": True, "payload": payload, "md_path": str(md_path), "json_path": str(json_path)}


__all__ = [
    "build_q8_lane_decision_table",
    "render_q8_lane_decision_table_markdown",
    "write_q8_lane_decision_table",
]
