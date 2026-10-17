"""Reporter R10-A: offline BASE-vs-HEAD contracts for the READ_ONLY subset of the 47 RETAIN_FACADE functions.

Not a relocation proof and not a move authorisation. Each retained read-only function runs twice in fresh interpreters —
inside an extracted pinned-BASE tree and inside the current HEAD tree — against identical temp report trees (valid,
Korean, CRLF, malformed, empty, missing, directory inputs). Required: equal outcome (JSON bytes or exception type+message),
equal ORDERED filesystem observation log (open/read/exists/is_dir/iterdir/glob/rglob/...), and NO write to the temp tree.
The clock is frozen in both runs. Functions needing a Python callable argument are reported NEEDS_FIXTURE (not run).
The BASE tree comes from `git archive` of the pinned commit; if that commit is not present (shallow CI checkout) the
module fails with an explicit instruction instead of silently skipping."""
import inspect
import importlib
import io
import json
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = "d773709ba2f70471fad9badba4f92400f7818319"
RUNNER = ROOT / "scripts/refactor/work_reporter_contract_runner.py"
TRIAGE = json.loads((ROOT / "docs/refactor/work_projects/evidence/reporter/r8_function_triage.json").read_text(encoding="utf-8"))
READ_ONLY = [(r["legacy_path"], r["name"]) for r in TRIAGE["rows"] if r.get("r10_class") == "READ_ONLY"]


def _base_tree(tmp_root):
    if subprocess.run(["git", "cat-file", "-e", BASE + "^{commit}"], cwd=ROOT).returncode != 0:
        raise AssertionError(f"pinned BASE {BASE} not in this clone: fetch with full history (fetch-depth: 0)")
    data = subprocess.run(["git", "archive", BASE, "libs", "graphs"], cwd=ROOT, capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as tf:
        tf.extractall(tmp_root)
    return tmp_root


@pytest.fixture(scope="module")
def base_tree(tmp_path_factory):
    return _base_tree(tmp_path_factory.mktemp("base_tree"))


def make_data(root):
    trade = root / "trades" / "2026-10-17" / "0930" / "TRD_20261017_005930_01"
    (trade / "lifecycle").mkdir(parents=True)
    (trade / "reports").mkdir()
    (trade / "lifecycle" / "trade_lifecycle.json").write_text(json.dumps(
        {"trade_id": "TRD_20261017_005930_01", "symbol": "005930", "day": "2026-10-17", "status": "closed",
         "entry": {"run_id": "e1", "ts": "2026-10-17T00:01:00Z"}, "exit": {"run_id": "x1"},
         "summary": {"entry_reason_human": "VWAP 돌파"}}, ensure_ascii=False), encoding="utf-8")
    (trade / "lifecycle_bundle.json").write_text('{"symbol": "005930", "trade_lifecycle_status": "closed"}', encoding="utf-8")
    (trade / "story_input.json").write_bytes(b'{"symbol": "005930",\r\n "trade_id": "TRD_20261017_005930_01"}\r\n')
    (trade / "reports" / "ai_trade_report.json").write_text('{"summary": "요약", "status": "ok"}', encoding="utf-8")
    (trade / "reports" / "ai_trade_report.md").write_text("# 리포트\n- a\n", encoding="utf-8")
    (trade / "reports" / "broken.json").write_text("{not json", encoding="utf-8")
    (trade / "reports" / "empty.json").write_text("", encoding="utf-8")
    (root / "events.jsonl").write_bytes(b'{"ts": "2026-10-17T01:00:00Z", "symbol": "005930"}\r\n{bad}\n\n[1]\n')
    (root / "data.json").write_text('{"k": "값", "rows": [1, 2]}', encoding="utf-8")
    return root


def snapshot(root):
    return sorted((p.relative_to(root).as_posix(), p.read_bytes() if p.is_file() else b"<dir>") for p in root.rglob("*"))


PATH_VALUES = ["$ROOT", "$ROOT/trades/2026-10-17", "$ROOT/missing.json",
               "$ROOT/trades/2026-10-17/0930/TRD_20261017_005930_01/lifecycle/trade_lifecycle.json",
               "$ROOT/events.jsonl", "$ROOT/trades/2026-10-17/0930/TRD_20261017_005930_01/reports/broken.json",
               "$ROOT/trades/2026-10-17/0930/TRD_20261017_005930_01/reports/empty.json"]


def _value(p, i):
    n, ann = p.name, str(p.annotation)
    if "Path" in ann or any(t in n for t in ("root", "dir", "path", "file")):
        return PATH_VALUES[i % len(PATH_VALUES)]
    if n == "day" or n.endswith("_day"):
        return ["2026-10-17", "", "2026-10-16"][i % 3]
    if n == "symbol":
        return ["005930", "", "000660"][i % 3]
    if "trade_id" in n:
        return ["TRD_20261017_005930_01", "", "X"][i % 3]
    if "bool" in ann:
        return bool(i % 2)
    if "int" in ann:
        return [3, 0, 1][i % 3]
    if "str" in ann:
        return ["005930", "", "x"][i % 3]
    return [{}, {"symbol": "005930", "trade_id": "TRD_20261017_005930_01", "day": "2026-10-17"}, None][i % 3]


def build_calls(fn):
    sig = inspect.signature(fn)
    req = [p for p in sig.parameters.values() if p.default is p.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
    kw = [p for p in sig.parameters.values() if p.default is p.empty and p.kind is p.KEYWORD_ONLY]
    if any("Callable" in str(p.annotation) for p in req + kw):
        return None
    return [{"args": [_value(p, i) for p in req], "kwargs": {p.name: _value(p, i) for p in kw}} for i in range(len(PATH_VALUES))]


def observe(tree, module, function, calls, data_root, tmp):
    spec = tmp / f"spec_{abs(hash((str(tree), function)))}.json"
    spec.write_text(json.dumps({"module": module, "function": function, "calls": calls, "data_root": str(data_root)}), encoding="utf-8")
    r = subprocess.run([sys.executable, str(RUNNER), str(tree), str(spec)], cwd=str(tmp), capture_output=True,
                       env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0", "PATH": __import__("os").environ.get("PATH", ""),
                            "SYSTEMROOT": __import__("os").environ.get("SYSTEMROOT", "")})
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")[-2000:]
    return r.stdout.decode("utf-8")


def test_read_only_subset_is_classified_and_non_empty():
    assert len(READ_ONLY) >= 30
    assert len(set(READ_ONLY)) == len(READ_ONLY)


@pytest.mark.parametrize("path,name", READ_ONLY)
def test_retained_read_only_function_base_equals_head(path, name, base_tree, tmp_path):
    module = path[:-3].replace("/", ".")
    fn = getattr(importlib.import_module(module), name)
    calls = build_calls(fn)
    if calls is None:
        assert name in CALLBACK_FIXTURES, f"{name}: callable argument without a hand-written fixture"
        pytest.skip("callable argument: covered by test_callback_reader_fixture_base_equals_head")
    data = make_data(tmp_path / "data")  # same tree for both runs; it must stay byte-identical (read-only claim)
    before = snapshot(data)
    base_obs = observe(base_tree, module, name, calls, data, tmp_path)
    assert snapshot(data) == before, "BASE run wrote to the data tree"
    head_obs = observe(ROOT, module, name, calls, data, tmp_path)
    assert snapshot(data) == before, "HEAD run wrote to the data tree"
    assert head_obs == base_obs


def test_negative_read_order_mutation_is_detected(base_tree, tmp_path):
    """Reversing the line order of a BASE jsonl reader must change the observation (guards against vacuous equality)."""
    mutated = tmp_path / "mutated"
    shutil.copytree(base_tree / "libs", mutated / "libs")
    shutil.copytree(base_tree / "graphs", mutated / "graphs")
    target = mutated / "libs/reporting/symbol_trade_report.py"
    src = target.read_text(encoding="utf-8-sig")
    assert "for raw_line in handle:" in src
    target.write_text(src.replace("for raw_line in handle:", "for raw_line in list(handle)[::-1]:", 1), encoding="utf-8")
    calls = [{"args": ["$ROOT/two.jsonl"], "kwargs": {}}]
    data = make_data(tmp_path / "d")
    (data / "two.jsonl").write_text('{"n": 1}\n{"n": 2}\n', encoding="utf-8")
    base_obs = observe(base_tree, "libs.reporting.symbol_trade_report", "_iter_jsonl", calls, data, tmp_path)
    mut_obs = observe(mutated, "libs.reporting.symbol_trade_report", "_iter_jsonl", calls, data, tmp_path)
    assert base_obs != mut_obs


def test_negative_exception_mutation_is_detected(base_tree, tmp_path):
    mutated = tmp_path / "mutated_exc"
    shutil.copytree(base_tree / "libs", mutated / "libs")
    shutil.copytree(base_tree / "graphs", mutated / "graphs")
    target = mutated / "libs/reporting/reporter_analysis.py"
    src = target.read_text(encoding="utf-8-sig")
    marker = "def _read_json(path: Path) -> Dict[str, Any]:\n"
    assert marker in src
    target.write_text(src.replace(marker, marker + "    raise KeyError('mutated')\n", 1), encoding="utf-8")
    calls = [{"args": ["$ROOT/data.json"], "kwargs": {}}]
    data = make_data(tmp_path / "e")
    assert observe(base_tree, "libs.reporting.reporter_analysis", "_read_json", calls, data, tmp_path) != \
        observe(mutated, "libs.reporting.reporter_analysis", "_read_json", calls, data, tmp_path)


OBSERVED = [(r["legacy_path"], r["name"], r["r10_class"]) for r in TRIAGE["rows"]
            if r.get("r10_class") in ("WRITER", "CLOCK_LOG_ENV", "MODULE_IDENTITY", "REDEFINITION")]


def test_observed_classes_are_the_13_non_read_only_rows():
    assert len(OBSERVED) == 13


@pytest.mark.parametrize("path,name,klass", OBSERVED)
def test_retained_side_effect_function_base_equals_head_by_observation(path, name, klass, base_tree, tmp_path):
    """Observation only (no production paths): BASE and HEAD each run on a fresh copy of the same pristine temp tree at
    the SAME absolute location (frozen clock). Outcomes, ordered fs log and the resulting temp tree must be identical."""
    module = path[:-3].replace("/", ".")
    fn = getattr(importlib.import_module(module), name)
    calls = build_calls(fn)
    if calls is None:
        assert name in CALLBACK_FIXTURES, f"{name}: callable argument without a hand-written fixture"
        pytest.skip("callable argument: covered by test_callback_reader_fixture_base_equals_head")
    pristine = make_data(tmp_path / "pristine")
    data = tmp_path / "data"
    obs = []
    for tree in (base_tree, ROOT):
        if data.exists():
            shutil.rmtree(data)
        shutil.copytree(pristine, data)
        obs.append(observe(tree, module, name, calls, data, tmp_path))
    assert obs[0] == obs[1]


@pytest.mark.parametrize("path,name,klass", [o for o in OBSERVED if o[2] == "REDEFINITION"])
def test_redefinition_effective_last_definition_is_unchanged(path, name, klass):
    import ast
    src = (ROOT / path).read_text(encoding="utf-8-sig")
    base = subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT).decode("utf-8-sig")
    last = lambda s: [n for n in ast.parse(s).body if isinstance(n, ast.FunctionDef) and n.name == name]  # noqa: E731
    cur_defs, base_defs = last(src), last(base)
    assert len(cur_defs) == len(base_defs) >= 2
    assert [ast.dump(n) for n in cur_defs] == [ast.dump(n) for n in base_defs]
    fn = getattr(importlib.import_module(path[:-3].replace("/", ".")), name)
    assert fn.__code__.co_firstlineno == cur_defs[-1].lineno + len(cur_defs[-1].decorator_list)


TRADE = "trades/2026-10-17/0930/TRD_20261017_005930_01"
META_CASES = [
    {"trade_root_path": f"$STRROOT/{TRADE}", "aggregated_bundle_path": f"$STRROOT/{TRADE}/lifecycle_bundle.json",
     "trade_lifecycle_json_path": f"$STRROOT/{TRADE}/lifecycle/trade_lifecycle.json",
     "trade_report_json_path": f"$STRROOT/{TRADE}/reports/ai_trade_report.json",
     "trade_report_md_path": f"$STRROOT/{TRADE}/reports/ai_trade_report.md",
     "trade_story_input_path": f"$STRROOT/{TRADE}/story_input.json",
     "operator_brief_json_path": f"$STRROOT/{TRADE}/reports/ai_trade_report.json",
     "operator_brief_md_path": f"$STRROOT/{TRADE}/reports/ai_trade_report.md"},
    {"trade_root_path": f"$STRROOT/{TRADE}", "trade_report_json_path": f"$STRROOT/{TRADE}/reports/broken.json",
     "operator_brief_json_path": f"$STRROOT/{TRADE}/reports/empty.json"},
    {"trade_root_path": "$STRROOT/missing_dir"},
    {},
]
CALLBACK_FIXTURES = {
    "load_trade_report_detail_payloads": lambda meta: {"args": [meta], "kwargs": {"read_json": "$FN:libs.reporting.single_trade_report:_read_json"}},
    "load_trade_report_payloads": lambda meta: {"args": [meta], "kwargs": {"read_json": "$FN:libs.reporting.single_trade_report:_read_json"}},
    "load_operator_brief_detail_payloads": lambda meta: {"args": [meta], "kwargs": {"read_json": "$FN:libs.reporting.single_trade_report:_read_json",
                                                                                    "allow_saved_brief": True}},
}


@pytest.mark.parametrize("name", sorted(CALLBACK_FIXTURES))
def test_callback_reader_fixture_base_equals_head(name, base_tree, tmp_path):
    """Hand-written fixtures for the three NEEDS_FIXTURE readers: the production caller passes the facade's own
    (local) `_read_json`; the fixture uses the equivalent module-level reader single_trade_report._read_json from each
    tree under test (BASE vs HEAD)."""
    calls = [CALLBACK_FIXTURES[name](m) for m in META_CASES]
    data = make_data(tmp_path / "data")
    before = snapshot(data)
    base_obs = observe(base_tree, "libs.reporting.trade_read_model", name, calls, data, tmp_path)
    head_obs = observe(ROOT, "libs.reporting.trade_read_model", name, calls, data, tmp_path)
    assert snapshot(data) == before
    assert head_obs == base_obs
    assert '"ok"' in head_obs and "요약" in head_obs  # populated success path really read the report JSON
