import unittest
from scripts.diagnostics import generate_ops_diagnostic_report as s
class T(unittest.TestCase):
 def test_v(self):self.assertEqual(s._to_float('3.5'),3.5);self.assertIsNone(s._to_float('bad'))
