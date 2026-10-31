from pathlib import Path
from typing import Any
def _baseline_artifacts(root:Path,day:str,*,facade:Any)->dict[str,Any]:
 a=facade._artifact;e=root/'evaluation';q10=e/'baseline_samsung_hynix'/day;q11=e/'opportunity_engine_shadow'/day;q12=e/'baseline_btc_woori_tech'/day
 out={'q10':{'decisions':a(q10/'baseline_samsung_hynix_decisions.json'),'forward':a(q10/'baseline_samsung_hynix_forward_returns.json'),'comparison':a(q10/'q9_vs_samsung_hynix_daily_comparison.json')},'q11':{'signals':a(q11/'opportunity_engine_signals.json'),'virtual_trades':a(q11/'opportunity_engine_virtual_trades.json'),'report':a(q11/'opportunity_engine_daily_report.json')},'q12':{'decisions':a(q12/'baseline_btc_woori_decisions.json'),'forward':a(q12/'baseline_btc_woori_forward_returns.json'),'comparison':a(q12/'baseline_btc_woori_comparison.json'),'hypothesis_validation':a(q12/'q12_btc_woori_hypothesis_validation.json'),'hypothesis_cumulative':a(e/'baseline_btc_woori_tech'/'hypothesis_validation'/'q12_btc_woori_hypothesis_cumulative.json')}}
 if day>=facade.Q10_LEAD_MARKET_ACTIVATION_DAY:
  r=q10/'q10_forward_validation';out['q10'].update({'lead_market_preopen':a(r/'q10_preopen_signal_snapshot.json'),'lead_market_reactions':a(r/'q10_actual_market_reactions.json'),'lead_market_expected_actual':a(r/'q10_expected_vs_actual.json'),'lead_market_shadow':a(r/'q10_shadow_entry_comparison.json'),'lead_market_report':a(r/'q10_forward_validation_report.md')})
 return out
