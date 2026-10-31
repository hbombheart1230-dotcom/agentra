from typing import Any,Dict,List
def _is_incident_event(rec:Dict[str,Any],*,facade:Any)->bool:
 event=str(rec.get('event') or '');payload=rec.get('payload') if isinstance(rec.get('payload'),dict) else {};return event=='error' or(event=='transition' and str(payload.get('transition') or '')=='cooldown')or(event=='resilience' and str(payload.get('reason') or '') in ('cooldown_active','incident_threshold_cooldown'))
def _filtered_events(rows:List[Dict[str,Any]],*,run_id:str='',only_incidents:bool=False,include_route:bool=False,facade:Any)->List[Dict[str,Any]]:
 out=[]
 for rec in rows:
  if rec.get('stage')!='commander_router':continue
  event=str(rec.get('event') or '')
  if event=='route' and not include_route:continue
  if run_id and str(rec.get('run_id') or '')!=run_id:continue
  if only_incidents and not facade._is_incident_event(rec):continue
  out.append(rec)
 return out
