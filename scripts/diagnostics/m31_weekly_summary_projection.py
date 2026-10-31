from typing import Any, Dict
def _item(*,item_id:str,title:str,passed:bool,evidence:str,required:bool=True)->Dict[str,Any]:
    return {"id":item_id,"title":title,"required":bool(required),"passed":bool(passed),"evidence":str(evidence)}
