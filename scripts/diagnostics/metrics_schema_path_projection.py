from typing import Any,Dict,Tuple
def _json_path_get(obj:Dict[str,Any],path:str)->Tuple[bool,Any]:
 cur:Any=obj
 for part in path.split('.'):
  if not isinstance(cur,dict) or part not in cur:return False,None
  cur=cur[part]
 return True,cur
