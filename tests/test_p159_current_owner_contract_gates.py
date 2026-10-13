"""T3: CURRENT-HEAD Owner contract gates (independent of the immutable historical extraction gates).

Historical gates (p156/p157/p158) prove each extraction against its own end snapshot. These tests prove that the
CURRENT tree - after any later behavior-preserving Owner cleanup - still honours: import resolution, public/ABI
callability of the original modules, Owner authority restrictions, record/tuple compatibility and name mapping.
"""
import ast
import importlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/refactor"
LEDGERS = {
    "second_pass": ("p1_5_second_pass_moved_segments_ledger.json", "bf59c4d2941442fc2dff41c3c2888f053b4b1577"),
    "t1": ("p1_5_third_pass_t1_moved_segments_ledger.json", "67e0dc0ee0b91d45d242ccbfb3e1133d3a06e5ea"),
    "t2": ("p1_5_third_pass_t2_moved_segments_ledger.json", "d4a5364bae817504c253e06b9150ee49c692e120"),
}
T3 = DOCS / "p1_5_third_pass_t3_owner_contract_ledger.json"
MAX_OWNER_LOC = 350
ALLOWED_OWNER_IMPORTS = {"__future__": {"annotations"}, "typing": {"Any", "NamedTuple"}}
FORBIDDEN_TOKENS = ("os.environ", "os.getenv", "getenv(", "time.time(", "datetime.now", "datetime.utcnow", "uuid.uuid",
                    "subprocess", "sqlite3", "requests.", "print(", "open(", "logging.")


def _segments():
    out = []
    for tag, (name, end) in LEDGERS.items():
        for s in json.loads((DOCS / name).read_text(encoding="utf-8"))["segments"]:
            out.append((tag, end, s))
    return out


def _t3():
    return json.loads(T3.read_text(encoding="utf-8"))


def _mapping():
    """(old_module, old_function) -> (new_module, new_function, change)"""
    m = {}
    for c in _t3()["changes"]:
        m[(c["old_module"], c["old_function"])] = (c["new_module"], c["new_function"], c)
    return m


def _current(owner_module, owner_function):
    mapping = _mapping()
    new_module, new_function, change = mapping.get((owner_module, owner_function), (owner_module, owner_function, None))
    return new_module, new_function, change


def _tree(path):
    return ast.parse((ROOT / path).read_text(encoding="utf-8-sig"))


def _git_show(path, sha):
    return subprocess.check_output(["git", "show", f"{sha}:{path}"], cwd=ROOT).decode("utf-8-sig")


def test_every_historical_owner_function_resolves_at_head_through_the_t3_mapping():
    for tag, _end, s in _segments():
        module, function, _ = _current(s["owner_module"], s["owner_function"])
        path = ROOT / module
        assert path.is_file(), f"{tag}: owner module missing at HEAD: {s['owner_module']} -> {module}"
        funcs = {n.name: n for n in _tree(module).body if isinstance(n, ast.FunctionDef)}
        assert function in funcs, f"{tag}: {s['owner_function']} -> {function} missing in {module}"
        kwonly = [a.arg for a in funcs[function].args.kwonlyargs]
        assert kwonly == ["facade"], (module, function, kwonly)


def test_t3_ledger_is_consistent_with_historical_ledgers_and_tree():
    hist = {(s["owner_module"], s["owner_function"]): s for _t, _e, s in _segments()}
    seen = set()
    for c in _t3()["changes"]:
        key = (c["old_module"], c["old_function"])
        assert key in hist, key
        assert key not in seen, key
        seen.add(key)
        assert c["fields"] == hist[key]["outputs"], "field order must equal the legacy positional order"
    for gone in _t3()["module_removed"]:
        assert not (ROOT / gone["module"]).exists(), gone


def test_result_records_are_positional_compatible_named_tuples():
    for c in _t3()["changes"]:
        mod = importlib.import_module(c["new_module"][:-3].replace("/", "."))
        rec = getattr(mod, c["record"])
        assert issubclass(rec, tuple) and rec._fields == tuple(c["fields"]), c["record"]
        values = tuple(range(len(c["fields"])))
        r = rec(*values)
        assert r == values and tuple(r) == values  # equality / unpacking with the legacy tuple
        assert hash(r) == hash(values)
        assert getattr(r, c["fields"][0]) == 0


def test_all_owner_modules_import_and_obey_authority_restrictions_at_head():
    owners = set()
    for _tag, _end, s in _segments():
        owners.add(_current(s["owner_module"], s["owner_function"])[0])
    for c in _t3()["changes"]:
        owners.add(c["new_module"])
    assert owners
    for owner in sorted(owners):
        importlib.import_module(owner[:-3].replace("/", "."))  # import resolution / no cycles at import time
        text = (ROOT / owner).read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= MAX_OWNER_LOC, owner
        tree = ast.parse(text)
        for node in tree.body:
            if isinstance(node, ast.Import):
                raise AssertionError(f"{owner}: plain import not allowed in a pure Owner")
            if isinstance(node, ast.ImportFrom):
                allowed = ALLOWED_OWNER_IMPORTS.get(node.module)
                assert allowed is not None, (owner, node.module)
                assert {a.name for a in node.names} <= allowed, (owner, node.module, [a.name for a in node.names])
        for tok in FORBIDDEN_TOKENS:
            assert tok not in text, (owner, tok)
        changed = {c["new_function"] for c in _t3()["changes"] if c["new_module"] == owner}
        for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
            if fn.name in changed or owner.startswith("libs/reporting/reporter_bundle_runtime_parts/"):
                first = fn.body[0]
                assert not (isinstance(first, ast.If) and isinstance(first.test, ast.Constant) and first.test.value is True
                            and len(fn.body) >= 2), f"{owner}:{fn.name}: mechanical `if True:` scaffolding left"


def test_original_modules_keep_their_public_callable_signatures_since_each_stage_end():
    seen = set()
    for tag, end, s in _segments():
        key = (s["module"], s["function"], end)
        if key in seen:
            continue
        seen.add(key)
        before = {n.name: n for n in ast.parse(_git_show(s["module"], end)).body if isinstance(n, ast.FunctionDef)}
        after = {n.name: n for n in _tree(s["module"]).body if isinstance(n, ast.FunctionDef)}
        assert s["function"] in after, key
        assert ast.dump(before[s["function"]].args) == ast.dump(after[s["function"]].args), key
        # every public (non-underscore) callable of the stage snapshot is still defined and importable
        for name in before:
            if not name.startswith("_"):
                assert name in after, (s["module"], name)


def test_facade_symbol_breadth_did_not_increase_for_converted_owners():
    for c in _t3()["changes"]:
        old_src = _git_show(c["old_module"], "ede47324e8db4be12c45e0a09ca3dcd22c68c5c1")
        new_src = (ROOT / c["new_module"]).read_text(encoding="utf-8-sig")

        def facade_syms(src, fname):
            fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == fname)
            return {n.attr for n in ast.walk(fn) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                    and n.value.id == "facade"}
        assert facade_syms(new_src, c["new_function"]) <= facade_syms(old_src, c["old_function"]), c["new_function"]


def test_t3_changed_paths_contain_no_authority_surface():
    out = subprocess.check_output(["git", "diff", "--name-only", "-z", "ede47324e8db4be12c45e0a09ca3dcd22c68c5c1", "HEAD"],
                                  cwd=ROOT).decode().split(chr(0))
    forbidden = ("libs/execution/", "libs/broker/", "libs/supervisor/", "libs/risk/", "libs/llm/",
                 "graphs/nodes/execute_from_packet.py", "graphs/nodes/decide_trade.py",
                 "graphs/nodes/update_state_after_execution.py", "libs/runtime/controlled_mock_lanes/",
                 "libs/reporting/trade_report_ai.py", "libs/reporting/trade_report_markdown_clean.py",
                 "libs/reporting/trade_story_pipeline.py")
    for p in [x for x in out if x]:
        assert not p.startswith(forbidden), f"T3 touched a protected surface: {p}"
        assert not re.search(r"bodies_0\d\.py$", p), f"numbered body touched: {p}"
