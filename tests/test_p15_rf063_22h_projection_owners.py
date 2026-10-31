import unittest
from scripts.diagnostics import run_m26_scorecard as m
class T(unittest.TestCase):
 def test_b1_to_epoch(self):
  self.assertIsNone(m._to_epoch(None));self.assertEqual(m._to_epoch('0'),0);self.assertEqual(m._to_epoch('1970-01-01T00:00:00Z'),0);self.assertIsNone(m._to_epoch('bad'))
if __name__=='__main__':unittest.main()
