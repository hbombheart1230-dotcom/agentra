import ast
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.diagnostics import run_m26_scorecard as m
from scripts.diagnostics import m26_scorecard_day_projection as day_owner
from scripts.diagnostics import m26_scorecard_jsonl_projection as jsonl_owner
from scripts.diagnostics import m26_scorecard_int_projection as int_owner
from scripts.diagnostics import m26_scorecard_float_projection as float_owner
from scripts.diagnostics import m26_scorecard_close_projection as close_owner
from scripts.diagnostics import m26_scorecard_parser_projection as parser_owner
from scripts.diagnostics import m26_scorecard_validate_projection as validate_owner


class ProjectionOwners(unittest.TestCase):
    def _thin(self, name):
        node = next(n for n in ast.parse(Path(m.__file__).read_text()).body if isinstance(n, ast.FunctionDef) and n.name == name)
        self.assertEqual(len(node.body), 2)  # local owner import plus one return facade call
        self.assertIsInstance(node.body[-1], ast.Return)

    def test_b2_utc_day(self):
        self.assertEqual(m._utc_day(0), "1970-01-01")
        self.assertEqual(m._utc_day(86400), "1970-01-02")
        with patch.object(m, "_to_epoch", return_value=None):
            self.assertEqual(m._utc_day("bad"), day_owner._utc_day("bad", facade=m))
        self._thin("_utc_day")

    def test_b3_iter_jsonl(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.jsonl"
            self.assertEqual(m._iter_jsonl(p), [])
            p.write_text('{"x":1}\nBAD\n[]\n', encoding="utf-8")
            self.assertEqual(m._iter_jsonl(p), [{"x": 1}])
            self.assertEqual(m._iter_jsonl(p), jsonl_owner._iter_jsonl(p, facade=m))
        self._thin("_iter_jsonl")

    def test_b4_safe_int(self):
        self.assertEqual(m._safe_int("3.9"), 3)
        self.assertEqual(m._safe_int("bad", 4), 4)
        self.assertEqual(m._safe_int("bad", 4), int_owner._safe_int("bad", 4))
        self._thin("_safe_int")

    def test_b5_safe_float(self):
        self.assertEqual(m._safe_float("1.25"), 1.25)
        self.assertEqual(m._safe_float("bad", 2.5), 2.5)
        self.assertTrue(math.isnan(m._safe_float(float("nan"))))
        self.assertTrue(math.isnan(float_owner._safe_float(float("nan"))))
        self._thin("_safe_float")

    def test_b6_load_close_price_by_symbol(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "prices.csv"
            self.assertEqual(m._load_close_price_by_symbol(p, day="1970-01-01"), {})
            p.write_text("symbol,ts,close\nA,1970-01-01T00:00:00Z,10\n", encoding="utf-8")
            expected = {"A": 10.0}
            self.assertEqual(m._load_close_price_by_symbol(p, day="1970-01-01"), expected)
            self.assertEqual(m._load_close_price_by_symbol(p, day="1970-01-01"), close_owner._load_close_price_by_symbol(p, day="1970-01-01", facade=m))
        self._thin("_load_close_price_by_symbol")

    def test_b7_build_parser(self):
        args = m._build_parser().parse_args(["--day", "2026-10-31", "--json"])
        self.assertEqual((args.day, args.json), ("2026-10-31", True))
        self.assertEqual(m._build_parser().description, parser_owner._build_parser(facade=m).description)
        self._thin("_build_parser")

    def test_b8_validate_required(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            failures, missing = m._validate_required(root)
            self.assertIn("missing_required_files", failures)
            for rel in m.REQUIRED_FILES:
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text('{"schema_version":"m26.dataset_manifest.v1"}' if rel == "manifest.json" else "", encoding="utf-8")
            self.assertEqual(m._validate_required(root), ([], []))
            self.assertEqual(m._validate_required(root), validate_owner._validate_required(root, facade=m))
        self._thin("_validate_required")


if __name__ == "__main__":
    unittest.main()
