import unittest
from scripts.diagnostics import query_m25_notification_events as s
class T(unittest.TestCase):
 def test_v(self):self.assertTrue(s._build_parser().parse_args(['--json']).json)
