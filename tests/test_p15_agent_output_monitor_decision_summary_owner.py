from types import SimpleNamespace
from libs.contracts.agent_output_parts.monitor_decision_summary import monitor_decision_summary
def test_monitor_summary_cases():
    seen=[]; f=SimpleNamespace(_clip=lambda x,max_len: (seen.append(max_len) or str(x or '')[:max_len]), _dict=lambda x: x if isinstance(x,dict) else {})
    assert monitor_decision_summary(decision_phase='',primary_reason_text='',threshold_snapshot={},signal_snapshot={},missing_inputs=['foo'],facade=f)=='Decision: insufficient data (foo)'
    assert monitor_decision_summary(decision_phase='entry',primary_reason_text='',threshold_snapshot={'entry_thresholds':{'max_extended_from_vwap_pct':1.5}},signal_snapshot={'entry_pattern':'breakout'},missing_inputs=[],facade=f)=='Entry: breakout met with 1.5 -> BUY'
    assert monitor_decision_summary(decision_phase='hold',primary_reason_text='',threshold_snapshot={},signal_snapshot={},missing_inputs=[],facade=f)=='Hold: conditions stable, no exit trigger'
