from typing import Any
def _env_float(name:str,default:float,*,facade:Any)->float:
 raw=str(facade.os.getenv(name,"") or "").strip();return float(default) if not raw else facade._to_float(raw,float(default))
def _env_int(name:str,default:int,*,facade:Any)->int:
 raw=str(facade.os.getenv(name,"") or "").strip();return int(default) if not raw else facade._to_int(raw,int(default))
def _env_fail_on(default:str="critical",*,facade:Any)->str:
 raw=str(facade.os.getenv("ALERT_POLICY_FAIL_ON","") or "").strip().lower();return raw if raw in ("none","warning","critical") else str(default)
