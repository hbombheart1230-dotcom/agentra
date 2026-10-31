import io,unittest
from contextlib import redirect_stdout
from pathlib import Path
from scripts.diagnostics import query_strategist_llm_events as s
class T(unittest.TestCase):
 def test_empty(self):
  out=io.StringIO()
  with redirect_stdout(out):s._print_human(Path('x'),[])
  self.assertIn('shown=0',out.getvalue())
