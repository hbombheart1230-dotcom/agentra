import io,unittest
from contextlib import redirect_stdout
from pathlib import Path
from scripts.diagnostics import query_strategist_llm_events as s
from scripts.diagnostics import strategist_query_render_projection as owner
class T(unittest.TestCase):
 def test_nonempty_stdout_parity_and_format(self):
  rows=[{'ts':'2026-10-31T01:02:03Z','run_id':'r1','payload':{'ok':True,'intent_action':'buy','intent_reason':'signal','latency_ms':7,'attempts':1}}]
  wrapped, owned=io.StringIO(),io.StringIO()
  with redirect_stdout(wrapped): s._print_human(Path('x'),rows)
  with redirect_stdout(owned): owner._print_human(Path('x'),rows,facade=s)
  self.assertEqual(wrapped.getvalue(),owned.getvalue())
  self.assertEqual(wrapped.getvalue(), "=== Strategist LLM Events ===\npath=x\nshown=1\n2026-10-31T01:02:03Z run_id=r1 call_kind=legacy_trade_intent ok=True action=buy reason=signal latency_ms=7 attempts=1 prompt_version= schema_version= prompt_tokens=None completion_tokens=None total_tokens=None estimated_cost_usd=None context_regime= context_signal_score=None context_symbol_sentiment_score=None context_global_sentiment_score=None context_symbol_sentiment_status= context_global_sentiment_status= context_composite_score=None error_type=\n")
