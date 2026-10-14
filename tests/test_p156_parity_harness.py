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


SYNTHETIC_SECRET = "FAKE_TEST_API_KEY_DO_NOT_USE"  # synthetic marker only; never a real credential


def _contaminated(tmp_path):
    """A tree with a benign-named secret-bearing new file, a secret-named file, a changed existing file and a deletion."""
    root = _tree(tmp_path)
    before = P.snapshot_manifest(root)
    (root / "harmless.txt").write_text("api_key = " + SYNTHETIC_SECRET + chr(10), encoding="utf-8")
    (root / ".env.local").write_text("SECRET=" + SYNTHETIC_SECRET + chr(10), encoding="utf-8")
    (root / "sub" / "b.txt").write_text("0123456789 " + SYNTHETIC_SECRET, encoding="utf-8")  # changed existing file
    (root / "a.txt").unlink()
    after = P.snapshot_manifest(root)
    return root, before, after, P.audit_session(before, after, "ok", 0)


def _all_files(path):
    return [q for q in Path(path).rglob("*") if q.is_file()]


def test_security_failed_session_never_copies_file_bodies_whatever_the_name(tmp_path):
    root, before, after, verdict = _contaminated(tmp_path)
    dest = tmp_path / "out" / "failed_sessions" / "b1"
    summary = P.preserve_failed_evidence(root, verdict, dest, before, after)
    assert summary["file_bodies_retained"] is False and summary["copied"] == []
    assert not (dest / "files").exists()  # no body directory at all
    for f in _all_files(dest):
        assert SYNTHETIC_SECRET.encode() not in f.read_bytes(), f  # A (harmless.txt), B (.env.local), changed file
    assert not any(f.name in ("harmless.txt", ".env.local") for f in _all_files(dest))


def test_security_failed_evidence_keeps_classification_and_manifest_hashes(tmp_path):
    root, before, after, verdict = _contaminated(tmp_path)
    dest = tmp_path / "out" / "failed_sessions" / "b1"
    P.preserve_failed_evidence(root, verdict, dest, before, after)
    d = json.loads((dest / "diff.json").read_text(encoding="utf-8"))
    kinds = {(x["path"], x["kind"]) for x in d["differences"]}
    assert {("harmless.txt", "CREATED"), (".env.local", "CREATED"), ("sub/b.txt", "CONTENT_CHANGED"),
            ("a.txt", "DELETED")} <= kinds
    assert d["difference_counts"]["CREATED"] == 2 and d["difference_counts"]["DELETED"] == 1
    mb = json.loads((dest / "manifest_before.json").read_text(encoding="utf-8"))
    ma = json.loads((dest / "manifest_after.json").read_text(encoding="utf-8"))
    assert mb["entries"]["a.txt"]["sha256"] == before["entries"]["a.txt"]["sha256"]
    assert ma["entries"]["harmless.txt"]["sha256"] == after["entries"]["harmless.txt"]["sha256"]
    assert ma["entries"]["harmless.txt"]["size"] == after["entries"]["harmless.txt"]["size"]
    assert mb["manifest_sha256"] == before["manifest_sha256"] and ma["manifest_sha256"] == after["manifest_sha256"]
    assert (dest / "LOCAL_ONLY.txt").is_file() and (dest / P.TASK_OWNED_MARKER).is_file()


def test_security_metadata_survives_deletion_of_the_clone_same_path_cleanup(tmp_path):
    import shutil
    root, before, after, verdict = _contaminated(tmp_path)
    dest = tmp_path / "out" / "failed_sessions" / "f2"
    P.preserve_failed_evidence(root, verdict, dest, before, after)
    shutil.rmtree(root)  # --same-path removes the clone right after the run
    d = json.loads((dest / "diff.json").read_text(encoding="utf-8"))
    assert d["verdict"] == "FAIL" and d["differences_total_recorded"] == 4
    assert json.loads((dest / "bundle.json").read_text(encoding="utf-8"))["retention"] == "metadata_only"


def test_security_export_safe_view_has_no_path_text_hashes_or_payload(tmp_path):
    _root, _before, _after, verdict = _contaminated(tmp_path)
    export = P.export_safe_differences(verdict["differences"])
    text = json.dumps(export)
    assert export and all(set(e) == {"kind", "path_digest"} for e in export)
    for needle in ("harmless", ".env", "a.txt", "b.txt", SYNTHETIC_SECRET, "sha256"):
        assert needle not in text, needle
    assert "new_paths_sample" not in verdict  # raw path sample removed from the verdict itself


def test_security_failed_bundles_obey_the_finite_retention_limits(tmp_path):
    import time as _t
    parent = tmp_path / "evidence"
    parent.mkdir()
    root, before, after, verdict = _contaminated(tmp_path)
    now = _t.time()
    for i in range(5):
        d = parent / f"run{i}_f2"
        P.preserve_failed_evidence(root, verdict, d, before, after)
        os.utime(d, (now - i * 60, now - i * 60))
    removed = P.prune_task_owned(parent, keep=2, max_age_days=14, now=now)
    assert sorted(removed) == ["run2_f2", "run3_f2", "run4_f2"]
    assert sorted(q.name for q in parent.iterdir()) == ["run0_f2", "run1_f2"]


def test_security_no_environment_switch_re_enables_body_copies(tmp_path, monkeypatch):
    for key in ("P156_COPY_FILES", "P156_KEEP_FILE_BODIES", "P156_UNSAFE_EVIDENCE", "KEEP_FAILED_FILES"):
        monkeypatch.setenv(key, "1")
    root, before, after, verdict = _contaminated(tmp_path)
    dest = tmp_path / "out" / "failed_sessions" / "b1"
    P.preserve_failed_evidence(root, verdict, dest, before, after, {"max_files": 64, "max_file_bytes": 1 << 30})
    assert not (dest / "files").exists()
    assert not any(SYNTHETIC_SECRET.encode() in f.read_bytes() for f in _all_files(dest))


def test_security_containment_still_reads_and_hashes_bodies_for_verification(tmp_path):
    """Disabling body retention must not weaken strict verification: same-size restored-mtime still FAILs."""
    root = _tree(tmp_path)
    before = P.snapshot_manifest(root)
    _same_size_restored_mtime(root)
    after = P.snapshot_manifest(root)
    assert before["entries"]["a.txt"]["sha256"] != after["entries"]["a.txt"]["sha256"]
    verdict = P.audit_session(before, after, "ok", 0)
    assert verdict["verdict"] == "FAIL" and verdict["content_equivalence_proven"] is True
    dest = tmp_path / "o" / "f"
    P.preserve_failed_evidence(root, verdict, dest, before, after)
    assert not (dest / "files").exists()


def test_security_ci_workflow_never_uploads_failed_session_bundles_or_run_outputs():
    wf = (ROOT / ".github" / "workflows" / "p152-r2c-residual-regression.yml").read_text(encoding="utf-8")
    for needle in ("failed_sessions", "harness_run_out", "raw_calls_", "containment_b1", "containment_f2", "pytest_b1", "pytest_f1"):
        assert needle not in wf, f"workflow references a local-only harness output: {needle}"


def _run_contaminated_e2e(tmp_path, print_secret=False):
    """Real orchestrator, one contaminated session (benign-named file, .env.local, changed existing file): the run
    FAILS (exit 2) and no file under the output directory contains the synthetic secret body."""
    t = tmp_path / "test_contaminate.py"
    t.write_text(
        "import os, pathlib\n"
        "def test_contaminate_f2_only():\n"
        "    if 's_f2' not in os.environ.get('R3_LOG', ''):\n"
        "        return\n"
        "    root = pathlib.Path.cwd()\n"
        f"    (root / 'harmless.txt').write_text('api_key = {SYNTHETIC_SECRET}')\n"
        f"    (root / '.env.local').write_text('SECRET={SYNTHETIC_SECRET}')\n"
        f"    (root / 'README.md').write_text(r'{SYNTHETIC_SECRET}', encoding='utf-8')\n"
        + (f"    print('{SYNTHETIC_SECRET}')\n    assert False, 'printed'\n" if print_secret else ""), encoding="utf-8")
    names = tmp_path / "names.json"
    names.write_text("{}", encoding="utf-8")
    tests = tmp_path / "tests.txt"
    tests.write_text(str(t), encoding="utf-8")
    repo = tmp_path / "tiny_repo"  # a tiny disposable repository keeps the four clones fast (no production tree)
    repo.mkdir()
    (repo / "README.md").write_text("tiny fixture repository"+chr(10), encoding="utf-8")
    for cmd in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm", "init"]):
        subprocess.run(["git", *cmd], cwd=repo, check=True, capture_output=True)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()
    out = tmp_path / "out"
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "refactor" / "p156_parity_differential.py"),
                        "--repo", str(repo), "--baseline-sha", head, "--feature-sha", head, "--names", str(names),
                        "--tests", str(tests), "--work-root", str(tmp_path / "work"), "--out-dir", str(out),
                        "--mode", "det"], cwd=str(ROOT), capture_output=True, text=True, timeout=900)
    return r, out


def test_security_end_to_end_default_run_exports_no_synthetic_payload(tmp_path):
    """Real orchestrator, one contaminated session (benign-named file, .env.local, changed existing file): the run
    FAILS (exit 2) and no file under the output directory contains the synthetic secret body."""
    r, out = _run_contaminated_e2e(tmp_path)
    assert r.returncode == 2, (r.stdout[-300:], r.stderr[-300:])  # contaminated session -> FAIL, nonzero exit
    assert "ISOLATION_VERDICT=FAIL" in r.stdout
    leaked = [str(q.relative_to(out)) for q in _all_files(out) if SYNTHETIC_SECRET.encode() in q.read_bytes()]
    assert leaked == [], leaked
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert summary["failed_sessions"] == ["f2"]
    bundle = json.loads((out / "failed_sessions" / "f2" / "bundle.json").read_text(encoding="utf-8"))
    assert bundle["retention"] == "metadata_only" and not (out / "failed_sessions" / "f2" / "files").exists()
    text = (out / "summary.json").read_text(encoding="utf-8")
    assert "harmless.txt" not in text and ".env.local" not in text  # no raw sensitive path in the export-safe file
    assert sorted(q.name for q in (tmp_path / "work").iterdir() if q.name.startswith("s_")) == []  # clones cleaned


def test_security_residual_exposure_arbitrary_test_output_is_local_only_not_sanitized(tmp_path):
    """RESIDUAL (documented, not fixed): a test that PRINTS a secret lands in pytest_<tag>.out. Those local files are
    not sanitized; only summary.json is export-safe and it never carries the payload."""
    r, out = _run_contaminated_e2e(tmp_path, print_secret=True)
    assert r.returncode == 2
    leaked = sorted(str(q.relative_to(out)).replace("\\", "/") for q in _all_files(out)
                    if SYNTHETIC_SECRET.encode() in q.read_bytes())
    assert leaked and all(x.startswith("pytest_") for x in leaked), leaked  # only the unsanitized local pytest output
    assert SYNTHETIC_SECRET not in (out / "summary.json").read_text(encoding="utf-8")
    assert (out / "LOCAL_ONLY.txt").is_file()


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


# ---- T3.2.1 export-safe summary: fixed allowlist, nothing uncontrolled can reach summary.json ----------------------
EXPORT_MARK = "EXPMARK"  # synthetic marker; every uncontrolled value below carries it


def _hostile_internal():
    """Internal evidence shaped like run_sessions() output, with a marker in every uncontrolled field."""
    tag = lambda t: {"verdict": "FAIL" if t == "f2" else "PASS", "exit_code": 2 if t == "f2" else 0,  # noqa: E731
                     "differences_total": 1 if t == "f2" else 0,
                     "difference_counts": {"CREATED": 1 if t == "f2" else 0, "DELETED": 0, "TYPE_CHANGED": 0,
                                           "CONTENT_CHANGED": 0, "METADATA_CHANGED": 0, "SCAN_ERROR": 0},
                     "project_write_audit_banner": False,
                     "differences_export_safe": ([{"kind": "CREATED", "path_digest": "0123456789abcdef"}] if t == "f2" else []),
                     "differences": [{"path": f"/raw/{EXPORT_MARK}_RAW_PATH.txt", "kind": "CREATED"}],  # internal only
                     "problems": [f"{EXPORT_MARK}_PROBLEM_TEXT"], "new_paths_sample": [f"{EXPORT_MARK}_SAMPLE"]}
    sessions = {t: {"sha": "a" * 40, "exit_code": 0, "log_sha256": "b" * 64, "log_bytes": 1,
                    "pytest_summary": f"{EXPORT_MARK}_PYTEST_TAIL_unconfigure"} for t in ("b1", "b2", "f1", "f2")}
    return {
        "schema": "p156_parity_differential.v1", "mode": "det", "sequential": False, "same_session_path": False,
        "baseline_sha": "a" * 40, "feature_sha": "c" * 40, "repo_head_for_harness": "d" * 40,
        "names": {f"mod_{EXPORT_MARK}_NAMES": [f"fn_{EXPORT_MARK}_DYNAMIC_KEY"]},
        "test_files": [f"/tmp/{EXPORT_MARK}_TEST_PATH/test_x.py"], "execution_order": ["b1", "b2", "f1", "f2"],
        "sessions": sessions,
        "isolation": {"write_containment": {t: tag(t) for t in ("b1", "b2", "f1", "f2")},
                      "containment_manifest_mode": "strict_sha256", "content_equivalence_proven": True,
                      "containment_verdict": "FAIL", "failed_sessions": ["f2"]},
        "tolerance_rules": {"R-X": {"keys": [f"{EXPORT_MARK}_KEY"], "why": f"{EXPORT_MARK}_WHY"}},
        "summary": {"total_calls": 5, "BYTE_IDENTICAL": 4, "JUSTIFIED_TOLERANCE": 1, "REAL_MISMATCH": 0, "UNRESOLVED": 0,
                    "test_outcomes_identical_across_all_sessions": True,
                    "failed_tests": [f"tests/test_{EXPORT_MARK}_FAILED_NAME.py::test_x"],
                    "per_function": {f"fn_{EXPORT_MARK}_DYNAMIC_KEY": {"calls": 5}}},
        "reproduce": f"python p156 --names /x/{EXPORT_MARK}_REPRODUCE.json",
        "unknown_future_field": f"{EXPORT_MARK}_UNKNOWN_FIELD", "debug": {"payload": f"{EXPORT_MARK}_RECORDER_PAYLOAD"},
    }


def test_export_summary_contains_no_uncontrolled_value_from_any_internal_field():
    """Vectors 1-8: names JSON, test path, pytest output, failed-test name, recorder payload, dynamic key, raw path,
    unknown field - the whole serialized bytes must not contain any of them."""
    internal = _hostile_internal()
    assert EXPORT_MARK in json.dumps(internal)  # the fixture really is hostile
    blob = json.dumps(P.build_export_safe_summary(internal), indent=1)
    assert EXPORT_MARK not in blob
    for needle in ("names", "reproduce", "pytest_summary", "failed_tests", "per_function", "test_files", "unknown_future",
                   "debug", "tolerance_rules", "/raw/", "log_sha256"):
        assert needle not in blob, needle


def test_export_summary_schema_is_fixed_and_unknown_fields_are_not_exported():
    out = P.build_export_safe_summary(_hostile_internal())
    assert set(out) == {"schema", "baseline_sha", "feature_sha", "mode", "execution", "execution_order", "containment",
                        "comparison", "failed_sessions", "sessions", "local_only_files"}
    assert out["schema"] == P.EXPORT_SCHEMA and set(out["sessions"]) == {"b1", "b2", "f1", "f2"}
    assert set(out["containment"]) == {"guarantee", "manifest_mode", "content_equivalence_proven", "verdict", "not_proven"}
    assert set(out["comparison"]) == {"total_calls", "byte_identical", "justified_tolerance", "real_mismatch",
                                      "unresolved", "test_outcomes_identical"}
    assert set(out["sessions"]["f2"]) == {"exit_code", "containment_verdict", "differences_total", "difference_counts",
                                          "differences", "project_write_audit_banner"}
    assert set(out["sessions"]["f2"]["difference_counts"]) == set(P.DIFF_KINDS)
    internal = _hostile_internal()
    internal["brand_new_field"] = "should-not-appear"
    internal["isolation"]["write_containment"]["f2"]["brand_new_nested"] = "should-not-appear"
    assert "should-not-appear" not in json.dumps(P.build_export_safe_summary(internal))
    assert out["failed_sessions"] == ["f2"] and out["containment"]["verdict"] == "FAIL"


def test_export_summary_validates_types_enums_shas_and_bounds():
    internal = _hostile_internal()
    internal["baseline_sha"] = f"{EXPORT_MARK}_NOT_A_SHA"
    internal["feature_sha"] = "G" * 40
    internal["mode"] = f"{EXPORT_MARK}_mode"
    internal["summary"]["total_calls"] = f"{EXPORT_MARK}_not_int"
    internal["summary"]["REAL_MISMATCH"] = True  # bool is not a count
    internal["summary"]["UNRESOLVED"] = -3
    internal["summary"]["test_outcomes_identical_across_all_sessions"] = f"{EXPORT_MARK}_str"
    wc = internal["isolation"]["write_containment"]["f2"]
    wc["exit_code"] = f"{EXPORT_MARK}_code"
    wc["verdict"] = f"{EXPORT_MARK}_verdict"
    wc["difference_counts"]["CREATED"] = f"{EXPORT_MARK}_n"
    wc["differences_export_safe"] = [{"kind": f"{EXPORT_MARK}_kind", "path_digest": "0123456789abcdef"},
                                     {"kind": "CREATED", "path_digest": f"{EXPORT_MARK}_digest"}] + \
                                    [{"kind": "CREATED", "path_digest": "%016x" % i} for i in range(100)]
    out = P.build_export_safe_summary(internal)
    assert EXPORT_MARK not in json.dumps(out)
    assert out["baseline_sha"] is None and out["feature_sha"] is None and out["mode"] is None
    assert out["comparison"]["total_calls"] is None and out["comparison"]["real_mismatch"] is None
    assert out["comparison"]["unresolved"] is None and out["comparison"]["test_outcomes_identical"] is None
    f2 = out["sessions"]["f2"]
    assert f2["exit_code"] is None and f2["containment_verdict"] is None and f2["difference_counts"]["CREATED"] is None
    assert len(f2["differences"]) <= P.EXPORT_MAX_DIFFERENCES and all(
        d["kind"] in P.DIFF_KINDS and len(d["path_digest"]) == 16 for d in f2["differences"])
    assert out["containment"]["verdict"] == "FAIL" and "f2" in out["failed_sessions"]  # unknown verdict is not PASS


def test_export_strict_containment_is_unchanged_by_the_export_boundary(tmp_path):
    root = _tree(tmp_path)
    before = P.snapshot_manifest(root)
    _same_size_restored_mtime(root)
    verdict = P.audit_session(before, P.snapshot_manifest(root), "ok", 0)
    assert verdict["verdict"] == "FAIL" and verdict["difference_counts"]["CONTENT_CHANGED"] == 1
    assert verdict["content_equivalence_proven"] is True


def _run_export_e2e(tmp_path, contaminate):
    """Four real sessions on a tiny disposable repository. Every uncontrolled input carries EXPMARK: the names JSON key
    and function name, the test directory/file name, a failing test name, `pytest_unconfigure` output, the recorder
    payload (return value of the recorded function), the raw work/out paths, and a contaminating file name."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("tiny fixture repository" + chr(10), encoding="utf-8")
    (repo / "m.py").write_text("def work_EXPMARK_FN(x):" + chr(10) + "    return 'EXPMARK_REC_OUT:' + str(x)" + chr(10),
                               encoding="utf-8")
    for cmd in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit",
                                                 "-qm", "init"]):
        subprocess.run(["git", *cmd], cwd=repo, check=True, capture_output=True)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()
    tdir = tmp_path / "dir_EXPMARK_TESTPATH"
    tdir.mkdir()
    (tdir / "conftest.py").write_text(
        "def pytest_unconfigure(config):" + chr(10) + "    print('EXPMARK_UNCONFIGURE_OUTPUT')" + chr(10), encoding="utf-8")
    body = [
        "import os, pathlib, sys",
        "sys.path.insert(0, os.getcwd())",
        "import m",
        "def test_recorded_EXPMARK_call():",
        "    assert m.work_EXPMARK_FN(1).startswith('EXPMARK_REC_OUT')",
        "def test_failing_EXPMARK_FAILED_NAME():",
        "    if 's_b1' in os.environ.get('R3_LOG', ''):",
        "        assert False, 'EXPMARK_ASSERT_TEXT'" if contaminate else "        pass",
        "def test_contaminate_EXPMARK_f2():",
        "    if 's_f2' in os.environ.get('R3_LOG', '') and " + ("True" if contaminate else "False") + ":",
        "        root = pathlib.Path.cwd()",
        "        (root / 'harmless_EXPMARK_FILENAME.txt').write_text('EXPMARK_BODY')",
        "        (root / 'README.md').write_text('EXPMARK_CHANGED')",
    ]
    (tdir / "test_probe_EXPMARK_TESTFILE.py").write_text(chr(10).join(body) + chr(10), encoding="utf-8")
    names = tmp_path / "names_EXPMARK.json"
    names.write_text(json.dumps({"m": ["work_EXPMARK_FN"]}), encoding="utf-8")
    tests = tmp_path / "tests.txt"
    tests.write_text(str(tdir / "test_probe_EXPMARK_TESTFILE.py"), encoding="utf-8")
    out = tmp_path / "out_EXPMARK_OUT"
    work = tmp_path / "work_EXPMARK_WORK"
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "refactor" / "p156_parity_differential.py"),
                        "--repo", str(repo), "--baseline-sha", head, "--feature-sha", head, "--names", str(names),
                        "--tests", str(tests), "--work-root", str(work), "--out-dir", str(out), "--mode", "det"],
                       cwd=str(ROOT), capture_output=True, text=True, timeout=900)
    return r, out, work


def test_export_clean_four_session_run_passes_with_a_safe_summary(tmp_path):
    r, out, work = _run_export_e2e(tmp_path, contaminate=False)
    assert r.returncode == 0, (r.stdout[-300:], r.stderr[-300:])
    raw = (out / "summary.json").read_bytes()
    assert EXPORT_MARK.encode() not in raw  # whole serialized export
    summary = json.loads(raw)
    assert summary["containment"]["verdict"] == "PASS" and summary["failed_sessions"] == []
    assert summary["comparison"]["total_calls"] >= 1 and summary["comparison"]["real_mismatch"] == 0
    assert all(summary["sessions"][t]["exit_code"] == 0 for t in ("b1", "b2", "f1", "f2"))
    # the fixture really was hostile: the markers are present in the LOCAL-only files (so the test can detect a leak)
    assert EXPORT_MARK.encode() in (out / "local_evidence.json").read_bytes()
    assert any(EXPORT_MARK.encode() in q.read_bytes() for q in out.glob("raw_calls_*.json"))
    assert any(EXPORT_MARK.encode() in q.read_bytes() for q in out.glob("pytest_*.out"))


def test_export_contaminated_four_session_run_exits_2_with_correct_counts_and_safe_summary(tmp_path):
    r, out, work = _run_export_e2e(tmp_path, contaminate=True)
    assert r.returncode == 2, (r.stdout[-300:], r.stderr[-300:])
    raw = (out / "summary.json").read_bytes()
    assert EXPORT_MARK.encode() not in raw
    summary = json.loads(raw)
    assert summary["containment"]["verdict"] == "FAIL"
    assert summary["failed_sessions"] == ["b1", "f2"]  # b1: failing test (exit 1); f2: filesystem contamination
    f2 = summary["sessions"]["f2"]
    assert f2["difference_counts"]["CREATED"] == 1 and f2["difference_counts"]["CONTENT_CHANGED"] == 1
    assert f2["differences_total"] == 2 and len(f2["differences"]) == 2
    assert summary["sessions"]["b1"]["exit_code"] == 1 and summary["sessions"]["b2"]["exit_code"] == 0


def test_export_local_diagnostics_remain_after_failed_session_cleanup(tmp_path):
    r, out, work = _run_export_e2e(tmp_path, contaminate=True)
    assert r.returncode == 2
    assert sorted(q.name for q in work.iterdir() if q.name.startswith("s_")) == []  # disposable clones removed
    diff = json.loads((out / "failed_sessions" / "f2" / "diff.json").read_text(encoding="utf-8"))
    paths = {(d["path"], d["kind"]) for d in diff["differences"]}
    assert ("harmless_EXPMARK_FILENAME.txt", "CREATED") in paths and ("README.md", "CONTENT_CHANGED") in paths
    local = json.loads((out / "local_evidence.json").read_text(encoding="utf-8"))
    assert local["reproduce"] and local["names"] and local["test_files"]  # full internal evidence stays available
    assert (out / "failed_sessions" / "f2" / "LOCAL_ONLY.txt").is_file() and (out / "LOCAL_ONLY.txt").is_file()
