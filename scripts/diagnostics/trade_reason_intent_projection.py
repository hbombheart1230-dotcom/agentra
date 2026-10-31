from __future__ import annotations
from typing import Any,Dict,Optional
def _event_intent_id(payload: Dict[str,Any], *, facade: Any) -> Optional[str]:
    packet=payload.get("decision_packet");packet=packet if isinstance(packet,dict) else {};intent=packet.get("intent");intent=intent if isinstance(intent,dict) else {};ids={str(v).strip() for v in (payload.get("intent_id"),packet.get("intent_id"),intent.get("intent_id")) if v is not None and str(v).strip()};return next(iter(ids)) if len(ids)==1 else None if ids else ""
