"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/trade_report_common.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def list_text_r4_impl(values, *, limit, max_len, facade):
    if not isinstance(values, list):
        return []
    out: List[str] = []
    for value in values:
        text = facade.clip_text(value, max_len=max_len)
        if not text:
            continue
        out.append(text)
        if len(out) >= max(1, int(limit)):
            break
    return out


def listify_r4_impl(values, *, max_items, max_len, facade):
    out: List[str] = []
    if not isinstance(values, list):
        return out
    for value in values:
        text = facade.report_clip(value, max_len=max_len)
        if text:
            out.append(text)
        if len(out) >= max_items:
            break
    return out


def dedupe_list_r4_impl(values, *, max_items, max_len, facade):
    out: List[str] = []
    seen: set[str] = set()
    for value in values:
        text = facade.report_clip(value, max_len=max_len)
        if not text or text in seen:
            continue
        out.append(text)
        seen.add(text)
        if len(out) >= max_items:
            break
    return out


def compact_named_rows_r4_impl(values, *, max_items, facade):
    if not isinstance(values, list):
        return []
    out: List[Dict[str, Any]] = []
    for value in values:
        if len(out) >= max(1, int(max_items)):
            break
        if not isinstance(value, dict):
            continue
        row = {'rank': value.get('rank'), 'symbol': facade.report_clip(value.get('symbol'), max_len=24), 'score_total': value.get('score_total'), 'risk_score': value.get('risk_score'), 'confidence': value.get('confidence'), 'why': facade.report_clip(value.get('why'), max_len=180)}
        row = {key: item for key, item in row.items() if item not in ('', None, [])}
        if row.get('symbol'):
            out.append(row)
    return out


def compact_scalar_dict_r4_impl(values, *, max_items, max_len, facade):
    if not isinstance(values, dict):
        return {}
    out: Dict[str, Any] = {}
    for key, value in values.items():
        if len(out) >= max(1, int(max_items)):
            break
        if isinstance(value, (int, float, bool)) or value is None:
            out[str(key)] = value
            continue
        text = facade.report_clip(value, max_len=max_len)
        if text:
            out[str(key)] = text
    return out


def merge_missing_values_r4_impl(base, fallback, *, facade):
    out = dict(base or {})
    for key, value in dict(fallback or {}).items():
        if key not in out or out.get(key) in (None, '', [], {}):
            out[key] = value
    return out


def is_empty_placeholder_r4_impl(value, *, facade):
    if value is None:
        return True
    if isinstance(value, bool):
        return value is False
    if isinstance(value, (int, float)):
        return value == 0
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return len(value) == 0
    if isinstance(value, dict):
        if not value:
            return True
        return all((facade.is_empty_placeholder(item) for item in value.values()))
    return False


def fmt_pct_r4_impl(value, *, facade):
    try:
        number = float(value)
    except Exception:
        return '-'
    return f'{number * 100.0:.2f}%'


def fmt_price_r4_impl(value, *, facade):
    try:
        number = float(value)
    except Exception:
        return '-'
    return f'{number:.2f}'
