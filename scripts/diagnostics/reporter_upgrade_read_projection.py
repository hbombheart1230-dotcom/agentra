from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
def _read_json(path: Path, *, facade: Any) -> Dict[str, Any]:
    try:
        if not path.exists(): return {}
        payload = facade.json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception: return {}
def _trade_dirs_for_day(reports_root: Path, day: str, *, facade: Any) -> List[Path]:
    base = reports_root / "trades" / str(day or "").strip()
    if not base.exists(): return []
    out = [path for path in base.iterdir() if path.is_dir()]
    out.sort(key=lambda p: p.name)
    return out
