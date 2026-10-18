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
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/refactor"))
import shared_role_contracts as SHARED

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/refactor"
LEDGERS = {
    "second_pass": ("p1_5_second_pass_moved_segments_ledger.json", "bf59c4d2941442fc2dff41c3c2888f053b4b1577"),
    "t1": ("p1_5_third_pass_t1_moved_segments_ledger.json", "67e0dc0ee0b91d45d242ccbfb3e1133d3a06e5ea"),
    "t2": ("p1_5_third_pass_t2_moved_segments_ledger.json", "d4a5364bae817504c253e06b9150ee49c692e120"),
}
T3 = DOCS / "p1_5_third_pass_t3_owner_contract_ledger.json"
T3_1 = DOCS / "p1_5_third_pass_t3_1_owner_contract_ledger.json"
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
    """T3 ledger plus the T3.1 ledger (its `changes` are appended; `module_removed` is the union)."""
    base = json.loads(T3.read_text(encoding="utf-8"))
    extra = json.loads(T3_1.read_text(encoding="utf-8"))
    base["changes"] = base["changes"] + extra["changes"]
    base["module_removed"] = base["module_removed"] + extra["module_removed"]
    return base


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


# V3-055: two historical Scanner owners are now strict identity shims. Only these exact, hard-coded pairs are followed,
# and only after the shim source passes the same fail-closed AST verifier as the Wave B gate (never imported to validate).
V3_SHIM_ALLOWLIST = {
    "libs/runtime/scanner/candidate_context_projection.py": "libs/agents/scanner/projections/candidate_context_projection.py",
    "libs/runtime/scanner/selection_evidence_projection.py": "libs/agents/scanner/projections/selection_evidence_projection.py",
}


def _follow(module):
    module = SHARED.follow(module)
    if module not in V3_SHIM_ALLOWLIST:
        return module
    import importlib.util
    spec = importlib.util.spec_from_file_location("_wave_b_gate_p159", Path(__file__).resolve().parent / "test_p154_wave_b_moved_bodies.py")
    wb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wb)
    canonical = V3_SHIM_ALLOWLIST[module]
    wb._verify_identity_shim_source((ROOT / module).read_text(encoding="utf-8"), module, canonical)
    return canonical


def test_every_historical_owner_function_resolves_at_head_through_the_t3_mapping():
    for tag, _end, s in _segments():
        module, function, _ = _current(s["owner_module"], s["owner_function"])
        module = _follow(module)
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
        owners.add(_follow(_current(s["owner_module"], s["owner_function"])[0]))
    for c in _t3()["changes"]:
        owners.add(_follow(c["new_module"]))
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
    # Preserve the historical prohibition through the frozen whole-role BASE.
    # Every later runtime delta must exactly match a pinned role input AND restore its facade AST.
    SHARED.verify_runtime()
    out = subprocess.check_output(["git", "diff", "--name-only", "-z", "ede47324e8db4be12c45e0a09ca3dcd22c68c5c1", SHARED.BASE],
                                  cwd=ROOT).decode().split(chr(0))
    forbidden = ("libs/execution/", "libs/broker/", "libs/supervisor/", "libs/risk/", "libs/llm/",
                 "graphs/nodes/execute_from_packet.py", "graphs/nodes/decide_trade.py",
                 "graphs/nodes/update_state_after_execution.py", "libs/runtime/controlled_mock_lanes/",
                 "libs/reporting/trade_report_ai.py", "libs/reporting/trade_report_markdown_clean.py",
                 "libs/reporting/trade_story_pipeline.py")
    for p in [x for x in out if x]:
        assert not p.startswith(forbidden), f"T3 touched a protected surface: {p}"
        assert not re.search(r"bodies_0\d\.py$", p), f"numbered body touched: {p}"


# ---- T3-0.1: real-object payload / alias tests for the converted records -------------------------------------------
import copy  # noqa: E402
import types  # noqa: E402


def _record_classes():
    for c in _t3()["changes"]:
        mod = importlib.import_module(c["new_module"][:-3].replace("/", "."))
        yield c, getattr(mod, c["record"])


def _object_payload(n):
    """Distinct mutable dict/list payloads (not integers): field i is a dict for even i, a list for odd i."""
    return [({"i": i, "nested": {"vals": [i, {"deep": i}]}} if i % 2 == 0 else [i, {"x": i}, [i]]) for i in range(n)]


def test_records_keep_field_order_and_positional_unpacking_with_object_payloads():
    for c, rec in _record_classes():
        payload = _object_payload(len(c["fields"]))
        r = rec(*payload)
        assert tuple(r._fields) == tuple(c["fields"])
        assert list(r._asdict().keys()) == list(c["fields"])
        first, *rest = r
        assert first is payload[0] and all(a is b for a, b in zip(rest, payload[1:]))
        assert r == tuple(payload)  # nested dict/list equality, same as the legacy tuple
        assert tuple(r) == tuple(payload)


def test_records_preserve_reference_identity_and_shared_mutation_like_the_legacy_tuple():
    for c, rec in _record_classes():
        payload = _object_payload(len(c["fields"]))
        legacy = tuple(payload)
        r = rec(*payload)
        assert all(a is b for a, b in zip(r, legacy)), c["record"]
        # a mutation through the original reference is visible through the record exactly as through the tuple
        payload[0]["added_after_return"] = True
        assert r[0]["added_after_return"] is True and legacy[0]["added_after_return"] is True
        # ... and a mutation made through the record is visible to every other holder of the reference
        getattr(r, c["fields"][0])["via_record"] = 1
        assert payload[0]["via_record"] == 1


def test_records_copy_and_deepcopy_semantics_match_a_tuple():
    for c, rec in _record_classes():
        payload = _object_payload(len(c["fields"]))
        r = rec(*payload)
        shallow = copy.copy(r)
        assert type(shallow) is rec and all(a is b for a, b in zip(shallow, r))  # shallow copy shares the objects
        deep = copy.deepcopy(r)
        assert type(deep) is rec and deep == r and all(a is not b for a, b in zip(deep, r))
        deep[0]["only_in_deep"] = 1
        assert "only_in_deep" not in r[0]
        assert pickle_roundtrip_equal(r)


def pickle_roundtrip_equal(obj):
    import pickle
    return pickle.loads(pickle.dumps(obj)) == obj


def test_records_are_shallowly_immutable_only_and_json_state_view_is_unchanged():
    for c, rec in _record_classes():
        payload = _object_payload(len(c["fields"]))
        r = rec(*payload)
        try:
            setattr(r, c["fields"][0], {})
        except AttributeError:
            pass
        else:  # pragma: no cover
            raise AssertionError("NamedTuple fields must not be rebindable")
        # NamedTuple is NOT deeply immutable: contained dict/list objects stay mutable (legacy behavior preserved)
        r[0]["still_mutable"] = True
        import json
        assert json.dumps(list(r), sort_keys=True) == json.dumps(list(tuple(payload)), sort_keys=True)
        assert json.dumps(dict(r._asdict()), sort_keys=True) == json.dumps(dict(zip(c["fields"], payload)), sort_keys=True)


def _historical_function(sha, module, name):
    ns = {}
    exec(compile(_git_show(module, sha), f"{sha}:{module}", "exec"), ns)  # noqa: S102 (test-only, pure Owner module)
    return ns[name]


def test_real_closed_sell_owner_matches_the_historical_tuple_and_alias_behavior():
    hist = _historical_function(LEDGERS["t2"][1], "libs/reporting/reporter_bundle_runtime_parts/lifecycle_report_policy.py",
                                "closed_sell_execution_details")
    cur_mod = importlib.import_module("libs.reporting.reporter_bundle_runtime_parts.closed_sell_reconciliation")

    def build_inputs():
        nested = {"vals": [1, 2, {"deep": True}]}
        ctx = {"lifecycle": {"symbol": "AAA", "nested": nested}, "lifecycle_bundle": {"b": [1]},
               "summary_obj": {"s": 1}, "entry_execution_details": {"e": 1}, "exit_execution_details": {"x": 1},
               "execution_details": {"d": 1}, "holding_phase_observability": {"h": [1]}}
        return {"lifecycle": {"symbol": "ZZZ"}, "live_trade_context": ctx, "lifecycle_bundle": {"b": []},
                "summary_obj": {}}, nested

    def facade_for(trace):
        def reconcile(*, lifecycle, lifecycle_bundle, execution_details):
            lifecycle_bundle["reconciled"] = True          # in-place mutation the caller must observe
            trace.append(("reconcile", id(lifecycle), id(lifecycle_bundle), id(execution_details)))
            return "closed"

        def refresh(*, lifecycle, lifecycle_bundle, summary_obj, execution_details, status):
            trace.append(("refresh", status, id(summary_obj)))
            return {"refreshed": status, **summary_obj}
        return types.SimpleNamespace(_reconcile_partial_full_sell_lifecycle=reconcile,
                                     _refresh_closed_sell_lifecycle_summary=refresh)

    args_old, nested_old = build_inputs()
    args_new, nested_new = build_inputs()
    t_old, t_new = [], []
    old = hist(**args_old, facade=facade_for(t_old))
    new = cur_mod.closed_sell_execution_details(**args_new, facade=facade_for(t_new))
    assert isinstance(old, tuple) and not hasattr(old, "_fields")
    assert type(new).__name__ == "ClosedSellExecutionDetails" and tuple(new) == old and new == old
    assert [t[0] for t in t_new] == [t[0] for t in t_old] == ["reconcile", "refresh"]  # same call order
    assert new.status == old[6] == "closed"
    # alias behavior: shallow dict() copies share nested objects, and the stub's in-place mutation is visible
    assert new.lifecycle["nested"] is nested_new and old[4]["nested"] is nested_old
    assert new.lifecycle_bundle["reconciled"] is True and old[5]["reconciled"] is True
    assert new.lifecycle_bundle is not args_new["live_trade_context"]["lifecycle_bundle"]  # dict() copy, as before


# ---- T3.1: the eight converted Owner functions are the historical bodies, byte-for-byte at the AST level ------------
T3_1_START_SHA = "9e312c9fec0d4eb09f0b729456509b0469c7470f"


def _t3_1_changes():
    return json.loads(T3_1.read_text(encoding="utf-8"))["changes"]


def _unwrap_if_true(body):
    if len(body) == 2 and isinstance(body[0], ast.If) and isinstance(body[0].test, ast.Constant) \
            and body[0].test.value is True and not body[0].orelse:
        return body[0].body + body[1:]
    return body


def test_t3_1_converted_functions_equal_their_pre_t3_1_bodies_modulo_record_wrapper():
    changes = _t3_1_changes()
    assert len(changes) == 8
    for c in changes:
        before = {n.name: n for n in ast.parse(_git_show(c["old_module"], T3_1_START_SHA)).body
                  if isinstance(n, ast.FunctionDef)}[c["old_function"]]
        after = {n.name: n for n in _tree(c["new_module"]).body if isinstance(n, ast.FunctionDef)}[c["new_function"]]
        assert ast.dump(before.args) == ast.dump(after.args), c["new_function"]
        b_body, a_body = _unwrap_if_true(before.body), after.body
        assert [ast.dump(x) for x in b_body[:-1]] == [ast.dump(x) for x in a_body[:-1]], c["new_function"]
        b_ret, a_ret = b_body[-1].value, a_body[-1].value
        assert isinstance(b_ret, ast.Tuple) and isinstance(a_ret, ast.Call) and a_ret.func.id == c["record"]
        assert [ast.dump(e) for e in b_ret.elts] == [ast.dump(e) for e in a_ret.args]
        assert [e.id for e in b_ret.elts] == c["fields"] and len(c["fields"]) == c["arity"]
        assert not a_ret.keywords


def test_t3_1_old_names_are_gone_from_production_callers_and_new_names_are_imported():
    for c in _t3_1_changes():
        hits = subprocess.run(["git", "grep", "-l", "-w", c["old_function"], "--", "*.py", ":!tests/"], cwd=ROOT,
                              capture_output=True, text=True).stdout.split()
        assert hits == [], (c["old_function"], hits)
        users = subprocess.run(["git", "grep", "-l", "-w", c["new_function"], "--", "*.py", ":!tests/"], cwd=ROOT,
                               capture_output=True, text=True).stdout.split()
        assert len(users) >= 2, (c["new_function"], users)  # the Owner and at least one real caller
