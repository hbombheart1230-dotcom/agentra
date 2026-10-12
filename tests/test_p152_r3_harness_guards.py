"""P15-R3-AUDIT-HARNESS-GUARDS-006: the offline R3 audit harnesses fail closed.

Live-path cases use ONLY supplied strings (`ntpath` lexical rules plus a filesystem stub that
fails the test on any access); the live checkout is never run, imported, stat'ed or hashed.
Success paths run in disposable mini clones under tmp_path.
"""
import importlib.util
import json
import ntpath
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts" / "refactor"
SEAM = SCRIPTS / "p152_r3_seam_challenge.py"
RECORDER = SCRIPTS / "p152_r3_call_recorder.py"
ENV_OK = {"PYTHONDONTWRITEBYTECODE": "1"}


def _load(path, name):
    os.environ.setdefault("R3_RECORDER_INERT", "1")  # recorder stays inert when imported by tests
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SEAM_MOD = _load(SEAM, "r3_seam_under_test")
REC_MOD = _load(RECORDER, "r3_rec_under_test")
MODULES = [SEAM_MOD, REC_MOD]


class _NoFS:
    """Any filesystem access during a lexical-failure case is a test failure."""

    def __getattr__(self, name):
        raise AssertionError("filesystem touched before lexical rejection: %s" % name)


def _validate(mod, root, cwd=None, env=None, inputs=None, outputs=None, extra=(), pm=ntpath, fs=None):
    return mod.validate_environment(
        root, root if cwd is None else cwd, ENV_OK if env is None else env,
        {"IN": "D:\\evidence\\in.json"} if inputs is None else inputs,
        {"OUT": "D:\\evidence\\out.json"} if outputs is None else outputs,
        extra_protected=extra, pm=pm, fs=fs if fs is not None else _NoFS(),
    )


@pytest.mark.parametrize("mod", MODULES)
@pytest.mark.parametrize("root", [
    "C:\\Agentra", "c:\\AGENTRA", "C:/Agentra/", "C:\\Agentra\\", "C:\\Agentra\\libs\\reporting",
    "\\\\?\\C:\\Agentra", "\\\\?\\c:\\agentra\\venv", "C:\\Agentra\\r3_clone", "C:\\",
])
def test_live_root_and_descendants_and_ancestors_are_refused_without_fs_access(mod, root):
    with pytest.raises(mod.GuardError):
        _validate(mod, root)


@pytest.mark.parametrize("mod", MODULES)
@pytest.mark.parametrize("path", ["C:\\Agentra\\..\\Agentra", "D:\\clone\\..\\..\\x", "D:\\a\\b\\..\\c"])
def test_dotdot_components_are_refused(mod, path):
    with pytest.raises(mod.GuardError, match=r"\.\."):
        _validate(mod, path)


@pytest.mark.parametrize("mod", MODULES)
@pytest.mark.parametrize("root", [None, "", "   ", "clone", ".\\clone", "..\\clone", "\\clone", "D:clone", "D:"])
def test_missing_or_relative_root_is_refused(mod, root):
    with pytest.raises(mod.GuardError):
        _validate(mod, root)


@pytest.mark.parametrize("mod", MODULES)
def test_short_name_alias_is_refused(mod):
    with pytest.raises(mod.GuardError, match="8.3"):
        _validate(mod, "C:\\AGENTR~1")


@pytest.mark.parametrize("mod", MODULES)
def test_extra_protected_root_and_descendants_refused(mod):
    with pytest.raises(mod.GuardError, match="protected"):
        _validate(mod, "D:\\Other\\clone", extra=["D:\\other"])
    with pytest.raises(mod.GuardError, match="protected"):
        _validate(mod, "D:\\clone", outputs={"OUT": "E:\\protected\\x.json"}, extra=["E:\\Protected"])
    with pytest.raises(mod.GuardError, match="protected"):
        _validate(mod, "D:\\clone", inputs={"IN": "E:\\protected\\in.json"}, extra=["E:\\Protected"])


@pytest.mark.parametrize("mod", MODULES)
def test_cwd_must_equal_root_and_bytecode_env_required(mod):
    with pytest.raises(mod.GuardError, match="cwd"):
        _validate(mod, "D:\\clone", cwd="C:\\Agentra\\scripts")
    with pytest.raises(mod.GuardError, match="cwd"):
        _validate(mod, "D:\\clone", cwd="D:\\clone\\sub")
    for env in ({}, {"PYTHONDONTWRITEBYTECODE": ""}, {"PYTHONDONTWRITEBYTECODE": "0"}):
        with pytest.raises(mod.GuardError, match="PYTHONDONTWRITEBYTECODE"):
            _validate(mod, "D:\\clone", env=env)


@pytest.mark.parametrize("mod", MODULES)
def test_input_output_path_rules(mod):
    for inputs, outputs, msg in [
        ({"IN": "in.json"}, {"OUT": "D:\\e\\o.json"}, "absolute"),
        ({"IN": "D:\\e\\in.json"}, {"OUT": "out.json"}, "absolute"),
        ({"IN": ""}, {"OUT": "D:\\e\\o.json"}, "missing"),
        ({"IN": "D:\\e\\x.json"}, {"OUT": "D:\\E\\X.JSON"}, "collides"),          # output overwrites input (case-insens.)
        ({"IN": "D:\\e\\in.json"}, {"OUT": "D:\\clone\\out.json"}, "outside"),     # output inside audited root
        ({"IN": "D:\\e\\in.json"}, {"OUT": "C:\\Agentra\\reports\\o.json"}, "protected"),
        ({"IN": "C:\\Agentra\\data\\in.json"}, {"OUT": "D:\\e\\o.json"}, "protected"),
    ]:
        with pytest.raises(mod.GuardError, match=msg):
            _validate(mod, "D:\\clone", inputs=inputs, outputs=outputs)
    with pytest.raises(mod.GuardError, match="collides"):
        _validate(mod, "D:\\clone", inputs={"A": "D:\\e\\same.json"}, outputs={"B": "D:\\e\\same.json"})


def test_both_guards_are_behaviourally_identical():
    cases = [
        ("C:\\Agentra", "C:\\Agentra", ENV_OK, "D:\\e\\i.json", "D:\\e\\o.json"),
        ("D:\\clone", "D:\\clone", ENV_OK, "i.json", "D:\\e\\o.json"),
        ("D:\\clone", "D:\\other", ENV_OK, "D:\\e\\i.json", "D:\\e\\o.json"),
        ("D:\\clone", "D:\\clone", {}, "D:\\e\\i.json", "D:\\e\\o.json"),
        ("D:\\clone", "D:\\clone", ENV_OK, "D:\\e\\i.json", "D:\\clone\\o.json"),
        ("\\\\?\\C:\\Agentra\\x", "\\\\?\\C:\\Agentra\\x", ENV_OK, "D:\\e\\i.json", "D:\\e\\o.json"),
    ]
    for root, cwd, env, i, o in cases:
        msgs = []
        for mod in MODULES:
            try:
                _validate(mod, root, cwd=cwd, env=env, inputs={"IN": i}, outputs={"OUT": o})
                msgs.append("OK")
            except mod.GuardError as exc:
                msgs.append(str(exc))
        assert msgs[0] == msgs[1], (root, msgs)
        assert msgs[0] != "OK"
    assert SEAM_MOD.LIVE_ROOT == REC_MOD.LIVE_ROOT == "C:\\Agentra"


def test_live_strings_cause_no_real_filesystem_calls(monkeypatch):
    seen = []

    def spy(name):
        real = getattr(os, name)

        def wrapped(path=".", *a, **k):
            seen.append(str(path))
            return real(path, *a, **k)
        monkeypatch.setattr(os, name, wrapped)

    for name in ("lstat", "stat", "scandir", "listdir"):
        spy(name)
    for name in ("exists", "isdir", "isfile", "islink", "lexists", "realpath"):
        real = getattr(os.path, name)

        def wrapped(path, *a, _real=real, **k):
            seen.append(str(path))
            return _real(path, *a, **k)
        monkeypatch.setattr(os.path, name, wrapped)
    for mod in MODULES:
        for root in ("C:\\Agentra", "c:/agentra/venv", "\\\\?\\C:\\Agentra", "C:\\"):
            with pytest.raises(mod.GuardError):
                mod.validate_environment(root, root, ENV_OK, {"IN": "C:\\Agentra\\i.json"}, {"OUT": "C:\\Agentra\\o.json"})
    live = [p for p in seen if p.replace("/", "\\").lower().rstrip("\\").startswith("c:\\agentra")
            and not p.lower().startswith("c:\\agentraevidence")]
    assert live == [], live


# ---- disposable isolated mini clone (real filesystem under tmp_path) ----------------------------
def _mini_clone(tmp_path, name="clone"):
    root = tmp_path / name
    (root / ".git").mkdir(parents=True)
    (root / ".git" / "HEAD").write_text("ref: refs/heads/refactor/p1.5\n")
    ev = tmp_path / "evidence"
    ev.mkdir(exist_ok=True)
    (ev / "in.json").write_text("{}")
    return root, ev


@pytest.mark.parametrize("mod", MODULES)
def test_success_in_isolated_mini_clone_and_fs_failure_modes(mod, tmp_path):
    root, ev = _mini_clone(tmp_path)
    ok = mod.validate_environment(str(root), str(root), ENV_OK, {"IN": str(ev / "in.json")}, {"OUT": str(ev / "out.json")})
    assert Path(ok["root"]) == root and Path(ok["outputs"]["OUT"]) == ev / "out.json"
    if os.name == "nt":  # case normalisation: upper-cased cwd still equals root
        mod.validate_environment(str(root), str(root).upper(), ENV_OK, {"IN": str(ev / "in.json")}, {"OUT": str(ev / "out.json")})
    # output exists -> refused
    (ev / "taken.json").write_text("x")
    with pytest.raises(mod.GuardError, match="exists"):
        mod.validate_environment(str(root), str(root), ENV_OK, {"IN": str(ev / "in.json")}, {"OUT": str(ev / "taken.json")})
    # output parent missing / input missing
    with pytest.raises(mod.GuardError, match="parent"):
        mod.validate_environment(str(root), str(root), ENV_OK, {"IN": str(ev / "in.json")}, {"OUT": str(ev / "nope" / "o.json")})
    with pytest.raises(mod.GuardError, match="existing file|not accessible"):
        mod.validate_environment(str(root), str(root), ENV_OK, {"IN": str(ev / "absent.json")}, {"OUT": str(ev / "o2.json")})
    # not a clone: no .git / .git is a file (linked worktree) / .git without HEAD
    bare = tmp_path / "bare"
    bare.mkdir()
    for setup in (lambda: None, lambda: (bare / ".git").write_text("gitdir: elsewhere"),):
        setup()
        with pytest.raises(mod.GuardError, match="Git clone"):
            mod.validate_environment(str(bare), str(bare), ENV_OK, {"IN": str(ev / "in.json")}, {"OUT": str(ev / "o3.json")})
    nohead = tmp_path / "nohead"
    (nohead / ".git").mkdir(parents=True)
    with pytest.raises(mod.GuardError, match="Git clone"):
        mod.validate_environment(str(nohead), str(nohead), ENV_OK, {"IN": str(ev / "in.json")}, {"OUT": str(ev / "o4.json")})


@pytest.mark.parametrize("mod", MODULES)
def test_symlink_alias_of_root_is_refused(mod, tmp_path):
    root, ev = _mini_clone(tmp_path)
    link = tmp_path / "alias"
    try:
        os.symlink(root, link, target_is_directory=True)
    except (OSError, NotImplementedError):
        made = False
        if os.name == "nt":  # junctions need no privilege
            made = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(root)],
                                  capture_output=True).returncode == 0
        if not made:
            pytest.skip("neither symlink nor junction creation permitted")
    with pytest.raises(mod.GuardError, match="symlink|reparse"):
        mod.validate_environment(str(link), str(link), ENV_OK, {"IN": str(ev / "in.json")}, {"OUT": str(ev / "o.json")})


# ---- end-to-end fail-before-import behaviour in subprocesses -----------------------------------
def _run(cmd, cwd, env_extra=None, base_env=True):
    env = {k: v for k, v in os.environ.items() if not k.startswith("R3_")}
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONDONTWRITEBYTECODE", None)  # each scenario states it explicitly
    env.update(env_extra or {})
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, encoding="utf-8", errors="replace", timeout=180)


def _marker_pkg(root, marker):
    (root / "libs").mkdir(exist_ok=True)
    (root / "libs" / "__init__.py").write_text(
        "open(%r, 'w').write('imported')\n" % str(marker))


def test_seam_script_fails_before_importing_production_code(tmp_path):
    root, ev = _mini_clone(tmp_path)
    marker = tmp_path / "marker.txt"
    _marker_pkg(root, marker)
    out = ev / "o.json"
    cases = [
        ([], {}),                                                                       # no --root: cwd NOT inferred
        (["--root", "relative"], {}),
        (["--root", str(root), "--moved-free", str(ev / "in.json"), "--out", str(out)], {}),   # no bytecode env
        (["--root", str(root), "--moved-free", str(ev / "in.json"), "--out", str(root / "o.json")], ENV_OK),
        (["--root", str(root), "--moved-free", str(ev / "in.json"), "--out", str(ev / "in.json")], ENV_OK),
        (["--root", "C:\\Agentra", "--moved-free", str(ev / "in.json"), "--out", str(out)], ENV_OK),
    ]
    for args, env in cases:
        r = _run([sys.executable, "-I", "-B", str(SEAM)] + args, cwd=root, env_extra=env)
        assert r.returncode != 0, (args, r.stdout, r.stderr)
        assert not marker.exists() and not out.exists(), args
    r = _run([sys.executable, "-I", "-B", str(SEAM), "--root", str(root), "--moved-free", str(ev / "in.json"),
              "--out", str(out)], cwd=tmp_path, env_extra=ENV_OK)               # wrong cwd
    assert r.returncode == 2 and "cwd" in r.stderr and not marker.exists()


def test_seam_script_success_semantics_in_mini_clone(tmp_path):
    root, ev = _mini_clone(tmp_path)
    rep = root / "libs" / "reporting"
    rep.mkdir(parents=True)
    (root / "libs" / "__init__.py").write_text("")
    (rep / "__init__.py").write_text("")
    (rep / "trade_report_markdown_clean.py").write_text(
        "def _humanize_reporter_pattern(n, d, v):\n    return 'h:%s' % (n,)\n")
    (rep / "trade_report_ai.py").write_text(
        "def _helper():\n    return 1\n\n"
        "def resolve_shared_trade_facts(story):\n    _helper()\n    return {'k': _helper()}\n")
    (ev / "free.json").write_text(json.dumps({"libs.reporting.trade_report_ai": {"resolve_shared_trade_facts": ["_helper"]}}))
    out = ev / "seam.json"
    r = _run([sys.executable, "-I", "-B", str(SEAM), "--root", str(root), "--moved-free", str(ev / "free.json"),
              "--out", str(out)], cwd=root, env_extra=ENV_OK)
    assert r.returncode == 0, r.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert set(data) == {"direct", "seam"} and "trade_report_ai.resolve_shared_trade_facts" in data["seam"]
    assert len(data["direct"]) > 0
    # second run refuses to overwrite the existing output
    r2 = _run([sys.executable, "-I", "-B", str(SEAM), "--root", str(root), "--moved-free", str(ev / "free.json"),
               "--out", str(out)], cwd=root, env_extra=ENV_OK)
    assert r2.returncode == 2 and "exists" in r2.stderr
    assert not list(root.rglob("__pycache__")), "bytecode written into the audited clone"


def test_recorder_plugin_fails_before_conftest_and_collection(tmp_path):
    root, ev = _mini_clone(tmp_path)
    marker = tmp_path / "conftest_loaded.txt"
    (root / "conftest.py").write_text("open(%r, 'w').write('x')\n" % str(marker))
    (root / "test_a.py").write_text("def test_a():\n    pass\n")
    base = {"PYTHONPATH": str(SCRIPTS), "PYTHONDONTWRITEBYTECODE": "1"}
    scenarios = [
        {},                                                                   # R3_ROOT missing
        {"R3_ROOT": str(root), "R3_NAMES": str(ev / "in.json")},              # R3_LOG missing
        {"R3_ROOT": "relative", "R3_NAMES": str(ev / "in.json"), "R3_LOG": str(ev / "l.json")},
        {"R3_ROOT": "C:\\Agentra", "R3_NAMES": str(ev / "in.json"), "R3_LOG": str(ev / "l.json")},
        {"R3_ROOT": str(root), "R3_NAMES": str(ev / "in.json"), "R3_LOG": str(root / "l.json")},
    ]
    for extra in scenarios:
        r = _run([sys.executable, "-B", "-m", "pytest", "-p", "p152_r3_call_recorder", "-p", "no:cacheprovider", "-q"],
                 cwd=root, env_extra={**base, **extra})
        assert r.returncode != 0
        assert "R3-GUARD-FAIL" in (r.stdout + r.stderr), (extra, r.stdout, r.stderr)
        assert not marker.exists(), "conftest imported before the guard rejected the run"
    r = _run([sys.executable, "-B", "-m", "pytest", "-p", "p152_r3_call_recorder", "-p", "no:cacheprovider", "-q"],
             cwd=root, env_extra={"PYTHONPATH": str(SCRIPTS), "R3_ROOT": str(root), "R3_NAMES": str(ev / "in.json"),
                                  "R3_LOG": str(ev / "l.json")})                # no bytecode env
    assert r.returncode != 0 and "PYTHONDONTWRITEBYTECODE" in (r.stdout + r.stderr) and not marker.exists()


def test_recorder_plugin_success_semantics_in_mini_clone(tmp_path):
    root, ev = _mini_clone(tmp_path)
    (root / "fakepkg").mkdir()
    (root / "fakepkg" / "__init__.py").write_text("")
    (root / "fakepkg" / "mod.py").write_text("def f(x):\n    return {'v': x}\n")
    (root / "test_a.py").write_text("from fakepkg import mod\n\ndef test_a():\n    assert mod.f(3) == {'v': 3}\n")
    (ev / "names.json").write_text(json.dumps({"fakepkg.mod": ["f"]}))
    log = ev / "calls.json"
    env = {"PYTHONPATH": str(SCRIPTS), "PYTHONDONTWRITEBYTECODE": "1", "R3_ROOT": str(root),
           "R3_NAMES": str(ev / "names.json"), "R3_LOG": str(log)}
    r = _run([sys.executable, "-B", "-m", "pytest", "-p", "p152_r3_call_recorder", "-p", "no:cacheprovider", "-q"],
             cwd=root, env_extra=env)
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads(log.read_text(encoding="utf-8"))
    assert list(data["outcomes"].values()) == ["passed"]
    (calls,) = data["calls"].values()
    assert [c[0] for c in calls] == ["mod.f"] and len(calls[0][1]) == 16 and len(calls[0][2]) == 16
    r2 = _run([sys.executable, "-B", "-m", "pytest", "-p", "p152_r3_call_recorder", "-p", "no:cacheprovider", "-q"],
              cwd=root, env_extra=env)                                       # output exists -> refuse
    assert r2.returncode != 0 and "exists" in (r2.stdout + r2.stderr)


def test_powershell_templates_are_isolated_and_never_use_live_cwd():
    text = (ROOT / "docs/refactor/work_orders/evidence/P15-R3-HARNESS-POWERSHELL-TEMPLATES-006.md").read_text(encoding="utf-8")
    assert "PYTHONDONTWRITEBYTECODE" in text and "--root" in text and "R3_ROOT" in text
    low = text.lower().replace("/", "\\")
    assert "set-location c:\\agentra\n" not in low and "set-location c:\\agentra`" not in low
    assert "set-location 'c:\\agentra'" not in low and 'set-location "c:\\agentra"' not in low
