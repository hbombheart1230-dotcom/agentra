"""Strategist numeric/value helpers moved verbatim from the facade (S5, pure).

Bodies moved from graphs/nodes/strategist_node.py. Every former facade module global is qualified at its use site as
`facade.NAME` (explicit injected module; use-time lookup, no entry-time capture, no getattr fallback), so monkeypatching
matches the original module-level resolution. Owner never imports the facade.
"""
from __future__ import annotations


def _clamp_r3_impl(x, lo, hi, *, facade):
    return lo if x < lo else hi if x > hi else x


def _to_float_r3_impl(v, default, *, facade):
    try:
        return float(v)
    except Exception:
        return float(default)


def _to_int_r3_impl(v, default, *, facade):
    try:
        return int(float(v))
    except Exception:
        return int(default)


def _round_optional_r3_impl(value, digits, *, facade):
    try:
        return round(float(value), int(digits))
    except Exception:
        return value


def _unit_score_r3_impl(value, default, *, facade):
    try:
        return float(facade._clamp(float(value), 0.0, 1.0))
    except Exception:
        return float(facade._clamp(default, 0.0, 1.0))


def _is_trueish_r3_impl(v, *, facade):
    return str(v or "").strip().lower() in ("1", "true", "yes", "y", "on")
