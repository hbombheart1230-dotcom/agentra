"""Compatibility shim (V2-053): the implementation lives in ``libs.agents.scanner.context.scoring_inputs``.

This module is replaced in ``sys.modules`` by the canonical module object, so the old and new import paths are the
*same* module (identity, private names, use-time monkeypatch). There is exactly one implementation; do not add code here.
"""
import sys as _sys

from libs.agents.scanner.context import scoring_inputs as _canonical

_sys.modules[__name__] = _canonical
