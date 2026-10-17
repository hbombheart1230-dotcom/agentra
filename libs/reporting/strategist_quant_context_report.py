"""Compatibility shim (Reporter seed batch): the implementation lives in ``libs.agents.reporter.narrative.strategist_quant_context_report``.

This module is replaced in ``sys.modules`` by the canonical module object, so the old and new import paths are the
*same* module (identity, private names, use-time monkeypatch). There is exactly one implementation; do not add code here.
"""
import sys as _sys

from libs.agents.reporter.narrative import strategist_quant_context_report as _canonical

_sys.modules[__name__] = _canonical
