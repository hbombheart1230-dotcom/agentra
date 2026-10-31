from typing import Any
def _to_float(v:Any,default:float=0.0)->float:
 try:return float(v)
 except Exception:return default
def _to_int(v:Any,default:int=0)->int:
 try:return int(float(v))
 except Exception:return default
