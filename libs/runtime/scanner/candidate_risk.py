"""Compatibility shim (V1-052): the implementation lives in ``libs.agents.scanner.candidate_risk``.

This module is replaced in ``sys.modules`` by the canonical module object, so ``libs.runtime.scanner.candidate_risk``
and ``libs.agents.scanner.candidate_risk`` are the *same* module (identity, private names, use-time monkeypatch).
There is exactly one implementation; do not add code here.
"""
import sys as _sys

from libs.agents.scanner import candidate_risk as _canonical

_sys.modules[__name__] = _canonical
