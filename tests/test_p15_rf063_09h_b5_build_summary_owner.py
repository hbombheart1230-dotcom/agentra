import unittest
from scripts.diagnostics import generate_ops_diagnostic_report as s
class T(unittest.TestCase):
 def test_v(self):self.assertEqual(s._build_summary([],day='x')['events'],0)
