import unittest
from scripts.diagnostics import check_reporter_upgrade_regression as s
class T(unittest.TestCase):
 def test_delta_and_default(self):self.assertEqual(s.compare_days({"day":"a","closed_trades":2},{"day":"b","closed_trades":5})["deltas"]["closed_trades"],3);self.assertEqual(s.compare_days({}, {})["deltas"]["thin_trace_count"],0)
