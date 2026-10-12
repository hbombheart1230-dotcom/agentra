"""Behavior-preserving R3 implementation bodies moved from the public facade.

Each function keeps its original body. Names it used as facade module globals are
read from the injected `facade` module at call entry (explicit names, no getattr
fallback), preserving monkeypatch semantics. Owner never imports the facade.
"""
from __future__ import annotations


def _extract_strategy_detail_from_source_r3_impl(source, *, facade):
    _as_dict = facade._as_dict
    _clip = facade._clip
    _compact_scalar_dict = facade._compact_scalar_dict
    _first_nonempty_text = facade._first_nonempty_text
    _listify = facade._listify
    data = source if isinstance(source, dict) else {}
    if not data:
        return {}
    strategy_policy = _as_dict(data.get("strategy_policy"))
    market_policy = _as_dict(strategy_policy.get("market_policy"))
    scanner_policy = _as_dict(strategy_policy.get("scanner_policy"))
    direct_detail = _as_dict(data.get("strategy_detail"))

    def _pick_text(key: str, *, max_len: int = 80) -> str:
        return _first_nonempty_text(
            direct_detail.get(key),
            data.get(key),
            market_policy.get(key),
            max_len=max_len,
        )

    detail: Dict[str, Any] = {}
    for key in (
        "pre_llm_playbook",
        "llm_requested_playbook",
        "requested_playbook",
        "requested_playbook_source",
        "final_playbook",
        "tactical_strategy",
        "tactical_subtype",
    ):
        value = _pick_text(key)
        if value:
            detail[key] = value

    scores = (
        _as_dict(direct_detail.get("strategy_scores"))
        or _as_dict(data.get("strategy_scores"))
        or _as_dict(market_policy.get("strategy_scores"))
    )
    if scores:
        detail["strategy_scores"] = {
            str(key): value
            for key, value in list(scores.items())[:8]
            if str(key or "").strip()
        }

    rejected = (
        _as_dict(direct_detail.get("rejected_strategy_reasons"))
        or _as_dict(data.get("rejected_strategy_reasons"))
        or _as_dict(market_policy.get("rejected_strategy_reasons"))
    )
    if rejected:
        detail["rejected_strategy_reasons"] = _compact_scalar_dict(rejected, max_items=6, max_len=180)

    watch = (
        _as_dict(direct_detail.get("candidate_watch_policy"))
        or _as_dict(data.get("candidate_watch_policy"))
        or _as_dict(scanner_policy.get("candidate_watch_policy"))
    )
    if watch:
        detail["candidate_watch_policy"] = {
            "behavior_effect": _clip(watch.get("behavior_effect"), max_len=40),
            "source": _clip(watch.get("source"), max_len=80),
            "max_priority_rank": watch.get("max_priority_rank"),
            "max_runner_ups": watch.get("max_runner_ups"),
            "cascade_enabled": watch.get("cascade_enabled"),
            "tactical_strategy": _clip(watch.get("tactical_strategy"), max_len=80),
            "reason": _clip(watch.get("reason"), max_len=220),
            "cascade_allowed_reasons": _listify(watch.get("cascade_allowed_reasons"), max_items=6, max_len=80),
            "cascade_blocked_reasons": _listify(watch.get("cascade_blocked_reasons"), max_items=8, max_len=80),
        }

    return {key: value for key, value in detail.items() if value not in ("", None, [], {})}


def _compact_strategy_detail_context_r3_impl(value, *, facade):
    _as_dict = facade._as_dict
    _clip = facade._clip
    _compact_scalar_dict = facade._compact_scalar_dict
    _listify = facade._listify
    detail = _as_dict(value)
    if not detail:
        return {}
    out: Dict[str, Any] = {}
    for key, max_len in (
        ("pre_llm_playbook", 60),
        ("llm_requested_playbook", 60),
        ("requested_playbook", 60),
        ("requested_playbook_source", 60),
        ("final_playbook", 60),
        ("tactical_strategy", 80),
        ("tactical_subtype", 80),
    ):
        text = _clip(detail.get(key), max_len=max_len)
        if text:
            out[key] = text
    scores = _compact_scalar_dict(detail.get("strategy_scores"), max_items=8, max_len=80)
    if scores:
        out["strategy_scores"] = scores
    rejected = _compact_scalar_dict(detail.get("rejected_strategy_reasons"), max_items=6, max_len=180)
    if rejected:
        out["rejected_strategy_reasons"] = rejected
    watch = _as_dict(detail.get("candidate_watch_policy"))
    if watch:
        watch_out = {
            "behavior_effect": _clip(watch.get("behavior_effect"), max_len=40),
            "source": _clip(watch.get("source"), max_len=80),
            "max_priority_rank": watch.get("max_priority_rank"),
            "max_runner_ups": watch.get("max_runner_ups"),
            "cascade_enabled": watch.get("cascade_enabled"),
            "tactical_strategy": _clip(watch.get("tactical_strategy"), max_len=80),
            "reason": _clip(watch.get("reason"), max_len=220),
            "cascade_allowed_reasons": _listify(watch.get("cascade_allowed_reasons"), max_items=6, max_len=80),
            "cascade_blocked_reasons": _listify(watch.get("cascade_blocked_reasons"), max_items=8, max_len=80),
        }
        watch_out = {key: val for key, val in watch_out.items() if val not in ("", None, [], {})}
        if watch_out:
            out["candidate_watch_policy"] = watch_out
    return out


def _enrich_candidate_watch_proposal_from_entry_control_r3_impl(proposal, entry_control, *, facade):
    _as_dict = facade._as_dict
    _compact_candidate_watch_proposal = facade._compact_candidate_watch_proposal
    out = dict(proposal or {})
    control = _as_dict(entry_control)
    nested = _as_dict(control.get("proposal")) or _as_dict(control.get("candidate_watch_policy_proposal"))
    if not out and nested:
        out = dict(nested)
    if not out:
        return {}
    if out.get("max_priority_rank") in (None, "") and control.get("proposed_max_priority_rank") not in (None, ""):
        out["max_priority_rank"] = control.get("proposed_max_priority_rank")
    if out.get("max_runner_ups") in (None, "") and control.get("proposed_max_runner_ups") not in (None, ""):
        out["max_runner_ups"] = control.get("proposed_max_runner_ups")
    if out.get("cascade_enabled") in (None, "") and nested.get("cascade_enabled") not in (None, ""):
        out["cascade_enabled"] = nested.get("cascade_enabled")
    for key in ("source", "behavior_effect", "tactical_strategy", "reason"):
        if out.get(key) in (None, "") and nested.get(key) not in (None, ""):
            out[key] = nested.get(key)
    for key in ("cascade_allowed_reasons", "cascade_blocked_reasons"):
        if out.get(key) in (None, "", []) and nested.get(key) not in (None, "", []):
            out[key] = nested.get(key)
    return _compact_candidate_watch_proposal(out)


def _compact_commander_entry_control_r3_impl(value, *, facade):
    _as_dict = facade._as_dict
    _clip = facade._clip
    _compact_candidate_watch_proposal = facade._compact_candidate_watch_proposal
    _listify = facade._listify
    data = _as_dict(value)
    if not data:
        return {}
    proposal = _compact_candidate_watch_proposal(data.get("candidate_watch_policy_proposal"))
    out = {
        "schema_version": _clip(data.get("schema_version"), max_len=80),
        "mode": _clip(data.get("mode"), max_len=80),
        "decision": _clip(data.get("decision"), max_len=100),
        "reason": _clip(data.get("reason"), max_len=220),
        "max_priority_rank": data.get("max_priority_rank"),
        "max_runner_ups": data.get("max_runner_ups"),
        "cascade_enabled": data.get("cascade_enabled"),
        "candidate_watch_policy_detected": data.get("candidate_watch_policy_detected"),
        "candidate_watch_policy_applied": data.get("candidate_watch_policy_applied"),
        "candidate_watch_policy_effect": _clip(data.get("candidate_watch_policy_effect"), max_len=80),
        "candidate_watch_policy_clamp_reason": _clip(
            data.get("candidate_watch_policy_clamp_reason"),
            max_len=220,
        ),
        "proposed_max_priority_rank": data.get("proposed_max_priority_rank") or proposal.get("max_priority_rank"),
        "proposed_max_runner_ups": data.get("proposed_max_runner_ups") or proposal.get("max_runner_ups"),
        "proposal": proposal,
        "cascade_allowed_reasons": _listify(data.get("cascade_allowed_reasons"), max_items=6, max_len=80),
        "cascade_blocked_reasons": _listify(data.get("cascade_blocked_reasons"), max_items=8, max_len=80),
    }
    return {key: value for key, value in out.items() if value not in ("", None, [], {})}


def _compact_entry_candidate_cascade_r3_impl(value, *, facade):
    _as_dict = facade._as_dict
    _clip = facade._clip
    _listify = facade._listify
    data = _as_dict(value)
    if not data:
        return {}
    trace_rows: List[Dict[str, Any]] = []
    for row in list(data.get("fallback_trace") or [])[:6]:
        item = _as_dict(row)
        if not item:
            continue
        trace_rows.append(
            {
                "symbol": _clip(item.get("symbol"), max_len=24),
                "rank": item.get("rank"),
                "score_total": item.get("score_total"),
                "triggered": item.get("triggered"),
                "reason": _clip(item.get("reason"), max_len=120),
                "primary_failure_axis": _clip(item.get("primary_failure_axis"), max_len=80),
                "guard_blocked": item.get("guard_blocked"),
                "confidence_score": item.get("confidence_score"),
                "confidence_threshold": item.get("confidence_threshold"),
                "volume_ratio": item.get("volume_ratio"),
                "vwap_distance": item.get("vwap_distance"),
            }
        )
    trace_rows = [
        {key: value for key, value in row.items() if value not in ("", None, [], {})}
        for row in trace_rows
    ]
    out = {
        "attempted": data.get("attempted"),
        "eligible": data.get("eligible"),
        "cascade_enabled": data.get("cascade_enabled"),
        "reason": _clip(data.get("reason"), max_len=140),
        "blocked_reason": _clip(data.get("blocked_reason"), max_len=140),
        "top_pick_symbol": _clip(data.get("top_pick_symbol"), max_len=24),
        "top_pick_triggered": data.get("top_pick_triggered"),
        "top_pick_reason": _clip(data.get("top_pick_reason"), max_len=140),
        "top_pick_guard_blocked": data.get("top_pick_guard_blocked"),
        "max_priority_rank": data.get("max_priority_rank"),
        "max_runner_ups": data.get("max_runner_ups"),
        "control_source": _clip(data.get("control_source"), max_len=80),
        "control_mode": _clip(data.get("control_mode"), max_len=80),
        "runner_up_symbols": _listify(data.get("runner_up_symbols"), max_items=9, max_len=24),
        "fallback_used": data.get("fallback_used"),
        "fallback_from_symbol": _clip(data.get("fallback_from_symbol"), max_len=24),
        "fallback_to_symbol": _clip(data.get("fallback_to_symbol"), max_len=24),
        "fallback_to_rank": data.get("fallback_to_rank"),
        "final_selected_symbol": _clip(data.get("final_selected_symbol"), max_len=24),
        "final_selected_rank": data.get("final_selected_rank"),
        "fallback_trace": trace_rows,
        "cascade_allowed_reasons": _listify(data.get("cascade_allowed_reasons"), max_items=6, max_len=80),
        "cascade_blocked_reasons": _listify(data.get("cascade_blocked_reasons"), max_items=8, max_len=80),
    }
    return {key: value for key, value in out.items() if value not in ("", None, [], {})}


def _entry_execution_visibility_summary_r3_impl(*, proposal, entry_control, cascade, facade):
    _clip = facade._clip
    parts: List[str] = []
    if proposal:
        parts.append(
            "strategy proposed "
            f"rank<={proposal.get('max_priority_rank', '-')}, runner_ups={proposal.get('max_runner_ups', '-')}"
        )
    if entry_control:
        parts.append(
            "commander applied "
            f"rank<={entry_control.get('max_priority_rank', '-')}, runner_ups={entry_control.get('max_runner_ups', '-')}"
        )
        clamp_reason = _clip(entry_control.get("candidate_watch_policy_clamp_reason"), max_len=120)
        if clamp_reason:
            parts.append(f"clamp={clamp_reason}")
    if cascade:
        attempted = "attempted" if bool(cascade.get("attempted")) else "not_attempted"
        fallback = cascade.get("fallback_to_symbol") if bool(cascade.get("fallback_used")) else ""
        if fallback:
            parts.append(f"monitor {attempted}, fallback_to={fallback}")
        else:
            blocked = _clip(cascade.get("blocked_reason"), max_len=120)
            suffix = f", blocked={blocked}" if blocked else ""
            parts.append(f"monitor {attempted}{suffix}")
    return "; ".join(part for part in parts if part)
