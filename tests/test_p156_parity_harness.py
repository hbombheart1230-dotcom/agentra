"""P1.5 Second Pass parity-evidence harness tests (harness only; no production code path is exercised)."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "refactor"))

import p156_parity_differential as P  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def _repository_root_must_stay_clean():
    """Clone-root write containment for this whole module: no test may create (or leave) anything at the top level
    of the repository checkout - this is exactly what silently happened with the %SystemDrive% tree (T3-0.2)."""
    def top():
        return {p.name for p in ROOT.iterdir() if p.name not in (".git", "__pycache__", ".pytest_cache", "branch_output")}
    before = top()
    yield
    created = sorted(top() - before)
    assert not created, f"harness tests created entries in the repository root: {created}"


def _rec(name, ah, rh, post, payload):
    return [name, ah, rh, post, json.dumps(payload)]


def _norm_dict(**kv):
    return {"d": sorted([[repr(k), v] for k, v in kv.items()], key=lambda x: x[0])}


def _runs(b1, b2, f1, f2, test="tests/t.py::t"):
    mk = lambda rec: {"outcomes": {test: "passed"}, "calls": {test: [rec]}}
    return {"b1": mk(b1), "b2": mk(b2), "f1": mk(f1), "f2": mk(f2)}


def _call(payload, tag):
    return _rec("scanner_node.scanner_node", "a", "r-" + tag, "p-" + tag, payload)


def test_identical_records_are_byte_identical():
    r = _call(_norm_dict(rank=1), "x")
    summary, details = P.compare(_runs(r, r, r, r))
    assert summary["BYTE_IDENTICAL"] == 1 and not details


def test_ranking_field_difference_is_never_tolerated():
    b, f = _call(_norm_dict(selected="AAA", rank_score=0.99), "b"), _call(_norm_dict(selected="AAA", rank_score=0.98), "f")
    summary, details = P.compare(_runs(b, b, f, f))  # both sides repeatable -> real mismatch
    assert summary["REAL_MISMATCH"] == 1 and summary["JUSTIFIED_TOLERANCE"] == 0
    # unstable repeats must not turn an unjustified difference into PASS either
    f2 = _call(_norm_dict(selected="AAA", rank_score=0.97), "f2")
    summary, _ = P.compare(_runs(b, b, f, f2))
    assert summary["UNRESOLVED"] == 1 and summary["BYTE_IDENTICAL"] == 0


def test_only_allowlisted_identifier_fields_are_justified():
    b = _call(_norm_dict(packet_id="memory_aaaaaaaaaaaaaaaaaaaa"), "b")
    f = _call(_norm_dict(packet_id="memory_bbbbbbbbbbbbbbbbbbbb"), "f")
    summary, details = P.compare(_runs(b, b, f, f))
    assert summary["JUSTIFIED_TOLERANCE"] == 1 and details[0]["rules"] == ["R-MEMORY-PACKET-ID"]
    # an id-shaped value under a decision field is not tolerated
    b = _call(_norm_dict(side="aaaaaaaaaaaaaaaaaaaa"), "b")
    f = _call(_norm_dict(side="bbbbbbbbbbbbbbbbbbbb"), "f")
    summary, _ = P.compare(_runs(b, b, f, f))
    assert summary["JUSTIFIED_TOLERANCE"] == 0 and summary["REAL_MISMATCH"] == 1


def test_call_count_difference_is_a_real_mismatch():
    r = _call(_norm_dict(a=1), "x")
    runs = _runs(r, r, r, r)
    runs["f1"]["calls"]["tests/t.py::t"] = []
    summary, _ = P.compare(runs)
    assert summary["REAL_MISMATCH"] == 1


def test_orchestrator_refuses_unsafe_paths(tmp_path):
    names = tmp_path / "n.json"
    names.write_text("{}", encoding="utf-8")
    tests = tmp_path / "t.txt"
    tests.write_text("tests/x.py\n", encoding="utf-8")
    base = ["--repo", str(ROOT), "--baseline-sha", "0" * 40, "--feature-sha", "0" * 40,
            "--names", str(names), "--tests", str(tests)]
    with pytest.raises(SystemExit):  # work-root inside the audited repository
        P.main(base + ["--work-root", str(ROOT / "wk"), "--out-dir", str(tmp_path / "o1")])
    with pytest.raises(SystemExit):  # work-root inside the protected live root
        P.main(base + ["--work-root", "C:\\Agentra\\wk", "--out-dir", str(tmp_path / "o2")])
    existing = tmp_path / "exists"
    existing.mkdir()
    with pytest.raises(FileExistsError):
        P.main(base + ["--work-root", str(tmp_path / "w"), "--out-dir", str(existing)])


def test_session_env_isolates_paths_per_run(tmp_path):
    seen = {k: set() for k in ("TEMP", "R3_ROOT", "R3_LOG")}
    for tag in ("b1", "b2", "f1", "f2"):
        sdir = tmp_path / f"s_{tag}"
        env = P.session_env(sdir / "tree", sdir, tmp_path / "_h", tmp_path / "names.json", sdir / "calls.json", "det", True)
        assert env["TEMP"] == env["TMP"]
        for key in seen:
            assert env[key] not in seen[key], (tag, key)
            seen[key].add(env[key])
        assert env["TEMP"].startswith(str(sdir)) and env["R3_LOG"].startswith(str(sdir))
        assert env["PYTHONHASHSEED"] == "0" and env["P156_DETERMINISM"] == "1" and "OPENAI_API_KEY" not in env
        assert not any(k.upper().startswith(("KIWOOM", "ANTHROPIC", "OPENAI", "AWS")) for k in env)


def _run_plugin(code, cwd):
    """Run a snippet in a child interpreter with a scrubbed environment. The child ALWAYS gets a resolved SYSTEMDRIVE
    and an explicit disposable cwd: a Microsoft Store CPython started without SYSTEMDRIVE writes a literal
    `%SystemDrive%\\ProgramData\\...` tree into its cwd, and an inherited cwd is the repository root (T3-0.2 root cause
    of the clone-root debris created by this very helper)."""
    env = {"SYSTEMROOT": os.environ.get("SYSTEMROOT", ""), "SYSTEMDRIVE": P._system_drive(),
           "PATH": os.environ.get("PATH", ""),
           "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1", "P156_DETERMINISM": "1",
           "PYTHONPATH": str(ROOT / "scripts" / "refactor")}
    out = subprocess.run([sys.executable, "-c", "import p156_determinism_plugin as p\n" + code], env=env,
                         cwd=str(cwd), capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr[-500:]
    return out.stdout.strip()


def test_determinism_plugin_clock_uuid_and_network_are_repeatable(tmp_path):
    code = ("import time, uuid, datetime, socket, random\n"
            "p._reset()\n"
            "a = [time.time(), time.time(), datetime.datetime.now().isoformat(), str(uuid.uuid4()), random.random()]\n"
            "time.sleep(5); a.append(time.time())\n"
            "try:\n    socket.create_connection(('example.com', 80), timeout=1); a.append('CONNECTED')\n"
            "except OSError as e:\n    a.append('blocked')\n"
            "print(repr(a))\n")
    first, second = _run_plugin(code, tmp_path), _run_plugin(code, tmp_path)
    assert first == second and "blocked" in first and "CONNECTED" not in first


def test_layer_packet_ids_and_mtime_derived_hashes_are_conditional():
    j = P._justify
    assert j(["'x'", "'packet_ids'", "'daily'"], "memory_" + "a" * 20, "memory_" + "b" * 20) == "R-MEMORY-PACKET-ID"
    assert j(["'x'", "'daily'"], "memory_" + "a" * 20, "memory_" + "b" * 20) is None  # not under a packet-id container
    assert j(["'x'", "'prompt_hash'"], "a" * 60, "b" * 60) is None
    assert j(["'x'", "'prompt_hash'"], "a" * 60, "b" * 60, True) == "R-MTIME-DERIVED"
    assert j(["'x'", "'quantity'"], "a" * 60, "b" * 60, True) is None


def test_strategy_named_fields_are_never_tolerated_as_ids():
    j = P._justify
    # generic strategy-like id strings (previously accepted because the key "strategy" was on the R-ID list)
    assert j(["'x'", "'strategy'"], "strategy_" + "a" * 12, "strategy_" + "b" * 12) is None
    assert j(["'x'", "'selected_strategy'"], "strategy_" + "a" * 12, "strategy_" + "b" * 12) is None
    assert j(["'x'", "'strategy'"], "memory_" + "a" * 20, "memory_" + "b" * 20) is None  # outside a packet-id container
    assert j(["'x'", "'packet_ids'", "'strategy'"], "strategy_" + "a" * 12, "strategy_" + "b" * 12) is None  # not memory id
    assert j(["'x'", "'packet_ids'", "'strategy'"], "memory_" + "a" * 20, "memory_" + "b" * 20) == "R-MEMORY-PACKET-ID"
    assert j(["'x'", "'packet_ids'", "'strategy'"], "memory_" + "a" * 20, "strategy_" + "b" * 12) is None  # both sides


def test_strategy_id_difference_is_real_mismatch_through_compare():
    b = _call(_norm_dict(strategy="strategy_aaaaaaaaaaaa"), "b")
    f = _call(_norm_dict(strategy="strategy_bbbbbbbbbbbb"), "f")
    summary, _ = P.compare(_runs(b, b, f, f))
    assert summary["REAL_MISMATCH"] == 1 and summary["JUSTIFIED_TOLERANCE"] == 0
    b = _call(_norm_dict(selected_strategy="momentum_1a2b3c4d5e6f"), "b")
    f = _call(_norm_dict(selected_strategy="momentum_9f8e7d6c5b4a"), "f")
    summary, _ = P.compare(_runs(b, b, f, f))
    assert summary["REAL_MISMATCH"] == 1


def test_container_memory_id_through_compare_is_conditional_r_id():
    b = _call({"d": [["'packet_ids'", {"d": [["'strategy'", "memory_" + "a" * 20]]}]]}, "b")
    f = _call({"d": [["'packet_ids'", {"d": [["'strategy'", "memory_" + "b" * 20]]}]]}, "f")
    summary, details = P.compare(_runs(b, b, f, f))
    assert summary["JUSTIFIED_TOLERANCE"] == 1 and details[0]["rules"] == ["R-MEMORY-PACKET-ID"]
    # same strategy-key memory-id shape OUTSIDE the container is a real mismatch
    b = _call(_norm_dict(strategy="memory_" + "a" * 20), "b")
    f = _call(_norm_dict(strategy="memory_" + "b" * 20), "f")
    summary, _ = P.compare(_runs(b, b, f, f))
    assert summary["REAL_MISMATCH"] == 1


def test_snapshot_detects_empty_and_ignored_directories(tmp_path):
    root = tmp_path / "tree"
    (root / ".git").mkdir(parents=True)
    (root / "tracked.txt").write_text("x", encoding="utf-8")
    before = P.snapshot_tree(root)
    (root / "data" / "logs").mkdir(parents=True)  # empty directory: invisible to `git status`
    (root / "__pycache__").mkdir()  # typically git-ignored
    (root / ".git" / "inside-git").write_text("ignored by design", encoding="utf-8")
    after = P.snapshot_tree(root)
    assert sorted(after - before) == ["__pycache__", "data", "data/logs"]
    verdict = P.audit_session(before, after, "6 passed", 0)
    assert verdict["verdict"] == "FAIL" and verdict["new_paths_in_session_root"] == 3
    clean = P.audit_session(before, before, "6 passed", 0)
    assert clean["verdict"] == "PASS"


def test_audit_fails_on_project_write_banner_or_bad_exit_code():
    base = {"tracked.txt"}
    banner = "x\nPRODUCTION PATH WRITE DETECTED DURING TEST SESSION\n6 passed"
    assert P.audit_session(base, base, banner, 0)["verdict"] == "FAIL"  # banner alone fails, even with exit 0
    assert P.audit_session(base, base, "6 passed", 1)["verdict"] == "FAIL"  # exit 1 not expected
    assert P.audit_session(base, base, "1 failed, 5 passed", 1, expect_failures=1)["verdict"] == "PASS"
    assert P.audit_session(base, base, "2 failed, 4 passed", 1, expect_failures=1)["verdict"] == "FAIL"


def test_session_env_redirects_controlled_mock_lane_logs_outside_the_clone(tmp_path):
    sdir = tmp_path / "s_b1"
    env = P.session_env(sdir / "tree", sdir, tmp_path / "_h", tmp_path / "n.json", sdir / "calls.json", "det", True)
    root = Path(env["CONTROLLED_MOCK_LANE_LOG_ROOT"])
    assert str(root).startswith(str(sdir)) and (sdir / "tree") not in root.parents


# ---- T3-0.1: unresolved environment placeholders must never reach a session (clone-local cache debris) ---------------
import subprocess as _sp  # noqa: E402
import sys as _sys  # noqa: E402

import pytest as _pytest  # noqa: E402


def test_assert_resolved_env_rejects_placeholders_and_relative_paths():
    ok = {"TEMP": str(Path("C:/x/tmp") if os.name == "nt" else Path("/x/tmp")), "PYTHONUTF8": "1"}
    assert P.assert_resolved_env(dict(ok)) == ok
    for bad in ({"PYTHONPYCACHEPREFIX": r"%SystemDrive%\pyc"}, {"TEMP": "%TEMP%\run"}, {"TMP": "${HOME}/t"},
                {"PYTHONPYCACHEPREFIX": "relative/pyc"}, {"R3_LOG": "calls.json"}):
        with pytest.raises(SystemExit):
            P.assert_resolved_env(bad)


def test_session_env_pins_a_resolved_per_session_pycache_prefix(tmp_path):
    seen = set()
    for tag in ("b1", "b2", "f1", "f2"):
        sdir = tmp_path / f"s_{tag}"
        env = P.session_env(sdir / "tree", sdir, tmp_path / "_h", tmp_path / "n.json", sdir / "calls.json", "det", True)
        prefix = env["PYTHONPYCACHEPREFIX"]
        assert os.path.isabs(prefix) and prefix.startswith(str(sdir)) and "%" not in prefix
        assert (sdir / "tree") not in Path(prefix).parents and prefix not in seen
        seen.add(prefix)
        assert env["PYTHONDONTWRITEBYTECODE"] == "1"
        assert not any("%" in str(v) for v in env.values())


def _windows_interpreters():
    """Distinct CPython executables available on this Windows host: the running one, `python` on PATH and the
    Microsoft Store app-execution alias (which is the one that misbehaves without SYSTEMDRIVE)."""
    import shutil
    cands = [_sys.executable, shutil.which("python"), shutil.which("python3")]
    local = os.environ.get("LOCALAPPDATA")
    if local:
        cands.append(str(Path(local) / "Microsoft" / "WindowsApps" / "python.exe"))
    seen, out = set(), []
    for c in cands:
        if c and os.path.isfile(c) and os.path.normcase(os.path.abspath(c)) not in seen:
            seen.add(os.path.normcase(os.path.abspath(c)))
            out.append(c)
    return out


def _listing(path):
    return sorted(p.name for p in Path(path).iterdir())


def test_session_env_carries_a_resolved_system_drive(tmp_path):
    sdir = tmp_path / "s"
    env = P.session_env(sdir / "tree", sdir, tmp_path / "_h", tmp_path / "n.json", sdir / "calls.json", "det", True)
    assert "SYSTEMDRIVE" in env  # present on every platform: the scrubbed environment must not depend on the parent
    assert env["SYSTEMDRIVE"] and "%" not in env["SYSTEMDRIVE"]
    if os.name == "nt":
        assert env["SYSTEMDRIVE"].endswith(":")


@_pytest.mark.skipif(os.name != "nt", reason="Windows-only: literal %SystemDrive% directory is a cmd-style placeholder")
def test_windows_unresolved_placeholder_prefix_is_the_hazard_it_is_claimed_to_be(tmp_path):
    hazard = tmp_path / "hazard_clone"
    hazard.mkdir()
    (hazard / "m.py").write_text("X = 1\n", encoding="utf-8")
    (hazard / "run.py").write_text("import m\nprint(m.X)\n", encoding="utf-8")
    env = {"SYSTEMROOT": os.environ.get("SYSTEMROOT", r"C:\Windows"), "SYSTEMDRIVE": P._system_drive(),
           "PATH": os.environ.get("PATH", ""), "PYTHONPYCACHEPREFIX": r"%SystemDrive%\pyc"}
    r = _sp.run([_sys.executable, "run.py"], cwd=str(hazard), env=env, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    assert "%SystemDrive%" in _listing(hazard)  # relative placeholder prefix -> literal tree inside the clone
    with pytest.raises(SystemExit):  # ... which the harness refuses to hand to a session
        P.assert_resolved_env(env)


@_pytest.mark.skipif(os.name != "nt", reason="Windows-only: interpreter startup behavior under a scrubbed environment")
def test_windows_real_session_env_leaves_no_clone_root_debris_for_every_available_interpreter(tmp_path):
    """The REAL session_env() (not a hand-made minimal env) must keep every available interpreter - including the
    Microsoft Store alias - from creating files or directories in the clone root, with or without bytecode writing."""
    interpreters = _windows_interpreters()
    assert interpreters, "no interpreter found"
    for n, interp in enumerate(interpreters):
        for write_bytecode in (False, True):
            case = tmp_path / f"i{n}_{int(write_bytecode)}"
            clone, sdir = case / "clone", case / "session"
            clone.mkdir(parents=True)
            (sdir / "tmp").mkdir(parents=True)
            (clone / "m.py").write_text("X = 1\n", encoding="utf-8")
            (clone / "run.py").write_text("import m\nprint(m.X)\n", encoding="utf-8")
            env = P.session_env(clone, sdir, case / "_h", case / "n.json", sdir / "calls.json", "det", True)
            if write_bytecode:
                env.pop("PYTHONDONTWRITEBYTECODE")  # bytecode must then land in the per-session prefix, not the clone
            before = _listing(clone)
            r = _sp.run([interp, "run.py"], cwd=str(clone), env=env, capture_output=True, text=True, timeout=120)
            assert r.returncode == 0, (interp, r.stderr[-300:])
            assert _listing(clone) == before == ["m.py", "run.py"], (interp, write_bytecode, _listing(clone))
            if write_bytecode:
                assert (sdir / "pycache").is_dir(), (interp, "bytecode did not go to the session prefix")


@_pytest.mark.skipif(os.name != "nt", reason="Windows-only: reproduces the confirmed root cause (missing SYSTEMDRIVE)")
def test_windows_store_python_without_systemdrive_creates_debris_and_the_harness_env_does_not(tmp_path):
    local = os.environ.get("LOCALAPPDATA")
    store = Path(local) / "Microsoft" / "WindowsApps" / "python.exe" if local else None
    if not store or not store.is_file():
        _pytest.skip("Microsoft Store python alias not installed on this host")
    d = tmp_path / "cwd"
    d.mkdir()
    env = {"SYSTEMROOT": os.environ.get("SYSTEMROOT", r"C:\Windows"), "PATH": os.environ.get("PATH", "")}
    r = _sp.run([str(store), "-c", "pass"], cwd=str(d), env=env, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        _pytest.skip("Store python alias is not runnable from this context")
    assert "%SystemDrive%" in _listing(d), "root cause not reproducible on this host (no SYSTEMDRIVE -> debris)"
    # the harness environment carries SYSTEMDRIVE, so the preflight passes for the same interpreter
    assert P.preflight_interpreter(str(store), tmp_path / "pre", tmp_path / "_h", tmp_path / "n.json") == []


def test_preflight_fails_closed_when_the_interpreter_writes_into_its_cwd(tmp_path, monkeypatch):
    class _Done:
        returncode = 0
        stderr = ""
        stdout = "ok"

    def fake_run(cmd, cwd=None, **kw):
        (Path(cwd) / "%SystemDrive%").mkdir()  # what the Store alias does when SYSTEMDRIVE is missing
        return _Done()

    monkeypatch.setattr(P.subprocess, "run", fake_run)
    with pytest.raises(SystemExit) as exc:
        P.preflight_interpreter("python", tmp_path / "pre", tmp_path / "_h", tmp_path / "n.json")
    assert "%SystemDrive%" in str(exc.value) and "debris" in str(exc.value)


def test_preflight_passes_for_a_well_behaved_interpreter(tmp_path):
    assert P.preflight_interpreter(_sys.executable, tmp_path / "pre", tmp_path / "_h", tmp_path / "n.json") == []
