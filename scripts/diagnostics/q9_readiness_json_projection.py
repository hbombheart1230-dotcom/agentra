from pathlib import Path
from typing import Any
def _read_json(path:Path,*,facade:Any)->dict[str,Any]:
 try:
  payload=facade.json.loads(path.read_text(encoding="utf-8-sig"));return payload if isinstance(payload,dict) else {}
 except Exception:return {}
