from types import SimpleNamespace
from libs.contracts.agent_output_parts.commander_shadow_checks import has_open_order
def test_has_open_order_cases():
    calls=[]; f=SimpleNamespace(_dict=lambda x:x if isinstance(x,dict) else {},_clip=lambda x,max_len:(calls.append(max_len) or str(x or '')[:max_len]))
    assert has_open_order({'monitor':{'order_lifecycle':{'stage':'pending','terminal':False}}},facade=f) is True; assert has_open_order({'monitor':{'order_lifecycle':{'stage':'filled'}}},facade=f) is False; assert has_open_order({'monitor':{'order_lifecycle':{'stage':'pending','terminal':True}}},facade=f) is False; assert has_open_order({},facade=f) is None and calls
