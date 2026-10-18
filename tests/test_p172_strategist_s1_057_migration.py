"""Branch-local S1 self-tests; a separate reviewer must audit this implementation."""
import ast
import copy
import hashlib
import importlib
import inspect
import json
import os
from pathlib import Path
import pickle
import subprocess
import sys

import pytest

from scripts.refactor import p172_strategist_s1_057_capture as C
from scripts.refactor import shared_strategist_contracts as S5

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/p1_5_strategist_s1_057/cases.json"
DOC = json.loads(FIXTURE.read_text(encoding="utf-8"))
CASES = DOC["cases"]


def modules(prefix):
    return {name: importlib.import_module(prefix + "." + name.replace("/", ".")) for name in C.MODULES}


def verify_shim(source, name):
    tree = ast.parse(source)
    if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant) \
            and isinstance(tree.body[0].value.value, str):
        tree.body.pop(0)
    pkg, base = name.split("/")
    expected = ast.parse(f"import sys as _sys\nfrom libs.agents.strategist.{pkg} import {base} as _canonical\n"
                         "_sys.modules[__name__] = _canonical\n")
    if ast.dump(tree, include_attributes=False) != ast.dump(expected, include_attributes=False):
        raise AssertionError("unexpected shim source: " + name)


@pytest.mark.parametrize("name", C.MODULES)
def test_base_and_canonical_git_blob_and_signature(name):
    old, new = "libs/runtime/strategist/" + name + ".py", "libs/agents/strategist/" + name + ".py"
    raw = subprocess.check_output(["git", "show", C.PINNED_BASE + ":" + old], cwd=ROOT)
    data = (ROOT / new).read_bytes().replace(b"\r\n", b"\n")
    assert raw == data
    assert hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest() == C.MODULES[name]
    base = ast.parse(raw)
    current = ast.parse(data)
    assert ast.dump(base, include_attributes=False) == ast.dump(current, include_attributes=False)


@pytest.mark.parametrize("name", C.MODULES)
def test_identity_both_orders_package_private_exports_and_legacy_pickle(name):
    old = "libs.runtime.strategist." + name.replace("/", ".")
    new = "libs.agents.strategist." + name.replace("/", ".")
    for first, second in ((old, new), (new, old)):
        code = f"""
import importlib
a=importlib.import_module({first!r}); b=importlib.import_module({second!r})
if a is not b or any(getattr(a,k) is not v for k,v in vars(b).items()):
    raise RuntimeError('module/export identity mismatch')
p=importlib.import_module({old.rsplit('.',1)[0]!r})
q=importlib.import_module({new.rsplit('.',1)[0]!r})
if p.{name.split('/')[1]} is not a or q.{name.split('/')[1]} is not a:
    raise RuntimeError('package attribute mismatch')
"""
        subprocess.run([sys.executable, "-c", code], cwd=ROOT, check=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONPATH=str(ROOT)))
    a, b = importlib.import_module(old), importlib.import_module(new)
    funcs = {k: v for k, v in vars(b).items() if inspect.isfunction(v)}
    assert funcs
    for key, fn in funcs.items():
        assert getattr(a, key) is fn and inspect.signature(getattr(a, key)) == inspect.signature(fn)
        assert fn.__globals__ is vars(b)
        assert pickle.loads(pickle.dumps(fn)) is fn
        assert pickle.loads(f"c{old}\n{key}\n.".encode()) is fn


@pytest.mark.parametrize("name", C.MODULES)
def test_strict_shim_and_three_negative_payloads(name):
    source = (ROOT / ("libs/runtime/strategist/" + name + ".py")).read_text(encoding="utf-8")
    verify_shim(source, name)
    for bad in (source + "\nraise RuntimeError(123)\n", source + "\nimport subprocess\n",
                source.replace("from libs.agents.strategist.", "from unapproved.strategist.")):
        with pytest.raises(AssertionError):
            verify_shim(bad, name)


@pytest.mark.parametrize("index", range(len(CASES)))
def test_base_frozen_result_exception_utf8_order_inputs_aliases_and_calls(index):
    spec = CASES[index]
    assert "facade" not in spec["kwargs"]
    for prefix in ("libs.runtime.strategist", "libs.agents.strategist"):
        actual = C.observe(spec, modules(prefix))
        assert C.encode(actual) == C.encode(spec["expected"]), (spec["module"], spec["function"], index)


def test_frozen_oracle_reproduces_from_disposable_pinned_base_tree(tmp_path):
    assert DOC["producer_sha"] == C.PINNED_BASE and DOC["source_blobs"] == C.MODULES
    assert FIXTURE.stat().st_size < 256 * 1024
    output = tmp_path / "reproduced.json"
    C.generate(ROOT, output)
    rebuilt = json.loads(output.read_text(encoding="utf-8"))
    assert C.encode(rebuilt["cases"]) == C.encode(CASES)
    assert len(CASES) == 74
    assert len({c["function"] for c in CASES}) == 16
    assert sum("exc" in c["expected"]["result"] for c in CASES) == 10


def test_private_monkeypatch_is_shared_and_facade_binding_changes_within_call(monkeypatch):
    for name, mod in modules("libs.agents.strategist").items():
        old = importlib.import_module("libs.runtime.strategist." + name.replace("/", "."))
        fn = next(k for k, v in vars(mod).items() if inspect.isfunction(v))
        marker = lambda *a, **k: "patched"
        with monkeypatch.context() as patch:
            patch.setattr(old, fn, marker)
            assert getattr(mod, fn)() == "patched"
    spec = next(c for c in CASES if c.get("repatch"))
    result = C.observe(spec, modules("libs.agents.strategist"))
    assert result["calls"] == ["round:rebind"]
    assert result["result"]["ok"]["index_moves"]["sp500_pct"] == 0.125


def test_strategic_answer_aliases_are_shallow_and_bidirectionally_visible():
    spec = next(c for c in CASES if c["module"] == "output/strategic_answers"
                and c["kwargs"]["commander_context"].get("open_position_refresh_context"))
    kwargs = copy.deepcopy(spec["kwargs"])
    mods = modules("libs.agents.strategist")
    out = mods[spec["module"]]._build_strategic_answers_r3_impl(**kwargs, facade=C.FakeFacade(mods))
    assert out["scanner_bias"] is kwargs["scanner_bias"]
    assert out["q11_monitor_exit_guidance"] is kwargs["monitor_guidance"]
    out["scanner_bias"]["kind"]["score"] = .9
    assert kwargs["scanner_bias"]["kind"]["score"] == .9
    kwargs["monitor_guidance"]["nested"].append(2)
    assert out["q11_monitor_exit_guidance"]["nested"] == [1, 2]
    original = kwargs["commander_context"]["open_position_refresh_context"]["entry_state"]
    copied = out["q15_commander_refresh_context"]["entry_state"]
    assert copied is not original and copied["nested"] is original["nested"]


def test_mock_llm_compact_input_payload_bytes_and_key_order():
    wanted = ("_compact_read_model_facts_for_llm_r3_impl", "_compact_global_signal_for_llm_r3_impl",
              "_build_strategic_answers_r3_impl")
    specs = [max((c for c in CASES if c["function"] == name and "ok" in c["expected"]["result"]),
                 key=lambda c: len(C.encode([c["args"], c["kwargs"]]))) for name in wanted]
    expected = C.encode({name: spec["expected"]["result"]["ok"] for name, spec in zip(wanted, specs)}).encode()
    mods = modules("libs.agents.strategist")
    actual = C.encode({name: C.observe(spec, mods)["result"]["ok"] for name, spec in zip(wanted, specs)}).encode()
    assert actual == expected and b"\\u" not in actual
    assert "한국".encode() in actual


def test_original_node_consumers_bind_canonical_implementations_and_source_is_unchanged():
    node = importlib.import_module("graphs.nodes.strategist_node")
    count = 0
    for mod in modules("libs.agents.strategist").values():
        for name, fn in vars(mod).items():
            if inspect.isfunction(fn):
                assert getattr(node, name) is fn
                count += 1
    assert count == 16
    restored = S5.current_contract()["restored"]
    pinned = subprocess.check_output(["git", "show", C.PINNED_BASE + ":graphs/nodes/strategist_node.py"], cwd=ROOT).decode("utf-8-sig")
    assert ast.dump(restored) == ast.dump(ast.parse(pinned))
