"""Capture a supplied CLI callable; no CLI is imported or selected here."""
from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from typing import Any, Callable, List, Tuple


def capture_cli_json(main_fn: Callable[[List[str]], Any], argv: List[str]) -> Tuple[int, Any]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main_fn(argv)
    out = buf.getvalue().strip()
    if not out:
        return int(rc), {}
    try:
        return int(rc), json.loads(out)
    except Exception:
        return int(rc), {}
