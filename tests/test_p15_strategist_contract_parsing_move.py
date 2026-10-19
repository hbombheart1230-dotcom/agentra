"""Strategist LLM response-contract parsing move: _extract_contract_from_prose, _extract_json_object and
_classify_llm_parse_failure move from graphs/nodes/strategist_node.py into
libs/runtime/strategist/llm/response_contract_parsing.py behind thin R3 facade wrappers.

Proofs (offline; no LLM/network/clock/report write):
 * static: wrapper signature == BASE; owner body AST == BASE body after `facade.X -> X`; no bare facade global left;
 * runtime: BASE tree (git archive) and this checkout run identical typed cases in fresh interpreters, including
   use-time facade monkeypatching of _strip_fenced_block / _parse_text_list_fragment / _extract_contract_from_prose /
   json / re (called-through counts recorded), exception type+message;
 * negative: planted owner mutations change the observation."""
import ast
import copy
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = "3a44bed26433d03408999fb43aa45d2e4f280f55"  # == integration 90ec2383 for strategist_node.py / S5 owners
NODE = "graphs/nodes/strategist_node.py"
OWNER = "libs/runtime/strategist/llm/response_contract_parsing.py"
MOVED = ("_extract_contract_from_prose", "_extract_json_object", "_classify_llm_parse_failure")

FENCE = "`" * 3
PROSE = [
    "",
    "   ",
    "no colon here",
    "market_regime: risk_on\nplaybook: breakout\nthemes: [\"AI\", \"반도체\"]",
    "1. **Market Regime Hint**: neutral then RISK_OFF\n- playbook_hint: pullback\n* key_events_hint: \"CPI\", \"FOMC\"",
    "market_sentiment: bullish\nscanner_bias: momentum and value\ntrade_aggressiveness: HIGH",
    "scanner_priority: [trading_value, bogus, momentum, risk_penalty]\nmonitor_guidance: defensive_exit",
    "risk_tone: aggressive\nreport_focus: \"news\" and \"flows\"\nthemes: plain text theme",
    "intro text market_regime : risk_off trailing\nother: x\nthemes:\n[\"a\",\n \"b\"]",
    "avoid_themes: [x; y | z]\nplaybook: defensive",
    "monitor_guidance: hold_through_noise\nmarket_regime: unknownvalue",
    FENCE + "text\nmarket_regime: risk_on\nthemes: [\"t\"]\n" + FENCE,
    "themes_hint: ['q1', 'q2']\nmarket_regime_hint: Neutral",
    "market_regime: neutral, scanner_priority: momentum",
    "market_regime: risk_on or maybe neutral\nplaybook: breakout",  # last allowed enum wins (reversed scan)
    'scanner_priority: ["trading_value", "bogus", "momentum"]\nplaybook: breakout',  # priority allowlist filter
]
JSONISH = PROSE + [
    '{"market_regime": "risk_on", "themes": ["a"]}',
    FENCE + "json\n{\"playbook\": \"breakout\"}\n" + FENCE,
    '{"strategist_output": {"market_regime": "neutral"}, "meta": 1}',
    '{"output": {"themes": ["x"]}, "output2": 2}',
    '[{"market_regime": "risk_off"}]',
    '{"foo": 1}',
    'prefix {"bad": } then {"market_regime": "risk_on"} tail',
    '{"market_regime": "risk_on"',
    "[1, 2, 3]",
    'leading {"result": {"playbook": "reversal"}} trailing',
]
CLASSIFY = ["", "  ", "{\"a\": 1", "[1,", "themes are nice", "plain words", FENCE + "\n" + FENCE, None, 123]

RUNNER = r'''
import importlib, json, re as _re, sys
tree, spec = sys.argv[1], sys.argv[2]
sys.path[:] = [tree] + [p for p in sys.path if p not in ("", ".")]
sys.dont_write_bytecode = True
node = importlib.import_module("graphs.nodes.strategist_node")
cases = json.loads(open(spec, encoding="utf-8").read())
def enc(v):
    return [type(v).__name__, _re.sub(r" at 0x[0-9A-Fa-f]+", " at 0x?", repr(v))]
out = []
def call(fn, arg):
    try:
        return {"result": enc(getattr(node, fn)(arg))}
    except BaseException as exc:
        return {"exc": [type(exc).__name__, str(exc)]}
for fn, args in cases["plain"].items():
    for a in args:
        out.append([fn, repr(a), call(fn, a)])
# use-time facade monkeypatching: wrap the facade globals and record call-through counts
saved = dict(node.__dict__)
log = []
def wrap(name):
    orig = getattr(node, name)
    def w(*a, **k):
        log.append(name)
        return orig(*a, **k)
    return w
for name in ("_strip_fenced_block", "_parse_text_list_fragment", "_extract_contract_from_prose"):
    setattr(node, name, wrap(name))
class JsonProxy:
    def __getattr__(self, k):
        log.append("json." + k)
        return getattr(json, k)
class ReProxy:
    def __getattr__(self, k):
        if callable(getattr(_re, k)):
            log.append("re." + k)
        return getattr(_re, k)
node.json, node.re = JsonProxy(), ReProxy()
for fn, args in cases["plain"].items():
    for a in args:
        del log[:]
        r = call(fn, a)
        out.append(["patched:" + fn, repr(a), r, list(log)])
# replacing a facade helper changes the result (use-time lookup, not entry-time capture)
node.__dict__.clear(); node.__dict__.update(saved)
node._strip_fenced_block = lambda text: "market_regime: risk_off\nthemes: [\"patched\"]"
out.append(["replaced_strip", call("_extract_json_object", "anything")])
node.__dict__.clear(); node.__dict__.update(saved)
node._extract_contract_from_prose = lambda s: {"sentinel": True}
out.append(["replaced_prose", call("_extract_json_object", "no json here")])
node.__dict__.clear(); node.__dict__.update(saved)
sys.stdout.buffer.write((json.dumps(out, ensure_ascii=False, indent=0) + "\n").encode("utf-8"))
'''


def _git(*args):
    return subprocess.check_output(["git", "-c", "core.autocrlf=false", *args], cwd=ROOT)


def _defs(src):
    return {n.name: n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef)}


@pytest.fixture(scope="module")
def base_src():
    return _git("show", f"{BASE}:{NODE}").decode("utf-8")


@pytest.fixture(scope="module")
def base_tree(tmp_path_factory):
    root = tmp_path_factory.mktemp("cp_base")
    with tarfile.open(fileobj=io.BytesIO(_git("archive", BASE, "libs", "graphs"))) as tf:
        tf.extractall(root, filter="data")
    return root


@pytest.fixture(scope="module")
def spec(tmp_path_factory):
    p = tmp_path_factory.mktemp("cp_spec") / "cases.json"
    p.write_text(json.dumps({"plain": {"_extract_contract_from_prose": PROSE, "_extract_json_object": JSONISH,
                                       "_classify_llm_parse_failure": CLASSIFY}}, ensure_ascii=False), encoding="utf-8")
    return p


def observe(tree, spec, tmp):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    env.pop("PYTHONPATH", None)
    r = subprocess.run([sys.executable, "-c", RUNNER, str(tree), str(spec)], cwd=str(tmp), capture_output=True, env=env)
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")[-2500:]
    return r.stdout.decode("utf-8")


class _Unqualify(ast.NodeTransformer):
    def visit_Attribute(self, node):
        self.generic_visit(node)
        if isinstance(node.value, ast.Name) and node.value.id == "facade":
            return ast.copy_location(ast.Name(id=node.attr, ctx=node.ctx), node)
        return node


# ---------------------------------------------------------------- static
@pytest.mark.parametrize("name", MOVED)
def test_node_keeps_a_thin_wrapper_with_the_base_signature(name, base_src):
    base = _defs(base_src)[name]
    head = _defs((ROOT / NODE).read_text(encoding="utf-8"))[name]
    assert ast.dump(head.args) == ast.dump(base.args) and ast.dump(head.returns) == ast.dump(base.returns)
    assert len(head.body) == 1 and isinstance(head.body[0], ast.Return)
    call = head.body[0].value
    assert ast.unparse(call.func) == f"{name}_r3_impl" and [ast.unparse(a) for a in call.args] == [base.args.args[0].arg]
    assert [(k.arg, ast.unparse(k.value)) for k in call.keywords] == [("facade", "_r3_sys.modules[__name__]")]


@pytest.mark.parametrize("name", MOVED)
def test_owner_body_equals_base_body_after_unqualifying_facade(name, base_src):
    base = _defs(base_src)[name]
    impl = _defs((ROOT / OWNER).read_text(encoding="utf-8"))[f"{name}_r3_impl"]
    assert [a.arg for a in impl.args.args] == [a.arg for a in base.args.args]
    assert [a.arg for a in impl.args.kwonlyargs] == ["facade"] and not impl.decorator_list
    restored = _Unqualify().visit(copy.deepcopy(impl))
    assert [ast.dump(n) for n in restored.body] == [ast.dump(n) for n in base.body]
    facade_globals = {"re", "json", "_strip_fenced_block", "_parse_text_list_fragment", "_extract_contract_from_prose"}
    bare = {n.id for n in ast.walk(impl) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)} & facade_globals
    assert bare == set(), f"{name}: entry-time/global capture of {sorted(bare)}"


def test_owner_is_small_and_never_imports_the_facade():
    text = (ROOT / OWNER).read_text(encoding="utf-8")
    tree = ast.parse(text)
    assert len(text.splitlines()) <= 350
    assert [ast.unparse(n) for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))] == [
        "from __future__ import annotations", "from typing import Any, Dict"]
    assert sorted(n.name for n in tree.body if isinstance(n, ast.FunctionDef)) == sorted(f"{m}_r3_impl" for m in MOVED)


def test_node_change_is_exactly_three_wrappers_and_one_import(base_src):
    head = ast.parse((ROOT / NODE).read_text(encoding="utf-8"))
    base_defs = _defs(base_src)
    body = []
    for n in head.body:
        if isinstance(n, ast.ImportFrom) and n.module == OWNER[:-3].replace("/", "."):
            assert sorted(a.name for a in n.names) == sorted(f"{m}_r3_impl" for m in MOVED) and not any(a.asname for a in n.names)
            continue
        body.append(base_defs[n.name] if isinstance(n, ast.FunctionDef) and n.name in MOVED else n)
    assert [ast.dump(n) for n in body] == [ast.dump(n) for n in ast.parse(base_src).body]


# ---------------------------------------------------------------- runtime parity
@pytest.fixture(scope="module")
def base_obs(base_tree, spec, tmp_path_factory):
    return observe(base_tree, spec, tmp_path_factory.mktemp("cp_run_base"))


@pytest.fixture(scope="module")
def head_obs(spec, tmp_path_factory):
    return observe(ROOT, spec, tmp_path_factory.mktemp("cp_run_head"))


def test_runtime_observation_is_identical_to_base(base_obs, head_obs):
    assert head_obs == base_obs


def test_observation_covers_populated_patched_and_replaced_paths(head_obs):
    rows = json.loads(head_obs)
    plain = {(r[0], r[1]): r[2] for r in rows if r[0] in MOVED}
    assert plain[("_extract_contract_from_prose", repr(PROSE[3]))]["result"][0] == "dict"
    assert "risk_on" in plain[("_extract_contract_from_prose", repr(PROSE[3]))]["result"][1]
    assert plain[("_extract_contract_from_prose", repr(""))]["result"] == ["dict", "{}"]
    assert plain[("_extract_contract_from_prose", repr(PROSE[6]))]["result"] == ["dict", "{}"]  # BASE quirk kept
    assert "'neutral'" in plain[("_extract_contract_from_prose", repr(PROSE[14]))]["result"][1]
    assert "'momentum'" in plain[("_extract_contract_from_prose", repr(PROSE[15]))]["result"][1]
    assert "bogus" not in plain[("_extract_contract_from_prose", repr(PROSE[15]))]["result"][1]
    assert plain[("_classify_llm_parse_failure", repr(""))]["result"][1] == "'strategist_llm_response_empty'"
    patched = [r for r in rows if r[0].startswith("patched:")]
    assert any("_extract_contract_from_prose" in r[3] for r in patched if r[0] == "patched:_extract_json_object")
    assert any("json.loads" in r[3] for r in patched) and any("re.search" in r[3] for r in patched)
    tail = {r[0]: r[1] for r in rows if r[0].startswith("replaced_")}
    assert "patched" in tail["replaced_strip"]["result"][1]
    assert tail["replaced_prose"]["result"] == ["dict", "{'sentinel': True}"]


# ---------------------------------------------------------------- negative mutations
MUTATIONS = [
    ('for candidate in reversed(matches):', 'for candidate in matches:'),
    ('parsed = [x for x in parsed if str(x or "").strip().lower() in allowed_priority]', 'parsed = parsed'),
    ('return out if has_contract_signal else {}', 'return out'),
    ('    prose_contract = facade._extract_contract_from_prose(s)', '    prose_contract = {}'),
    ('for key in ("strategist_output", "output", "result", "data"):', 'for key in ("output", "result", "data"):'),
    ('return "strategist_llm_response_truncated_json"', 'return "strategist_llm_response_not_json"'),
    ('s = facade._strip_fenced_block(str(raw or "")).strip()', 's = str(raw or "").strip()'),
]


@pytest.fixture(scope="module")
def mutable_tree(tmp_path_factory):
    dst = tmp_path_factory.mktemp("cp_mut")
    shutil.copytree(ROOT / "libs", dst / "libs", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(ROOT / "graphs", dst / "graphs", ignore=shutil.ignore_patterns("__pycache__"))
    return dst


@pytest.mark.parametrize("old,new", MUTATIONS, ids=range(len(MUTATIONS)))
def test_planted_owner_mutation_changes_the_observation(old, new, mutable_tree, spec, base_obs, tmp_path):
    target = mutable_tree / OWNER
    original = target.read_bytes()
    text = original.decode("utf-8")
    nl = "\r\n" if "\r\n" in text else "\n"
    old, new = old.replace("\n", nl), new.replace("\n", nl)
    assert text.count(old) == 1, f"mutation anchor missing: {old!r}"
    try:
        target.write_bytes(text.replace(old, new).encode("utf-8"))
        mutated = observe(mutable_tree, spec, tmp_path)
    finally:
        target.write_bytes(original)
    assert mutated != base_obs
