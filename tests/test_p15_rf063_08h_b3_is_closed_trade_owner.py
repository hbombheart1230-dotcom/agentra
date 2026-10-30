import unittest
from scripts.diagnostics import check_reporter_upgrade_regression as s
class T(unittest.TestCase):
 def test_cases(self):
  self.assertFalse(s._is_closed_trade({"lifecycle":{"exit":{}}}))
  self.assertTrue(s._is_closed_trade({"lifecycle":{"exit":{"x":1}}}))
  self.assertTrue(s._is_closed_trade({"status":"closed"}))
  self.assertFalse(s._is_closed_trade({}))
