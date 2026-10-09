from __future__ import annotations

from typing import Any, Dict, Mapping

def build_seed_scanner_reasoning(scanner_reason: Dict[str, Any], scanner_selection_trace: Dict[str, Any], *, deps: Mapping[str, Any]) -> Any:
    _first_nonempty_text = deps["first_nonempty_text"]
    _compact_scalar_dict = deps["compact_scalar_dict"]
    _clip = deps["clip"]
    _listify = deps["listify"]

    scanner_reasoning = {
        "playbook": _first_nonempty_text(scanner_reason.get("playbook"), max_len=80),
        "policy_source": _first_nonempty_text(scanner_reason.get("policy_source"), max_len=80),
        "applied_policy_present": bool(scanner_reason.get("applied_policy_present")),
        "monitor_entry_policy_summary": _compact_scalar_dict(
            scanner_reason.get("monitor_entry_policy_summary"),
            max_items=8,
            max_len=120,
        ),
        "scanner_bias_applied": bool(scanner_reason.get("scanner_bias_applied")),
        "scanner_bias_summary": _compact_scalar_dict(
            scanner_reason.get("scanner_bias_summary"),
            max_items=8,
            max_len=120,
        ),
        "candidate_bias_adjustments": [
            {
                "symbol": _clip((row or {}).get("symbol"), max_len=24),
                "bias_adjustment": (row or {}).get("bias_adjustment"),
                "bias_adjustments": _listify(
                    [
                        str((item or {}).get("reason") or "")
                        for item in list((row or {}).get("bias_adjustments") or [])
                        if isinstance(item, dict)
                    ],
                    max_items=4,
                    max_len=120,
                ),
            }
            for row in list(scanner_reason.get("candidate_bias_adjustments") or [])[:5]
            if isinstance(row, dict)
        ],
        "selection_reason_with_bias": _first_nonempty_text(
            scanner_reason.get("selection_reason_with_bias"),
            scanner_reason.get("selection_basis"),
            scanner_reason.get("summary"),
            max_len=320,
        ),
        "selection_trace": {
            "ranked_candidates": [
                {
                    "rank": (row or {}).get("rank"),
                    "symbol": _clip((row or {}).get("symbol"), max_len=24),
                    "score_total": (row or {}).get("score_total"),
                    "risk_score": (row or {}).get("risk_score"),
                    "confidence": (row or {}).get("confidence"),
                }
                for row in list(scanner_selection_trace.get("ranked_candidates") or [])[:5]
                if isinstance(row, dict)
            ],
            "selected_symbol": _first_nonempty_text(
                scanner_selection_trace.get("selected_symbol"),
                scanner_reason.get("selected_symbol"),
                max_len=24,
            ),
            "selected_rank": scanner_selection_trace.get("selected_rank") or scanner_reason.get("selected_rank"),
            "selection_reason": _first_nonempty_text(
                scanner_selection_trace.get("selection_reason"),
                scanner_reason.get("selection_reason"),
                scanner_reason.get("selection_basis"),
                max_len=280,
            ),
            "selected_symbol_score_drivers": _compact_scalar_dict(
                scanner_selection_trace.get("selected_symbol_score_drivers")
                or scanner_reason.get("selected_symbol_score_drivers"),
                max_items=6,
                max_len=120,
            ),
        },
    }
    return scanner_reasoning

def enrich_seed_scanner_reasoning(scanner_reasoning: Dict[str, Any], trade_model_scanner: Dict[str, Any], *, deps: Mapping[str, Any]) -> Any:
    _clip = deps["clip"]
    _compact_scalar_dict = deps["compact_scalar_dict"]

    if not scanner_reasoning.get("selection_reason_with_bias") and str(trade_model_scanner.get("summary") or "").strip():
        scanner_reasoning["selection_reason_with_bias"] = _clip(trade_model_scanner.get("summary"), max_len=320)
    selection_trace = scanner_reasoning.get("selection_trace") if isinstance(scanner_reasoning.get("selection_trace"), dict) else {}
    if not selection_trace.get("ranked_candidates") and isinstance(trade_model_scanner.get("top_candidates"), list):
        selection_trace["ranked_candidates"] = [
            {
                "symbol": _clip((row or {}).get("symbol"), max_len=24),
                "score_total": (row or {}).get("score_total"),
                "rank": (row or {}).get("rank"),
            }
            for row in list(trade_model_scanner.get("top_candidates") or [])[:5]
            if isinstance(row, dict)
        ]
    if not selection_trace.get("selected_symbol"):
        first_ranked = ((selection_trace.get("ranked_candidates") or [None])[0] or {}) if isinstance(selection_trace.get("ranked_candidates"), list) else {}
        if isinstance(first_ranked, dict) and str(first_ranked.get("symbol") or "").strip():
            selection_trace["selected_symbol"] = _clip(first_ranked.get("symbol"), max_len=24)
    if not selection_trace.get("selected_rank"):
        first_ranked = ((selection_trace.get("ranked_candidates") or [None])[0] or {}) if isinstance(selection_trace.get("ranked_candidates"), list) else {}
        if isinstance(first_ranked, dict) and first_ranked.get("rank") not in (None, ""):
            selection_trace["selected_rank"] = first_ranked.get("rank")
    if not selection_trace.get("selected_symbol_score_drivers") and isinstance(trade_model_scanner.get("score_drivers"), dict):
        selection_trace["selected_symbol_score_drivers"] = _compact_scalar_dict(
            trade_model_scanner.get("score_drivers"), max_items=6, max_len=120
        )
    scanner_reasoning["selection_trace"] = selection_trace

    return None

