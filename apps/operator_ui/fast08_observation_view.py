"""Pure observation semantics for read-only UI; no artifact probes or authority."""
from __future__ import annotations
import math
from urllib.parse import unquote, urlsplit


def observed_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        if value.strip().lower() in {'true', '1'}:
            return True
        if value.strip().lower() in {'false', '0'}:
            return False
    return None


def observed_number(value):
    """Only finite JSON numbers are evidence; None is distinct from zero."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        return value if math.isfinite(value) else None
    except (OverflowError, TypeError):
        return None


def has_observed_payload(value):
    if isinstance(value, dict):
        return any(has_observed_payload(v) for v in value.values())
    if isinstance(value, list):
        return any(has_observed_payload(v) for v in value)
    return value is not None and value != ''


def execution_observation(action, status, allowed=None, reason=''):
    """Classify recorded fields for display, never approve/submit an order."""
    action = str(action or '').strip().upper()
    raw = str(status or '').strip().lower()
    guard = observed_bool(allowed)
    if guard is False or raw in {'denied', 'blocked', 'guarded', 'never_sent'}:
        state, tone = 'GUARDED', 'warn'
    elif raw in {'failed', 'error', 'rejected', 'cancelled', 'canceled'}:
        state, tone = 'FAILED', 'critical'
    elif action in {'NOOP', 'WAIT', 'HOLD'}:
        state, tone = 'NO_ORDER', 'neutral'
    elif raw in {'pending', 'accepted', 'submitted', 'partially_filled'}:
        state, tone = 'PENDING', 'warn'
    elif action in {'BUY', 'SELL'} and raw in {'ok', 'success', 'filled', 'executed', 'completed'}:
        state, tone = 'SUCCESS', 'ok'
    else:
        state, tone = ('UNKNOWN' if action or raw else 'NO_DATA'), 'neutral'
    return {'state': state, 'tone': tone, 'action': action, 'raw_status': raw,
            'guard': guard, 'reason': str(reason or '')}


def safe_trace_link(value):
    """Only existing internal run/report detail URL families are clickable."""
    if not isinstance(value, str) or not value:
        return ''
    try:
        url = urlsplit(value)
        decoded = unquote(value)
    except ValueError:
        return ''
    if url.scheme or url.netloc or not url.path.startswith(('/runs/', '/reports/trade/')):
        return ''
    if '\\' in decoded or any(ord(c) < 32 or ord(c) == 127 for c in decoded):
        return ''
    if any(segment in {'.', '..'} for segment in unquote(url.path).split('/')):
        return ''
    return value
