from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

from libs.reporting.q8_evaluation_contract import TRUSTED_FORWARD_MIN_COVERAGE
from libs.reporting import q8_historical_projection_fast06 as _proj
from libs.reporting import q8_review_render_fast06 as _render
from libs.reporting.q8_review_render_fast06 import render_q8_lane_decision_table_markdown
from libs.reporting.quant_shadow_candidate_evaluation import (
    build_quant_shadow_candidate_evaluation,
    load_quant_shadow_candidate_payloads,
)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return float(default)
        return float(value)
    except Exception:
        return float(default)


def _int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, ""):
            return int(default)
        return int(float(value))
    except Exception:
        return int(default)


_rows = _proj.lane_rows
_counts_by_name = _proj.lane_counts_by_name
_reason_summary = _proj.lane_reason_summary


def _forward_rows(evaluation: Mapping[str, Any]) -> List[Dict[str, Any]]:
    forward = evaluation.get("entry_lane_forward_outcomes")
    if not isinstance(forward, Mapping):
        return []
    return _rows(forward.get("by_primary_lane"))


def _verdict(row: Mapping[str, Any], *, promotion_allowed: bool) -> Dict[str, str]:
    observed = _int(row.get("observed_count"))
    coverage = _float(row.get("coverage"))
    ret5 = _float(row.get("avg_return_5m_pct"))
    ret15 = _float(row.get("avg_return_15m_pct"))
    mfe5 = _float(row.get("avg_mfe_5m_pct"))
    mae5 = _float(row.get("avg_mae_5m_pct"))
    lane = _text(row.get("name"))

    if not promotion_allowed:
        return {
            "verdict": "TRUST_GATE_BLOCKED",
            "decision": "retain under observation",
            "rationale": "Q8 trust gate blocked promotion review; lane signal is diagnostic only.",
        }
    if observed < 10 or coverage < TRUSTED_FORWARD_MIN_COVERAGE:
        return {
            "verdict": "DATA_INCOMPLETE",
            "decision": "observe",
            "rationale": "sample or trusted forward coverage is insufficient.",
        }
    if lane == "vwap_reclaim" and ret5 < 0.0 and ret15 < 0.0:
        return {
            "verdict": "GOOD_BLOCK",
            "decision": "keep blocked",
            "rationale": "VWAP reclaim lane showed weak short/mid forward returns.",
        }
    if ret5 >= 0.50 or ret15 >= 0.80 or mfe5 >= 1.50:
        risk_note = " MAE is high, so only small probe or rule review is allowed." if mae5 <= -1.50 else ""
        return {
            "verdict": "MISSED_OPPORTUNITY",
            "decision": "relaxation candidate",
            "rationale": f"Blocked candidates showed positive forward potential.{risk_note}".strip(),
        }
    if ret5 <= 0.0 and ret15 <= 0.0:
        return {
            "verdict": "GOOD_BLOCK",
            "decision": "keep blocked",
            "rationale": "Blocked candidates showed weak forward returns.",
        }
    return {
        "verdict": "DATA_INCOMPLETE",
        "decision": "observe",
        "rationale": "Signal direction is not decisive enough for a policy review.",
    }


def build_q8_lane_decision_table(
    *,
    reports_root: Path = Path("reports"),
    day: str,
) -> Dict[str, Any]:
    payloads = load_quant_shadow_candidate_payloads(reports_root=reports_root, days=[str(day)[:10]])
    evaluation = build_quant_shadow_candidate_evaluation(payloads)
    return _proj.lane_table_payload(evaluation, day=day, verdict=_verdict)


_fmt_pct = _render._lane_fmt_pct


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
