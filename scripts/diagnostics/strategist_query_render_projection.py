from __future__ import annotations
from typing import Any, Dict, List

def _print_human(path: Any, rows: List[Dict[str, Any]], *, facade: Any) -> None:
    print("=== Strategist LLM Events ===")
    print(f"path={path}")
    print(f"shown={len(rows)}")
    for rec in rows:
        p = rec.get("payload") if isinstance(rec.get("payload"), dict) else {}
        ts = str(rec.get("ts") or ""); run_id = str(rec.get("run_id") or ""); call_kind = facade._infer_call_kind(p)
        print(f"{ts} run_id={run_id} call_kind={call_kind} ok={p.get('ok')} action={str(p.get('intent_action') or '')} reason={str(p.get('intent_reason') or '')} latency_ms={p.get('latency_ms')} attempts={p.get('attempts')} prompt_version={str(p.get('prompt_version') or '')} schema_version={str(p.get('schema_version') or '')} prompt_tokens={p.get('prompt_tokens')} completion_tokens={p.get('completion_tokens')} total_tokens={p.get('total_tokens')} estimated_cost_usd={p.get('estimated_cost_usd')} context_regime={str(p.get('context_regime') or '')} context_signal_score={p.get('context_signal_score')} context_symbol_sentiment_score={p.get('context_symbol_sentiment_score')} context_global_sentiment_score={p.get('context_global_sentiment_score')} context_symbol_sentiment_status={str(p.get('context_symbol_sentiment_status') or '')} context_global_sentiment_status={str(p.get('context_global_sentiment_status') or '')} context_composite_score={p.get('context_composite_score')} error_type={str(p.get('error_type') or '')}")

def _print_summary(rows: List[Dict[str, Any]], *, facade: Any) -> None:
    by_kind: Dict[str, Dict[str, int]]={};by_reason: Dict[str,int]={};by_action: Dict[str,int]={}
    for rec in rows:
        p=rec.get('payload') if isinstance(rec.get('payload'),dict) else {};kind=facade._infer_call_kind(p);ok='ok' if bool(p.get('ok')) else 'non_ok';by_kind.setdefault(kind,{});by_kind[kind][ok]=int(by_kind[kind].get(ok) or 0)+1;reason=str(p.get('intent_reason') or p.get('status') or 'none');by_reason[reason]=int(by_reason.get(reason) or 0)+1;action=str(p.get('intent_action') or 'none');by_action[action]=int(by_action.get(action) or 0)+1
    print('summary.call_kind=',facade.json.dumps(by_kind,ensure_ascii=False,sort_keys=True));print('summary.intent_action=',facade.json.dumps(by_action,ensure_ascii=False,sort_keys=True));print('summary.intent_reason_top=',facade.json.dumps(sorted(by_reason.items(),key=lambda kv:kv[1],reverse=True)[:10],ensure_ascii=False))
