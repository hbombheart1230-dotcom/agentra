from libs.contracts.agent_outputs import build_commander_output_artifact
def test_empty(): assert build_commander_output_artifact({},mode='shadow',phase='test',path='none',status='ok')['agent']=='commander'
