"""Commander output route/runtime context facts.

T3.5 (P1.5 Third Pass): contiguous statement runs / dict item ranges of `libs/contracts/agent_outputs.py::build_commander_output_artifact` moved verbatim into
contract-owned projection stages. Locals enter as explicit parameters and leave as the returned record or dict; value
helpers are imported from `libs.contracts.agent_output_values`; remaining module globals of the public facade are
resolved at use time as `facade.NAME`. Final artifact assembly and `validate_artifact` stay in the public builder.
"""
from __future__ import annotations

from typing import Any, NamedTuple

from libs.contracts.agent_output_values import (
    _clip,
    _dedupe_text,
    _dict,
    _listify,
    _safe_int,
)


class CommanderRouteRuntimeFacts(NamedTuple):
    """Result of `commander_route_runtime_facts` (positional order is the pre-T3.5 tuple order)."""

    allowed_playbooks: Any
    banned_playbooks: Any
    commander_decision: Any
    commander_market_regime: Any
    commander_risk_mode: Any
    commander_session_bias: Any
    cooldown_applied: Any
    cooldown_until_epoch: Any
    decision_frame: Any
    handoff_instruction: Any
    open_symbols: Any
    phase_text: Any
    portfolio_snapshot: Any
    positions: Any
    preflight: Any
    resilience: Any
    route_reason_codes: Any
    runtime_fast_path: Any
    runtime_plan: Any
    selected_route: Any
    shadow_assessment: Any
    strategist_blocked: Any
    strategist_cache_used: Any
    strategist_output: Any

def commander_route_runtime_facts(state, mode, phase, path, status, reason, *, facade):
    decision_frame = _dict(state.get("commander_decision_frame"))
    commander_decision = _dict(state.get("commander_decision"))
    shadow_assessment = facade._build_commander_shadow_artifact_summary(
        state,
        mode=mode,
        phase=phase,
        path=path,
        status=status,
        reason=reason,
    )
    runtime_plan = _dict(state.get("runtime_plan"))
    runtime_fast_path = _dict(state.get("runtime_fast_path"))
    resilience = _dict(state.get("runtime_resilience_state"))
    if not resilience:
        resilience = _dict(state.get("resilience"))
    strategist_output = _dict(state.get("strategist_output"))
    portfolio_snapshot = _dict(state.get("portfolio_snapshot"))
    preflight = _dict(state.get("portfolio_preflight"))
    positions = [row for row in list(portfolio_snapshot.get("positions") or []) if isinstance(row, dict)]
    open_symbols = _dedupe_text([str(row.get("symbol") or "").strip() for row in positions], limit=12, max_len=32)
    status_text = str(status or "ok")
    runtime_status = _clip(state.get("runtime_status"), max_len=80)
    path_text = str(path or "").strip()
    phase_text = str(phase or "").strip()
    selected_route = "full_cycle"
    if "monitor_only" in path_text:
        selected_route = "monitor_only"
    elif "cached" in path_text:
        selected_route = "cached_strategist"
    elif phase_text == "preopen" or "preopen" in path_text:
        selected_route = "preopen"
    elif phase_text == "closeout" or "closeout" in path_text:
        selected_route = "closeout"
    elif "blocked" in path_text or status_text in {"blocked", "preflight_blocked"}:
        selected_route = "blocked"
    elif runtime_status in {"error", "cooldown_wait", "degraded"}:
        selected_route = "degraded"
    route_reason_codes = _dedupe_text(
        [
            _clip(reason, max_len=120),
            _clip(runtime_status, max_len=120),
            _clip(state.get("runtime_transition"), max_len=120),
            _clip(runtime_fast_path.get("reason"), max_len=120),
            "portfolio_preflight_blocked" if bool(preflight.get("blocked")) else "",
            "strategist_blocked" if bool(state.get("strategist_blocked")) else "",
        ],
        limit=8,
        max_len=120,
    )
    cooldown_until_epoch = _safe_int(resilience.get("cooldown_until_epoch"), 0)
    cooldown_applied = (
        _clip(state.get("runtime_transition"), max_len=40) == "cooldown"
        or runtime_status == "cooldown_wait"
        or cooldown_until_epoch > 0
    )
    strategist_cache_used = selected_route == "cached_strategist" or bool(runtime_fast_path.get("cache_age_sec"))
    strategist_blocked = (
        bool(state.get("strategist_blocked"))
        or bool(strategist_output.get("llm_frame_blocked"))
        or ("strategist_blocked" in path_text)
    )
    handoff_instruction = _clip(
        decision_frame.get("handoff_instruction")
        or ("Proceed with planned agent chain." if status_text in {"ok", "ready", "preopen_ready", "closeout_ready"} else "Stop downstream execution and inspect runtime status."),
        max_len=220,
    )
    commander_market_regime = _clip(
        commander_decision.get("market_regime")
        or _dict(decision_frame.get("market_regime_summary")).get("market_regime")
        or strategist_output.get("market_regime"),
        max_len=80,
    )
    commander_session_bias = _clip(
        commander_decision.get("session_bias")
        or decision_frame.get("session_type")
        or phase,
        max_len=80,
    )
    commander_risk_mode = _clip(commander_decision.get("risk_mode"), max_len=80)
    allowed_playbooks = _listify(commander_decision.get("allowed_playbooks"), limit=6, max_len=40)
    banned_playbooks = _listify(commander_decision.get("banned_playbooks"), limit=6, max_len=40)
    return CommanderRouteRuntimeFacts(allowed_playbooks, banned_playbooks, commander_decision, commander_market_regime, commander_risk_mode, commander_session_bias, cooldown_applied, cooldown_until_epoch, decision_frame, handoff_instruction, open_symbols, phase_text, portfolio_snapshot, positions, preflight, resilience, route_reason_codes, runtime_fast_path, runtime_plan, selected_route, shadow_assessment, strategist_blocked, strategist_cache_used, strategist_output)
