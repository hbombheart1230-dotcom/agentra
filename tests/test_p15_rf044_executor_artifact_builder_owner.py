from libs.contracts.agent_outputs import build_executor_output_artifact
def test_blocked(): assert build_executor_output_artifact({},execution={'allowed':False,'status':'rejected'},order={'action':'BUY','qty':1})['final_execution_status']=='rejected'
