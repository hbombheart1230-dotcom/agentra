from types import SimpleNamespace
from libs.contracts.agent_output_parts.commander_shadow_assessments import post_monitor_assessment

def test_gate_alias_slice_and_order():
    calls = []
    facade = SimpleNamespace(_clip=lambda value, max_len: calls.append(max_len) or str(value or '')[:max_len])
    details = {'failed_gates': list(range(10)), 'passed_gates': list(range(12)), 'entry_block_reason': 'B'*190, 'primary_failure_axis': 'A'*90}
    result = post_monitor_assessment(actual_runtime={'monitor_decision': 'BUY'}, monitor_gate_details=details, facade=facade)
    if not (result['monitor_gate_details'] is details): raise AssertionError('failed: test_p15_shadow_post_monitor_owner')
    if not (result['failed_gates'] == list(range(8)) and result['passed_gates'] == list(range(8))): raise AssertionError('failed: test_p15_shadow_post_monitor_owner')
    if not (result['entry_block_reason'] == 'B'*180 and result['primary_failure_axis'] == 'A'*80): raise AssertionError('failed: test_p15_shadow_post_monitor_owner')
    if not (list(result) == ['monitor_decision','entry_block_reason','failed_gates','passed_gates','primary_failure_axis','monitor_gate_details']): raise AssertionError('failed: test_p15_shadow_post_monitor_owner')
    if not (calls == [24, 180, 80]): raise AssertionError('failed: test_p15_shadow_post_monitor_owner')

def test_empty_gates():
    facade = SimpleNamespace(_clip=lambda value, max_len: str(value or '')[:max_len])
    result = post_monitor_assessment(actual_runtime={}, monitor_gate_details={}, facade=facade)
    if not (result['failed_gates'] == [] and result['passed_gates'] == [] and result['monitor_decision'] == ''): raise AssertionError('failed: test_p15_shadow_post_monitor_owner')
