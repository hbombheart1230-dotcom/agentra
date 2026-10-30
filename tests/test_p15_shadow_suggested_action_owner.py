import pytest
from libs.contracts.agent_output_parts.commander_shadow_advice_extended import suggested_action

@pytest.mark.parametrize('rec,llm,reason,expected', [
    ('SKIP', 'RETRY_MINIMAL', 'POSITION_ALREADY_OPEN', 'monitor_only_observe'),
    ('SKIP', 'RETRY_COMPACT', 'REPEATED_SAME_CONTEXT', 'skip_strategist_reuse_context'),
    ('RUN', 'RETRY_COMPACT', 'NONE', 'compact_strategist_retry'),
    ('RUN', 'ALLOW', 'NONE', 'allow_current_flow'),
])
def test_priority(rec, llm, reason, expected):
    if not (suggested_action(strategist_action_recommendation=rec, llm_call_advice=llm, no_trade_reason_code=reason, facade=None) == expected): raise AssertionError('failed: test_p15_shadow_suggested_action_owner')
