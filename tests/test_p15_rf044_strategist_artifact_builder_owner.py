from libs.contracts.agent_outputs import build_strategist_output_artifact
def test_empty(): assert build_strategist_output_artifact({})['agent']=='strategist'
