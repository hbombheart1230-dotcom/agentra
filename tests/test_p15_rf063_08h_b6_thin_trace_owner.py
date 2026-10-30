import unittest
from scripts.diagnostics import check_reporter_upgrade_regression as s
class T(unittest.TestCase):
 def test_empty_and_complete(self):self.assertTrue(s._thin_trace({}));self.assertFalse(s._thin_trace({"scanner_selection_trace":{"ranked_candidates":[1]},"monitor_stop_policy_trace":{"x":1}}))
