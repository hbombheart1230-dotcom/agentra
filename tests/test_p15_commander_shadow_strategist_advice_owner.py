from libs.contracts.agent_outputs import _commander_shadow_strategist_recommendation
from libs.contracts.agent_output_parts.commander_shadow_advice import strategist_recommendation


def test_skip_reason_and_llm_unstable_recommendations():
    assert _commander_shadow_strategist_recommendation(no_trade_reason_code="RISK_BLOCKED", observations={}) == "SKIP"
    assert _commander_shadow_strategist_recommendation(no_trade_reason_code="LLM_UNSTABLE", observations={"last_llm_status": "partial"}) == "RETRY_COMPACT"
    assert _commander_shadow_strategist_recommendation(no_trade_reason_code="LLM_UNSTABLE", observations={"last_llm_status": "fallback"}) == "USE_FALLBACK"
    assert _commander_shadow_strategist_recommendation(no_trade_reason_code="LLM_UNSTABLE", observations={"last_llm_status": "error"}) == "RETRY_MINIMAL"
    assert strategist_recommendation(no_trade_reason_code="", observations={}) == "RUN"
