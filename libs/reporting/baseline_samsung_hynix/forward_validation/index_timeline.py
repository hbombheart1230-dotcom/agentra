"""Q10 index macro-snapshot timeline reader Owner (moved from reaction_reader.load_index_timeline).

File reads happen only when the function is called (import is IO-free). ``facade`` is ``reaction_reader``.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping


def load_index_timeline_impl(*, day: str, macro_root: Path, index_name: str, facade: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((macro_root / day).glob("*_macro_indicators.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, Mapping):
                continue  # non-object JSON (e.g. a list) is skipped instead of aborting the whole timeline
            generated = datetime.fromisoformat(str(payload.get("generated_at") or "").replace("Z", "+00:00"))
            korea = payload.get("korea_indices")
            indices = korea.get("indices") if isinstance(korea, Mapping) else None
            item = (indices.get(index_name) if isinstance(indices, Mapping) else None) or {}
            if not isinstance(item, Mapping):
                continue
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError):
            continue
        current = facade._number(item.get("current"))
        if current is None:
            continue
        rows.append(
            {
                "ts": int(generated.timestamp()),
                "close": current,
                "open": facade._number(item.get("open")) or current,
                "high": facade._number(item.get("high")) or current,
                "low": facade._number(item.get("low")) or current,
                "volume": facade._number(item.get("volume")),
                "previous_close": facade._number(item.get("previous_close")),
                "source_path": str(path),
            }
        )
    return [row for _, row in sorted({int(row["ts"]): row for row in rows}.items())]

