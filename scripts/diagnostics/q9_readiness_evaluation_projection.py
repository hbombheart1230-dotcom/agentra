from typing import Any
def _evaluate(*,phase:str,day:str,live:dict[str,Any],processes:dict[str,Any],q9:dict[str,Any],artifacts:dict[str,Any],facade:Any)->tuple[list[dict[str,Any]],list[dict[str,Any]]]:
 blockers=[];warnings=[]
 if phase in {'preopen','intraday'}:
  if not live.get('running'):blockers.append({'code':'live_session_not_running'})
  elif facade.to_int(live.get('heartbeat_age_sec'),999999)>180:blockers.append({'code':'live_heartbeat_stale','age_sec':live.get('heartbeat_age_sec')})
  for name,row in processes.items():
   if not row.get('running'):blockers.append({'code':f'{name}_loop_not_running'})
   if facade.to_int(row.get('process_count'),0)>2:warnings.append({'code':f'{name}_duplicate_processes','pids':row.get('pids')})
 if phase=='intraday':
  now=facade.datetime.now(facade.KST)
  if (now.hour,now.minute)>=(9,10):
   first=facade._parse_dt(q9.get('first_window_kst'))
   if not first:blockers.append({'code':'q9_first_window_missing_after_0910'})
   elif (first.hour,first.minute)>(9,5):blockers.append({'code':'q9_first_window_late','first_window_kst':first.isoformat()})
 if phase=='closeout':
  for group,rows in artifacts.items():
   for key,record in rows.items():
    if not record.get('exists'):blockers.append({'code':f'{group}_{key}_missing','path':record.get('path')})
  if day>=facade.Q10_LEAD_MARKET_ACTIVATION_DAY:
   preopen=(artifacts.get('q10') or {}).get('lead_market_preopen') or {}
   if preopen.get('capture_status')!='CAPTURED':blockers.append({'code':'q10_lead_market_preopen_not_captured','capture_status':preopen.get('capture_status') or 'MISSING','path':preopen.get('path')})
  if q9.get('day_validity_status')=='INVALID':blockers.append({'code':'q9_day_invalid','blockers':q9.get('validity_blockers')})
  elif q9.get('day_validity_status') not in {'VALID',''}:warnings.append({'code':'q9_day_not_final_valid','status':q9.get('day_validity_status')})
 return blockers,warnings
