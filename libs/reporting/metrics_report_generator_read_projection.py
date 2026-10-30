"""Metrics report generator JSONL event reader (moved verbatim from metrics_report_generator).

``json`` is resolved on ``facade`` (the metrics_report_generator module) at call time; this module never imports it.
Read-only; lazy generator.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable


def _iter_events(path: Path, *, facade: Any) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []

    def gen() -> Iterable[Dict[str, Any]]:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = facade.json.loads(line)
                except Exception:
                    continue
                if isinstance(obj, dict):
                    yield obj

    return gen()
