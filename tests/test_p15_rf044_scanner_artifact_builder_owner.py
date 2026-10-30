from libs.contracts.agent_outputs import build_scanner_output_artifact
def test_empty(): assert build_scanner_output_artifact({})['agent']=='scanner'
