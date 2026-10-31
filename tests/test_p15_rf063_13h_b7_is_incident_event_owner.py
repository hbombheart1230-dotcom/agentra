import unittest
from scripts.diagnostics import query_commander_resilience_events as s
class T(unittest.TestCase):
 def test_v(self):self.assertTrue(s._is_incident_event({'event':'error'}));self.assertFalse(s._is_incident_event({'event':'route'}))
