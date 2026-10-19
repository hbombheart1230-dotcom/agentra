"""Strategist S5 closed-scope helper moves (GPT charter 16): _clamp,_to_float | _to_int,_round_optional,_unit_score,_is_trueish |
_strip_fenced_block,_parse_text_list_fragment move from graphs/nodes/strategist_node.py into small R3 owners.

Proofs, all offline and deterministic (no LLM/network/clock/report write; temp cwd; inherited OS environment):
 * static: wrapper shape + signature equal to the pinned source; owner body AST == pinned body after `facade.X -> X`;
   every former module global is a `facade.` attribute in the owner (use-time lookup); module-level AST restore == pinned source;
 * runtime: the pinned source (git archive of d269c906) and this checkout run the same typed cases in FRESH interpreters
   (typed repr so 3 vs 3.0, nan, True vs 1 differ; exception type+message; facade patch-call logs; before-call and mid-call rebinding);
 * negative: planted mutations of a copy of this checkout's owners change the observation;
 * scope: the diff against the pinned source touches only the closed path set.
Fails loudly if the pinned commit is absent (fetch-depth 0)."""
import ast
import copy
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from p15_strategist_s5_cases import CASES  # noqa: E402

SRC = "d269c906ebadad75a0b833778ebc6a632a388e7c"  # approved Strategist input source (== BASE d773709 for libs/graphs)
NODE = "graphs/nodes/strategist_node.py"
RUNNER = ROOT / "scripts/refactor/p15_strategist_s5_runner.py"
VAL = "libs/runtime/strategist/context/value_helpers.py"
TXT = "libs/runtime/strategist/llm/text_fragment_helpers.py"
# name -> owner file; extended packet by packet (S5-A, S5-B, S5-C)
MOVED = {"_clamp": VAL, "_to_float": VAL, "_to_int": VAL, "_round_optional": VAL, "_unit_score": VAL, "_is_trueish": VAL,
         "_strip_fenced_block": TXT, "_parse_text_list_fragment": TXT}
ALL8 = ["_clamp", "_to_float", "_to_int", "_round_optional", "_unit_score", "_is_trueish", "_strip_fenced_block", "_parse_text_list_fragment"]
OWNER_MODULES = {VAL[:-3].replace("/", "."), TXT[:-3].replace("/", ".")}
CLOSED_PATHS = {NODE, VAL, TXT, "scripts/refactor/p15_strategist_s5_runner.py", "tests/p15_strategist_s5_cases.py",
                "tests/test_p15_strategist_s5_helper_moves.py"}
CLOSED_PREFIX = ("docs/refactor/work_projects/evidence/strategist/",)


def _git(*args):
    return subprocess.check_output(["git", "-c", "core.autocrlf=false", *args], cwd=ROOT)


def _require_src():
    if subprocess.run(["git", "cat-file", "-e", SRC + "^{commit}"], cwd=ROOT).returncode != 0:
        raise AssertionError(f"pinned source {SRC} not in this clone: fetch with full history (fetch-depth: 0)")


@pytest.fixture(scope="module")
def base_node_src():
    _require_src()
    return _git("show", f"{SRC}:{NODE}").decode("utf-8")


@pytest.fixture(scope="module")
def base_tree(tmp_path_factory):
    _require_src()
    root = tmp_path_factory.mktemp("s5_base")
    with tarfile.open(fileobj=io.BytesIO(_git("archive", SRC, "libs", "graphs"))) as tf:
        tf.extractall(root, filter="data")
    return root


def _defs(src):
    return {n.name: n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef)}


def _head_node_src():
    from scripts.refactor.shared_strategist_contracts import historical_source
    return historical_source(NODE)


def observe(tree, tmp):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    env.pop("PYTHONPATH", None)
    r = subprocess.run([sys.executable, str(RUNNER), str(tree), str(ROOT / "tests")], cwd=str(tmp), capture_output=True, env=env)
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")[-2500:]
    return r.stdout.decode("utf-8")


# ---------------------------------------------------------------- static ownership / R3 shape
@pytest.mark.parametrize("name", sorted(MOVED))
def test_node_definition_is_a_thin_r3_wrapper_with_the_original_signature(name, base_node_src):
    base, head = _defs(base_node_src)[name], _defs(_head_node_src())[name]
    assert ast.dump(head.args) == ast.dump(base.args) and ast.dump(head.returns) == ast.dump(base.returns)
    assert len(head.body) == 1 and isinstance(head.body[0], ast.Return)
    call = head.body[0].value
    params = [a.arg for a in head.args.args]
    assert isinstance(call, ast.Call) and ast.unparse(call.func) == f"{name}_r3_impl"
    assert [ast.unparse(a) for a in call.args] == params and not head.args.vararg and not head.args.kwonlyargs
    assert [(k.arg, ast.unparse(k.value)) for k in call.keywords] == [("facade", "_r3_sys.modules[__name__]")]


class _Unqualify(ast.NodeTransformer):
    def visit_Attribute(self, node):
        self.generic_visit(node)
        if isinstance(node.value, ast.Name) and node.value.id == "facade":
            return ast.copy_location(ast.Name(id=node.attr, ctx=node.ctx), node)
        return node


@pytest.mark.parametrize("name", sorted(MOVED))
def test_owner_body_equals_pinned_body_after_unqualifying_facade_and_every_global_is_qualified(name, base_node_src):
    base = _defs(base_node_src)[name]
    owner_src = (ROOT / MOVED[name]).read_text(encoding="utf-8-sig")
    impl = _defs(owner_src)[f"{name}_r3_impl"]
    assert [a.arg for a in impl.args.args] == [a.arg for a in base.args.args]
    assert [a.arg for a in impl.args.kwonlyargs] == ["facade"] and not impl.decorator_list
    restored = _Unqualify().visit(copy.deepcopy(impl))
    strip = lambda body: [ast.dump(n) for n in body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]  # noqa: E731
    assert strip(restored.body) == strip(base.body)
    import builtins
    params = {a.arg for a in impl.args.args + impl.args.kwonlyargs}
    local = {n.id for n in ast.walk(impl) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
    bare = {n.id for n in ast.walk(impl) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)} - params - local - set(dir(builtins))
    # a bare Name left over could only be an entry-time/import-time capture of a facade global
    quals = {n.value.id for n in ast.walk(impl) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)}
    assert bare <= {"facade"}, f"{name}: unqualified global(s) {sorted(bare - {'facade'})}"
    assert quals <= {"facade"} | local | params


@pytest.mark.parametrize("owner", sorted(set(MOVED.values())))
def test_owner_module_is_small_has_no_facade_import_and_exports_exactly_the_moved_impls(owner):
    text = (ROOT / owner).read_text(encoding="utf-8-sig")
    tree = ast.parse(text)
    assert len(text.splitlines()) <= 350
    imports = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    assert [ast.unparse(n) for n in imports] == ["from __future__ import annotations"]
    assert sorted(n.name for n in tree.body if isinstance(n, ast.FunctionDef)) == sorted(f"{k}_r3_impl" for k, v in MOVED.items() if v == owner)
    assert not [n for n in tree.body if not isinstance(n, (ast.FunctionDef, ast.ImportFrom, ast.Expr))]  # no module-level statements


def _restores_to_base(head_src, base_src):
    """Replace each approved wrapper by its pinned def and drop only the approved owner imports; True iff module AST == pinned."""
    base_defs = _defs(base_src)
    body = []
    for n in ast.parse(head_src).body:
        if isinstance(n, ast.ImportFrom) and n.module in OWNER_MODULES:
            if sorted(a.name for a in n.names) != sorted(f"{k}_r3_impl" for k, v in MOVED.items() if v[:-3].replace("/", ".") == n.module):
                return False
            continue
        body.append(base_defs[n.name] if isinstance(n, ast.FunctionDef) and n.name in MOVED else n)
    return [ast.dump(n) for n in body] == [ast.dump(n) for n in ast.parse(base_src).body]


def test_node_module_ast_restores_to_the_pinned_source(base_node_src):
    assert _restores_to_base(_head_node_src(), base_node_src)


# S5-D: planted edits outside the approved 8 wrappers / 2 owner imports must break the restoration proof
RESTORE_NEGATIVES = [
    ("    if not raw:\n        return bool(default)", "    if not raw:\n        return bool(not default)"),  # non-moved def body (_env_bool)
    ("    _is_trueish_r3_impl,\n)", "    _is_trueish_r3_impl,\n    _env_int_r3_impl,\n)"),  # extra owner import name
    ("    _strip_fenced_block_r3_impl,\n    _parse_text_list_fragment_r3_impl,\n)",
     "    _strip_fenced_block_r3_impl,\n)"),  # missing owner import name
    ("import sys as _r3_sys\n", "import sys as _r3_sys\n_clamp_cache = None\n"),  # new module-level statement
]  # (a changed wrapper body is rejected by the thin-wrapper shape test; restoration swaps moved defs by name)


@pytest.mark.parametrize("old,new", RESTORE_NEGATIVES, ids=range(len(RESTORE_NEGATIVES)))
def test_restoration_proof_rejects_planted_non_approved_node_edits(old, new, base_node_src):
    src = _head_node_src()
    assert src.count(old) == 1, f"negative anchor missing/ambiguous: {old!r}"
    assert not _restores_to_base(src.replace(old, new), base_node_src)


def test_frozen_t4c_and_s1_057_gate_delta_is_exactly_the_eight_approved_symbols(base_node_src):
    """Explains (does not waive) the 3 frozen-gate failures on this branch: p164 non-moved-def/import-line and p172 byte-identity
    see exactly these 8 changed defs and 8 new owner-import names, nothing else. Path mapping is a Codex shared-gate request."""
    dump = lambda s: {n.name: ast.dump(n) for n in ast.parse(s).body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}  # noqa: E731
    imps = lambda s: {(n.module, a.name) for n in ast.parse(s).body if isinstance(n, ast.ImportFrom) for a in n.names}  # noqa: E731
    base, head = dump(base_node_src), dump(_head_node_src())
    assert set(base) == set(head) and {k for k in base if base[k] != head[k]} == set(ALL8)
    assert imps(base_node_src) <= imps(_head_node_src())
    assert imps(_head_node_src()) - imps(base_node_src) == {(MOVED[k][:-3].replace("/", "."), f"{k}_r3_impl") for k in ALL8}


def test_moved_names_stay_public_attributes_of_the_node_module():
    sys.path.insert(0, str(ROOT))
    import importlib
    node = importlib.import_module("graphs.nodes.strategist_node")
    for name in ALL8:
        assert callable(getattr(node, name))
    for name in MOVED:
        assert getattr(node, name).__module__ == "graphs.nodes.strategist_node"


# ---------------------------------------------------------------- runtime parity (pinned source vs this checkout)
@pytest.fixture(scope="module")
def base_obs(base_tree, tmp_path_factory):
    return observe(base_tree, tmp_path_factory.mktemp("s5_run_base"))


@pytest.fixture(scope="module")
def head_obs(tmp_path_factory):
    return observe(ROOT, tmp_path_factory.mktemp("s5_run_head"))


@pytest.fixture(scope="module")
def by_id(head_obs):
    return {r["id"]: r for r in json.loads(head_obs)}


def test_all_typed_cases_are_identical_to_the_pinned_source_including_exceptions_and_patch_logs(base_obs, head_obs):
    assert head_obs == base_obs
    assert [r["id"] for r in json.loads(head_obs)] == [c["id"] for c in CASES]


def test_populated_values_and_use_time_facade_behaviour(by_id):
    res = lambda i: by_id[i]["result"]  # noqa: E731
    # _clamp / _to_float: populated, boundary, type-preserving and exception-bearing paths
    assert res("_clamp.v0") == ["int", "5"] and res("_clamp.v1") == ["int", "0"] and res("_clamp.v2") == ["int", "10"]
    assert res("_clamp.v4") == ["float", "nan"] and res("_clamp.v5") == ["int", "1"] and res("_clamp.v8") == ["bool", "True"]
    assert by_id["_clamp.v7"]["exc"][0] == "TypeError"
    assert res("_to_float.v0") == ["float", "1.5"] and res("_to_float.v2") == ["float", "2.0"] and res("_to_float.v11") == ["float", "12.0"]
    assert by_id["_to_float.v3"]["exc"][0] == "ValueError" and by_id["_to_float.v12"]["exc"][0] == "TypeError"
    assert res("_to_float.v9") == ["float", "4.0"] and res("_to_float.v15") == ["float", "1.0"]  # OverflowError -> default
    # S5-B value helpers: populated, type-preserving, default-branch and exception-bearing paths
    assert res("_to_int.v0") == ["int", "3"] and res("_to_int.v1") == ["int", "5"] and res("_to_int.v3") == ["int", "7"]  # inf -> default
    assert by_id["_to_int.v6"]["exc"][0] == "ValueError" and res("_to_int.v10") == ["int", "2"]  # bad default propagates / int() applied
    assert res("_round_optional.v0") == ["float", "1.2346"] and res("_round_optional.v2") == ["str", "'x'"]
    assert res("_round_optional.v7") == ["str", "'1.2345'"] and res("_round_optional.v9") == ["float", "inf"]
    assert res("_unit_score.v0") == ["float", "0.5"] and res("_unit_score.v1") == ["float", "1.0"] and res("_unit_score.v2") == ["float", "0.0"]
    assert res("_unit_score.v4") == ["float", "0.7"] and res("_unit_score.v5") == ["float", "1.0"]
    assert res("_is_trueish.v1") == ["bool", "True"] and res("_is_trueish.v2") == ["bool", "True"] and res("_is_trueish.v4") == ["bool", "False"]
    assert res("_is_trueish.v10") == ["bool", "True"] and res("_is_trueish.v12") == ["bool", "False"]
    # S5-C text helpers: fenced-block stripping, json -> ast.literal_eval order, separator splitting, facade json/ast/re patching
    assert res("_strip_fenced_block.v0") == ["str", "'{\"a\":1}'"] and res("_strip_fenced_block.v2") == ["str", "'plain'"]
    assert res("_strip_fenced_block.v10") == ["str", "'mid ```tail'"]
    assert res("_parse_text_list_fragment.v6") == ["list", [["str", "'a'"], ["str", "'b'"]]]
    assert res("_parse_text_list_fragment.v9") == ["list", [["str", "'a'"], ["str", "'b'"], ["str", "'c'"], ["str", "'d'"], ["str", "'e'"]]]
    assert res("_parse_text_list_fragment.v13") == ["list", [["str", "'1'"], ["str", "'2'"]]]  # ast.literal_eval tuple fallback
    assert res("_parse_text_list_fragment.v26") == ["list", [["str", "'a/b'"]]]  # json parser wins: "\/" -> "/" (ast would keep the backslash)
    assert by_id["_parse_text_list_fragment.re_patched_before"]["log"] == [["re.split", "[\\n,;|]+", "a,b"]]
    assert res("_parse_text_list_fragment.re_patched_mid") == ["list", [["str", "'M1'"], ["str", "'M2'"]]]
    assert by_id["_parse_text_list_fragment.json_patched_before"]["log"] == [["json.loads", "['p', 'q']"]]
    assert by_id["_parse_text_list_fragment.ast_patched_before"]["log"] == [["ast.literal_eval", "anything"]]
    # use-time resolution of the facade global `_clamp` inside _unit_score (before the call and in the except branch)
    assert res("_unit_score.patched_clamp_before") == ["float", "0.25"] and by_id["_unit_score.patched_clamp_before"]["log"] == [["clamp", "0.4", "0.0", "1.0"]]
    assert res("_unit_score.patched_clamp_mid_default_branch") == ["float", "0.375"]
    assert by_id["_unit_score.patched_clamp_in_default_branch"]["log"] == [["clamp_default", "0.9", "0.0", "1.0"]]


# ---------------------------------------------------------------- negative mutations of this checkout's owners
O = {"value": VAL, "text": TXT}
MUTATIONS = [  # (owner file, old, new, case id that MUST change)
    (VAL, "else hi if x > hi else x", "else hi if x > hi else lo", "_clamp.v0"),
    (VAL, "return lo if x < lo", "return hi if x < lo", "_clamp.v1"),
    (VAL, "return float(default)", "return default", "_to_float.v2"),
    (VAL, "return float(v)", "return float(str(v))", "_to_float.v7"),
    (VAL, "return int(float(v))", "return int(str(v))", "_to_int.v0"),
    (VAL, "return int(default)", "return default", "_to_int.v10"),
    (VAL, "    except Exception:\n        return value", "    except Exception:\n        return None", "_round_optional.v2"),
    (VAL, "round(float(value), int(digits))", "round(float(value), digits)", "_round_optional.v10"),
    (VAL, "float(facade._clamp(float(value), 0.0, 1.0))", "float(min(max(float(value), 0.0), 1.0))", "_unit_score.patched_clamp_before"),
    (VAL, "return float(facade._clamp(default, 0.0, 1.0))", "return float(min(max(default, 0.0), 1.0))", "_unit_score.patched_clamp_in_default_branch"),
    (VAL, '"yes", "y", "on"', '"yes", "on"', "_is_trueish.v7"),
    (VAL, ".strip().lower() in", ".strip() in", "_is_trueish.v1"),
    (TXT, "lines = lines[1:]", "lines = lines[2:]", "_strip_fenced_block.v0"),
    (TXT, "lines[-1].strip().startswith", "lines[-1].startswith", "_strip_fenced_block.v11"),
    (TXT, 'if not s.startswith("```"):', 'if s.startswith("```"):', "_strip_fenced_block.v0"),
    (TXT, "(facade.json.loads, facade.ast.literal_eval)", "(facade.ast.literal_eval, facade.json.loads)", "_parse_text_list_fragment.v26"),
    (TXT, '[\\n,;|]+', '[\\n,;]+', "_parse_text_list_fragment.v9"),
    (TXT, "facade.re.split(", "re_local_split(", "_parse_text_list_fragment.re_patched_before"),
    (TXT, "if raw is None:\n        return []", "if raw is None:\n        return ['']", "_parse_text_list_fragment.v0"),
]


@pytest.fixture(scope="module")
def mutable_tree(tmp_path_factory):
    dst = tmp_path_factory.mktemp("s5_mut")
    shutil.copytree(ROOT / "libs", dst / "libs", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(ROOT / "graphs", dst / "graphs", ignore=shutil.ignore_patterns("__pycache__"))
    return dst


@pytest.mark.parametrize("rel,old,new,case_id", MUTATIONS, ids=[f"{Path(m[0]).name}:{m[3]}:{i}" for i, m in enumerate(MUTATIONS)])
def test_planted_mutation_of_a_moved_owner_changes_the_observation(rel, old, new, case_id, mutable_tree, base_obs, tmp_path):
    target = mutable_tree / rel
    original = target.read_bytes()
    text = original.decode("utf-8")
    nl = "\r\n" if "\r\n" in text else "\n"  # checkouts with core.autocrlf=true carry CRLF; anchors are LF-authored
    old, new = old.replace("\n", nl), new.replace("\n", nl)
    assert old in text, f"mutation anchor missing in {rel}: {old!r}"
    try:
        target.write_bytes(text.replace(old, new).encode("utf-8"))
        mutated = {r["id"]: r for r in json.loads(observe(mutable_tree, tmp_path))}
    finally:
        target.write_bytes(original)
    base = {r["id"]: r for r in json.loads(base_obs)}
    assert mutated[case_id] != base[case_id], f"mutation not detected by {case_id}"


def test_every_moved_function_has_a_detecting_mutation():
    covered = {re.match(r"(_\w+?)\.", m[3]).group(1) for m in MUTATIONS}
    assert covered == set(MOVED)


# ---------------------------------------------------------------- scope
def test_diff_against_pinned_source_touches_only_the_closed_path_set():
    from scripts.refactor.shared_strategist_contracts import verify_integration_scope
    verify_integration_scope()  # Pinned integrated parent; exact closed paths, including untracked files.
