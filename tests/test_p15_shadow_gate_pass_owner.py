from types import SimpleNamespace
from libs.contracts.agent_output_parts.commander_shadow_checks import gate_pass
def test_gate_pass_cases():
    f=SimpleNamespace(); assert gate_pass({'x':False},['x'],[], 'x',facade=f) is False; assert gate_pass({},['x'],['x'],'x',facade=f) is True; assert gate_pass({},[],['x'],'x',facade=f) is False; assert gate_pass({},[],[],'x',facade=f) is None
