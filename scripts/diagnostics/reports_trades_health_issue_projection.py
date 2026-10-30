from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def _issue(*, severity: str, trade_id: str, component: str, code: str, message: str, path: Path, facade: Any) -> Dict[str, Any]:
    return {"severity": severity, "trade_id": trade_id, "component": component, "code": code, "message": message, "path": str(path)}
