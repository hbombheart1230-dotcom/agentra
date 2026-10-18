"""Real R7 source mutation probes; set AGENTRA_REVIEW_ROOT to its checkout."""
import ast
import copy
import os
from pathlib import Path
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/refactor"))

import reporter_facade_guard as G


ROOT = Path(__file__).resolve().parents[1]
REVIEWED = os.environ.get("AGENTRA_REVIEW_SHA", G.REVIEWED)
PATH = "libs/reporting/trade_report_ai.py"


class FacadeGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = [r for r in G.moves(ROOT, REVIEWED) if r["path"] == PATH]
        cls.base = G.git_text(ROOT, G.BASE, PATH)
        cls.source = (ROOT / PATH).read_text(encoding="utf-8-sig")

    def reject(self, mutate):
        tree = ast.parse(self.source)
        mutate(tree)
        with self.assertRaises(AssertionError):
            G.verify_facade(self.base, ast.unparse(tree), self.rows, PATH)

    def test_all_registered_facades_restore_to_base(self):
        self.assertEqual(G.verify_tree(ROOT, reviewed=REVIEWED)["moves"],
                         G.PINNED_INVENTORIES[REVIEWED])

    def test_same_path_unmoved_function_body_change(self):
        def mutate(tree):
            fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                      and n.name == "_build_skipped_separated_report")
            fn.body = ast.parse("return {'silently_changed': True}").body
        self.reject(mutate)

    def test_module_assignment_change(self):
        def mutate(tree):
            tree.body.append(ast.parse("logger = None").body[0])
        self.reject(mutate)

    def test_module_executable_call(self):
        self.reject(lambda t: t.body.append(ast.parse("print('unauthorized')").body[0]))

    def test_extra_import(self):
        self.reject(lambda t: t.body.insert(1, ast.parse("import os as rogue").body[0]))

    def test_unapproved_owner_symbol_import(self):
        def mutate(tree):
            imp = next(n for n in tree.body if isinstance(n, ast.ImportFrom)
                       and n.module == "libs.agents.reporter.narrative.report_ai_bodies_01")
            imp.names.append(ast.alias(name="rogue"))
        self.reject(mutate)

    def test_owner_import_redirect(self):
        def mutate(tree):
            imp = next(n for n in tree.body if isinstance(n, ast.ImportFrom)
                       and n.module == "libs.agents.reporter.narrative.report_ai_bodies_01")
            imp.module = "libs.agents.reporter.narrative.unapproved"
        self.reject(mutate)

    def test_late_owner_import(self):
        def mutate(tree):
            imp = next(n for n in tree.body if isinstance(n, ast.ImportFrom)
                       and n.module == "libs.agents.reporter.narrative.report_ai_bodies_01")
            tree.body.remove(imp)
            tree.body.append(imp)
        self.reject(mutate)

    def test_wrapper_argument_substitution(self):
        def mutate(tree):
            fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                      and n.name == "_sanitize_report_language_fields")
            fn.body[0].value.args[0] = ast.Constant(value=None)
        self.reject(mutate)

    def test_wrapper_extra_statement(self):
        def mutate(tree):
            fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                      and n.name == "_sanitize_report_language_fields")
            fn.body.insert(0, ast.parse("value = None").body[0])
        self.reject(mutate)

    def test_wrapper_signature_mutation(self):
        def mutate(tree):
            fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                      and n.name == "_sanitize_report_language_fields")
            fn.args.defaults.append(ast.Constant(value=None))
        self.reject(mutate)

    def test_duplicate_wrapper(self):
        def mutate(tree):
            fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                      and n.name == "_sanitize_report_language_fields")
            tree.body.append(copy.deepcopy(fn))
        self.reject(mutate)

    def test_original_module_statement_order(self):
        def mutate(tree):
            original = next(n for n in tree.body if isinstance(n, ast.ImportFrom)
                            and n.module == "__future__")
            tree.body.remove(original)
            tree.body.append(original)
        self.reject(mutate)


if __name__ == "__main__":
    unittest.main()
