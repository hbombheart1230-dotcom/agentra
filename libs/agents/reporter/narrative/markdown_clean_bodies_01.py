"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/trade_report_markdown_clean.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _first_report_path_r4_impl(root, paths, *, facade):
    for path in paths:
        value = facade._get_report_path(root, path)
        if value not in (None, '', [], {}):
            return value
    return None


def _listify_r4_impl(value, *, facade):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _has_payload_r4_impl(value, *, facade):
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) > 0
    return True


def _merge_preferred_r4_impl(primary, fallback, *, facade):
    merged = dict(fallback or {})
    for key, value in (primary or {}).items():
        if facade._has_payload(value):
            merged[key] = value
    return merged


def _num_opt_r4_impl(value, *, facade):
    try:
        if value in (None, ''):
            return None
        return float(value)
    except Exception:
        return None


def _fmt_signed_pct_r4_impl(value, *, facade):
    num = facade._num_opt(value)
    if num is None:
        return '-'
    sign = '+' if num > 0 else ''
    return f'{sign}{num * 100.0:.2f}%'


def _summary_money_r4_impl(value, *, facade):
    num = facade._num_opt(value)
    if num is None:
        return '-'
    if abs(num) >= 100:
        return f'{num:,.0f}'
    return f'{num:,.2f}'.rstrip('0').rstrip('.')


def _resolve_strategy_refresh_trace_r4_impl(report, *, facade):
    direct = facade._as_dict(report.get('strategist_refresh_trace'))
    if direct:
        return direct
    output = facade._resolve_strategist_output_surface(report)
    return facade._as_dict(output.get('strategy_refresh_trace'))


def _looks_corrupted_r4_impl(text, *, facade):
    if not text:
        return False
    if '?' in text:
        return True
    if any((63744 <= ord(ch) <= 64255 for ch in text)):
        return True
    weird_markers = ['?꾨', '留ㅻ', '媛먯', '鍮꾪', '湲곗', '蹂댁', '吏꾩', '嫄곕', '理쒖', '泥?궛', '??']
    return sum((marker in text for marker in weird_markers)) >= 2


def _dedupe_r4_impl(lines, *, facade):
    seen = set()
    out: List[str] = []
    for line in lines:
        key = line.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(line)
    return out
