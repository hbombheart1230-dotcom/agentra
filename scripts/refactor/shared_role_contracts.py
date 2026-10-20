"""Pinned Reporter/Monitor integration proof; static, exact and fail-closed under -O."""
import ast
import copy
import hashlib
import json
import subprocess
import types
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


@lru_cache(maxsize=None)
def _pinned_guard(sha):
    """Execute only an immutable, reviewed static checker, never A runtime.

    Both versions import stdlib only. The actual current A guard is checked
    against this exact Git source before this proof is selected.
    """
    require(sha in {S5.A_PRE_SOURCE, S5.A_SOURCE}, "unapproved Reporter proof SHA")
    module = types.ModuleType("_agentra_reporter_proof_" + sha)
    module.__file__ = str(ROOT / S5.A_GUARD)
    exec(compile(git_text(sha, S5.A_GUARD), "<pinned Reporter proof " + sha + ">", "exec"), module.__dict__)
    return module


def reporter_inventory(overrides=None):
    """Strict old package inventory plus exactly one verified A Owner."""
    overrides = overrides or {}
    active = S5.verify_a_sources(overrides)
    prefix = "libs/agents/reporter/"
    pinned = set(subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", REPORTER, "--", prefix], cwd=ROOT, text=True).splitlines())
    expected = pinned | ({S5.A_OWNER} if active else set())
    actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / prefix).rglob("*.py")}
    actual |= {p for p in overrides if p.startswith(prefix)}
    require(actual == expected, "Reporter package inventory differs: " + repr(actual ^ expected))
    return frozenset(expected)


def verify_historical_reporter(overrides=None):
    """Original R7 inventory and 313 bodies on immutable historical inputs."""
    overrides = overrides or {}
    paths = role_paths(REPORTER)
    require(set(overrides) <= paths | {S5.A_GUARD},
            "historical Reporter unapproved path: " + repr(set(overrides) - paths - {S5.A_GUARD}))
    historical = {}
    for path in sorted(paths):
        pinned = git_text(REPORTER, path)
        current = overrides.get(path, pinned)
        require(current.replace("\r\n", "\n") == pinned, "historical Reporter source differs: " + path)
        historical[path] = current
    if S5.A_GUARD in overrides:
        require(overrides[S5.A_GUARD].replace("\r\n", "\n") == git_text(S5.A_PRE_SOURCE, S5.A_GUARD),
                "historical Reporter guard differs: " + S5.A_GUARD)
    return _pinned_guard(S5.A_PRE_SOURCE).verify_tree(ROOT, overrides=historical, reviewed=REPORTER)


def _portable_a_transitions(proof):
    """Current-stage digest from immutable Git AST, not the candidate input.

    ast.dump's empty-list serialization changed in Python 3.13. Preserve the
    reviewed guard/default literal unchanged; its explicit transition argument
    can represent the SAME pinned function in the host interpreter's format.
    Full facade/Owner/guard source pins still precede every invocation.
    """
    transitions = copy.deepcopy(proof.P15_TRANSITIONS)
    require(set(transitions) == {S5.A_FACADE}, "A-stage exact transition inventory")
    spec = transitions[S5.A_FACADE]
    require(spec["function"] == "generate_reporter_analysis_report", "A-stage exact function")
    reference = next(n for n in ast.parse(git_text(S5.A_SOURCE, S5.A_FACADE)).body
                     if isinstance(n, ast.FunctionDef) and n.name == spec["function"])
    spec["function_ast_sha256"] = hashlib.sha256(proof.dump(reference).encode("utf-8")).hexdigest()
    return transitions


def reporter_stage(overrides=None):
    """Prove A's exact transition then run original R7 on restored inputs."""
    overrides = overrides or {}
    active = S5.verify_a_sources(overrides)
    reporter_inventory(overrides)
    restored = dict(overrides)
    if active:
        proof = _pinned_guard(S5.A_SOURCE)
        transitions = _portable_a_transitions(proof)
        current = overrides.get(S5.A_FACADE, (ROOT / S5.A_FACADE).read_text(encoding="utf-8-sig"))
        headers = []
        for text in (git_text(REPORTER, S5.A_FACADE), current):
            fn = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)
                      and n.name == "generate_reporter_analysis_report")
            fn.body = []
            headers.append(R.dump(fn))
        require(headers[0] == headers[1], "A-stage facade ABI changed: " + S5.A_FACADE)
        tree = proof.revert_p15_transition(git_text(BASE, S5.A_FACADE), current, S5.A_FACADE,
                                          transitions=transitions)
        require(R.dump(tree) == R.dump(ast.parse(git_text(REPORTER, S5.A_FACADE))),
                "A-stage restored historical facade differs: " + S5.A_FACADE)
        # The exact current-stage proof also checks the pinned new Owner and
        # all 313 existing wrappers on the ACTUAL composed facade inputs.
        proof.verify_tree(ROOT, overrides=overrides, reviewed=REPORTER, transitions=transitions)
        restored[S5.A_FACADE] = ast.unparse(tree)
    result = _pinned_guard(S5.A_PRE_SOURCE).verify_tree(ROOT, overrides=restored, reviewed=REPORTER)
    # Use old bytes in runtime comparisons only after the entire restoration
    # above has succeeded. No changed unselected function/import can hide here.
    if active:
        restored[S5.A_FACADE] = git_text(REPORTER, S5.A_FACADE)
    return result, restored, bool(active)


def verify_runtime(overrides=None):
    """No arbitrary path allowlist: all runtime deltas must equal an immutable input."""
    overrides = overrides or {}
    S5.verify_b_scope({p: value for p, value in overrides.items()
                       if p in S5.A_STAGE_PATHS or not p.startswith(("libs/", "graphs/", "apps/"))})
    active_a = bool(S5.verify_a_sources(overrides))
    reporter, monitor = role_paths(REPORTER), role_paths(MONITOR)
    require(not reporter & monitor, "ambiguous runtime overlap")
    strategist = S5.current_contract(overrides)["runtime_paths"]
    require(not (reporter | monitor) & strategist, "ambiguous S5 runtime overlap")
    S5.verify_next_stage(overrides)
    actual = set(subprocess.check_output(["git", "diff", "--name-only", BASE, "--", "libs", "graphs", "apps"], cwd=ROOT, text=True).splitlines())
    actual |= set(subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard", "--", "libs", "graphs", "apps"], cwd=ROOT, text=True).splitlines())
    actual |= {p for p in overrides if p.startswith(("libs/", "graphs/", "apps/"))}
    # B's three Owners are admitted only by their exact reviewed content. The
    # historical Reporter/Monitor/Strategist inputs and inventories stay fixed.
    expected = reporter | monitor | strategist | set(S5.NEXT_RUNTIME) | S5.B_RUNTIME | ({S5.A_OWNER} if active_a else set())
    require(actual == expected, "unexpected/missing runtime path: " + repr(actual ^ expected))
    result, projected, active_a = reporter_stage(overrides)
    for sha, paths in ((REPORTER, reporter), (MONITOR, monitor), (S5.CANDIDATE_CODE, strategist)):
        for path in sorted(paths):
            current = projected.get(path)
            if current is None:
                current = S5.historical_source(path)
            require(current == git_text(sha, path), "unapproved runtime body/import/authority: " + path)
    # Include untracked files: Git diff alone cannot see a new Broker capability.
    for role, sha, allowed in (("reporter", REPORTER, {"narrative", "read_models"}),
                               ("monitor", MONITOR, {"events", "projections"})):
        prefix = "libs/agents/" + role
        pinned = set(subprocess.check_output(["git", "ls-tree", "-r", "--name-only", sha, "--", prefix], cwd=ROOT, text=True).splitlines())
        disk = {p.relative_to(ROOT).as_posix() for p in (ROOT / prefix).rglob("*.py")}
        disk |= {p for p in overrides if p.startswith(prefix + "/")}
        if role == "reporter" and active_a:
            pinned.add(S5.A_OWNER)
        require(disk == pinned, "agent package file inventory differs: " + repr(disk ^ pinned))
        require(all(len(Path(p).parts) == 4 and Path(p).name == "__init__.py" or Path(p).parts[3] in allowed
                    for p in disk), "agent package capability")
    for path in whole_moves() | M.BODY_MOVES:
        source(path, overrides)
    require(len(M.BODY_MOVES) == 8 and sum(len(x["functions"]) for x in M.BODY_MOVES.values()) == 20, "Monitor 20 bodies")
    return result | {"monitor_modules": 14, "monitor_bodies": 20, "reporter_a": active_a}
