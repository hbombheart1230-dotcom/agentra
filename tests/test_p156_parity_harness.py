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
    before = P.snapshot_manifest(root)
    (root / "data" / "logs").mkdir(parents=True)  # empty directory: invisible to `git status`
    (root / "__pycache__").mkdir()  # typically git-ignored
    (root / ".git" / "inside-git").write_text("ignored by design", encoding="utf-8")
    after = P.snapshot_manifest(root)
    created = sorted(d["path"] for d in P.diff_manifests(before, after) if d["kind"] == "CREATED")
    assert created == ["__pycache__", "data", "data/logs"]
    verdict = P.audit_session(before, after, "6 passed", 0)
    assert verdict["verdict"] == "FAIL" and verdict["new_paths_in_session_root"] == 3
    clean = P.audit_session(before, before, "6 passed", 0)
    assert clean["verdict"] == "PASS"


def _empty_manifest():
    return {"schema": P.MANIFEST_SCHEMA, "mode": P.MODE_STRICT, "entries": {}, "errors": [], "stats": {},
            "manifest_sha256": "0"}


def test_audit_fails_on_project_write_banner_or_bad_exit_code():
    base = _empty_manifest()
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


def _interpreter_works(path):
    """True only for a real, runnable CPython 3 (a Microsoft Store *alias stub* exists as a file but exits 9009 and only
    prints an install hint - e.g. on GitHub runners without the Store package)."""
    try:
        r = _sp.run([path, "-c", "import sys; print(sys.version_info[0])"], capture_output=True, text=True, timeout=60)
    except (OSError, _sp.SubprocessError):
        return False
    return r.returncode == 0 and r.stdout.strip() == "3"


def _windows_interpreters():
    """Distinct RUNNABLE CPython executables on this Windows host: the running one, `python` on PATH and the Microsoft
    Store app-execution alias (the one that misbehaves without SYSTEMDRIVE) when it is a real interpreter."""
    import shutil
    cands = [_sys.executable, shutil.which("python"), shutil.which("python3")]
    local = os.environ.get("LOCALAPPDATA")
    if local:
        cands.append(str(Path(local) / "Microsoft" / "WindowsApps" / "python.exe"))
    seen, out = set(), []
    for c in cands:
        key = os.path.normcase(os.path.abspath(c)) if c else None
        if c and os.path.isfile(c) and key not in seen:
            seen.add(key)
            if _interpreter_works(c):
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


@_pytest.mark.skipif(os.name != "nt", reason="Windows-only: .bat stub emulating the Store alias stub")
def test_windows_non_runnable_interpreter_stubs_are_excluded_from_the_isolation_matrix(tmp_path):
    stub = tmp_path / "python.bat"
    stub.write_text("@echo off\r\necho Python was not found\r\nexit /b 9009\r\n", encoding="utf-8")
    assert _interpreter_works(str(stub)) is False
    assert _interpreter_works(_sys.executable) is True
    assert _sys.executable in _windows_interpreters()


# ---- T3-0.3 write containment: structured, integrity-aware manifests -----------------------------------------------
def _tree(tmp_path):
    root = tmp_path / "tree"
    (root / ".git").mkdir(parents=True)
    (root / "sub").mkdir()
    (root / "emptydir").mkdir()
    (root / "a.txt").write_text("hello world", encoding="utf-8")
    (root / "sub" / "b.txt").write_text("0123456789", encoding="utf-8")
    (root / "ignored.log").write_text("x", encoding="utf-8")
    return root


def _mtime_only(root):
    st = (root / "a.txt").stat()
    os.utime(root / "a.txt", ns=(st.st_atime_ns, st.st_mtime_ns + 5_000_000_000))


def _same_size_restored_mtime(root):
    st = (root / "a.txt").stat()
    (root / "a.txt").write_text("HELLO WORLD", encoding="utf-8")
    os.utime(root / "a.txt", ns=(st.st_atime_ns, st.st_mtime_ns))


def _same_size(root):
    st = (root / "a.txt").stat()
    (root / "a.txt").write_text("HELLO WORLD", encoding="utf-8")
    os.utime(root / "a.txt", ns=(st.st_atime_ns, st.st_mtime_ns + 7_000_000_000))


def _type_changed(root):
    (root / "emptydir").rmdir()
    (root / "emptydir").write_text("now a file", encoding="utf-8")


_MUTATIONS = {
    "new_file": (lambda r: (r / "new.txt").write_text("n", encoding="utf-8"), "CREATED"),
    "new_empty_directory": (lambda r: (r / "newdir").mkdir(), "CREATED"),
    "content_modified": (lambda r: (r / "a.txt").write_text("changed content!!", encoding="utf-8"), "CONTENT_CHANGED"),
    "file_deleted": (lambda r: (r / "a.txt").unlink(), "DELETED"),
    "empty_directory_deleted": (lambda r: (r / "emptydir").rmdir(), "DELETED"),
    "mtime_only": (_mtime_only, "METADATA_CHANGED"),
    "same_size_content": (_same_size, "CONTENT_CHANGED"),
    "same_size_content_restored_mtime": (_same_size_restored_mtime, "CONTENT_CHANGED"),
    "type_changed": (_type_changed, "TYPE_CHANGED"),
}


@pytest.mark.parametrize("name", sorted(_MUTATIONS))
def test_containment_every_filesystem_mutation_fails_the_session_in_strict_mode(tmp_path, name):
    root = _tree(tmp_path)
    before = P.snapshot_manifest(root)
    mutate, kind = _MUTATIONS[name]
    mutate(root)
    verdict = P.audit_session(before, P.snapshot_manifest(root), "6 passed", 0)
    assert verdict["verdict"] == "FAIL", verdict
    assert verdict["difference_counts"][kind] >= 1, verdict["difference_counts"]
    assert verdict["content_equivalence_proven"] is True and verdict["guarantee"] == P.CONTAINMENT_GUARANTEE


def test_containment_unchanged_tree_is_a_clean_pass_without_false_differences(tmp_path):
    root = _tree(tmp_path)
    before = P.snapshot_manifest(root)
    after = P.snapshot_manifest(root)
    verdict = P.audit_session(before, after, "6 passed", 0)
    assert verdict["verdict"] == "PASS" and verdict["differences_total"] == 0
    assert before["manifest_sha256"] == after["manifest_sha256"]
    assert before["stats"]["files"] == 3 and before["stats"]["dirs"] == 2


def test_containment_git_metadata_is_excluded_but_ordinary_ignored_and_empty_entries_are_not(tmp_path):
    root = _tree(tmp_path)
    before = P.snapshot_manifest(root)
    (root / ".git" / "HEAD").write_text("ref", encoding="utf-8")
    assert P.audit_session(before, P.snapshot_manifest(root), "ok", 0)["verdict"] == "PASS"
    assert "ignored.log" in before["entries"] and "emptydir" in before["entries"]


def test_containment_fast_mode_is_labelled_and_cannot_see_same_size_restored_mtime_changes(tmp_path):
    root = _tree(tmp_path)
    before = P.snapshot_manifest(root, P.MODE_FAST)
    _same_size_restored_mtime(root)
    verdict = P.audit_session(before, P.snapshot_manifest(root, P.MODE_FAST), "ok", 0)
    assert verdict["manifest_mode"] == P.MODE_FAST and verdict["content_equivalence_proven"] is False
    assert verdict["verdict"] == "PASS"  # the documented, labelled coverage limit of the fast tier
    strict_before = P.snapshot_manifest(root)
    st = (root / "a.txt").stat()
    (root / "a.txt").write_text("Hello World", encoding="utf-8")  # same size again, mtime restored
    os.utime(root / "a.txt", ns=(st.st_atime_ns, st.st_mtime_ns))
    assert P.audit_session(strict_before, P.snapshot_manifest(root), "ok", 0)["verdict"] == "FAIL"


@pytest.mark.parametrize("which", ["mtime", "size"])
def test_containment_fast_mode_still_fails_size_and_mtime_changes(tmp_path, which):
    root = _tree(tmp_path)
    before = P.snapshot_manifest(root, P.MODE_FAST)
    if which == "mtime":
        _mtime_only(root)
    else:
        (root / "a.txt").write_text("longer content", encoding="utf-8")
    assert P.audit_session(before, P.snapshot_manifest(root, P.MODE_FAST), "ok", 0)["verdict"] == "FAIL"


def test_containment_scan_error_fails_closed(tmp_path, monkeypatch):
    root = _tree(tmp_path)
    before = P.snapshot_manifest(root)
    real = P._sha256

    def boom(path):
        if str(path).endswith("a.txt"):
            raise PermissionError("denied")
        return real(path)

    monkeypatch.setattr(P, "_sha256", boom)
    after = P.snapshot_manifest(root)
    assert after["errors"] and "a.txt" in after["errors"][0]["path"]
    verdict = P.audit_session(before, after, "ok", 0)
    assert verdict["verdict"] == "FAIL" and verdict["difference_counts"]["SCAN_ERROR"] >= 1


def test_containment_unstable_file_during_hash_fails_closed(tmp_path, monkeypatch):
    root = _tree(tmp_path)
    real = P._sha256

    def racing(path):
        digest = real(path)
        if str(path).endswith("a.txt"):
            Path(path).write_text("rewritten while hashing", encoding="utf-8")
        return digest

    monkeypatch.setattr(P, "_sha256", racing)
    m = P.snapshot_manifest(root)
    assert any("unstable" in e["error"] for e in m["errors"])
    assert P.audit_session(m, m, "ok", 0)["verdict"] == "FAIL"


def test_containment_refuses_path_name_only_snapshots_and_mixed_modes(tmp_path):
    root = _tree(tmp_path)
    names = P.snapshot_tree(root)
    with pytest.raises(TypeError):
        P.audit_session(names, names, "ok", 0)
    with pytest.raises(ValueError):
        P.audit_session(P.snapshot_manifest(root), P.snapshot_manifest(root, P.MODE_FAST), "ok", 0)


def test_containment_guarantee_is_named_and_states_what_it_does_not_prove():
    assert P.CONTAINMENT_GUARANTEE == "PRE_POST_END_STATE_MANIFEST_EQUIVALENCE"
    joined = " ".join(P.CONTAINMENT_NOT_PROVEN)
    assert "transient write-and-restore" in joined and "OS-wide write interception" in joined


def test_failed_session_evidence_is_bounded_sanitized_and_recorded_before_cleanup(tmp_path):
    root = _tree(tmp_path)
    before = P.snapshot_manifest(root)
    (root / "leak.txt").write_text("debris", encoding="utf-8")
    (root / ".env.local").write_text("SECRET=1", encoding="utf-8")
    (root / "big.bin").write_bytes(b"0" * 2048)
    (root / "a.txt").unlink()
    after = P.snapshot_manifest(root)
    verdict = P.audit_session(before, after, "ok", 0)
    caps = {"max_files": 64, "max_file_bytes": 1024, "max_total_bytes": 4096}
    dest = tmp_path / "out" / "failed_sessions" / "b1"
    summary = P.preserve_failed_evidence(root, verdict, dest, before, after, caps)
    assert summary["copied"] == ["leak.txt"]
    reasons = {x["path"]: x["reason"] for x in summary["skipped"]}
    assert "secret" in reasons[".env.local"] and "max_file_bytes" in reasons["big.bin"]
    assert not (dest / "files" / ".env.local").exists()
    import shutil
    shutil.rmtree(root)  # the disposable clone is gone; the bundle must still describe the deletion
    d = json.loads((dest / "diff.json").read_text(encoding="utf-8"))
    kinds = {(x["path"], x["kind"]) for x in d["differences"]}
    assert ("a.txt", "DELETED") in kinds and ("leak.txt", "CREATED") in kinds
    assert (dest / "manifest_before.json").is_file() and (dest / "manifest_after.json").is_file()


def test_retention_prunes_only_marked_task_owned_bundles(tmp_path):
    parent = tmp_path / "evidence"
    parent.mkdir()
    import time as _t
    now = _t.time()
    for i in range(4):
        d = parent / f"bundle{i}"
        d.mkdir()
        (d / P.TASK_OWNED_MARKER).write_text("x", encoding="utf-8")
        (d / "diff.json").write_text("{}", encoding="utf-8")
        os.utime(d, (now - i * 100, now - i * 100))
    foreign = parent / "codex_clone"
    foreign.mkdir()
    (foreign / "keep.txt").write_text("not ours", encoding="utf-8")
    os.utime(foreign, (now - 99 * 86400, now - 99 * 86400))
    removed = P.prune_task_owned(parent, keep=2, max_age_days=14, now=now)
    assert sorted(removed) == ["bundle2", "bundle3"]
    assert (parent / "bundle0").exists() and (parent / "bundle1").exists()
    assert (foreign / "keep.txt").exists(), "an unmarked directory must never be removed"


def test_cleanup_refuses_directories_outside_the_task_owned_work_root(tmp_path):
    work, other = tmp_path / "work", tmp_path / "codex_clone"
    (work / "s_b1").mkdir(parents=True)
    other.mkdir()
    (other / "f.txt").write_text("x", encoding="utf-8")
    with pytest.raises(SystemExit):
        P._remove_task_owned(other, work)
    with pytest.raises(SystemExit):
        P._remove_task_owned(work, work)
    P._remove_task_owned(work / "s_b1", work)
    assert not (work / "s_b1").exists() and (other / "f.txt").exists()


# ---- T3-0.3 NTFS directory-mtime diagnostics (P2 stays UNRESOLVED; facts only) ---------------------------------------
def _diag():
    import importlib
    return importlib.import_module("p160_ntfs_dir_mtime_diagnostics")


def test_containment_ntfs_diag_summarize_settle_parses_directory_only_modifications(tmp_path):
    log = tmp_path / "settle.log"
    log.write_text(
        "PRODUCTION PATH WRITE DETECTED DURING TEST SESSION (audit_mode=fast)\n"
        "  MODIFIED data/eval  size=-1->-1 mtime_ns=100->2000100 sha256_after=<unreadable>\n"
        "  MODIFIED data/specs  size=-1->-1 mtime_ns=5->2000005 sha256_after=<unreadable>\n", encoding="utf-8")
    rec = _diag().summarize_settle(str(log), 1)
    assert rec["banner_present"] is True and rec["directory_only"] is True and rec["status"] == "UNRESOLVED"
    assert [r["mtime_delta_ns"] for r in rec["modified_entries"]] == [2000000, 2000000]


def test_containment_ntfs_diag_clean_settle_log_is_reported_as_clean(tmp_path):
    log = tmp_path / "settle.log"
    log.write_text("23 tests collected\n", encoding="utf-8")
    rec = _diag().summarize_settle(str(log), 0)
    assert rec["banner_present"] is False and rec["modified_entries"] == [] and rec["first_session_exit_code"] == 0


def test_containment_ntfs_diag_probe_is_read_only_and_never_tolerant(tmp_path):
    before = P.snapshot_manifest(_diag().ROOT.joinpath("scripts"), P.MODE_FAST)
    rec = _diag().probe(delays=(0.0, 0.0))
    assert rec["status"] == "UNRESOLVED" and "no tolerance" in rec["note"]
    assert P.audit_session(before, P.snapshot_manifest(_diag().ROOT.joinpath("scripts"), P.MODE_FAST), "ok", 0)["verdict"] == "PASS"
