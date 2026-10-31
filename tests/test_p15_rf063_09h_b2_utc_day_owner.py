import unittest
from scripts.diagnostics import generate_ops_diagnostic_report as s
class T(unittest.TestCase):
 def test_v(self):self.assertEqual(s._utc_day('2026-10-31T01:00:00Z'),'2026-10-31')
