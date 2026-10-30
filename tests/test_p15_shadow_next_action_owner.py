import pytest
from types import SimpleNamespace
from libs.contracts.agent_output_parts.commander_shadow_advice_extended import next_action_recommendation

@pytest.mark.parametrize('reason,rec,llm,monitor,expected', [
    ('POSITION_ALREADY_OPEN', 'RUN', 'RETRY_COMPACT', 'BUY', 'HOLD_OBSERVE'),
    ('NONE', 'USE_FALLBACK', 'ALLOW', 'BUY', 'RETRY_COMPACT_NEXT'),
    ('WAIT_FOR_CONFIRMATION', 'RUN', 'ALLOW', 'BUY', 'WAIT_NEXT_BAR'),
    ('NONE', 'RUN', 'ALLOW', 'HOLD', 'HOLD_OBSERVE'),
    ('NONE', 'RUN', 'ALLOW', None, 'NO_ACTION'),
])
def test_priority(reason, rec, llm, monitor, expected):
    calls = []
    facade = SimpleNamespace(_clip=lambda value, max_len: calls.append((value, max_len)) or str(value or '')[:max_len])
    if not (next_action_recommendation(strategist_action_recommendation=rec, llm_call_advice=llm, no_trade_reason_code=reason, actual_runtime={'monitor_decision': monitor}, facade=facade) == expected): raise AssertionError('failed: test_p15_shadow_next_action_owner')
    if not (len(calls) == (0 if reason in {'POSITION_ALREADY_OPEN','WAIT_FOR_CONFIRMATION'} or rec == 'USE_FALLBACK' else 1)): raise AssertionError('failed: test_p15_shadow_next_action_owner')
