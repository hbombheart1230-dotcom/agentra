"""Report source commander route projections (moved verbatim from report_source_helpers).

``_commander_route_from_payload`` is resolved on ``facade`` (the report_source_helpers module) at call time; this module never imports it.
Pure functions; no IO.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable


def _commander_route_from_payload(payload: Dict[str, Any], *, artifact_path: str = "") -> Dict[str, Any]:
    route_obs = payload.get("route_observability") if isinstance(payload.get("route_observability"), dict) else {}
    commander_decision = payload.get("commander_decision") if isinstance(payload.get("commander_decision"), dict) else {}
    route_selected = str(
        payload.get("route_selected")
        or payload.get("selected_route")
        or route_obs.get("route_selected")
        or commander_decision.get("route_selected")
        or ""
    ).strip()
    return {
        "route_selected": route_selected,
        "strategy_generation_mode": str(
            payload.get("strategy_generation_mode")
            or route_obs.get("strategy_generation_mode")
            or commander_decision.get("strategy_generation_mode")
            or ""
        ).strip(),
        "strategist_call_decision": str(
            payload.get("strategist_call_decision")
            or route_obs.get("strategist_call_decision")
            or commander_decision.get("strategist_call_decision")
            or ""
        ).strip(),
        "strategist_fallback_used": bool(
            payload.get("strategist_fallback_used")
            if payload.get("strategist_fallback_used") is not None
            else route_obs.get("fallback_used")
            if route_obs.get("fallback_used") is not None
            else commander_decision.get("strategist_fallback_used")
        ),
        "route_source": "canonical_commander" if artifact_path else "",
        "artifact_path": artifact_path,
    }


def _event_route_rows(day_rows: Iterable[Dict[str, Any]], *, facade: Any) -> Dict[str, Dict[str, Any]]:
    # OOM RCA follow-up (2026-09-23): folds directly off the iterator in
    # file/stream order instead of pre-sorting a materialized day_rows list
    # -- see _build_run_contexts's own comment in operator_visibility.py
    # for why file order is already chronological order in this system,
    # and why per-run same-stage-repeat re-ordering isn't a real concern.
    by_run: Dict[str, Dict[str, Any]] = {}
    for row in day_rows:
        run_id = str(row.get("run_id") or "").strip()
        if not run_id:
            continue
        stage = str(row.get("stage") or "").strip()
        event = str(row.get("event") or "").strip()
        route_event = stage == "commander_router" and event in {"route_selected", "end", "route"}
        policy_event = stage == "strategist" and event == "policy_resolution"
        if not (route_event or policy_event):
            continue
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        current = by_run.setdefault(
            run_id,
            {
                "route_selected": "",
                "strategy_generation_mode": "",
                "strategist_call_decision": "",
                "strategist_fallback_used": False,
                "route_source": "event_fallback",
                "artifact_path": "",
            },
        )
        if route_event:
            merged = facade._commander_route_from_payload(payload)
            for key in ("route_selected", "strategy_generation_mode", "strategist_call_decision"):
                if merged.get(key):
                    current[key] = merged[key]
            if merged.get("strategist_fallback_used"):
                current["strategist_fallback_used"] = True
        if policy_event:
            mode = str(payload.get("strategy_generation_mode") or "").strip()
            if mode:
                current["strategy_generation_mode"] = mode
            if bool(payload.get("fallback_used")):
                current["strategist_fallback_used"] = True
    return by_run
