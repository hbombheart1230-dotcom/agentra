from libs.contracts.agent_outputs import build_monitor_output_artifact
def test_empty(): assert build_monitor_output_artifact({})['agent']=='monitor'
