from types import SimpleNamespace
from libs.contracts.agent_output_parts.artifact_validation import required_keys_for_artifact
def test_required_artifact_keys():
    calls=[]; f=SimpleNamespace(_required_keys_for_agent=lambda a:(calls.append(a) or ['base',a]))
    a=required_keys_for_artifact({'agent':'commander','mode':'shadow'},facade=f); b=required_keys_for_artifact({'agent':'commander','shadow_only':True},facade=f)
    assert a==b and a[-1]=='generated_at'; assert required_keys_for_artifact({'agent':'scanner'},facade=f)==['base','scanner'] and calls==['scanner']
