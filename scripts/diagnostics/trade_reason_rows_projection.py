from __future__ import annotations
from collections import Counter
from typing import Any, Dict, List

def _build_rows(
    events: List[Dict[str, Any]],
    *,
    run_id_filter: str = "",
    action_filter: str = "",
    only_broker_success: bool = False,
    facade: Any = None) -> List[Dict[str, Any]]:
    by_run: Dict[str, Dict[str, Any]] = {}
    out: List[Dict[str, Any]] = []
    execution_counts = Counter(str(rec.get("run_id") or "").strip() for rec in events
                               if rec.get("stage") == "execute_from_packet" and rec.get("event") == "execution")

    for rec in events:
        run_id = str(rec.get("run_id") or "").strip()
        if not run_id:
            continue
        if run_id not in by_run:
            by_run[run_id] = {}
        ctx = by_run[run_id]

        stage = str(rec.get("stage") or "").strip()
        event = str(rec.get("event") or "").strip()
        payload = rec.get("payload") if isinstance(rec.get("payload"), dict) else {}

        if stage == "strategist_llm" and event == "result":
            intent_id = facade._event_intent_id(payload)
            if intent_id is not None:
                ctx.setdefault("llm", {})[intent_id] = payload
            continue

        if stage == "decision" and event == "trace":
            intent_id = facade._event_intent_id(payload)
            if intent_id is not None:
                ctx.setdefault("decision", {})[intent_id] = payload
            continue

        if stage == "execute_from_packet" and event == "verdict":
            intent_id = facade._event_intent_id(payload)
            if intent_id is not None:
                ctx.setdefault("verdict", {})[intent_id] = payload
            continue

        if stage == "execute_from_packet" and event == "execution":
            order = payload.get("order") if isinstance(payload.get("order"), dict) else {}
            ex_payload = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
            action = str(order.get("action") or "").strip().upper()
            if action not in ("BUY", "SELL"):
                continue

            if run_id_filter and run_id != run_id_filter:
                continue
            if action_filter and action != action_filter:
                continue

            broker_ok = facade._broker_code_success(ex_payload.get("broker_code"))
            if only_broker_success and broker_ok is not True:
                continue

            intent_id = facade._event_intent_id(payload)

            def context(kind: str) -> Dict[str, Any]:
                candidates = ctx.get(kind, {})
                if intent_id:
                    return candidates.get(intent_id, {})
                # Preserve legacy single-execution decision/LLM context only.
                # Verdict attribution always requires a matching explicit ID.
                if (intent_id == "" and kind != "verdict" and execution_counts[run_id] == 1
                        and set(candidates) == {""}):
                    return candidates[""]
                return {}

            llm = context("llm")
            decision = context("decision")
            decision_trace = decision.get("trace") if isinstance(decision.get("trace"), dict) else {}
            decision_packet = decision.get("decision_packet") if isinstance(decision.get("decision_packet"), dict) else {}
            decision_intent = decision_packet.get("intent") if isinstance(decision_packet.get("intent"), dict) else {}
            verdict = context("verdict")
            decision_rationale = str(decision_trace.get("rationale") or "")
            if not decision_rationale:
                decision_rationale = str(decision_intent.get("rationale") or "")
            llm_intent_rationale = str(llm.get("intent_rationale") or "")
            if not decision_rationale and llm_intent_rationale:
                decision_rationale = llm_intent_rationale

            row = {
                "ts": str(rec.get("ts") or ""),
                "run_id": run_id,
                "action": action,
                "symbol": str(order.get("symbol") or ""),
                "qty": order.get("qty"),
                "price": order.get("price"),
                "order_type": order.get("order_type"),
                "execution_reason": str(payload.get("reason") or ""),
                "allowed": payload["allowed"] if "allowed" in payload else verdict.get("allowed"),
                "verdict_reason": str(verdict.get("reason") or ""),
                "broker_code": str(ex_payload.get("broker_code") or ""),
                "broker_ok": broker_ok,
                "broker_message": str(ex_payload.get("broker_message") or ""),
                "order_id": str(ex_payload.get("order_id") or ""),
                "decision_strategy": str(decision_trace.get("strategy") or ""),
                "decision_rationale": decision_rationale,
                "decision_reason": str(decision_intent.get("reason") or ""),
                "llm_provider": str(llm.get("provider") or ""),
                "llm_model": str(llm.get("model") or ""),
                "llm_ok": llm.get("ok"),
                "llm_intent_action": str(llm.get("intent_action") or ""),
                "llm_intent_reason": str(llm.get("intent_reason") or ""),
                "llm_intent_rationale": llm_intent_rationale,
                "llm_latency_ms": llm.get("latency_ms"),
            }
            out.append(row)

    return out


