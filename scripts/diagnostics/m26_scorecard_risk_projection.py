from typing import Any, Dict, List
def _risk_adjusted(samples:List[float],*,facade:Any)->Dict[str,float]:
 if not samples:return {"sample_count":0.0,"pnl_mean":0.0,"pnl_std":0.0,"downside_std":0.0,"sharpe_proxy":0.0,"sortino_proxy":0.0}
 n=float(len(samples));mean=float(facade.statistics.fmean(samples));std=float(facade.statistics.pstdev(samples)) if len(samples)>1 else 0.0;down=[x for x in samples if x<0];ds=float(facade.statistics.pstdev(down)) if len(down)>1 else (float(abs(down[0])) if len(down)==1 else 0.0);sh=(mean/std)*facade.math.sqrt(n) if std>1e-12 else 0.0;so=(mean/ds)*facade.math.sqrt(n) if ds>1e-12 else 0.0
 return {"sample_count":n,"pnl_mean":mean,"pnl_std":std,"downside_std":ds,"sharpe_proxy":float(sh),"sortino_proxy":float(so)}
