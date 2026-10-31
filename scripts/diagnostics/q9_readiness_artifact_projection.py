from pathlib import Path
from typing import Any
def _artifact(path:Path,*,facade:Any)->dict[str,Any]:
 payload=facade._read_json(path);exists=path.exists()
 return {"path":str(path),"exists":exists,"size_bytes":path.stat().st_size if exists else 0,"schema_version":payload.get("schema_version") or "","capture_status":payload.get("capture_status") or "","evidence_status":payload.get("evidence_status") or ""}
