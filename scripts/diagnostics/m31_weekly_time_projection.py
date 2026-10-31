from typing import Any, List, Optional

def _to_epoch(ts: Any, *, facade: Any) -> Optional[int]:
    if ts is None: return None
    if isinstance(ts, (int,float)): return int(ts)
    s=str(ts).strip()
    if not s: return None
    try: return int(float(s))
    except Exception: pass
    if s.endswith("Z"): s=s[:-1]+"+00:00"
    try:
        dt=facade.datetime.fromisoformat(s)
        if dt.tzinfo is None: dt=dt.replace(tzinfo=facade.timezone.utc)
        return int(dt.timestamp())
    except Exception: return None

def _utc_day(ts: Any, *, facade: Any) -> Optional[str]:
    e=facade._to_epoch(ts)
    return None if e is None else facade.datetime.fromtimestamp(e,tz=facade.timezone.utc).strftime("%Y-%m-%d")

def _parse_day(value: str, *, facade: Any) -> Any:
    return facade.datetime.strptime(value,"%Y-%m-%d").replace(tzinfo=facade.timezone.utc)

def _window_days(*, week_end: str, days: int, facade: Any) -> List[str]:
    end_dt=facade._parse_day(week_end); n=max(1,int(days)); cur=end_dt-facade.timedelta(days=n-1); out=[]
    while cur<=end_dt: out.append(cur.strftime("%Y-%m-%d")); cur+=facade.timedelta(days=1)
    return out
