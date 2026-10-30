from types import SimpleNamespace
from libs.contracts.agent_output_parts.artifact_validation import required_keys_for_agent
def test_required_agent_keys():
    f=SimpleNamespace(); unknown=required_keys_for_agent('unknown',facade=f); assert unknown==['schema_version','agent','run_id','day','ts','phase','status']
    executor=required_keys_for_agent(' executor ',facade=f); assert executor[:7]==unknown and executor[-1]=='failure_reason'
    commander=required_keys_for_agent('COMMANDER',facade=f); assert commander.count('phase')==2 and commander is not required_keys_for_agent('commander',facade=f)
