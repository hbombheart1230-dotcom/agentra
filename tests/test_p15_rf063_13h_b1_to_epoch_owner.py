import unittest
from scripts.diagnostics import query_m25_notification_events as s
class T(unittest.TestCase):
 def test_v(self):self.assertIsInstance(s._to_epoch('2026-10-31T00:00:00Z'),int);self.assertIsNone(s._to_epoch(''))
