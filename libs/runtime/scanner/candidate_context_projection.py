"""Scanner candidate-source context projections (eligibility/guidance/quote diagnostics; I/O and hydration stay in the node).

Second Pass (P1.5) intra-function extraction from `graphs/nodes/scanner_node.py`. Each function below is a contiguous, effect-free
statement run (or a value expression) of the original orchestrator, copied verbatim; locals enter as explicit
parameters and leave as the return tuple. Module globals of the original module are resolved at use time as
`facade.NAME` (TEMPORARY_COMPATIBILITY: keeps monkeypatch seams; no state writes, events, I/O, LLM or broker
calls are present - those statements stay in the orchestrator).
"""
from __future__ import annotations


def scan_context_candidates_policy(state, *, facade):
    """Graph node: Scanner (Data + feature extraction).

    M17-3 contract (additive):
      - Builds candidate pool from Kiwoom market data (default)
      - Applies strategist theme hints when mapping data exists
      - Falls back to strategist candidates when Kiwoom pool is empty
      - Computes per-candidate features/risk/confidence
      - Selects exactly 1 candidate into state['selected'] (or None)

    Writes:
      - state['scan_results'] : list[dict]
      - state['selected'] : dict | None
      - state['risk'] : dict (risk_score/confidence for selected)

    Test hooks:
      - state['mock_scan_results'] : {symbol: {score, risk_score, confidence, features?}}
        If present, Scanner will use these values instead of generating.
    """
    # M18-4: sentiment-aware scoring (offline-friendly)
    policy = state.get("policy") if isinstance(state.get("policy"), dict) else {}
    candidates, pool_meta = facade._resolve_scanner_candidates(state, policy)
    return (candidates, policy, pool_meta)


def scan_context_commander_context_intrinsic_control_w(policy, state, *, facade):
    w = facade._get_scanner_weights(policy)
    practical_w = facade._resolve_scanner_score_weights(policy)
    intrinsic_control_w = dict(practical_w)
    scanner_guidance = facade._extract_scanner_guidance(state)
    playbook = str(scanner_guidance.get("playbook") or "").strip().lower()
    scanner_bias = str(scanner_guidance.get("scanner_bias") or "").strip().lower()
    scanner_bias_context = (
        dict(scanner_guidance.get("scanner_bias_context") or {})
        if isinstance(scanner_guidance.get("scanner_bias_context"), dict)
        else {}
    )
    scanner_memory_bias = (
        dict(scanner_guidance.get("scanner_memory_bias") or {})
        if isinstance(scanner_guidance.get("scanner_memory_bias"), dict)
        else {}
    )
    scanner_priority = facade._normalize_priority_list(scanner_guidance.get("scanner_priority"))
    trade_aggressiveness = str(scanner_guidance.get("trade_aggressiveness") or "").strip().lower()
    risk_tone = str(scanner_guidance.get("risk_tone") or "").strip().lower()
    monitor_guidance = str(scanner_guidance.get("monitor_guidance") or "").strip().lower()
    strategy_monitor_policy = (
        dict(scanner_guidance.get("monitor_policy") or {})
        if isinstance(scanner_guidance.get("monitor_policy"), dict)
        else {}
    )
    commander_context = (
        dict(scanner_guidance.get("commander_context") or {})
        if isinstance(scanner_guidance.get("commander_context"), dict)
        else {}
    )
    strategist_plan = (
        dict(scanner_guidance.get("strategist_plan") or {})
        if isinstance(scanner_guidance.get("strategist_plan"), dict)
        else {}
    )
    policy_provenance = (
        dict(scanner_guidance.get("policy_provenance") or {})
        if isinstance(scanner_guidance.get("policy_provenance"), dict)
        else {}
    )
    scanner_policy_trace = facade._build_scanner_policy_trace(
        commander_context=commander_context,
        strategist_plan=strategist_plan,
        policy_provenance=policy_provenance,
        playbook=playbook,
        scanner_priority=scanner_priority,
        scanner_bias=scanner_bias,
        scanner_bias_context=scanner_bias_context,
        scanner_memory_bias=scanner_memory_bias,
    )
    return (commander_context, intrinsic_control_w, monitor_guidance, playbook, policy_provenance, practical_w, risk_tone, scanner_bias, scanner_bias_context, scanner_guidance, scanner_memory_bias, scanner_policy_trace, scanner_priority, strategy_monitor_policy, trade_aggressiveness, w)
