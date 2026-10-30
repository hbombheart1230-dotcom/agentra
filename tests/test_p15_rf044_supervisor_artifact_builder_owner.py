from libs.contracts.agent_outputs import build_supervisor_output_artifact
def test_blocked(): assert build_supervisor_output_artifact({},order={'action':'BUY','qty':2},allowed=False,reason='risk')['status']=='blocked'
