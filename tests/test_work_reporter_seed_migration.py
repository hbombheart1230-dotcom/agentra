"""Reporter whole-role project: relocated pure owners under ``libs/agents/reporter`` with strict identity shims.

Per registered module (offline, no Broker/LLM/network/production reads): body byte-identical to the pinned runtime BASE
blob, legacy shim passes the strict source-AST verifier (hard-coded mapping) and rejects mutations, one module object in
every import order, shared objects/late-bound monkeypatch, exactly one body, <=350 LOC, and BASE-first replay cases
(results, exception types, key order, mutation and alias flags) reproduced through BOTH paths.
"""
import gzip
import hashlib
import importlib
import importlib.util
import inspect
import json
import re
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = "d773709ba2f70471fad9badba4f92400f7818319"  # pinned runtime BASE (blobs, replay)
START = "eeb742a33b16f6271ff364a904e187b470561c7e"  # activation commit (docs only over BASE); scope diff origin
FIX = ROOT / "tests" / "fixtures" / "work_reporter" / "seed_cases.json.gz"
PROV = ROOT / "tests" / "fixtures" / "work_reporter" / "seed_cases.provenance.json"
# legacy module -> (canonical subpackage, pinned BASE blob)
REGISTRY = {
    "narrative_axes": ("narrative", "8eee2c502ed8f1646c0008e7979a6c438a01972a"),
    "trade_fallback_text": ("narrative", "de225b4556c9780ec84a7a3ee321c8659aea9373"),
    "reasoning_trace": ("narrative", "0807b9f3a94238f73c7617e1e0e8d8f514e9e676"),
    "trade_execution_outcome_text": ("narrative", "ca7ff430a44cea2dcbf2a1a1b3adccde13b354c1"),
    "chart_structure_decision_hint_summary": ("read_models", "16a5d887bc3a49efb6280cb6ea1693f9c3255949"),
    "policy_surface_summary": ("read_models", "4a3aa078fefa2e83fac1d0b610a2b667befb851c"),
    "report_metadata": ("read_models", "d0fffd0097d55f37d1038bf20bb79bd8780ed654"),
    "trade_reporter_status_text": ("narrative", "ce3578e8d2e6e7036a9f1f48085516a73905fca3"),
    "truth_source_labels": ("narrative", "5a30f3df03c13468b8c81e083212d4063fd0ea0d"),
    "trade_pnl_estimate": ("read_models", "614f79242d78f4cdd536062bc0f0fe49c067c9ba"),
    "strategist_quant_context_report": ("narrative", "7068f16019b1c7c171cc35652bfc9748296abbd2"),
    "trade_report_post_exit_shadow": ("narrative", "040c582f99654778312216fe7ffbc1e6ccd3ea9c"),
}
# named decomposition (Phase B): legacy facade module -> owner modules in libs/agents/reporter/read_models (bodies verbatim)
DECOMPOSED = {"trade_report_symbol_metadata": ("read_models", ["symbol_metadata_fallbacks", "symbol_metadata_text", "symbol_metadata_sources",
                                                                "symbol_metadata_name_inference", "symbol_metadata_resolution"]),
              "trade_story_pipeline_news": ("narrative", ["news_text", "news_headlines", "news_scanner_contribution"]),
              "trade_story_pipeline_scanner": ("narrative", ["scanner_basis", "scanner_selection_trace", "scanner_evidence_fit"])}
P15_A_HISTORICAL_TREE = "d7ab82940deaa05810b28ef78fc0be88e201f9b6"  # integration/p1.5 BASE: exact historical folder inventory
P15_A_FACADES = {"libs/reporting/operator_visibility.py", "libs/reporting/phase_runtime_health.py",
                 "libs/reporting/operator_period_summary.py", "libs/reporting/metrics_report_generator.py"}
# P1.5 DEV-A Q8 post-hoc evaluation facades and their pure owners: exact closed set (no wildcard); the Q8 trust
# policy modules stay outside it and are still policed by the scope check below
# P1.5 DEV-A wave A1: reporter AI review facade and its pure *_parts owners (exact closed set, no wildcard)
P15_A_REVIEW_PATHS = {"libs/reporting/reporter_ai_review.py", "libs/reporting/reporter_ai_review_parts/__init__.py",
                      "libs/reporting/reporter_ai_review_parts/prompting.py", "libs/reporting/reporter_ai_review_parts/compact_input.py",
                      "libs/reporting/reporter_ai_review_parts/result_shaping.py", "libs/reporting/reporter_ai_review_parts/review_resolution.py"}
# P1.5 DEV-A large-first wave: Q9 full-chain component review facade and its pure *_parts owners (exact closed set, no wildcard)
P15_A_FULLCHAIN_PATHS = {"libs/reporting/evaluation/full_chain_component_review.py", "libs/reporting/evaluation/full_chain_review_parts/__init__.py",
                         "libs/reporting/evaluation/full_chain_review_parts/root_cause.py", "libs/reporting/evaluation/full_chain_review_parts/attribution.py",
                         "libs/reporting/evaluation/full_chain_review_parts/component_decisions.py", "libs/reporting/evaluation/full_chain_review_parts/render.py"}
P15_A_Q8_PATHS = {"libs/reporting/q8_historical_review.py", "libs/reporting/q8_shadow_blocker_review.py",
                  "libs/reporting/q8_lane_decision_table.py",
                  "libs/reporting/evaluation/q8_historical_aggregation_p15.py",
                  "libs/reporting/evaluation/q8_historical_render_p15.py",
                  "libs/reporting/evaluation/q8_shadow_readout_p15.py",
                  "libs/reporting/q8_trusted_reaggregation.py",
                  "libs/reporting/evaluation/q8_trusted_reaggregation_projection_p15.py",
                  "libs/reporting/quant_shadow_candidate_evaluation.py",
                  "libs/reporting/evaluation/quant_shadow_forward_readout_p15.py",
                  "libs/reporting/evaluation/quant_shadow_render_p15.py",
                  "libs/reporting/evaluation/quant_shadow_observation_projection_p15.py"}
P15_A_PURE_OWNERS = {("read_models", n + ".py") for n in (
    "operator_daily_projection", "operator_run_context_projection", "phase_health_projection", "phase_health_policy_views",
    "phase_health_text_rendering", "period_summary_projection", "metrics_projection", "metrics_summary_projection",
    "metrics_event_fold")}
REPORTER_PACKAGES = {"narrative", "read_models"}  # exact, versioned by this project (shared allowlist is Work-owned)
OLD, NEW = "libs.reporting.{}", "libs.agents.reporter.{}.{}"

_spec = importlib.util.spec_from_file_location("_wave_b_gate_reporter", ROOT / "tests" / "test_p154_wave_b_moved_bodies.py")
WB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(WB)


def _blob(data):
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def _run(code):
    # temp cwd, inherited env (R11 hygiene: a child interpreter never runs with the repository as its cwd)
    return subprocess.run([sys.executable, "-c", code], cwd=tempfile.gettempdir(), check=True, capture_output=True, text=True,
                          env={**os.environ, "PYTHONPATH": str(ROOT)}).stdout.strip()


def _paths(name):
    sub = REGISTRY[name][0]
    return f"libs/reporting/{name}.py", f"libs/agents/reporter/{sub}/{name}.py"


@pytest.mark.parametrize("name", sorted(REGISTRY))
def test_body_is_byte_identical_to_the_pinned_base_blob(name):
    _, canonical = _paths(name)
    data = (ROOT / canonical).read_bytes().replace(b"\r\n", b"\n")
    assert _blob(data) == REGISTRY[name][1]
    assert len(data.decode("utf-8").splitlines()) <= 350


@pytest.mark.parametrize("name", sorted(REGISTRY))
def test_shim_passes_the_strict_ast_verifier_and_rejects_mutations(name):
    legacy, canonical = _paths(name)
    sub = REGISTRY[name][0]
    good = (ROOT / legacy).read_text(encoding="utf-8")
    assert WB._verify_identity_shim_source(good, legacy, canonical) == canonical
    other = next(n for n in sorted(REGISTRY) if n != name)
    for bad in (good + "\nraise RuntimeError(1)\n", good + "\nimport subprocess\n",
                good.replace(f"{sub} import {name}", f"{sub} import {other}"),
                good.replace(f"libs.agents.reporter.{sub}", "libs.agents.reporter.context"),
                good.replace("as _canonical", "as canonical"), good.replace("import sys as _sys", "import sys")):
        with pytest.raises(AssertionError):
            WB._verify_identity_shim_source(bad, legacy, canonical)


@pytest.mark.parametrize("name", sorted(REGISTRY))
def test_old_and_new_paths_are_one_module_object_in_every_import_order(name):
    sub = REGISTRY[name][0]
    o, n = OLD.format(name), NEW.format(sub, name)
    assert _run(f"import importlib; a=importlib.import_module('{o}'); b=importlib.import_module('{n}'); print(a is b)") == "True"
    assert _run(f"import importlib; b=importlib.import_module('{n}'); a=importlib.import_module('{o}'); print(a is b)") == "True"
    assert _run(f"from libs.reporting import {name} as a; from libs.agents.reporter.{sub} import {name} as b; "
                f"import libs.reporting as p; print(a is b and p.{name} is b)") == "True"


@pytest.mark.parametrize("name", sorted(REGISTRY))
def test_objects_signatures_and_use_time_monkeypatch_are_shared(name, monkeypatch):
    sub = REGISTRY[name][0]
    old, new = importlib.import_module(OLD.format(name)), importlib.import_module(NEW.format(sub, name))
    assert old is new
    funcs = [k for k, v in vars(new).items() if inspect.isfunction(v) and v.__module__ == new.__name__]
    assert funcs
    for k in funcs:
        assert getattr(old, k) is getattr(new, k)
    marker = object()
    monkeypatch.setattr(old, funcs[0], marker)
    assert getattr(new, funcs[0]) is marker


@pytest.mark.parametrize("name", sorted(REGISTRY))
def test_shim_has_no_code_and_exactly_one_body_exists(name):
    sub = REGISTRY[name][0]
    new = importlib.import_module(NEW.format(sub, name))
    legacy, canonical = _paths(name)
    funcs = [k for k, v in vars(new).items() if inspect.isfunction(v) and v.__module__ == new.__name__]
    sources = {p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8", errors="replace")
               for p in list((ROOT / "libs").rglob("*.py")) + list((ROOT / "graphs").rglob("*.py"))}
    unique = 0
    for fn in funcs:  # names that were defined ONLY in this module at BASE must now be defined ONLY in the canonical body
        base = subprocess.run(["git", "grep", "-l", f"def {fn}(", BASE, "--", "libs", "graphs"], cwd=ROOT,
                              capture_output=True, text=True).stdout.split()
        base = {x.split(":", 1)[1] for x in base}
        assert legacy in base
        if base != {legacy}:
            continue
        unique += 1
        assert {p for p, s in sources.items() if f"def {fn}(" in s} == {canonical}, fn
    assert unique >= 1


def _cap():
    sys.path.insert(0, str(ROOT / "scripts" / "refactor"))
    try:
        import work_reporter_capture as cap
    finally:
        sys.path.pop(0)
    return cap


def _dump(rows):
    return json.dumps(rows, ensure_ascii=False, separators=(",", ":"))


def test_fixture_provenance_manifest_matches_the_fixture_bytes():
    prov = json.loads(PROV.read_text(encoding="utf-8"))
    raw = FIX.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == prov["gz_sha256"]
    assert hashlib.sha256(gzip.decompress(raw)).hexdigest() == prov["payload_sha256"]
    assert len(json.loads(gzip.decompress(raw))["cases"]) == prov["cases"] == 2565


_IN_TYPEERROR = re.compile(r"argument of type '([A-Za-z_][A-Za-z0-9_.]*)' is not (?:a container or )?iterable")
_TOO_MANY_UNPACK = re.compile(r"too many values to unpack \(expected (0|[1-9][0-9]*)(?:, got (0|[1-9][0-9]*))?\)")


def _is_cpython_message_rewording(got, rec):
    exc, gm, rm = got.get("exc"), got.get("msg", ""), rec.get("msg", "")
    if exc != rec.get("exc"):
        return False
    if exc == "ValueError":
        # Only CPython's optional ', got M' detail may differ. Direction,
        # expected arity and any got count present on both sides stay exact.
        g, r = _TOO_MANY_UNPACK.fullmatch(gm), _TOO_MANY_UNPACK.fullmatch(rm)
        return bool(g and r) and g.group(1) == r.group(1) and (
            g.group(2) is None or r.group(2) is None or g.group(2) == r.group(2)
        )
    if exc == "TypeError":  # 3.14: "... is not iterable" -> "... is not a container or iterable"
        g, r = _IN_TYPEERROR.fullmatch(gm), _IN_TYPEERROR.fullmatch(rm)
        return bool(g and r) and g.group(1) == r.group(1)
    return False


def test_cpython_message_rewording_allowance_is_exact():
    old, new = "argument of type 'NoneType' is not iterable", "argument of type 'NoneType' is not a container or iterable"
    assert _is_cpython_message_rewording({"exc": "TypeError", "msg": new}, {"exc": "TypeError", "msg": old})
    assert not _is_cpython_message_rewording({"exc": "TypeError", "msg": new.replace("NoneType", "int")}, {"exc": "TypeError", "msg": old})
    assert not _is_cpython_message_rewording({"exc": "ValueError", "msg": new}, {"exc": "TypeError", "msg": old})
    assert not _is_cpython_message_rewording({"exc": "TypeError", "msg": "unsupported operand"}, {"exc": "TypeError", "msg": old})
    assert not _is_cpython_message_rewording({"exc": "KeyError", "msg": "x"}, {"exc": "KeyError", "msg": "y"})
    assert _is_cpython_message_rewording({"exc": "ValueError", "msg": "too many values to unpack (expected 2, got 44)"},
                                         {"exc": "ValueError", "msg": "too many values to unpack (expected 2)"})


@pytest.mark.parametrize("got,recorded", [
    ("too many values to unpack (expected 2, got 44)", "too many values to unpack (expected 2)"),
    ("too many values to unpack (expected 2)", "too many values to unpack (expected 2, got 44)"),
    ("too many values to unpack (expected 3, got 4)", "too many values to unpack (expected 3)"),
    ("too many values to unpack (expected 2, got 44)", "too many values to unpack (expected 2, got 44)"),
])
def test_cpython_unpack_allowance_accepts_only_the_optional_observed_detail(got, recorded):
    assert _is_cpython_message_rewording({"exc": "ValueError", "msg": got},
                                        {"exc": "ValueError", "msg": recorded})


@pytest.mark.parametrize("got,recorded", [
    ("not enough values to unpack (expected 99, got 0)", "too many values to unpack (expected 2)"),
    ("too many values to unpack (expected 2)", "not enough values to unpack (expected 99, got 0)"),
    ("too many values to unpack (expected 3, got 44)", "too many values to unpack (expected 2)"),
    ("too many values to unpack (expected 2, got 44)", "too many values to unpack (expected 3)"),
    ("too many values to unpack (expected 2, got 44)", "too many values to unpack (expected 2, got 45)"),
    ("not enough values to unpack (expected 2, got 0)", "not enough values to unpack (expected 2, got 1)"),
    ("too many values to unpack (expected 2, got 44) extra", "too many values to unpack (expected 2)"),
    ("too many values to unpack (expected 2)\n", "too many values to unpack (expected 2)"),
    ("prefix too many values to unpack (expected 2)", "too many values to unpack (expected 2)"),
    ("too many values to unpack (expected 2, got 44, got 45)", "too many values to unpack (expected 2)"),
    ("too many values to unpack (expected 02, got 44)", "too many values to unpack (expected 2)"),
    ("too many values to unpack (expected 2, got -1)", "too many values to unpack (expected 2)"),
    ("cannot unpack non-iterable NoneType object", "too many values to unpack (expected 2)"),
    ("unpack unrelated failure", "unpack unrelated failure"),
])
@pytest.mark.parametrize("reverse", [False, True])
def test_cpython_unpack_allowance_rejects_semantic_or_malformed_changes(got, recorded, reverse):
    if reverse:
        got, recorded = recorded, got
    assert not _is_cpython_message_rewording({"exc": "ValueError", "msg": got},
                                            {"exc": "ValueError", "msg": recorded})


def test_recorded_base_cases_are_reproduced_exactly_through_both_paths():
    prov = json.loads(PROV.read_text(encoding="utf-8"))
    cases = json.loads(gzip.decompress(FIX.read_bytes()))["cases"]
    cap = _cap()
    assert {c["mod"] for c in cases} == {OLD.format(n) for n in [*REGISTRY, *DECOMPOSED]} == set(cap.MODULES)
    got = cap.compute()  # drives the LEGACY import path of every module
    if f"{sys.version_info[0]}.{sys.version_info[1]}" == prov["produced_on_python"]:
        assert _dump(got) == _dump(cases)  # recorded interpreter: byte-exact against the frozen fixture
    else:
        # other interpreter: only CPython-worded messages may differ from the frozen fixture — unpack ValueError, and the
        # exact 3.14 rewording of the `in` TypeError (same operand type). Same-interpreter BASE parity is
        # test_same_interpreter_base_archive_replay_equals_final.
        assert len(got) == len(cases)
        for g, c in zip(got, cases):
            if g != c:
                gr, cr = dict(g["result"]), dict(c["result"])
                assert _is_cpython_message_rewording(gr, cr), (g, c)
                gr.pop("msg"); cr.pop("msg")
                assert {**g, "result": gr} == {**c, "result": cr}
    for n, (sub, _b) in REGISTRY.items():
        assert importlib.import_module(OLD.format(n)) is importlib.import_module(NEW.format(sub, n))


def test_same_interpreter_base_archive_replay_equals_final(tmp_path):
    """Strict same-environment BASE-vs-FINAL contract, independent of the interpreter's message wording."""
    arc = subprocess.run(["git", "archive", BASE], cwd=ROOT, capture_output=True, check=True).stdout
    import io
    import tarfile
    base_root = tmp_path / "base"
    base_root.mkdir()
    with tarfile.open(fileobj=io.BytesIO(arc)) as tf:
        tf.extractall(base_root, filter="data")  # explicit: same result on 3.12-3.14, no DeprecationWarning
    out = tmp_path / "base_cases.json"
    subprocess.run([sys.executable, str(ROOT / "scripts/refactor/work_reporter_capture.py"), "generate", str(out), "--root", str(base_root)],
                   cwd=str(base_root), check=True, capture_output=True,
                   env={**os.environ, "PYTHONPATH": str(base_root), "PYTHONDONTWRITEBYTECODE": "1"})
    assert _dump(json.loads(out.read_text(encoding="utf-8"))["cases"]) == _dump(_cap().compute())


def test_target_tree_discipline_and_no_forbidden_surface():
    base = ROOT / "libs/agents/reporter"
    assert {p.name for p in base.iterdir() if p.is_dir() and p.name != "__pycache__"} == REPORTER_PACKAGES
    for sub in REPORTER_PACKAGES:
        historical = sorted(["__init__.py"] + [f"{n}.py" for n, (s, _b) in REGISTRY.items() if s == sub]
                            + [f"{o}.py" for d_sub, owners in DECOMPOSED.values() if d_sub == sub for o in owners]
                            + [Path(o).name for o in sorted(R4_OWNER_FILES) if Path(o).parent.name == sub])
        # the pinned historical inventory is proven against the real historical Git tree (integration BASE), while the
        # current folder is that inventory plus the exact approved P1.5 DEV-A Reporter pure owners (no prefix wildcard)
        tree = subprocess.check_output(["git", "ls-tree", "--name-only", P15_A_HISTORICAL_TREE, f"libs/agents/reporter/{sub}/"], cwd=ROOT).decode().split()
        assert sorted(Path(x).name for x in tree if x.endswith(".py")) == historical, sub
        assert sorted(p.name for p in (base / sub).glob("*.py")) ==             sorted(historical + [n for d_sub, n in P15_A_PURE_OWNERS if d_sub == sub]), sub
    out = [x for x in subprocess.check_output(["git", "diff", "--name-only", "-z", START, "HEAD"], cwd=ROOT).decode().split(chr(0)) if x]
    out = [x for x in out if x not in P15_A_FACADES | P15_A_Q8_PATHS | P15_A_REVIEW_PATHS | P15_A_FULLCHAIN_PATHS]  # exact closed P1.5 DEV-A edits; helper stays strict
    merged = subprocess.check_output(["git", "rev-list", "--merges", f"{START}..HEAD"], cwd=ROOT).decode().split()
    violations = _scope_violations(out, merged=bool(merged))
    assert not violations, violations


# R-4 facade-body batch (Issue #11 decision, Option 1): CLOSED, independently defined set of the exact extra paths this
# batch changes. It is NOT derived from any ledger; the R-4 ledger is checked against it (it cannot grant paths).
R4_FACADE_FILES = {"libs/reporting/trade_report_markdown_clean.py", "libs/reporting/trade_report_ai.py"}
R4_OWNER_FILES = {"libs/agents/reporter/narrative/markdown_clean_bodies_01.py",
                  "libs/agents/reporter/narrative/report_ai_bodies_01.py"}
R4_SHARED_CONTRACT_FILES = {"tests/test_p152_facade_symbol_ledger.py"}  # authorised facade-contract edit (v1 kept at BASE)
# R-5 batch (T1-pinned read models / deterministic helpers; same facade-injection proof): CLOSED explicit set
R5_FACADE_FILES = {"libs/reporting/trade_report_ai_deterministic.py", "libs/reporting/trade_report_ai_compact_input.py",
                   "libs/reporting/trade_read_model.py", "libs/reporting/trade_memory_surface.py",
                   "libs/reporting/trade_memory_application_surface.py"}
R5_OWNER_FILES = {"libs/agents/reporter/read_models/report_deterministic_bodies_01.py",
                  "libs/agents/reporter/read_models/compact_input_bodies_01.py",
                  "libs/agents/reporter/read_models/read_model_bodies_01.py",
                  "libs/agents/reporter/read_models/read_model_bodies_02.py",
                  "libs/agents/reporter/read_models/memory_surface_bodies_01.py",
                  "libs/agents/reporter/read_models/memory_application_bodies_01.py"}
# R-6 batch (pure bodies inside I/O-mixed Reporter modules; effect/identity-dependent bodies stay): CLOSED explicit set
R6_FACADE_FILES = {"libs/reporting/trade_explain.py", "libs/reporting/trade_bundle_assembly.py", "libs/reporting/trade_bundle_state.py",
                   "libs/reporting/trade_lifecycle_builder.py", "libs/reporting/single_trade_report.py",
                   "libs/reporting/trade_story_pipeline_provenance.py"}
R6_OWNER_FILES = {"libs/agents/reporter/narrative/trade_explain_bodies_01.py",
                  "libs/agents/reporter/read_models/bundle_assembly_bodies_01.py",
                  "libs/agents/reporter/read_models/bundle_state_bodies_01.py",
                  "libs/agents/reporter/read_models/lifecycle_builder_bodies_01.py",
                  "libs/agents/reporter/narrative/single_trade_report_bodies_01.py",
                  "libs/agents/reporter/narrative/story_provenance_bodies_01.py"}
# R-7 batch (Reporter read-model / analysis / markdown modules; same proof): CLOSED explicit set
R7_FACADE_FILES = {"libs/reporting/agent_pipeline_trace.py",
                   "libs/reporting/entry_blocker_read_model.py",
                   "libs/reporting/post_exit_shadow_recap.py",
                   "libs/reporting/reporter_analysis.py",
                   "libs/reporting/strategy_read_model.py",
                   "libs/reporting/symbol_trade_report.py",
                   "libs/reporting/trade_report_markdown_strategy_memory.py"}
R7_OWNER_FILES = {"libs/agents/reporter/narrative/pipeline_trace_bodies_01.py",
                   "libs/agents/reporter/narrative/post_exit_recap_bodies_01.py",
                   "libs/agents/reporter/narrative/post_exit_recap_bodies_02.py",
                   "libs/agents/reporter/narrative/strategy_memory_md_bodies_01.py",
                   "libs/agents/reporter/narrative/strategy_memory_md_bodies_02.py",
                   "libs/agents/reporter/narrative/symbol_trade_report_bodies_01.py",
                   "libs/agents/reporter/narrative/symbol_trade_report_bodies_02.py",
                   "libs/agents/reporter/read_models/entry_blocker_bodies_01.py",
                   "libs/agents/reporter/read_models/entry_blocker_bodies_02.py",
                   "libs/agents/reporter/read_models/reporter_analysis_bodies_01.py",
                   "libs/agents/reporter/read_models/reporter_analysis_bodies_02.py",
                   "libs/agents/reporter/read_models/reporter_analysis_bodies_03.py",
                   "libs/agents/reporter/read_models/reporter_analysis_bodies_04.py",
                   "libs/agents/reporter/read_models/strategy_read_model_bodies_01.py",
                   "libs/agents/reporter/read_models/strategy_read_model_bodies_02.py"}
# R-8 batch (triaged token false positives: no direct I/O/authority call; facades already in R-5..R-7 sets): CLOSED explicit set
R8_OWNER_FILES = {"libs/agents/reporter/narrative/agent_pipeline_trace_r8_bodies_01.py",
                  "libs/agents/reporter/narrative/post_exit_shadow_recap_r8_bodies_01.py",
                  "libs/agents/reporter/narrative/single_trade_report_r8_bodies_01.py",
                  "libs/agents/reporter/narrative/symbol_trade_report_r8_bodies_01.py",
                  "libs/agents/reporter/narrative/trade_explain_r8_bodies_01.py",
                  "libs/agents/reporter/read_models/reporter_analysis_r8_bodies_01.py",
                  "libs/agents/reporter/read_models/trade_bundle_assembly_r8_bodies_01.py",
                  "libs/agents/reporter/read_models/trade_lifecycle_builder_r8_bodies_01.py",
                  "libs/agents/reporter/read_models/trade_read_model_r8_bodies_01.py"}
# R-9 batch (pure bodies of retained Reporter modules; truth/LLM/effect bodies stay): CLOSED explicit set
R9_FACADE_FILES = {"libs/reporting/intraday_trade_reports.py",
                   "libs/reporting/symbol_read_model.py",
                   "libs/reporting/trade_report_common.py"}
R9_OWNER_FILES = {"libs/agents/reporter/narrative/trade_report_common_r9_bodies_01.py",
                   "libs/agents/reporter/read_models/intraday_trade_reports_r9_bodies_01.py",
                   "libs/agents/reporter/read_models/symbol_read_model_r9_bodies_01.py"}
R4_FACADE_FILES = R4_FACADE_FILES | R5_FACADE_FILES | R6_FACADE_FILES | R7_FACADE_FILES | R9_FACADE_FILES
R4_OWNER_FILES = R4_OWNER_FILES | R5_OWNER_FILES | R6_OWNER_FILES | R7_OWNER_FILES | R8_OWNER_FILES | R9_OWNER_FILES


def _scope_violations(paths, *, merged=False):
    allowed_exact = {f"libs/reporting/{n}.py" for n in [*REGISTRY, *DECOMPOSED]} | R4_FACADE_FILES | R4_SHARED_CONTRACT_FILES
    allowed_prefix = ("libs/agents/reporter/", "tests/test_work_reporter_", "tests/fixtures/work_reporter/",
                      "scripts/refactor/work_reporter_", "docs/refactor/work_projects/evidence/reporter/")
    if merged:  # integration checkout: other lanes/Work also change files; still police every Reporter-surface path
        paths = [p for p in paths if p.startswith(("libs/reporting/", "libs/agents/reporter/"))]
    return [p for p in paths if not (p in allowed_exact or p.startswith(allowed_prefix))]


def test_scope_checker_still_rejects_unexpected_and_forbidden_paths():
    bad = ["libs/reporting/trade_report_post_exit_shadow_x.py", "libs/reporting/operator_visibility.py", "libs/reporting/trade_story_pipeline.py", "tests/test_p152_r3_moved_bodies.py",
           "tests/p15_agent_tree_allowlist.py", "graphs/nodes/reporter_node.py", "libs/execution/x.py", ".github/workflows/a.yml",
           "docs/refactor/work_projects/ACTIVATION.md", "docs/refactor/work_projects/evidence/monitor/x.md",
           "libs/runtime/monitor/cycle_event_payloads.py", "docs/refactor/p1_5_2_facade_symbol_ledger_2026-10-09.json"]
    assert _scope_violations(bad) == bad
    assert _scope_violations(["libs/reporting/operator_visibility.py"], merged=True) == ["libs/reporting/operator_visibility.py"]
    # the Q8 grant is exact: the read-only trust policy and any sibling path are still rejected by the helper itself
    assert _scope_violations(["libs/reporting/q8_evaluation_contract.py", "libs/reporting/evaluation/q8_extra_p15.py"]) == [
        "libs/reporting/q8_evaluation_contract.py", "libs/reporting/evaluation/q8_extra_p15.py"]
    assert len(P15_A_Q8_PATHS) == 12 and all(p.startswith("libs/reporting/") for p in P15_A_Q8_PATHS)
    assert len(P15_A_FULLCHAIN_PATHS) == 6 and all(p.startswith("libs/reporting/evaluation/full_chain_") for p in P15_A_FULLCHAIN_PATHS)
    assert len(P15_A_REVIEW_PATHS) == 6 and all(p.startswith("libs/reporting/reporter_ai_review") for p in P15_A_REVIEW_PATHS)
    assert _scope_violations(sorted(R4_FACADE_FILES | R4_OWNER_FILES | R4_SHARED_CONTRACT_FILES)) == []


def test_r4_ledger_cannot_grant_paths_outside_the_closed_r4_set():
    doc = json.loads((ROOT / "docs/refactor/work_projects/evidence/reporter/r4_facade_ledger.json").read_text(encoding="utf-8"))
    assert doc["schema"] == "agentra.work.reporter.r4_ledger.v1" and doc["base"] == BASE
    assert doc["expected_moves"] == len(doc["moves"]) == 313  # R-4 14 + R-5 56 + R-6 66 + R-7 128 + R-8 22 + R-9 27
    assert {m["path"] for m in doc["moves"]} == R4_FACADE_FILES
    assert {m["r4_owner"] for m in doc["moves"]} == R4_OWNER_FILES
    pairs = {(m["path"], m["r4_owner"]) for m in doc["moves"]}
    assert pairs == {("libs/reporting/trade_report_markdown_clean.py", "libs/agents/reporter/narrative/markdown_clean_bodies_01.py"),
                     ("libs/reporting/trade_report_ai.py", "libs/agents/reporter/narrative/report_ai_bodies_01.py"),
                     ("libs/reporting/trade_report_ai_deterministic.py", "libs/agents/reporter/read_models/report_deterministic_bodies_01.py"),
                     ("libs/reporting/trade_report_ai_compact_input.py", "libs/agents/reporter/read_models/compact_input_bodies_01.py"),
                     ("libs/reporting/trade_read_model.py", "libs/agents/reporter/read_models/read_model_bodies_01.py"),
                     ("libs/reporting/trade_read_model.py", "libs/agents/reporter/read_models/read_model_bodies_02.py"),
                     ("libs/reporting/trade_memory_surface.py", "libs/agents/reporter/read_models/memory_surface_bodies_01.py"),
                     ("libs/reporting/trade_memory_application_surface.py", "libs/agents/reporter/read_models/memory_application_bodies_01.py"),
                     ("libs/reporting/trade_explain.py", "libs/agents/reporter/narrative/trade_explain_bodies_01.py"),
                     ("libs/reporting/trade_bundle_assembly.py", "libs/agents/reporter/read_models/bundle_assembly_bodies_01.py"),
                     ("libs/reporting/trade_bundle_state.py", "libs/agents/reporter/read_models/bundle_state_bodies_01.py"),
                     ("libs/reporting/trade_lifecycle_builder.py", "libs/agents/reporter/read_models/lifecycle_builder_bodies_01.py"),
                     ("libs/reporting/single_trade_report.py", "libs/agents/reporter/narrative/single_trade_report_bodies_01.py"),
                     ("libs/reporting/trade_story_pipeline_provenance.py", "libs/agents/reporter/narrative/story_provenance_bodies_01.py"),
                     ("libs/reporting/agent_pipeline_trace.py", "libs/agents/reporter/narrative/pipeline_trace_bodies_01.py"),
                     ("libs/reporting/entry_blocker_read_model.py", "libs/agents/reporter/read_models/entry_blocker_bodies_01.py"),
                     ("libs/reporting/entry_blocker_read_model.py", "libs/agents/reporter/read_models/entry_blocker_bodies_02.py"),
                     ("libs/reporting/post_exit_shadow_recap.py", "libs/agents/reporter/narrative/post_exit_recap_bodies_01.py"),
                     ("libs/reporting/post_exit_shadow_recap.py", "libs/agents/reporter/narrative/post_exit_recap_bodies_02.py"),
                     ("libs/reporting/reporter_analysis.py", "libs/agents/reporter/read_models/reporter_analysis_bodies_01.py"),
                     ("libs/reporting/reporter_analysis.py", "libs/agents/reporter/read_models/reporter_analysis_bodies_02.py"),
                     ("libs/reporting/reporter_analysis.py", "libs/agents/reporter/read_models/reporter_analysis_bodies_03.py"),
                     ("libs/reporting/reporter_analysis.py", "libs/agents/reporter/read_models/reporter_analysis_bodies_04.py"),
                     ("libs/reporting/strategy_read_model.py", "libs/agents/reporter/read_models/strategy_read_model_bodies_01.py"),
                     ("libs/reporting/strategy_read_model.py", "libs/agents/reporter/read_models/strategy_read_model_bodies_02.py"),
                     ("libs/reporting/symbol_trade_report.py", "libs/agents/reporter/narrative/symbol_trade_report_bodies_01.py"),
                     ("libs/reporting/symbol_trade_report.py", "libs/agents/reporter/narrative/symbol_trade_report_bodies_02.py"),
                     ("libs/reporting/trade_report_markdown_strategy_memory.py", "libs/agents/reporter/narrative/strategy_memory_md_bodies_01.py"),
                     ("libs/reporting/trade_report_markdown_strategy_memory.py", "libs/agents/reporter/narrative/strategy_memory_md_bodies_02.py"),
                     ("libs/reporting/agent_pipeline_trace.py", "libs/agents/reporter/narrative/agent_pipeline_trace_r8_bodies_01.py"),
                     ("libs/reporting/post_exit_shadow_recap.py", "libs/agents/reporter/narrative/post_exit_shadow_recap_r8_bodies_01.py"),
                     ("libs/reporting/reporter_analysis.py", "libs/agents/reporter/read_models/reporter_analysis_r8_bodies_01.py"),
                     ("libs/reporting/single_trade_report.py", "libs/agents/reporter/narrative/single_trade_report_r8_bodies_01.py"),
                     ("libs/reporting/symbol_trade_report.py", "libs/agents/reporter/narrative/symbol_trade_report_r8_bodies_01.py"),
                     ("libs/reporting/trade_bundle_assembly.py", "libs/agents/reporter/read_models/trade_bundle_assembly_r8_bodies_01.py"),
                     ("libs/reporting/trade_explain.py", "libs/agents/reporter/narrative/trade_explain_r8_bodies_01.py"),
                     ("libs/reporting/trade_lifecycle_builder.py", "libs/agents/reporter/read_models/trade_lifecycle_builder_r8_bodies_01.py"),
                     ("libs/reporting/trade_read_model.py", "libs/agents/reporter/read_models/trade_read_model_r8_bodies_01.py"),
                     ("libs/reporting/intraday_trade_reports.py", "libs/agents/reporter/read_models/intraday_trade_reports_r9_bodies_01.py"),
                     ("libs/reporting/symbol_read_model.py", "libs/agents/reporter/read_models/symbol_read_model_r9_bodies_01.py"),
                     ("libs/reporting/trade_report_common.py", "libs/agents/reporter/narrative/trade_report_common_r9_bodies_01.py")}


@pytest.mark.parametrize("facade", sorted(DECOMPOSED))
def test_decomposed_owners_keep_every_base_definition_ast_identical_and_the_facade_reexports_the_same_objects(facade):
    import ast
    base_src = subprocess.check_output(["git", "show", f"{BASE}:libs/reporting/{facade}.py"], cwd=ROOT).decode("utf-8-sig")
    keep = (ast.FunctionDef, ast.AnnAssign, ast.Assign)
    nm = lambda n: n.name if isinstance(n, ast.FunctionDef) else (n.targets[0].id if isinstance(n, ast.Assign) else n.target.id)  # noqa: E731
    base = {nm(n): ast.dump(n) for n in ast.parse(base_src).body if isinstance(n, keep)}
    owners, found = {}, {}
    d_sub, d_owners = DECOMPOSED[facade]
    for o in d_owners:
        path = ROOT / "libs/agents/reporter" / d_sub / f"{o}.py"
        text = path.read_text(encoding="utf-8")
        assert len(text.splitlines()) <= 350
        mod = importlib.import_module(f"libs.agents.reporter.{d_sub}.{o}")
        for n in ast.parse(text).body:
            if isinstance(n, keep):
                assert nm(n) not in found, nm(n)  # exactly one body
                found[nm(n)] = ast.dump(n)
                owners[nm(n)] = mod
    assert found == base  # same names, same AST (signatures, defaults, bodies)
    legacy = importlib.import_module(f"libs.reporting.{facade}")
    legacy_tree = ast.parse((ROOT / f"libs/reporting/{facade}.py").read_text(encoding="utf-8"))
    assert not [n for n in legacy_tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Assign, ast.AnnAssign))]
    for name, mod in owners.items():
        assert getattr(legacy, name) is getattr(mod, name), name


@pytest.mark.parametrize("facade", sorted(DECOMPOSED))
def test_decomposed_facade_keeps_every_base_module_attribute_with_the_same_objects(facade):
    """BASE run in a fresh interpreter: every public/private module attribute name of the BASE module must exist on the
    facade; imported helpers must be the very same objects as the ones the canonical owners/legacy code use."""
    import ast
    src = subprocess.check_output(["git", "show", f"{BASE}:libs/reporting/{facade}.py"], cwd=ROOT).decode("utf-8-sig")
    names = set()
    for n in ast.parse(src).body:
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            names |= {a.asname or a.name.split(".")[0] for a in n.names if a.name != "annotations"}
        elif isinstance(n, ast.FunctionDef):
            names.add(n.name)
        elif isinstance(n, ast.AnnAssign):
            names.add(n.target.id)
    mod = importlib.import_module(f"libs.reporting.{facade}")
    missing = sorted(x for x in names if not hasattr(mod, x))
    assert not missing, missing
