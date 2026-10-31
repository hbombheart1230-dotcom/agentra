import unittest
from scripts.diagnostics import generate_ops_diagnostic_report as s
class T(unittest.TestCase):
 def test_v(self):self.assertIn('# Ops Diagnostic Report',s._build_markdown({'day':'x'}))
