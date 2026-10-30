from types import SimpleNamespace
from libs.contracts.agent_output_parts.commander_shadow_checks import score_from_checks
def test_score_checks_cases():
    f=SimpleNamespace(); assert score_from_checks(passed_checks=[],failed_checks=[],fallback='0.33333',facade=f)==.3333; assert score_from_checks(passed_checks=['a'],failed_checks=['b','c'],fallback='bad',facade=f)==.3333; assert score_from_checks(passed_checks=[],failed_checks=[],fallback=None,facade=f) is None; assert score_from_checks(passed_checks=[],failed_checks=[],fallback=2,facade=f)==2.0
