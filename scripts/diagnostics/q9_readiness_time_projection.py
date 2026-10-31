from typing import Any
def _parse_dt(value:Any,*,facade:Any)->Any:
 text=str(value or "").strip()
 if not text:return None
 try:parsed=facade.datetime.fromisoformat(text.replace("Z","+00:00"))
 except ValueError:return None
 if parsed.tzinfo is None:parsed=parsed.replace(tzinfo=facade.timezone.utc)
 return parsed.astimezone(facade.KST)
