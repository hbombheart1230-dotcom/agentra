"""Strategist small value/trace helpers shared by context builders (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _env_int_r3_impl(key, *, facade):
    raw = facade.os.getenv(key)
    if raw in (None, ""):
        return None
    try:
        return int(float(str(raw).strip()))
    except Exception:
        return None


def _nested_mapping_value_r3_impl(mapping, *path, facade):
    cursor: Any = mapping if isinstance(mapping, dict) else {}
    for key in path:
        if not isinstance(cursor, dict):
            return None
        cursor = cursor.get(key)
    return cursor


def _attach_quant_context_to_strategy_refresh_trace_r3_impl(trace, quant_context, *, facade):
    out = dict(trace or {}) if isinstance(trace, dict) else {}
    ctx = dict(quant_context or {}) if isinstance(quant_context, dict) else {}
    if not ctx:
        return out
    target_stage = facade._quant_trace_stage_for_call_kind(ctx.get("call_kind"))
    raw_stages = out.get("stages") if isinstance(out.get("stages"), list) else []
    stages: List[Dict[str, Any]] = [dict(row or {}) for row in raw_stages if isinstance(row, dict)]
    attached = False
    for row in stages:
        if str(row.get("stage") or "").strip() == target_stage:
            row["quant_context"] = dict(ctx)
            attached = True
            break
    if not attached:
        stages.append(
            {
                "stage": target_stage,
                "label": facade._quant_trace_label_for_stage(target_stage),
                "summary": "Strategist LLM received observation-only quant context for this call.",
                "quant_context": dict(ctx),
            }
        )
    out["stages"] = stages
    out["quant_context_call_kind"] = str(ctx.get("call_kind") or "")
    return out


def _append_unique_text_r3_impl(out, seen, raw, *, facade):
    s = str(raw or "").strip()
    if not s:
        return
    key = s.lower()
    if key in seen:
        return
    seen.add(key)
    out.append(s)


def _signal_score_r3_impl(sig, *, facade):
    if not isinstance(sig, dict):
        return 0.0
    try:
        return float(sig.get("score") or 0.0)
    except Exception:
        return 0.0
