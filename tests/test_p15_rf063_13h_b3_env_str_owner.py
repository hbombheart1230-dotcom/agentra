import unittest
from scripts.diagnostics import query_m25_notification_events as s
class T(unittest.TestCase):
 def test_v(self):self.assertEqual(s._env_str('_NO_SUCH_','d'),'d')
