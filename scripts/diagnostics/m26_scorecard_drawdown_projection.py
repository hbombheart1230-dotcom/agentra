from typing import List, Tuple
def _max_drawdown_ratio(equity:List[float])->Tuple[float,float]:
 if not equity:return 0.0,0.0
 peak=float(equity[0]);max_dd=max_dd_ratio=0.0
 for v in equity:
  x=float(v);peak=max(peak,x);dd=peak-x;max_dd=max(max_dd,dd);denom=abs(peak) if abs(peak)>1e-12 else 0.0;max_dd_ratio=max(max_dd_ratio,(dd/denom) if denom>0 else 0.0)
 return float(max_dd),float(max_dd_ratio)
