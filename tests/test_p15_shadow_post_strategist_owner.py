from types import SimpleNamespace
from libs.contracts.agent_output_parts.commander_shadow_assessments import post_strategist_assessment

def _facade():
    return SimpleNamespace(_dict=lambda x: x if isinstance(x, dict) else {}, _clip=lambda value, max_len: str(value or '')[:max_len])

def test_alias_and_key_order():
    delta = {'unchanged': ['x']}
    result = post_strategist_assessment(state={'strategist_output': {'playbook': 'P', 'llm_frame_status': 'fallback', 'market_regime': 'calm'}}, actual_runtime={'strategist_executed': True}, context_delta_summary=delta, recommendation_gap='aligned', facade=_facade())
    if not (result['context_delta_summary'] is delta): raise AssertionError('failed: test_p15_shadow_post_strategist_owner')
    if not (result['llm_status'] == 'fallback' and result['market_regime'] == 'calm'): raise AssertionError('failed: test_p15_shadow_post_strategist_owner')
    if not (list(result) == ['strategist_executed','llm_called_by_strategist','used_cached_strategist','llm_status','playbook','market_regime','market_sentiment','recommendation_gap','context_delta_summary']): raise AssertionError('failed: test_p15_shadow_post_strategist_owner')

def test_llm_priority_and_truncation():
    result = post_strategist_assessment(state={'strategist_llm': {'status': 'error'}, 'strategist_output': {'llm_frame_status': 'fallback', 'playbook': 'X'*50}}, actual_runtime={}, context_delta_summary={}, recommendation_gap='gap', facade=_facade())
    if not (result['llm_status'] == 'error' and result['playbook'] == 'X'*40): raise AssertionError('failed: test_p15_shadow_post_strategist_owner')
