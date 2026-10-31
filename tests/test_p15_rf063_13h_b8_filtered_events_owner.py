import unittest
from scripts.diagnostics import query_commander_resilience_events as s
class T(unittest.TestCase):
 def test_v(self):self.assertEqual(len(s._filtered_events([{'stage':'commander_router','event':'error'},{'stage':'x','event':'error'}])),1)
