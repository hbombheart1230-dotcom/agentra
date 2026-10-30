from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Optional


def _iter_events(path: Path, *, facade: Any) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []
    def _gen() -> Iterable[Dict[str, Any]]:
        with path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    obj = facade.json.loads(line)
                except Exception:
                    continue
                if isinstance(obj, dict):
                    yield obj
    return _gen()


def _read_json(path: Path, *, facade: Any) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = facade.json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _to_day_key(ts: Any, *, facade: Any) -> Optional[str]:
    if ts is None:
        return None
    text = str(ts).strip()
    if not text:
        return None
    try:
        epoch = int(float(text))
        return facade.datetime.fromtimestamp(epoch, tz=facade.timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        pass
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = facade.datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=facade.timezone.utc)
        return dt.astimezone(facade.timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return None


def _resolve_day(event_log_path: Path, requested_day: Optional[str], *, facade: Any) -> str:
    if requested_day:
        return str(requested_day).strip()
    days = sorted({d for row in facade._iter_events(event_log_path) if (d := facade._to_day_key(row.get("ts") or row.get("ts_kst")))})
    if days:
        return days[-1]
    return facade.date.today().isoformat()


def _safe_rel(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path)


def _pick_latest_canonical_run_id(reports_root: Path, day: str) -> str:
    base = reports_root / "canonical" / day
    if not base.exists():
        return ""
    candidates = [path for path in base.iterdir() if path.is_dir()]
    if not candidates:
        return ""
    latest = max(candidates, key=lambda path: path.stat().st_mtime)
    return latest.name
