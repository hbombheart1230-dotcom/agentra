import unittest
from scripts.diagnostics import query_trade_reason_chain as s
class T(unittest.TestCase):
 def test_v(self):self.assertEqual(s._build_rows([{'run_id':'r','stage':'execute_from_packet','event':'execution','payload':{'order':{'action':'BUY','symbol':'T'},'payload':{'broker_code':'0'}}}])[0]['action'],'BUY')
