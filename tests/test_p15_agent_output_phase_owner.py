from types import SimpleNamespace
from libs.contracts.agent_output_parts.artifact_metadata import phase
def test_phase_cases():
    f=SimpleNamespace(); assert phase({'runtime_phase':' live '},facade=f)=='live'; assert phase({'runtime_phase':'','phase':' open '},facade=f)=='open'; assert phase({},facade=f)==''
