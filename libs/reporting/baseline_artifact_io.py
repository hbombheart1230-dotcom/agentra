"""Mutable baseline JSON dictionaries; not atomic/immutable vnext publication."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


def read_json_dict(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def write_json_dict(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Explicit LF guarantees identical bytes on Linux and Windows.\n    path.write_text(json.dumps(dict(payload), ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
