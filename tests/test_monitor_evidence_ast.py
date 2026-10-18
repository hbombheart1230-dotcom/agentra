"""Cross-version inventory serialization must retain semantic differences."""
import ast
import copy

import pytest

from scripts.refactor.monitor_evidence_ast import evidence_dump


def test_frozen_profile_reproduces_both_observed_cpython_dump_formats():
    node = ast.parse("def f(x):\n    return x\n").body[0]
    assert evidence_dump(node) == (
        "FunctionDef(name='f', args=arguments(args=[arg(arg='x')]), "
        "body=[Return(value=Name(id='x', ctx=Load()))])"
    )
    # 3.12 exposes these empty fields in ast.dump; evidence omits only ASDL lists.
    assert node.decorator_list == [] and node.args.defaults == []
    assert evidence_dump(ast.Constant(value=[])) == "Constant(value=[])"
    assert evidence_dump(ast.Constant(value=None)) == "Constant(value=None)"


@pytest.mark.parametrize("before,after", [
    ("x = 1", "x = 2"), ("import os", "import subprocess"),
    ("x = a", "a = x"), ("f()", "f(1)"),
    ("def f():\n return 1", "def f():\n return 2"),
    ("x = []", "x = [None]"),
])
def test_semantic_source_mutations_remain_distinct(before, after):
    assert evidence_dump(ast.parse(before)) != evidence_dump(ast.parse(after))


def test_unknown_new_fields_are_serialized_rather_than_silently_discarded():
    class FutureNode(ast.AST):
        _fields = ("new_list", "new_optional")
    node = FutureNode(new_list=[], new_optional=None)
    assert evidence_dump(node) == "FutureNode(new_list=[], new_optional=None)"
    changed = copy.deepcopy(node)
    changed.new_list = [1]
    assert evidence_dump(changed) != evidence_dump(node)
