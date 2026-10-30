import pytest
from types import SimpleNamespace
from libs.contracts.agent_output_parts.commander_shadow_advice_extended import reason_summary

@pytest.mark.parametrize('code,status,monitor,executor,expected', [
    ('NONE', None, 'BUY', 'NONE', 'Observed runtime ended with monitor=BUY and executor=NONE without a stronger commander block signal.'),
    ('LLM_UNSTABLE', 'error', None, None, 'Recent strategist LLM status was error, so a compact or minimal retry would have been safer than a full refresh.'),
    ('UNKNOWN', None, None, None, 'Shadow commander observed the cycle, but the evidence was limited and should be treated as advisory only.'),
])
def test_exact_text(code, status, monitor, executor, expected):
    calls = []
    facade = SimpleNamespace(_clip=lambda value, max_len: calls.append(max_len) or str(value or '')[:max_len])
    if not (reason_summary(no_trade_reason_code=code, observations={'last_llm_status': status}, actual_runtime={'monitor_decision': monitor, 'executor_action': executor}, facade=facade) == expected): raise AssertionError('failed: test_p15_shadow_reason_summary_owner')
    if not (calls == [40, 24, 24]): raise AssertionError('failed: test_p15_shadow_reason_summary_owner')
