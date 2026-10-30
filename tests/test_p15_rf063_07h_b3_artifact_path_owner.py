import tempfile, unittest
from pathlib import Path
from scripts.diagnostics import check_reports_trades_health as subject
class TestArtifactPath(unittest.TestCase):
 def test_first_existing_and_negative(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); (root/"b").write_text("x"); self.assertEqual(subject._artifact_path(root,"a","b"),root/"b"); self.assertEqual(subject._artifact_path(root,"a"),root/"a")
   with self.assertRaises(IndexError): subject._artifact_path(root)
