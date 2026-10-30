from types import SimpleNamespace
from libs.contracts.agent_output_parts.commander_shadow_cycle import end_of_cycle_summary
def test_end_cycle_summary_cases():
    runtime={}; out=end_of_cycle_summary(no_trade_reason_code='n',reason_summary='r',actual_runtime=runtime,next_action_recommendation='a',recommendation_gap='g',facade=SimpleNamespace())
    assert list(out)==['no_trade_reason_code','reason_summary','actual_runtime','next_action_recommendation','recommendation_gap'] and out['actual_runtime'] is runtime
    assert end_of_cycle_summary(no_trade_reason_code=None,reason_summary=None,actual_runtime=runtime,next_action_recommendation=None,recommendation_gap=None,facade=SimpleNamespace())['reason_summary'] is None
