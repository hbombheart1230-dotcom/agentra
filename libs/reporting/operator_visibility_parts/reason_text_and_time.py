"""Operator visibility reason humanisation, story explanation and epoch/time helpers (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _story_explanation_r3_impl(story, *, facade):
    no_trade = story.get("no_trade_surface") if isinstance(story.get("no_trade_surface"), dict) else {}
    explanation = facade.build_narrative_explanation(
        action=story.get("action"),
        decision_outcome=no_trade.get("decision_outcome"),
        final_outcome=story.get("final_outcome"),
        key_reason=story.get("key_reason"),
        no_trade_reason_summary=no_trade.get("no_trade_reason_summary"),
        dominant_blocker=no_trade.get("dominant_blocker"),
        distance_to_ready=facade._compact_distance_to_ready_text(no_trade.get("distance_to_ready")),
        exit_reason=story.get("key_reason") if facade._decision_axis(story) == "exit" else "",
    )
    return {
        "axis": str(explanation.get("decision_axis") or "unknown"),
        "primary_summary": str(explanation.get("primary_explanation") or "-"),
        "entry_narrative": str(explanation.get("entry_narrative") or "-"),
        "exit_narrative": str(explanation.get("exit_narrative") or "-"),
        "why_not_buy_summary": str(explanation.get("why_not_buy_summary") or "-"),
        "dominant_blocker": str(explanation.get("dominant_blocker_display") or "-"),
        "entry_context_blocker": str(explanation.get("entry_context_blocker") or "-"),
        "distance_to_ready": str(explanation.get("distance_to_ready") or "-"),
        "exit_trigger_basis": str(explanation.get("why_exit_summary") or "-"),
        "narrative_order": list(explanation.get("narrative_order") or []),
        "narrative_order_text": str(explanation.get("narrative_order_text") or "-"),
        "narrative_consistency_flag": bool(explanation.get("narrative_consistency_flag")),
        "explanation_mode": str(explanation.get("explanation_mode") or "unknown"),
        "explanation_source": str(explanation.get("explanation_source") or "-"),
        "mixed_reason": str(explanation.get("mixed_reason") or "-"),
    }


def _normalize_reason_code_r3_impl(raw_reason, *, action, execution_status, guard_status, facade):
    reason = str(raw_reason or "").strip()
    if reason:
        low = reason.lower()
        if any(k in low for k in ("allowlist", "notional", "guard", "blocked")):
            return "GUARD_BLOCK"
        if "market_closed" in low or ("market" in low and "closed" in low):
            return "MARKET_CLOSED"
        if low in ("unspecified", "none"):
            reason = ""

    if guard_status == "intervened" or execution_status == "BLOCKED":
        return "GUARD_BLOCK"
    if action == "NOOP":
        return "NO_CANDIDATE"
    if execution_status in ("UNKNOWN", "SKIPPED"):
        return "MARKET_CLOSED"
    return reason or "unspecified"


def _humanize_reason_r3_impl(raw, *, facade):
    reason = str(raw or "").strip()
    if not reason:
        return facade._REASON_LABELS["unspecified"]
    low = reason.lower()
    if low in facade._REASON_LABELS:
        return facade._REASON_LABELS[low]
    if reason in facade._REASON_LABELS:
        return facade._REASON_LABELS[reason]
    if low.startswith("exit_policy:"):
        tail = reason.split(":", 1)[1].replace("_", " ").strip()
        return f"Exit policy triggered ({tail})"
    if low.startswith("score_override:"):
        tail = reason.split(":", 1)[1].strip()
        return f"Score override applied ({tail})"
    if low.startswith("eod_force_liquidation:"):
        return f"EOD force liquidation ({reason.split(':', 1)[1]})"
    return reason


def _reason_text_r3_impl(intent, trace, llm, *, facade):
    cand = [
        intent.get("reason"),
        intent.get("rationale"),
        trace.get("rationale"),
        (trace.get("raw_intent") if isinstance(trace.get("raw_intent"), dict) else {}).get("reason"),
        llm.get("intent_reason"),
        llm.get("intent_rationale"),
    ]
    for v in cand:
        s = str(v or "").strip()
        if s:
            return s
    return "unspecified"


def _render_reason_top_r3_impl(counter, *, topn, facade):
    out: List[Dict[str, Any]] = []
    for reason, cnt in counter.most_common(topn):
        out.append(
            {
                "reason": str(reason or ""),
                "label": facade._humanize_reason(reason),
                "count": int(cnt),
            }
        )
    return out


def _format_reason_rows_r3_impl(rows, *, facade):
    if not rows:
        return "none"
    return "; ".join(
        f"{str(r.get('label') or r.get('reason') or '-')} ({int(r.get('count') or 0)})"
        for r in rows
    )


def _decision_axis_r3_impl(story, *, facade):
    action = str(story.get("action") or "").strip().upper()
    no_trade = story.get("no_trade_surface") if isinstance(story.get("no_trade_surface"), dict) else {}
    outcome = str(no_trade.get("decision_outcome") or "").strip().upper()
    if action == "SELL" or outcome == "SELL":
        return "exit"
    return "entry"


def _to_epoch_r3_impl(ts, *, facade):
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        return int(ts)

    s = str(ts).strip()
    if not s:
        return None
    try:
        return int(float(s))
    except Exception:
        pass

    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = facade.datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=facade.timezone.utc)
        return int(dt.timestamp())
    except Exception:
        return None


def _epoch_to_iso_r3_impl(epoch, *, facade):
    try:
        n = int(float(epoch))
    except Exception:
        return ""
    if n <= 0:
        return ""
    return facade.datetime.fromtimestamp(n, tz=facade.timezone.utc).isoformat(timespec="seconds")


def _compact_kv_text_r3_impl(raw, *, topn, facade):
    if isinstance(raw, dict):
        pairs = []
        for k, v in raw.items():
            if isinstance(v, (dict, list)):
                continue
            pairs.append((str(k), str(v)))
        pairs = pairs[:topn]
        if not pairs:
            return "-"
        return ", ".join(f"{k}={v}" for k, v in pairs)
    if isinstance(raw, list):
        vals = [str(x) for x in raw[:topn] if x is not None]
        return ", ".join(vals) if vals else "-"
    if raw is None:
        return "-"
    s = str(raw).strip()
    return s if s else "-"


def _broker_code_success_r3_impl(value, *, facade):
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        return int(float(s)) == 0
    except Exception:
        pass
    t = s.lower()
    if t in ("ok", "success", "accepted"):
        return True
    if t in ("error", "failed", "rejected"):
        return False
    return False


def _compact_distance_to_ready_text_r3_impl(raw, *, facade):
    row = raw if isinstance(raw, dict) else {}
    if not row:
        return "-"
    parts: List[str] = []
    for key in ("reclaim_score_gap", "breakout_gap", "volume_gap", "confidence_gap"):
        if row.get(key) in (None, ""):
            continue
        try:
            parts.append(f"{key}={float(row.get(key)):.4f}")
        except Exception:
            parts.append(f"{key}={row.get(key)}")
    return ", ".join(parts) if parts else "-"
