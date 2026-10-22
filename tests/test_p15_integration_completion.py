"""Current-stage exact admission; historical shape gates retain their own oracle.

No golden is regenerated. Pins are the independently reviewed source SHAs.
"""
import ast
import copy
import inspect
import json
import subprocess
import sys
import types

import pytest

from scripts.refactor import shared_strategist_contracts as S


@pytest.fixture(scope="module", autouse=True)
def exact_current_stage_is_green_before_mutation_tests():
    S.verify_next_stage()
    S.verify_b_scope()


def test_current_source_restores_only_the_five_approved_definitions():
    assert S.verify_next_stage() == frozenset(S.NEXT_RUNTIME)
    S.verify_next_scope()
    assert S.historical_source(S.NODE) == S.git_source(S.HISTORICAL_STAGE, S.NODE)
    # Historical size/import rules remain on the old stage; no new global cap.
    assert len(S.historical_source(S.UI_SECTIONS).splitlines()) <= 350
    assert len(S.git_source(S.UI_PIN, S.UI_SECTIONS).splitlines()) == 387
    pin = S.B_COMPOSED_BRIEF if S.b_composed_selected() else S.UI_PIN
    assert (S.ROOT / S.UI_SECTIONS).read_text(encoding="utf-8") == S.git_source(pin, S.UI_SECTIONS)


@pytest.mark.parametrize("path,name", [(p, n) for p, names in S.NEXT_MOVED.items() for n in names])
@pytest.mark.parametrize("kind", ["argument", "facade", "default"])
def test_each_new_wrapper_rejects_argument_facade_and_abi_mutations(path, name, kind):
    tree = ast.parse((S.ROOT / path).read_text(encoding="utf-8"))
    fn = S.functions(tree)[name]
    if kind == "argument":
        fn.body[0].value.args[0] = ast.Constant(value=None)
    elif kind == "facade":
        fn.body[0].value.keywords[0].value = ast.Constant(value=None)
    else:
        fn.args.defaults.append(ast.Constant(value=None))
    with pytest.raises(AssertionError, match="new-stage source"):
        S.verify_next_stage({path: ast.unparse(tree)})


@pytest.mark.parametrize("path", sorted(S.NEXT_RUNTIME))
@pytest.mark.parametrize("addition", ["import os", "__import__('os')", "State = {'authority': True}",
                                      "facade.LLMRouter.from_env()", "BROKER_PERMISSION = True"])
def test_no_import_time_effect_dynamic_import_state_llm_or_broker_addition(path, addition):
    source = (S.ROOT / path).read_text(encoding="utf-8")
    with pytest.raises(AssertionError, match="new-stage source"):
        S.verify_next_stage({path: source + "\n" + addition + "\n"})


@pytest.mark.parametrize("path", [S.NODE, S.UI_CORE])
def test_unmoved_function_change_cannot_hide_behind_historical_projection(path):
    tree = ast.parse((S.ROOT / path).read_text(encoding="utf-8"))
    fn = next(n for n in S.functions(tree).values() if n.name not in S.NEXT_MOVED[path])
    fn.body.insert(0, ast.parse("raise RuntimeError('unauthorized')").body[0])
    with pytest.raises(AssertionError):
        S.verify_next_stage({path: ast.unparse(tree)})


@pytest.mark.parametrize("path", ["libs/broker/rogue.py", "libs/supervisor/rogue.py", "libs/executor/rogue.py",
                                  "graphs/nodes/decide_trade.py", "tests/fixtures/p1_5_t4d_commander_ui/golden.json",
                                  "tests/test_uef9_formal_authority.py", "apps/operator_ui/main.py"])
def test_new_stage_has_no_prefix_or_authority_allowlist(path):
    for changed, untracked in (([path], []), ([], [path])):
        with pytest.raises(AssertionError):
            S.verify_next_scope(changed, untracked)


def _original_brief(name, core):
    tree = ast.parse(S.git_source(S.NEXT_BASE, S.UI_CORE))
    node = S.functions(tree)[name]
    ns = {}
    flags = __import__("__future__").annotations.compiler_flag
    exec(compile(ast.Module(body=[node], type_ignores=[]), "<accepted brief BASE>", "exec", flags=flags), ns)
    original = types.FunctionType(ns[name].__code__, vars(core))
    original.__annotations__ = ns[name].__annotations__
    return original


@pytest.mark.parametrize("name", sorted(S.NEXT_MOVED[S.UI_CORE]))
def test_brief_ordered_json_markdown_exceptions_and_readonly_effects(name, tmp_path, monkeypatch):
    import apps.operator_ui.data_access_core as core
    import apps.operator_ui.data_access as compat
    from test_operator_ui import _make_config, _FakeRouter

    monkeypatch.setattr(core.LLMRouter, "from_env", staticmethod(lambda: _FakeRouter()))
    detail = core.load_run_detail(_make_config(tmp_path), "run-1")  # existing synthetic UI fixture, no production data
    original, current = _original_brief(name, core), getattr(core, name)
    assert inspect.signature(original) == inspect.signature(current)
    assert getattr(compat, name) is current

    def forbidden(*args, **kwargs):
        raise AssertionError("pure brief projection attempted LLM/persistence")

    monkeypatch.setattr(core.LLMRouter, "from_env", staticmethod(forbidden))
    monkeypatch.setattr(core, "_save_operator_brief_input_artifact", forbidden)
    monkeypatch.setattr(core, "_save_operator_brief_artifact", forbidden)
    for sample in (detail, {}, {"monitor": None}, {"scanner": {"decision_trace": []}}, None, []):
        before = copy.deepcopy(sample)
        def outcome(fn):
            try:
                value = fn(sample)
                return ("ok", json.dumps(value, ensure_ascii=False).encode("utf-8"), value)
            except Exception as exc:
                return ("exception", type(exc), str(exc))
        expected, actual = outcome(original), outcome(current)
        assert expected == actual
        assert sample == before
        if actual[0] == "ok" and name == "_build_operator_brief_sections":
            assert core._render_operator_brief_markdown({"status": "ok", "sections": expected[2]}).encode() == core._render_operator_brief_markdown({"status": "ok", "sections": actual[2]}).encode()

    # Rebind a helper during canonical extraction, proving lookup after entry.
    canonical = core._build_canonical_trade_brief_input
    def rebind(trade_report):
        monkeypatch.setattr(core, "_safe_int", lambda *args, **kwargs: 73)
        return canonical(trade_report)
    monkeypatch.setattr(core, "_build_canonical_trade_brief_input", rebind)
    assert original(detail) == current(detail)


def test_exact_admission_rejects_mutations_under_optimized_python():
    code = r"""from scripts.refactor import shared_strategist_contracts as s
p = s.UI_CORE
try:
    s.verify_next_stage({p: (s.ROOT / p).read_text(encoding='utf-8') + '\n__import__("os")\n'})
except AssertionError:
    pass
else:
    raise SystemExit('dynamic import accepted')
"""
    subprocess.run([sys.executable, "-O", "-c", code], cwd=S.ROOT, check=True)


@pytest.mark.parametrize("path", [S.NODE, S.UI_CORE, S.UI_INPUT, S.UI_SECTIONS])
def test_historical_view_never_hides_a_modified_current_blob(path, monkeypatch):
    from pathlib import Path
    read = Path.read_text
    def changed(p, *args, **kwargs):
        source = read(p, *args, **kwargs)
        return source + "\n__import__('os')\n" if p == S.ROOT / path else source
    monkeypatch.setattr(Path, "read_text", changed)
    with pytest.raises(AssertionError, match="new-stage source"):
        S.historical_source(path)


# B-only composed admission: historical/current source are separate proof inputs.
@pytest.fixture(scope="module")
def real_pytest_junit(tmp_path_factory):
    """Use actual pytest output, not a fabricated production-output golden."""
    import os
    root = tmp_path_factory.mktemp("junit-producer")
    test = root / "test_report.py"
    test.write_text("def test_offline_metadata():\n    assert True\n", encoding="utf-8")
    report = root / "result.xml"
    flags = [] if __debug__ else ["-O"]
    result = subprocess.run([sys.executable, *flags, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider",
                             str(test), "--junitxml=" + str(report)], cwd=root,
                            env=dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD="1"),
                            capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, (result.returncode, result.stdout, result.stderr)
    return report.read_bytes()


@pytest.mark.parametrize("workflow", ["p15-integration-t4-regression.yml", "p152-r2c-residual-regression.yml"])
def test_ci_junit_names_are_exact_frozen_workflow_destinations(workflow):
    import re
    text = S.git_source(S.B_CI_REPAIR_BASE, ".github/workflows/" + workflow)
    names = set(re.findall(r"--junitxml=(branch_output/gate_[\w]+_junit\.xml)", text))
    assert names == S.B_CI_JUNIT and len(names) == 18


def test_ci_evidence_present_absent_unknown_and_tracked_remain_distinct(tmp_path, monkeypatch, real_pytest_junit):
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=S.ROOT, text=True).strip()
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_WORKFLOW", "P1.5 Integration T4 Linux Windows Regression")
    monkeypatch.setenv("GITHUB_SHA", head)
    evidence = set()
    tracked = set()
    original = subprocess.check_output
    validator = S._b_ci_junit_evidence
    def git_with_ci_output(args, *a, **kw):
        out = original(args, *a, **kw)
        if args == ["git", "ls-files", "--others", "--exclude-standard"]:
            return out + "\n".join(sorted(evidence)) + ("\n" if evidence else "")
        if args == ["git", "diff", "--name-only", S.B_COMPOSED_BASE]:
            return out + "\n".join(sorted(tracked)) + ("\n" if tracked else "")
        return out
    monkeypatch.setattr(subprocess, "check_output", git_with_ci_output)
    monkeypatch.setattr(S, "_b_ci_junit_evidence", lambda path, commit: validator(path, commit, root=tmp_path))
    expected = S.verify_b_composed()  # real current tree, no prior reports
    for name in S.B_CI_JUNIT:
        p = tmp_path / name
        p.parent.mkdir(exist_ok=True)
        p.write_bytes(real_pytest_junit)
    evidence.update(S.B_CI_JUNIT)
    assert S.verify_b_composed() == expected  # genuine prior pytest reports, all 18 exact names
    for unknown in ("branch_output/gate_unknown_junit.xml", "branch_output/gate_t4d_junit.xml.py",
                    "libs/broker/rogue.py", "branch_output/GATE_t4d_junit.xml", "branch_output/t35_diag_t35_base.txt",
                    "branch_output/t35_diag_agentra.txt"):
        evidence.add(unknown)
        with pytest.raises(AssertionError, match="unexpected/missing inventory"):
            S.verify_b_composed()
        evidence.remove(unknown)
    name = sorted(evidence)[0]
    evidence.remove(name)
    tracked.add(name)
    with pytest.raises(AssertionError, match="unexpected/missing inventory"):
        S.verify_b_composed()  # tracked/staged report never receives a source-path exemption


@pytest.mark.parametrize("payload", [b"import os\n", b"<source/>", b"<testsuites><evil/></testsuites>",
                                      b'<!DOCTYPE x [<!ENTITY y "z">]><testsuites/>',
                                      "<!DOCTYPE testsuites [<!ENTITY x 'fixture'>]><testsuites><testsuite name='&x;'/></testsuites>".encode("utf-16"),
                                      "<!DOCTYPE testsuites [<!ENTITY x 'fixture'>]><testsuites><testsuite name='&x;'/></testsuites>".encode("utf-16-be")])
def test_named_ci_report_with_non_junit_content_fails(tmp_path, monkeypatch, real_pytest_junit, payload):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_WORKFLOW", "P1.5 Integration T4 Linux Windows Regression")
    monkeypatch.setenv("GITHUB_SHA", "fixture-head")
    path = sorted(S.B_CI_JUNIT)[0]
    p = tmp_path / path
    p.parent.mkdir()
    p.write_bytes(real_pytest_junit)
    assert S._b_ci_junit_evidence(path, "fixture-head", root=tmp_path)
    p.write_bytes(payload)
    with pytest.raises(AssertionError, match="invalid CI JUnit evidence"):
        S._b_ci_junit_evidence(path, "fixture-head", root=tmp_path)


def test_ci_report_needs_actual_workflow_checkout_and_file(tmp_path, monkeypatch, real_pytest_junit):
    path = sorted(S.B_CI_JUNIT)[0]
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_WORKFLOW", "P1.5 Integration T4 Linux Windows Regression")
    monkeypatch.setenv("GITHUB_SHA", "fixture-head")
    with pytest.raises(AssertionError, match="evidence path"):
        S._b_ci_junit_evidence(path, "fixture-head", root=tmp_path)
    p = tmp_path / path
    p.parent.mkdir()
    p.write_bytes(real_pytest_junit)
    assert S._b_ci_junit_evidence(path, "fixture-head", root=tmp_path)
    for key, value in (("GITHUB_ACTIONS", "false"), ("GITHUB_WORKFLOW", "unapproved workflow"),
                       ("GITHUB_SHA", "wrong-checkout")):
        with monkeypatch.context() as m:
            m.setenv(key, value)
            assert not S._b_ci_junit_evidence(path, "fixture-head", root=tmp_path)


def test_b_composed_exact_input_and_old_function_bodies_remain_intact():
    assert len(S.B_COMPOSED_PATHS) == 23
    assert len(S.verify_b_composed()) == 29
    old = ast.parse(S.git_source(S.B_COMPOSED_COMMANDER, "scripts/refactor/shared_strategist_contracts.py"))
    new = ast.parse((S.ROOT / "scripts/refactor/shared_strategist_contracts.py").read_text(encoding="utf-8"))
    for fn in (n for n in old.body if isinstance(n, ast.FunctionDef)):
        # The first definition is the untouched historical predicate; later
        # wrappers validate current input before projecting its historical view.
        retained = next(n for n in new.body if isinstance(n, ast.FunctionDef) and n.name == fn.name)
        assert ast.dump(retained) == ast.dump(fn), fn.name
    assert S.verify_b_scope() == S.COMMANDER_V1_PATHS | S.COMMANDER_V1_CONTRACT_DELTA


@pytest.mark.parametrize("path", sorted(S.B_COMPOSED_PATHS - S.B_COMPOSED_CHECKS - S.COMMANDER_V1_NOTES))
def test_b_composed_source_mutants_reject_from_green_current_tree(path):
    import shared_role_contracts as roles
    assert len(S.verify_b_composed()) == 29
    assert roles.verify_runtime()["monitor_bodies"] == 20
    for gate in (S.verify_b_composed, roles.verify_runtime):
        with pytest.raises(AssertionError) as rejected:
            gate({path: (S.ROOT / path).read_text(encoding="utf-8") + "\n__import__('socket')\n"})
        assert path in str(rejected.value)
        with pytest.raises(AssertionError) as missing:
            gate({path: None})
        assert path in str(missing.value)


@pytest.mark.parametrize("path", [
    "libs/broker/unapproved.py", "libs/executor/unapproved.py", "libs/supervisor/unapproved.py",
    "libs/agents/commander/unapproved.py", "graphs/nodes/decide_trade.py",
    "apps/operator_ui/main.py", "tests/test_uef9_formal_authority.py",
    "tests/fixtures/uef9_synthetic/reports_inputs.json", ".github/workflows/unapproved.yml",
    "libs/reporting/q8_historical_review.py",
])
def test_b_composed_has_no_authority_ci_fixture_or_a_lane_prefix_grant(path):
    import shared_role_contracts as roles
    assert roles.verify_runtime()["moves"] == 313
    for gate in (S.verify_b_composed, roles.verify_runtime):
        with pytest.raises(AssertionError) as rejected:
            gate({path: "BROKER_EXECUTION_ALLOWED = True\n"})
        assert path in str(rejected.value)


@pytest.mark.parametrize("path", sorted(S.B_COMPOSED_CHECKS))
def test_b_composed_checker_mutation_rejects_without_new_hash_chain(path):
    assert S.verify_b_composed()
    with pytest.raises(AssertionError, match="checker/test drift"):
        S.verify_b_composed({path: (S.ROOT / path).read_text(encoding="utf-8") + "\n# drift\n"})


def test_b_composed_omission_and_note_history_mutation_remain_red():
    expected = S.verify_b_composed()
    for path in expected:
        with pytest.raises(AssertionError, match="unexpected/missing inventory"):
            S.verify_b_composed(inventory=expected - {path})
    path = "docs/trading_agent_patch_notes_detailed_update/patch_notes.json"
    note = json.loads((S.ROOT / path).read_text(encoding="utf-8"))
    note["entries"][0]["title"] += " rewritten"
    with pytest.raises(AssertionError, match="historical patchnotes"):
        S.verify_b_composed({path: json.dumps(note)})


@pytest.mark.parametrize("sha", [S.B_COMPOSED_BASE, S.B_COMPOSED_COMMANDER, S.B_COMPOSED_BRIEF])
def test_actual_original_predicates_on_pinned_archive_not_current_worktree(sha, tmp_path):
    """Ordinary test fixture, not a clone, branch or registered Git worktree.

    The original source archive uses the repository's read-only object store and
    a private index. No real Git index/ref/config or production source is changed.
    Original checker files/functions execute unmodified on their real old files.
    """
    import io
    import os
    import tarfile
    root = tmp_path / "source"
    root.mkdir()
    archive = subprocess.check_output(["git", "archive", "--format=tar", sha], cwd=S.ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        stream.extractall(root, filter="data")
    env = dict(os.environ, GIT_DIR=subprocess.check_output(
        ["git", "rev-parse", "--absolute-git-dir"], cwd=S.ROOT, text=True, encoding="utf-8").strip(),
        GIT_WORK_TREE=str(root), GIT_INDEX_FILE=str(tmp_path / "private-index"),
        PYTHONPATH=str(root), PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
        DRY_RUN="1", TRADING_MODE="mock", EXECUTION_ENABLED="false",
        TEMP=str(tmp_path), TMP=str(tmp_path), TMPDIR=str(tmp_path))
    # Git for Windows probes revision:path arguments as filenames. Deep test
    # fixture roots otherwise fail MAX_PATH before reading a valid Git object.
    # Invocation-local filesystem support only; no repository/global config edit.
    config_count = int(env.get("GIT_CONFIG_COUNT", "0"))
    env.update({"GIT_CONFIG_COUNT": str(config_count + 1),
                f"GIT_CONFIG_KEY_{config_count}": "core.longpaths",
                f"GIT_CONFIG_VALUE_{config_count}": "true"})
    subprocess.run(["git", "read-tree", sha], cwd=root, env=env, check=True)
    flags = [] if __debug__ else ["-O"]
    if sha == S.B_COMPOSED_BRIEF:
        # This test file intentionally pins its developer-stage gate bytes. It
        # remains unchanged and runs in the exact stage it was written to prove.
        command = [sys.executable, *flags, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider",
                   "tests/test_p15_b_operator_brief_boundaries.py", "--basetemp=" + str(tmp_path / "pytest")]
    else:
        command = [sys.executable, *flags, "-B", "-c", (
            "import sys;sys.path.insert(0,'scripts/refactor');"
            "from scripts.refactor import shared_strategist_contracts as s;"
            "import shared_role_contracts as r;"
            "s.verify_next_stage();s.verify_b_scope();"
            "x=r.verify_runtime();"
            "print('ORIGINAL_PINNED_GATE_PASS',x);"
            "assert x['moves']==313 and x['monitor_bodies']==20")]
    result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, (sha, result.returncode, result.stdout, result.stderr)
    if sha == S.B_COMPOSED_BASE:
        # The original pre-amendment current-head T3 file also executes unchanged
        # on its genuine old source tree. Later B current-head resolution does
        # not rewrite the old ledger, ABI, import oracle or historical test.
        historical = subprocess.run(
            [sys.executable, *flags, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider",
             "tests/test_p159_current_owner_contract_gates.py"],
            cwd=root, env=env, capture_output=True, text=True, encoding="utf-8")
        assert historical.returncode == 0, (sha, historical.returncode, historical.stdout, historical.stderr)


@pytest.mark.parametrize("path", sorted(S.B_CI_DIAGNOSTIC_WORKFLOWS))
def test_diagnostic_workflow_exact_frozen_substitution_and_hostile_changes(path):
    original = S.git_source(S.B_CI_REPAIR_BASE, path)
    current = (S.ROOT / path).read_text(encoding="utf-8")
    assert current == S._b_ci_diagnostic_workflow(path)
    assert current.count('--max-records 3 --variants 2') == original.count('--max-records 3 --variants 2') == 1
    assert current.count('continue-on-error: true') == original.count('continue-on-error: true')
    assert '"$GITHUB_WORKSPACE/branch_output/t35_diag_' not in current
    assert S.verify_b_composed()
    for old, new in (("--max-records 3", "--max-records 4"),
                     ("--variants 2", "--variants 3"),
                     ('"$RUNNER_TEMP/agentra-t35-diag/t35_diag_', '"$GITHUB_WORKSPACE/branch_output/t35_diag_'),
                     ("continue-on-error: true", "continue-on-error: false"),
                     ("[:3500]", "[:35000]"),
                     ("54bebe5ece0ac34c4f45df55c44889c9ce323e95", "0" * 40)):
        assert old in current
        with pytest.raises(AssertionError, match="workflow differs beyond approved paths"):
            S.verify_b_composed({path: current.replace(old, new)})
    with pytest.raises(AssertionError, match="missing source: " + path):
        S.verify_b_composed({path: None})
    with pytest.raises(AssertionError, match="workflow differs beyond approved paths"):
        S.verify_b_composed({path: current + "\n# unapproved workflow change\n"})


@pytest.mark.parametrize("path", sorted(S.B_CI_DIAGNOSTIC_WORKFLOWS))
@pytest.mark.parametrize("diagnostic_exit", [0, 7])
def test_actual_diagnostic_loop_and_notice_keep_bytes_outside_checkout(path, diagnostic_exit, tmp_path):
    """Run real loop/consumer; substitute only BASE input directory in fixture.

    The hosted git worktree creation is checked by the full-text oracle, never
    executed locally. Diagnostic data here are synthetic and contain no reports.
    """
    import os
    import shutil
    import textwrap
    bash = shutil.which("bash")
    if sys.platform == "win32":
        from pathlib import Path
        bash = str(Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe")
        assert Path(bash).is_file(), "Git Bash required for producer execution"
    assert bash, "Bash required for producer execution"
    workspace = tmp_path / "agentra"
    base = tmp_path / "t35_base"
    runner = tmp_path / "runner-temp"
    for folder in (workspace, base, runner):
        folder.mkdir()
    script = workspace / "scripts/refactor/p161_agent_output_diagnose.py"
    script.parent.mkdir(parents=True)
    script.write_text(
        "import pathlib, sys\n"
        "assert sys.argv[2:] == ['--max-records', '3', '--variants', '2']\n"
        "print(pathlib.Path(sys.argv[1]).name + ': \uad00\uce21 % \U0001f9ea')\n"
        "print('bounded:' + 'x' * 4000)\n"
        "print('diagnostic stderr', file=sys.stderr)\n"
        f"sys.exit({diagnostic_exit})\n", encoding="utf-8")
    env = dict(os.environ, GITHUB_WORKSPACE=workspace.as_posix(), RUNNER_TEMP=runner.as_posix(),
               PATH=str(__import__('pathlib').Path(sys.executable).parent) + os.pathsep + os.environ['PATH'],
               PYTHONIOENCODING="utf-8", PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
    def fragments(text):
        block = text.split('      - name: T3.5 Linux golden-replay diagnosis', 1)[1]
        block = block.split('        run: |\n', 1)[1].split('\n      - name:', 1)[0]
        block = textwrap.dedent(block)
        mkdir = block.splitlines()[0]
        loop = block[block.index('for t in '):block.index("python - <<'PY'")]
        assert loop.count('for t in /tmp/t35_base "$GITHUB_WORKSPACE"; do') == 1
        loop = loop.replace('for t in /tmp/t35_base ', 'for t in "' + base.as_posix() + '" ', 1)
        consumer = block.split("python - <<'PY'\n", 1)[1].split('\nPY', 1)[0]
        return mkdir + '\n' + loop, consumer
    def consume(code):
        result = subprocess.run([sys.executable, "-B", "-c", code], cwd=workspace, env=env, capture_output=True)
        assert result.returncode == 0, (result.returncode, result.stderr)
        return result.stdout
    new_loop, new_consumer = fragments((S.ROOT / path).read_text(encoding="utf-8"))
    old_loop, old_consumer = fragments(S.git_source(S.B_CI_REPAIR_BASE, path))
    assert consume(new_consumer) == b""  # absent output is still harmless
    for loop in (new_loop, old_loop):
        result = subprocess.run([bash, "-c", loop], cwd=workspace, env=env, capture_output=True)
        assert result.returncode == 0, (result.returncode, result.stdout, result.stderr)
        if loop == new_loop:
            assert not (workspace / "branch_output").exists()
            assert {f.name for f in (runner / "agentra-t35-diag").iterdir()} == {
                "t35_diag_t35_base.txt", "t35_diag_agentra.txt"}
    assert consume(new_consumer) == consume(old_consumer)
    output = consume(new_consumer)
    assert output.count(b"::notice title=t35-diag-") == 2
    assert b"%25" in output and b"%0A" in output and "\uad00\uce21".encode() in output
    for name in ("t35_diag_agentra.txt", "t35_diag_t35_base.txt"):
        (runner / "agentra-t35-diag" / name).unlink()
        (workspace / "branch_output" / name).unlink()
        assert consume(new_consumer) == consume(old_consumer)
    assert consume(new_consumer) == b""
