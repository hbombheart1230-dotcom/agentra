"""Reporter-feedback intake and gating owned outside the Strategist graph node.

This module has no import-time I/O. Collaborators are resolved from the calling
facade to retain existing runtime replacement and fake-injection semantics.
"""
from __future__ import annotations

from typing import Any, Dict, Tuple


def load_reporter_feedback_packet(state: Dict[str, Any], policy: Dict[str, Any], *, facade: Any) -> Dict[str, Any]:
    # Resolve collaborators at call time to preserve strategist_node monkeypatch contracts.
    isolate_canonical_path_for_pytest = facade.isolate_canonical_path_for_pytest
    os = facade.os
    _resolve_state_day = facade._resolve_state_day
    build_strategist_feedback_packet = facade.build_strategist_feedback_packet
    _round_optional = facade._round_optional
    def _load_source_packet() -> Dict[str, Any]:
        src = state.get("strategist_feedback_packet")
        if not isinstance(src, dict):
            src = state.get("reporter_feedback_packet")
        if isinstance(src, dict) and src:
            return dict(src)

        reports_root = isolate_canonical_path_for_pytest(str(state.get("reports_root") or os.getenv("REPORTS_ROOT", "reports")).strip() or "reports", canonical_path="reports", isolated_name="reports")
        day = str(policy.get("reporter_feedback_day") or state.get("day") or _resolve_state_day(state)).strip()
        try:
            packet = build_strategist_feedback_packet(
                mode="strategist_feedback",
                payload={"day": day},
                reports_root=reports_root,
                day=day,
            )
        except Exception:
            return {}
        return dict(packet or {})

    def _normalize_mode(value: Any) -> str:
        mode = str(value or "").strip().lower()
        return mode if mode in {"auto", "enabled", "disabled"} else "auto"

    def _empty_feedback_packet(
        *,
        mode: str,
        mode_source: str,
        status: str,
        gate_reason: str,
        source_status: str = "",
        source_available: bool = False,
        feedback_id: str = "",
        source_day: str = "",
    ) -> Dict[str, Any]:
        return {
            "available": False,
            "status": str(status or "disabled"),
            "advisory_only": True,
            "feedback_mode": "deterministic",
            "confidence": "none",
            "insight_summary": "",
            "dominant_patterns": [],
            "blocker_analysis": [],
            "route_analysis": {},
            "recommendation": [],
            "reporter_feedback_mode": str(mode or "auto"),
            "reporter_feedback_mode_source": str(mode_source or "default_auto"),
            "consumed": False,
            "feedback_gate_reason": str(gate_reason or ""),
            "source_status": str(source_status or ""),
            "source_available": bool(source_available),
            "feedback_id": str(feedback_id or ""),
            "source_day": str(source_day or ""),
            "data_freshness": {},
        }

    def _resolve_mode() -> Tuple[str, str]:
        applied_policy = state.get("applied_policy")
        applied_policy = applied_policy if isinstance(applied_policy, dict) else {}
        applied_policy_strategist = applied_policy.get("strategist")
        applied_policy_strategist = applied_policy_strategist if isinstance(applied_policy_strategist, dict) else {}
        strategist_runtime_input = state.get("strategist_runtime_input")
        strategist_runtime_input = strategist_runtime_input if isinstance(strategist_runtime_input, dict) else {}

        candidates = [
            (
                applied_policy_strategist.get("reporter_feedback_mode"),
                str(applied_policy_strategist.get("reporter_feedback_mode_source") or "commander_applied_policy"),
                "commander_applied_policy",
            ),
            (
                applied_policy.get("reporter_feedback_mode"),
                str(applied_policy.get("reporter_feedback_mode_source") or "applied_policy_fallback"),
                "applied_policy_fallback",
            ),
            (
                state.get("reporter_feedback_mode"),
                str(state.get("reporter_feedback_mode_source") or "state_fallback"),
                "state_fallback",
            ),
            (
                strategist_runtime_input.get("reporter_feedback_mode"),
                "legacy_fallback",
                "legacy_fallback",
            ),
            (
                policy.get("reporter_feedback_mode"),
                "legacy_fallback",
                "legacy_fallback",
            ),
        ]
        for raw_value, source_hint, default_source in candidates:
            if raw_value not in (None, ""):
                return _normalize_mode(raw_value), str(source_hint or default_source)
        return "auto", "default_auto"

    feedback_mode, feedback_mode_source = _resolve_mode()
    if feedback_mode == "disabled":
        return _empty_feedback_packet(
            mode=feedback_mode,
            mode_source=feedback_mode_source,
            status="disabled",
            gate_reason="mode_disabled",
        )

    src = _load_source_packet()
    if not src:
        return _empty_feedback_packet(
            mode=feedback_mode,
            mode_source=feedback_mode_source,
            status="missing",
            gate_reason="no_packet",
        )

    out = dict(src)
    out["available"] = bool(src.get("available"))
    out["status"] = str(src.get("status") or "ok")
    out["advisory_only"] = True
    out["feedback_mode"] = str(src.get("feedback_mode") or "deterministic")
    out["confidence"] = str(src.get("confidence") or "none")
    out["insight_summary"] = str(src.get("insight_summary") or "")
    out["dominant_patterns"] = list(src.get("dominant_patterns") or [])
    out["blocker_analysis"] = list(src.get("blocker_analysis") or [])
    out["route_analysis"] = dict(src.get("route_analysis") or {})
    out["recommendation"] = [str(x or "") for x in list(src.get("recommendation") or []) if str(x or "").strip()][:4]
    out["data_freshness"] = dict(src.get("data_freshness") or {})
    out["reporter_feedback_mode"] = feedback_mode
    out["reporter_feedback_mode_source"] = feedback_mode_source
    out["source_status"] = str(src.get("status") or "ok")
    out["source_available"] = bool(src.get("available"))
    out["consumed"] = False
    out["feedback_gate_reason"] = ""

    if feedback_mode == "enabled":
        if bool(out.get("available")):
            out["consumed"] = True
            out["feedback_gate_reason"] = "mode_enabled"
            return out
        return _empty_feedback_packet(
            mode=feedback_mode,
            mode_source=feedback_mode_source,
            status="unavailable",
            gate_reason="source_unavailable",
            source_status=str(src.get("status") or "unavailable"),
            source_available=bool(src.get("available")),
            feedback_id=str(out.get("feedback_id") or ""),
            source_day=str(src.get("source_day") or ""),
        )

    freshness = out.get("data_freshness") if isinstance(out.get("data_freshness"), dict) else {}
    freshness_status = str(freshness.get("freshness_status") or "").strip().lower()
    stale = bool(freshness.get("stale")) or freshness_status == "stale"
    confidence_raw = src.get("confidence")
    confidence_text = str(confidence_raw or "none").strip().lower()
    confidence_numeric = _round_optional(confidence_raw, 4) if confidence_raw not in (None, "") else None
    confidence_ok = confidence_text in {"medium", "high"} or (
        isinstance(confidence_numeric, (int, float)) and float(confidence_numeric) >= 0.5
    )
    route_analysis = out.get("route_analysis") if isinstance(out.get("route_analysis"), dict) else {}
    route_selected_total = dict(route_analysis.get("route_selected_total") or {})
    relevant = bool(
        str(out.get("insight_summary") or "").strip()
        or list(out.get("dominant_patterns") or [])
        or list(out.get("blocker_analysis") or [])
        or list(out.get("recommendation") or [])
        or route_selected_total
        or route_analysis
    )
    if not bool(out.get("available")):
        return _empty_feedback_packet(
            mode=feedback_mode,
            mode_source=feedback_mode_source,
            status="auto_ignored",
            gate_reason="source_unavailable",
            source_status=str(src.get("status") or "unavailable"),
            source_available=False,
            feedback_id=str(out.get("feedback_id") or ""),
            source_day=str(src.get("source_day") or ""),
        )
    if stale:
        return _empty_feedback_packet(
            mode=feedback_mode,
            mode_source=feedback_mode_source,
            status="auto_ignored",
            gate_reason="stale",
            source_status=str(src.get("status") or "ok"),
            source_available=True,
            feedback_id=str(out.get("feedback_id") or ""),
            source_day=str(src.get("source_day") or ""),
        )
    if not confidence_ok:
        return _empty_feedback_packet(
            mode=feedback_mode,
            mode_source=feedback_mode_source,
            status="auto_ignored",
            gate_reason="low_confidence",
            source_status=str(src.get("status") or "ok"),
            source_available=True,
            feedback_id=str(out.get("feedback_id") or ""),
            source_day=str(src.get("source_day") or ""),
        )
    if not relevant:
        return _empty_feedback_packet(
            mode=feedback_mode,
            mode_source=feedback_mode_source,
            status="auto_ignored",
            gate_reason="not_relevant",
            source_status=str(src.get("status") or "ok"),
            source_available=True,
            feedback_id=str(out.get("feedback_id") or ""),
            source_day=str(src.get("source_day") or ""),
        )
    out["consumed"] = True
    out["feedback_gate_reason"] = "auto_accepted"
    return out

