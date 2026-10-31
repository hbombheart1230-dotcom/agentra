import unittest
from scripts.diagnostics import query_trade_reason_chain as s
class T(unittest.TestCase):
 def test_v(self):self.assertEqual(s._event_intent_id({'intent_id':'A'}),'A');self.assertEqual(s._event_intent_id({}),'')
