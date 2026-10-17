"""Reporter R11 (P15-WORK-005): repository artefact hygiene, prevention only.

Every commit on the Reporter lane (activation START..HEAD) is checked path-by-path for OS/tool cache artefacts and
unexpanded environment-variable folders; the only tolerated hit is the exact, already-removed R10-002 incident
(c5d004b, four paths), which stays in history because a rewrite needs explicit owner approval. Negative cases prove the
checker rejects the incident shape and its common variants. The R10 subprocess helpers must keep a temp cwd and the
inherited environment (the root cause of the incident)."""
import ast
import importlib.util
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
START = "eeb742a33b16f6271ff364a904e187b470561c7e"  # Reporter activation commit (same origin as the scope test)
INCIDENT = "c5d004b085690d1a5fa04aa6f607c55f399b76f1"
_spec = importlib.util.spec_from_file_location("work_reporter_hygiene_check", ROOT / "scripts/refactor/work_reporter_hygiene_check.py")
hygiene = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hygiene)


def _git(*args):
    return subprocess.check_output(["git", "-c", "core.quotepath=off", *args], cwd=ROOT).decode("utf-8")


def _require(rev):
    if subprocess.run(["git", "cat-file", "-e", rev + "^{commit}"], cwd=ROOT).returncode != 0:
        raise AssertionError(f"{rev} not in this clone: fetch with full history (fetch-depth: 0)")


def test_every_reporter_lane_commit_adds_no_cache_or_env_artefact():
    _require(START)
    assert hygiene.range_violations(f"{START}..HEAD") == []


def test_head_tree_and_reporter_diff_contain_no_artefact():
    tracked = [p for p in _git("ls-files", "-z").split("\0") if p]
    lane = [p for p in _git("diff", "--name-only", "-z", START, "HEAD").split("\0") if p]
    assert [p for p in lane if hygiene.path_violation(p)] == []
    assert [p for p in tracked if "%" in p or p.lower().startswith(("programdata/", "appdata/"))] == []


def test_historical_incident_is_exactly_tolerated_and_not_in_head():
    """The incident is recorded, not rewritten: its four blobs are reachable only via c5d004b and absent at HEAD."""
    allowed = hygiene.KNOWN_HISTORICAL[INCIDENT]
    if subprocess.run(["git", "cat-file", "-e", INCIDENT + "^{commit}"], cwd=ROOT).returncode == 0:
        added = {p for p in _git("diff-tree", "--no-commit-id", "-r", "--name-only", "-z", "--diff-filter=A", INCIDENT).split("\0") if p}
        assert {p for p in added if hygiene.path_violation(p)} == allowed
    assert len(allowed) == 4 and all(hygiene.path_violation(p) for p in allowed)
    head = set(p for p in _git("ls-files", "-z").split("\0") if p)
    assert not (head & allowed)
    # the allowance is commit-bound: the same paths in any other commit are violations
    assert len(hygiene.violations(sorted(allowed), commit="0" * 40)) == 4
    assert len(hygiene.violations(sorted(allowed))) == 4


@pytest.mark.parametrize("bad", [
    "%SystemDrive%/ProgramData/Microsoft/Windows/Caches/cversions.2.db",
    "%LOCALAPPDATA%/Temp/x.txt",
    "$HOME/.cache/x",
    "$env:TEMP/x.json",
    "ProgramData/x.json",
    "tests/AppData/Local/x.json",
    "libs/agents/reporter/__pycache__/x.cpython-313.pyc",
    "libs/agents/reporter/narrative/x.pyc",
    ".pytest_cache/v/cache/nodeids",
    "docs/refactor/work_projects/evidence/reporter/Thumbs.db",
    "docs/desktop.ini",
    "docs/.DS_Store",
    "docs/~$draft.docx",
    "docs/refactor/x.sqlite3",
    "C:/Users/x/report.json",
    "tests/fixtures/work_reporter/shortcut.lnk",
])
def test_checker_rejects_incident_shape_and_variants(bad):
    assert hygiene.path_violation(bad), bad


@pytest.mark.parametrize("good", [
    "libs/agents/reporter/narrative/report_ai_bodies_01.py",
    "docs/refactor/work_projects/evidence/reporter/R10_CHECKPOINTS.md",
    "tests/fixtures/work_reporter/base_cases.json",
    "scripts/refactor/work_reporter_contract_runner.py",
    "docs/refactor/work_projects/evidence/reporter/proposed_patch_note.json",
])
def test_checker_accepts_normal_reporter_paths(good):
    assert hygiene.path_violation(good) is None


def test_staged_and_worktree_modes_run_on_a_scratch_repo(tmp_path):
    """End-to-end on a throwaway repo: staging a %SystemDrive% cache file is reported by --staged, a clean stage is not."""
    repo = tmp_path / "r"
    repo.mkdir()
    run = lambda *a: subprocess.run(["git", *a], cwd=repo, check=True, capture_output=True)  # noqa: E731
    run("init", "-q")
    (repo / "ok.py").write_text("x = 1\n", encoding="utf-8")
    bad = repo / "%SystemDrive%" / "ProgramData" / "Microsoft" / "Windows" / "Caches"
    bad.mkdir(parents=True)
    (bad / "cversions.2.db").write_bytes(b"\0" * 16)
    hygiene.ROOT = repo
    try:
        assert len(hygiene.violations(hygiene.worktree_paths())) == 1
        run("add", "ok.py")
        assert hygiene.violations(hygiene.staged_paths()) == []
        run("add", "-A")
        assert [v.split(":")[0] for v in hygiene.violations(hygiene.staged_paths())] == \
            ["%SystemDrive%/ProgramData/Microsoft/Windows/Caches/cversions.2.db"]
    finally:
        hygiene.ROOT = ROOT


REPORTER_TESTS = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "tests").glob("test_work_reporter_*.py"))


def test_interpreter_launching_reporter_tests_are_all_checked():
    launching = [f for f in REPORTER_TESTS if _interpreter_launches(ast.parse((ROOT / f).read_text(encoding="utf-8")))]
    assert {"tests/test_work_reporter_r10_retained_io_contracts.py", "tests/test_work_reporter_r10_artifact_parity.py",
            "tests/test_work_reporter_seed_migration.py"} <= set(launching)


def _interpreter_launches(tree):
    return [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr in ("run", "check_output", "check_call", "call", "Popen") and n.args
            and isinstance(n.args[0], ast.List) and n.args[0].elts
            and ast.unparse(n.args[0].elts[0]) == "sys.executable"]


@pytest.mark.parametrize("test_file", REPORTER_TESTS)
def test_subprocess_helpers_use_temp_cwd_and_inherited_environment(test_file):
    """Root cause of the incident: a child interpreter with cwd=repo and a stripped env (no SystemDrive) made Windows
    create a literal %SystemDrive% folder. Every interpreter launch in a Reporter test must pass an explicit cwd that is
    not the repository, and any explicit env must be built from os.environ."""
    tree = ast.parse((ROOT / test_file).read_text(encoding="utf-8"))
    for call in _interpreter_launches(tree):
        kw = {k.arg: ast.unparse(k.value) for k in call.keywords}
        assert "cwd" in kw and "ROOT" not in kw["cwd"], (test_file, call.lineno, kw.get("cwd"))
        if "env" in kw:
            env = kw["env"]
            sources = [ast.unparse(a.value) for a in ast.walk(tree) if isinstance(a, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == env for t in a.targets)] if env.isidentifier() else [env]
            assert sources and all("environ" in s for s in sources), (test_file, call.lineno, sources)
