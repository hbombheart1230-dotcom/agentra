import os,unittest
from unittest.mock import patch
from scripts.diagnostics import check_alert_policy_v1 as a
from scripts.diagnostics import check_metrics_schema_v1 as m
class T(unittest.TestCase):
 def test_b1_b2(self):self.assertEqual(a._to_float('1.5'),1.5);self.assertEqual(a._to_float('x',2),2);self.assertEqual(a._to_int('2.9'),2);self.assertEqual(a._to_int('x',4),4)
 def test_b3_b4_b5(self):
  with patch.dict(os.environ,{'X':'0.4','Y':'7.9','ALERT_POLICY_FAIL_ON':'WARNING'},clear=True):self.assertEqual(a._env_float('X',.7),.4);self.assertEqual(a._env_int('Y',3),7);self.assertEqual(a._env_fail_on(),'warning')
 def test_b6(self):self.assertTrue(a._build_parser().parse_args(['--json','--fail-on','none']).json)
 def test_b7_b8(self):self.assertTrue(m._is_number(1));self.assertFalse(m._is_number(True));self.assertEqual(m._json_path_get({'a':{'b':0}},'a.b'),(True,0));self.assertEqual(m._json_path_get({'a':{}},'a.c'),(False,None))
if __name__=='__main__':unittest.main()
