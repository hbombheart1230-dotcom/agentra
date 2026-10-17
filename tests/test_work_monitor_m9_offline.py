"""M9 new persisted synthetic DTO consumer and real forbidden-mutation oracles.

No protected file edits. Mutants execute ONLY as private AST modules with fake
data/closed capabilities. This is not real persisted production report parity.
"""
import ast
import copy
import importlib
import importlib.util
import json
import os
import subprocess
import sys
import types
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts/refactor"))
import work_monitor_current_tree as C
import work_monitor_contracts as O
import p163_monitor_freeze_tool as N

INTENT = "libs/runtime/monitor/entry_cascade_projection.py"


def isolated(path, transform=None):
    tree = C._tree(C.base_source(path))
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ImportFrom) and node.module in {"typing", "__future__"}:
            nodes.append(node)
        elif isinstance(node, ast.Import) and all(a.name == "os" for a in node.names):
            nodes.append(node)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None:
            try:
                ast.literal_eval(node.value)
            except (ValueError, TypeError):
                continue
            nodes.append(node)
    tree.body = nodes
    if transform:
        tree = transform(tree)
    module = types.ModuleType("_monitor_m9_private_ast")
    from libs.core.symbols import normalize_symbol
    module.normalize_symbol = normalize_symbol
    exec(compile(ast.fix_missing_locations(tree), path, "exec"), module.__dict__)
    return module


class ClosedFacade:
    def __getattr__(self, name):
        raise AssertionError("Forbidden runtime capability: " + name)


def intent_input(variant):
    values = dict(symbol="MOCK001", qty=1, order_price=101.8, order_price_source="synthetic",
                  entry_candidate_cascade={"runner_up_symbols": ["MOCK002"]}, selected={"score": 0.7},
                  entry_info={"metrics": {"nested": [1]}, "signal_chain": ["mock"]}, plan={"thesis": "Synthetic 한글"})
    if variant == "partial":
        values["entry_info"] = {}
    elif variant == "null_entry":
        values["entry_info"] = None
    elif variant == "null_plan":
        values["plan"] = None
    elif variant == "stale":
        values["entry_info"]["metrics"]["minute_snapshot_was_stale"] = True
        values["entry_info"]["metrics"]["latest_candle_ts"] = 1
    elif variant == "no_price":
        values["order_price"] = 0
    return values


@pytest.mark.parametrize("variant", ("rich", "partial", "null_entry", "null_plan", "stale", "no_price"))
def test_m9_synthetic_persisted_intent_order_alias_errors_and_artifact_consumer(variant, tmp_path):
    current = importlib.import_module(INTENT[:-3].replace("/", "."))
    import libs.runtime.canonical_artifacts as writer
    # Same unchanged real read/serialization consumer on both sides. This does
    # not pretend that FEATURE's entire import tree was a pristine BASE run.
    for path in ("libs/runtime/canonical_artifacts.py", "libs/contracts/agent_outputs.py"):
        assert (ROOT / path).read_text(encoding="utf-8") == C.base_source(path)
    observations, bytes_out = [], []
    for index, module in enumerate((isolated(INTENT), current)):
        values = copy.deepcopy(intent_input(variant))
        before = O.wire(values)
        result, error = None, None
        try:
            result = module.entry_cascade_intent(**values, facade=ClosedFacade())
        except Exception as exc:
            error = [type(exc).__name__, str(exc)]
        assert O.wire(values) == before
        if error is None:
            assert isinstance(result, tuple) and len(result) == 1
            intent = result[0]
            assert list(intent) == ["symbol", "side", "qty", "price", "thesis", "meta"]
            assert intent["side"] == "BUY" and intent["qty"] == 1
            if variant != "partial":
                assert intent["meta"]["entry_metrics"]["nested"] is values["entry_info"]["metrics"]["nested"]
            path = tmp_path / (str(index) + "-intent.json")
            path.write_text(json.dumps(intent, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
            assert list(json.loads(path.read_text(encoding="utf-8"))) == list(intent)
            fake = {"run_id": "m9-synthetic-only", "tick_ts": 1760000000, "intents": [intent], "monitor": {},
                    "reports_root": str(tmp_path / ("fake-reports-" + str(index)))}
            with N._freeze_globals():
                artifact = Path(writer.write_monitor_artifact(fake))
            assert artifact.resolve().is_relative_to(tmp_path.resolve())
            bytes_out.append(artifact.read_bytes())
            assert fake["intents"][0] is intent
        observations.append({"output": O.wire(result), "error": error, "aliases": O.alias_paths([values, result])})
    assert observations[0] == observations[1]
    if bytes_out:
        assert bytes_out[0] == bytes_out[1]


def test_m9_failed_fake_artifact_write_does_not_publish_success_path(monkeypatch, tmp_path):
    import libs.runtime.canonical_artifacts as writer
    error = OSError("synthetic write denied")
    def denied(*args, **kwargs):
        raise error
    monkeypatch.setattr(writer, "_write_artifact", denied)
    state = {"run_id": "m9-synthetic-only", "tick_ts": 1760000000, "monitor": {}, "reports_root": str(tmp_path)}
    with pytest.raises(OSError) as raised:
        writer.write_monitor_artifact(state)
    assert raised.value is error
    assert "canonical_artifacts" not in state and "_canonical_written_paths" not in state


@pytest.mark.parametrize("mid_call", (False, True))
def test_m9_retained_cooldown_before_and_mid_call_patch_identity(mid_call):
    path = "libs/runtime/monitor/entry_candidate_guards.py"
    current = importlib.import_module(path[:-3].replace("/", "."))
    outcomes = []
    for module in (isolated(path), current):
        calls = []
        facade = types.SimpleNamespace()
        def convert(value):
            calls.append(value)
            if mid_call:
                facade._to_int = lambda v: calls.append(v) or 0
            return int(value or 0)
        facade._to_int = convert
        cooldown, info = {"MOCK001": 200}, {}
        result = module.resolve_entry_intent_cooldown({"MOCK001": {"qty": 1}}, cooldown, info, 30, 100, "MOCK001", facade=facade)
        outcomes.append((result, cooldown, info, calls))
    assert outcomes[0] == outcomes[1]
    assert outcomes[0][0] == (200 if mid_call else 0)


def fn(tree, name):
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)


def check(condition, label):
    if not condition:
        raise AssertionError(label)


def probes():
    # Each oracle must pass on BASE and KILL a realistic unauthorized mutant.
    rows = []
    def priority(t):
        f = fn(t, "exit_reason_priority")
        for n in ast.walk(f):
            if isinstance(n, ast.Dict):
                for i, k in enumerate(n.keys):
                    if isinstance(k, ast.Constant) and k.value == "hard_stop":
                        n.values[i] = ast.Constant(1000)
        return t
    rows.append(("priority", "libs/runtime/monitor_exit/reasons.py", priority,
                 lambda m: check(m.exit_reason_priority("emergency_halt") > m.exit_reason_priority("hard_stop"), "priority reversed")))
    def hard_stop(t):
        for n in ast.walk(fn(t, "stop_loss_exit_check")):
            if isinstance(n, ast.Compare) and isinstance(n.ops[0], ast.LtE):
                n.ops[0] = ast.Gt()
                break
        return t
    def hard_oracle(m):
        marker = {}
        def finalize(**kw):
            marker.update(kw)
            return marker
        result = m.stop_loss_exit_check(finalize, 0.04, {"hard_stop_pnl_ratio": -0.05, "stop_pnl_ratio": -0.05}, -0.05, 0.03)
        check(result is marker and marker["reason"] == "hard_stop", "hard-stop boundary/order")
    rows.append(("hard_stop", "libs/runtime/monitor_exit/exit_trigger_ladder.py", hard_stop, hard_oracle))
    def cooldown(t):
        f = fn(t, "resolve_sell_cooldown_sec")
        n = next(n for n in f.body if isinstance(n, ast.Assign) and any(isinstance(a, ast.Name) and a.id == "raw" for a in n.targets))
        n.value = ast.Constant(0)
        return t
    rows.append(("cooldown", "libs/runtime/monitor_exit/hold_controls.py", cooldown,
                 lambda m: check(m.resolve_sell_cooldown_sec({"applied_policy": {"execution": {"cooldowns": {"sell_sec": 500}}}}, {"sell_cooldown_sec": 10}) == 500, "cooldown precedence")))
    def guard(t):
        n = next(n for n in fn(t, "evaluate_entry_guard").body if isinstance(n, ast.If))
        n.test = ast.Constant(False)
        return t
    def guard_oracle(m):
        kw = dict(entry_info={"triggered": True}, entry_quality_gate={}, entry_cost_filter={"passed": True}, selected_already_held=True, selected_pending_buy=False, max_positions_reached=False, closeout_window_active=False, buy_blocked_post_exit_cooldown=False, entry_intent_cooldown_sec=0, cooldown_until=0, now_epoch=1, forced_entry_block_reason="synthetic_forced")
        check(m.evaluate_entry_guard(**kw)["entry_guard_reason"] == "synthetic_forced", "forced guard override")
    rows.append(("guard", "libs/runtime/monitor_entry_blockers.py", guard, guard_oracle))
    def sizing(t):
        f = fn(t, "resolve_position_sizing_config")
        for n in ast.walk(f):
            if isinstance(n, ast.If) and ast.unparse(n.test) == "state.get('use_position_sizing') is not None":
                n.test = ast.Constant(False)
        return t
    rows.append(("sizing", "libs/runtime/monitor_entry_sizing.py", sizing,
                 lambda m: check(m.resolve_position_sizing_config({"use_position_sizing": False}, policy={"use_position_sizing": True}, strategy_policy={})[0] is False, "sizing opt-out overridden")))
    def rank(t):
        for n in t.body:
            if isinstance(n, ast.Assign) and any(isinstance(a, ast.Name) and a.id == "_DEFAULT_Q15_MAX_RUNNER_UP_RANK" for a in n.targets):
                n.value = ast.Constant(10)
        return t
    rows.append(("rank", "libs/runtime/monitor_candidate_cascade.py", rank,
                 lambda m: check(m.build_entry_candidate_cascade_plan(selected_symbol="MOCK001", ranked_candidates=[{"symbol":"MOCK001","rank":1},{"symbol":"MOCK004","rank":4}], scanner_output={}, open_position_count=0, max_runner_ups=5, entry_reason="breakout_not_ready")["max_priority_rank"] == 3, "runner rank cap bypass")))
    def broker(t):
        fn(t, "entry_cascade_intent").body.insert(0, ast.Expr(value=ast.Call(func=ast.Attribute(value=ast.Name(id="facade", ctx=ast.Load()), attr="submit_order", ctx=ast.Load()), args=[], keywords=[])))
        return t
    rows.append(("broker_leak", INTENT, broker,
                 lambda m: check(m.entry_cascade_intent(**intent_input("rich"), facade=ClosedFacade())[0]["side"] == "BUY", "intent-only contract")))
    return rows


@pytest.mark.parametrize("name,path,mutant,oracle", probes(), ids=lambda v: v if isinstance(v, str) else None)
def test_m9_realistic_forbidden_mutations_are_killed_without_source_edits(name, path, mutant, oracle):
    oracle(isolated(path))
    with pytest.raises(AssertionError):
        oracle(isolated(path, mutant))


def test_m9_semantic_mutation_oracles_still_work_under_python_optimized(tmp_path):
    code = '''
import importlib.util,sys
s=importlib.util.spec_from_file_location('m9tests',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
count=0
for name,path,mutant,oracle in m.probes():
 oracle(m.isolated(path))
 try:oracle(m.isolated(path,mutant))
 except AssertionError:count+=1
 else:raise RuntimeError('escaped mutant '+name)
if count!=7:raise RuntimeError(count)
print(count)
'''
    result = subprocess.run([sys.executable, "-O", "-c", code, __file__], cwd=tmp_path, env=dict(os.environ), capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "7"
