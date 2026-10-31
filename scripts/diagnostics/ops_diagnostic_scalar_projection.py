from __future__ import annotations
from typing import Any, Optional
def _to_epoch(ts: Any, *, facade: Any) -> Optional[int]:
    if ts is None:return None
    if isinstance(ts,(int,float)):return int(ts)
    s=str(ts).strip()
    if not s:return None
    try:return int(float(s))
    except Exception:pass
    if s.endswith("Z"):s=s[:-1]+"+00:00"
    try:
        dt=facade.datetime.fromisoformat(s)
        if dt.tzinfo is None:dt=dt.replace(tzinfo=facade.timezone.utc)
        return int(dt.timestamp())
    except Exception:return None
def _utc_day(ts: Any, *, facade: Any) -> str:
    epoch=facade._to_epoch(ts)
    if epoch is None:return facade.date.today().isoformat()
    return facade.datetime.fromtimestamp(epoch,tz=facade.timezone.utc).strftime("%Y-%m-%d")
def _to_float(v: Any, *, facade: Any) -> Optional[float]:
    try:return None if v is None else float(v)
    except Exception:return None
