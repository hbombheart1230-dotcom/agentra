"""Compatibility shim (Reporter seed batch): the implementation lives in ``libs.agents.reporter.narrative.trade_fallback_text``.

This module is replaced in ``sys.modules`` by the canonical module object, so the old and new import paths are the
*same* module (identity, private names, use-time monkeypatch). There is exactly one implementation; do not add code here.
"""
import sys as _sys

from libs.agents.reporter.narrative import trade_fallback_text as _canonical

_sys.modules[__name__] = _canonical
