from __future__ import annotations


def _to_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return float(default)


def _infer_call_kind(payload):
    explicit = str(payload.get("call_kind") or "").strip()
    if explicit:
        return explicit
    schema_version = str(payload.get("schema_version") or "").strip().lower()
    prompt_version = str(payload.get("prompt_version") or "").strip().lower()
    intent_action = str(payload.get("intent_action") or "").strip().upper()
    error_type = str(payload.get("error_type") or "").strip()
    if schema_version == "strategist_output.v1" or prompt_version.startswith("m31-strategic-frame"):
        return "strategic_frame"
    if schema_version == "intent.v1" or intent_action in {"BUY", "SELL", "NOOP"}:
        return "legacy_trade_intent"
    if error_type == "StrategistBlocked":
        return "blocked_legacy_runtime"
    return "unknown"


def _filtered_events(rows, *, run_id="", day="", only_failures=False, only_nonzero_news=False, facade):
    out = []
    for rec in rows:
        if rec.get("stage") != "strategist_llm" or rec.get("event") != "result":
            continue
        if day and not str(rec.get("ts_kst") or rec.get("ts") or "").startswith(day):
            continue
        if run_id and str(rec.get("run_id") or "") != run_id:
            continue
        p = rec.get("payload") if isinstance(rec.get("payload"), dict) else {}
        if only_failures and bool(p.get("ok")):
            continue
        if only_nonzero_news and abs(facade._to_float(p.get("context_symbol_sentiment_score"), 0.0)) <= 1e-12:
            continue
        out.append(rec)
    return out
