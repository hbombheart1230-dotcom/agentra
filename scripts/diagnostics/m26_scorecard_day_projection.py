from typing import Any


def _utc_day(ts: Any, *, facade: Any) -> str:
    ep = facade._to_epoch(ts)
    if ep is None:
        return facade.datetime.now(facade.timezone.utc).strftime("%Y-%m-%d")
    return facade.datetime.fromtimestamp(ep, tz=facade.timezone.utc).strftime("%Y-%m-%d")
