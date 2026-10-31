import io,unittest
from contextlib import redirect_stdout
from scripts.diagnostics import query_strategist_llm_events as s
from scripts.diagnostics import strategist_query_render_projection as owner
class T(unittest.TestCase):
 def test_nonempty_stdout_parity_and_format(self):
  rows=[{'payload':{'ok':True,'intent_action':'buy','intent_reason':'signal'}},{'payload':{'ok':False,'intent_action':'hold','intent_reason':'risk'}}]
  wrapped, owned=io.StringIO(),io.StringIO()
  with redirect_stdout(wrapped): s._print_summary(rows)
  with redirect_stdout(owned): owner._print_summary(rows,facade=s)
  self.assertEqual(wrapped.getvalue(),owned.getvalue())
  self.assertEqual(wrapped.getvalue(), 'summary.call_kind= {"legacy_trade_intent": {"ok": 1}, "unknown": {"non_ok": 1}}\nsummary.intent_action= {"buy": 1, "hold": 1}\nsummary.intent_reason_top= [["signal", 1], ["risk", 1]]\n')
