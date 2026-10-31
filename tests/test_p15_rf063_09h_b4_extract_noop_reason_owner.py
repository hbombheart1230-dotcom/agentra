import unittest
from scripts.diagnostics import generate_ops_diagnostic_report as s
class T(unittest.TestCase):
 def test_v(self):self.assertEqual(s._extract_noop_reason({}),'unknown');self.assertEqual(s._extract_noop_reason({'decision_packet':{'intent':{'reason':'A'}}}),'A')
