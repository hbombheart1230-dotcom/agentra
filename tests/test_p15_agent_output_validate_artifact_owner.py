from types import SimpleNamespace
from libs.contracts.agent_output_parts.artifact_validation import validate_artifact
def test_validate_artifact_cases():
    f=SimpleNamespace(_required_keys_for_artifact=lambda o:['schema_version','agent'],_is_present=lambda x:x not in (None,''),AGENT_VALIDATION_SCHEMA_VERSION='v')
    assert validate_artifact({},facade=f)['status']=='invalid'; assert validate_artifact({'agent':'unknown'},facade=f)['status']=='partial'
    out=validate_artifact({'schema_version':'x','agent':'a'},facade=f); assert out['status']=='ok' and out['completeness_score']==1.0 and out['schema_version']=='v'
