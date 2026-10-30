from libs.contracts.agent_outputs import build_commander_shadow_artifact
def test_empty(): assert build_commander_shadow_artifact({},mode='shadow',phase='test',path='none',status='ok')['mode']=='shadow'
