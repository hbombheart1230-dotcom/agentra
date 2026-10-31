from __future__ import annotations
from collections import Counter
from typing import Any, Dict, List
def _extract_noop_reason(payload: Dict[str, Any], *, facade: Any) -> str:
    packet=payload.get("decision_packet") if isinstance(payload.get("decision_packet"),dict) else {};intent=packet.get("intent") if isinstance(packet.get("intent"),dict) else {};reason=str(intent.get("reason") or "").strip()
    if reason:return reason
    trace=payload.get("trace") if isinstance(payload.get("trace"),dict) else {};raw=trace.get("raw_intent") if isinstance(trace.get("raw_intent"),dict) else {};return str(raw.get("reason") or "").strip() or "unknown"

def _build_summary(rows: List[Dict[str, Any]], *, day: str, facade: Any) -> Dict[str, Any]:
    run_ids = {str(r.get("run_id") or "") for r in rows if str(r.get("run_id") or "").strip()}

    verdict_reason_total: Counter[str] = Counter()
    broker_code_total: Counter[str] = Counter()
    broker_failure_total: Counter[str] = Counter()
    noop_reason_total: Counter[str] = Counter()
    llm_latency_ms: List[float] = []
    llm_total = 0
    llm_ok_total = 0
    llm_error_total = 0
    execution_total = 0
    verdict_block_total = 0
    broker_success_total = 0
    broker_fail_total = 0
    broker_unknown_total = 0

    for r in rows:
        stage = str(r.get("stage") or "")
        event = str(r.get("event") or "")
        payload = r.get("payload") if isinstance(r.get("payload"), dict) else {}

        if stage == "execute_from_packet" and event == "verdict":
            if payload.get("allowed") is False:
                verdict_block_total += 1
                reason = str(payload.get("reason") or "").strip() or "unknown"
                verdict_reason_total[reason] += 1

        if stage == "execute_from_packet" and event == "execution":
            execution_total += 1
            ex_payload = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
            bcode = str(ex_payload.get("broker_code") or "").strip()
            if bcode:
                broker_code_total[bcode] += 1
            b_ok = facade._broker_code_success(ex_payload.get("broker_code"))
            if b_ok is None:
                if "api_ok" in ex_payload:
                    b_ok = bool(ex_payload.get("api_ok"))
                else:
                    broker_unknown_total += 1
            if b_ok is True:
                broker_success_total += 1
            elif b_ok is False:
                broker_fail_total += 1
                k = bcode or "unknown"
                broker_failure_total[k] += 1

        if stage == "decision" and event == "trace":
            packet = payload.get("decision_packet") if isinstance(payload.get("decision_packet"), dict) else {}
            intent = packet.get("intent") if isinstance(packet.get("intent"), dict) else {}
            action = str(intent.get("action") or "").strip().upper()
            if action == "NOOP":
                noop_reason_total[facade._extract_noop_reason(payload)] += 1

        if stage == "strategist_llm" and event == "result":
            llm_total += 1
            if payload.get("ok") is True:
                llm_ok_total += 1
            else:
                llm_error_total += 1
            lat = facade._to_float(payload.get("latency_ms"))
            if lat is not None and lat >= 0.0:
                llm_latency_ms.append(float(lat))

    noop_total = int(sum(noop_reason_total.values()))
    noop_reason_ratio = {
        str(k): (float(v) / float(noop_total) if noop_total > 0 else 0.0)
        for k, v in noop_reason_total.items()
    }
    focus_noop_reasons = ("model_no_signal", "missing_rationale", "post_exit_cooldown")
    focus_ratio = {k: float(noop_reason_ratio.get(k, 0.0)) for k in focus_noop_reasons}

    out = {
        "schema_version": "ops_diagnostic.v1",
        "day": day,
        "events": int(len(rows)),
        "runs": int(len(run_ids)),
        "execution": {
            "execution_total": int(execution_total),
            "verdict_block_total": int(verdict_block_total),
            "verdict_reason_topN": [
                {"reason": str(reason), "count": int(cnt)}
                for reason, cnt in verdict_reason_total.most_common(10)
            ],
            "broker_success_total": int(broker_success_total),
            "broker_fail_total": int(broker_fail_total),
            "broker_unknown_total": int(broker_unknown_total),
            "broker_success_rate": (
                float(broker_success_total) / float(execution_total) if execution_total > 0 else 0.0
            ),
            "broker_code_topN": [
                {"broker_code": str(code), "count": int(cnt)}
                for code, cnt in broker_code_total.most_common(10)
            ],
            "broker_failure_topN": [
                {"broker_code": str(code), "count": int(cnt)}
                for code, cnt in broker_failure_total.most_common(10)
            ],
        },
        "noop": {
            "total": int(noop_total),
            "reason_total": {str(k): int(v) for k, v in noop_reason_total.items()},
            "reason_ratio": {str(k): float(v) for k, v in noop_reason_ratio.items()},
            "focus_reason_ratio": focus_ratio,
        },
        "strategist_llm": {
            "total": int(llm_total),
            "ok_total": int(llm_ok_total),
            "error_total": int(llm_error_total),
            "latency_ms": facade._numeric_summary(llm_latency_ms),
        },
    }
    return out

