"""Compatibility shim (V4-056): the implementation lives in ``libs.agents.scanner.policy.guidance``.

This module is replaced in ``sys.modules`` by the canonical module object, so the old and new import paths are the
*same* module (identity, private names, use-time monkeypatch). There is exactly one implementation; do not add code here.
"""
import sys as _sys

from libs.agents.scanner.policy import guidance as _canonical

_sys.modules[__name__] = _canonical
