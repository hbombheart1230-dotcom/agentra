from typing import Any
def _env_str(name:str,default:str,*,facade:Any)->str:
 raw=str(facade.os.getenv(name,'') or '').strip();return raw if raw else str(default)
