import unittest
from scripts.diagnostics import check_reporter_upgrade_regression as s
class T(unittest.TestCase):
 def test_facade_keys(self):
  b={"artifacts":{k:"x" for k in s.CANONICAL_ARTIFACT_KEYS}};self.assertFalse(s._missing_canonical_paths(b));b["artifacts"].pop(s.CANONICAL_ARTIFACT_KEYS[0]);self.assertTrue(s._missing_canonical_paths(b))
