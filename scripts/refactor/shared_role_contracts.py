"""Pinned Reporter/Monitor integration proof; static, exact and fail-closed under -O."""
import ast
import json
import subprocess
from pathlib import Path
from functools import lru_cache

import reporter_facade_guard as R
import work_monitor_current_tree as M
from scripts.refactor import shared_strategist_contracts as S5

ROOT = Path(__file__).resolve().parents[2]
BASE = R.BASE
REPORTER = R.REVIEWED
MONITOR = "4bc4250844093050438d8a9c29f5842991ad1c3a"
LEDGER = "docs/refactor/work_projects/evidence/monitor/path_ledger.json"


def require(value, message):
    if not value:
        raise AssertionError(message)


@lru_cache(maxsize=None)
def git_text(sha, path):
    return subprocess.check_output(["git", "show", sha + ":" + path], cwd=ROOT).decode("utf-8-sig").replace("\r\n", "\n")


@lru_cache(maxsize=None)
def whole_moves():
    pinned = json.loads(git_text(MONITOR, LEDGER))
    pairs = {r["source"]: r["destination"] for r in pinned["maps"]} | M.WHOLE_MOVES
    require(len(pairs) == 14 and len(set(pairs.values())) == 14, "Monitor 14 exact pairs")
    return pairs


def source(path, overrides=None):
    overrides = overrides or {}
    read = lambda p: overrides[p] if p in overrides else (ROOT / p).read_text(encoding="utf-8-sig")
    current = read(path)
    pairs = whole_moves()
    if path in pairs:
        target = pairs[path]
        body = M._tree(current).body
        if body and R.docstring(body[0]):
            body = body[1:]
        require(R.dump(ast.Module(body=body, type_ignores=[])) == R.dump(ast.parse(M.shim_source(path, target))),
                "nonexact identity shim: " + path)
        require(read(target) == git_text(BASE, path), "changed canonical body: " + target)
        return read(target)
    if path in M.BODY_MOVES:
        return M.verify_body_transfer(path, current, read(M.BODY_MOVES[path]["owner"]))
    return current


def follow(path):
    pairs = whole_moves()
    if path in pairs:
        source(path)
        return pairs[path]
    return path


@lru_cache(maxsize=None)
def role_paths(sha):
    paths = subprocess.check_output(["git", "diff", "--name-only", BASE, sha, "--", "libs", "graphs", "apps"], cwd=ROOT, text=True).splitlines()
    return set(paths)


def verify_runtime(overrides=None):
    """No arbitrary path allowlist: all runtime deltas must equal an immutable input."""
    overrides = overrides or {}
    reporter, monitor = role_paths(REPORTER), role_paths(MONITOR)
    require(not reporter & monitor, "ambiguous runtime overlap")
    strategist = S5.current_contract(overrides)["runtime_paths"]
    require(not (reporter | monitor) & strategist, "ambiguous S5 runtime overlap")
    actual = set(subprocess.check_output(["git", "diff", "--name-only", BASE, "--", "libs", "graphs", "apps"], cwd=ROOT, text=True).splitlines())
    actual |= set(subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard", "--", "libs", "graphs", "apps"], cwd=ROOT, text=True).splitlines())
    actual |= {p for p in overrides if p.startswith(("libs/", "graphs/", "apps/"))}
    expected = reporter | monitor | strategist
    require(actual == expected, "unexpected/missing runtime path: " + repr(actual ^ expected))
    for sha, paths in ((REPORTER, reporter), (MONITOR, monitor), (S5.CANDIDATE_CODE, strategist)):
        for path in sorted(paths):
            current = overrides.get(path)
            if current is None:
                current = (ROOT / path).read_text(encoding="utf-8-sig")
            require(current == git_text(sha, path), "unapproved runtime body/import/authority: " + path)
    # Include untracked files: Git diff alone cannot see a new Broker capability.
    for role, sha, allowed in (("reporter", REPORTER, {"narrative", "read_models"}),
                               ("monitor", MONITOR, {"events", "projections"})):
        prefix = "libs/agents/" + role
        pinned = set(subprocess.check_output(["git", "ls-tree", "-r", "--name-only", sha, "--", prefix], cwd=ROOT, text=True).splitlines())
        disk = {p.relative_to(ROOT).as_posix() for p in (ROOT / prefix).rglob("*.py")}
        disk |= {p for p in overrides if p.startswith(prefix + "/")}
        require(disk == pinned, "agent package file inventory differs: " + repr(disk ^ pinned))
        require(all(len(Path(p).parts) == 4 and Path(p).name == "__init__.py" or Path(p).parts[3] in allowed
                    for p in disk), "agent package capability")
    result = R.verify_tree(ROOT, overrides=overrides, reviewed=REPORTER)
    for path in whole_moves() | M.BODY_MOVES:
        source(path, overrides)
    require(len(M.BODY_MOVES) == 8 and sum(len(x["functions"]) for x in M.BODY_MOVES.values()) == 20, "Monitor 20 bodies")
    return result | {"monitor_modules": 14, "monitor_bodies": 20}
