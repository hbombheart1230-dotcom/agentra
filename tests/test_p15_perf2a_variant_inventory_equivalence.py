"""PERF-2A: pinned BASE equivalence, no node execution or result cache."""
import ast
import copy
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import types

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = "c5aa8dbfc16beda8cdb62d8c27b05abe52ae5c6e"
SPECS = [
    ("p162_scanner_node_freeze_tool.py", "p1_5_t4a_scanner_node/scanner_node_golden.json.gz", 73, 1575),
    ("p163_monitor_freeze_tool.py", "p1_5_t4b_monitor/monitor_golden.json.gz", 149, 2879),
    ("p165_commander_ui_freeze_tool.py", "p1_5_t4d_commander_ui/commander_ui_golden.json.gz", 189, 6456),
]


def _source(tool, baseline):
    path = "scripts/refactor/" + tool
    return subprocess.check_output(["git", "show", BASE + ":" + path], cwd=ROOT).decode() if baseline else (ROOT / path).read_text(encoding="utf-8")


def _pure(tool, baseline=False):
    tree = ast.parse(_source(tool, baseline))
    module = types.ModuleType("_inventory_only")
    module.__dict__.update(copy=copy, hashlib=hashlib)
    freeze = types.ModuleType("_pinned_BASE_freeze_types")
    exec(compile(_source("p161_agent_output_freeze.py", True), "<pinned-BASE-freeze-types>", "exec"), freeze.__dict__)
    module.F = freeze
    constants = {"TARGETS", "FROZEN_EPOCH", "VARIANTS_PER_RECORD", "_ENV_TOGGLES"}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for name in node.targets:
                if isinstance(name, ast.Name) and name.id in constants:
                    if name.id == "FROZEN_EPOCH":
                        # Preserve the source expression int(F.FROZEN_BASE.timestamp()), not a guessed clock.
                        exec(compile(ast.Module(body=[node], type_ignores=[]), "<BASE-derived-clock>", "exec"), module.__dict__)
                    else:
                        module.__dict__[name.id] = ast.literal_eval(node.value)
    names = {"_variants", "_scenarios", "variant_inventory", "expected_sample_ids", "_sampled", "_inventory_ids_safe"}
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names],
                            type_ignores=[]), "<pure-BASE-inventory>" if baseline else "<pure-FEATURE-inventory>", "exec"), module.__dict__)
    return module


def _golden(fixture):
    return json.loads(gzip.decompress((ROOT / "tests/fixtures" / fixture).read_bytes()))


def _variants(module, rec):
    return module._variants(rec["state_in"], rec["id"]) if "state_in" in rec else module._variants(rec["target"], rec["input"], rec["id"])


def _bytes(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()


@pytest.mark.parametrize("tool,fixture,records,variants", SPECS)
def test_every_frozen_id_order_payload_digest_and_sample_is_BASE_equal(tool, fixture, records, variants):
    before, after = _pure(tool, True), _pure(tool)
    golden = _golden(fixture)
    assert len(golden) == records
    count = 0
    for rec in golden:
        original = _bytes(rec)
        a, b = _variants(before, rec), _variants(after, rec)
        ids = [vid for vid, payload in a]
        assert ids == [vid for vid, payload in b] == before.variant_inventory(rec) == after.variant_inventory(rec)
        assert set(ids) == set(rec["variants"])
        assert hashlib.sha256(_bytes(a)).digest() == hashlib.sha256(_bytes(b)).digest(), rec["id"]
        assert _bytes(rec) == original
        for mod in (1, 4):
            assert before.expected_sample_ids(rec, mod) == after.expected_sample_ids(rec, mod)
        count += len(ids)
    assert count == variants


class _StripMetadataMode(ast.NodeTransformer):
    def visit_If(self, node):
        node = self.generic_visit(node)
        return node.orelse if isinstance(node.test, ast.Name) and node.test.id == "ids_only" else node

    def visit_Call(self, node):
        self.generic_visit(node)
        node.keywords = [k for k in node.keywords if k.arg != "ids_only"]
        return node


@pytest.mark.parametrize("tool,fixture,records,variants", SPECS)
def test_default_payload_generation_reconstructs_exact_BASE_AST(tool, fixture, records, variants):
    old = ast.parse(_source(tool, True))
    new = ast.parse(_source(tool, False))
    for name in ("_variants", "_scenarios"):
        a = next(n for n in old.body if isinstance(n, ast.FunctionDef) and n.name == name)
        b = next(n for n in new.body if isinstance(n, ast.FunctionDef) and n.name == name)
        b = _StripMetadataMode().visit(b)
        b.args.kwonlyargs = []
        b.args.kw_defaults = []
        assert ast.dump(a) == ast.dump(b), name


@pytest.mark.parametrize("tool,fixture,records,variants", SPECS)
def test_ID_inventory_avoids_payload_deepcopy_without_reading_frozen_variant_keys(tool, fixture, records, variants):
    before, after = _pure(tool, True), _pure(tool)
    rec = _golden(fixture)[0]
    expected = before.variant_inventory(rec)
    rec.pop("variants")  # independent ID oracle, never copied from the frozen digest map

    def forbidden(*args, **kwargs):
        raise AssertionError("metadata inventory attempted payload deepcopy")

    after.copy = types.SimpleNamespace(deepcopy=forbidden)
    assert after.variant_inventory(rec) == expected


def _outcome(module, rec):
    try:
        return "value", module.variant_inventory(rec)
    except Exception as exc:
        return "exception", type(exc).__name__, str(exc)


@pytest.mark.parametrize("tool,fixture,records,variants", SPECS)
def test_malformed_and_changed_inputs_do_not_reuse_old_metadata(tool, fixture, records, variants):
    before, after = _pure(tool, True), _pure(tool)
    rec = _golden(fixture)[0]
    key = "state_in" if "state_in" in rec else "input"
    for invalid in (None, [], "bad", 3, {}, {"args": []}, {"args": [None]}, {"state": []}, {"kwargs": []}):
        item = dict(rec, **{key: invalid})
        assert _outcome(before, item) == _outcome(after, item)
    assert after.variant_inventory(rec) == before.variant_inventory(rec)
    value = rec[key] if key == "state_in" else rec[key]["state"] if "state" in rec[key] else rec[key]["args"][0] if "args" in rec[key] else rec[key]["kwargs"]
    value["perf2a_new_key"] = None
    assert after.variant_inventory(rec) == before.variant_inventory(rec)


@pytest.mark.parametrize("tool,fixture,records,variants", SPECS)
def test_custom_deepcopy_exception_and_alias_inputs_fall_back(tool, fixture, records, variants):
    before, after = _pure(tool, True), _pure(tool)
    rec = _golden(fixture)[0]
    value = rec["state_in"] if "state_in" in rec else rec["input"]

    class Custom:
        def __deepcopy__(self, memo):
            raise ValueError("custom deepcopy sentinel")

    value["custom_perf2a"] = Custom()
    assert _outcome(before, rec) == _outcome(after, rec) == ("exception", "ValueError", "custom deepcopy sentinel")
    del value["custom_perf2a"]
    shared = {"nested": []}
    value["alias_a"] = value["alias_b"] = shared
    assert not after._inventory_ids_safe(value)
    a, b = _variants(before, rec), _variants(after, rec)
    assert _bytes(a) == _bytes(b)
    for (_, x), (_, y) in zip(a, b):
        assert (x.get("alias_a") is x.get("alias_b")) == (y.get("alias_a") is y.get("alias_b"))
