"""Versioned ownership allowlist of the HYBRID-7 V3 agent packages created by the migration batches.

A new package may appear ONLY by adding an entry here together with the batch's own contract test; the per-batch
discipline tests compare the actual directory set for equality (no unrestricted subset), so a stray package fails."""
from scripts.refactor import shared_strategist_contracts as S

AGENT_PACKAGES = {"scanner": "V1-052", "strategist": "S1-057", "reporter": "R11", "monitor": "M9"}
REPORTER_PACKAGES = {"narrative": "R11", "read_models": "R11"}
MONITOR_PACKAGES = {"events": "M9", "projections": "M9"}
SCANNER_PACKAGES = {"context": "V2-053", "projections": "V3-055", "policy": "V4-056"}
STRATEGIST_PACKAGES = {"context": "S1-057", "output": "S1-057"}
COMMANDER_FILES = frozenset({
    "__init__.py", "projections/__init__.py",
    "projections/decision_context_read_model.py", "projections/cache_refresh_read_model.py",
})
if S.b_composed_selected():
    AGENT_PACKAGES = {**AGENT_PACKAGES, "commander": "Commander-Pure-V1"}


def verify_commander_tree(path):
    entries = [p for p in path.rglob("*") if "__pycache__" not in p.relative_to(path).parts]
    S.require(not path.is_symlink() and not any(p.is_symlink() for p in entries), "Commander tree symlink")
    files = {p.relative_to(path).as_posix() for p in entries if p.is_file()}
    dirs = {p.relative_to(path).as_posix() for p in entries if p.is_dir()}
    S.require(files == COMMANDER_FILES and dirs == {"projections"}, "Commander exact package inventory")
    for name in COMMANDER_FILES:
        S.require((path / name).read_text(encoding="utf-8-sig") ==
                  S.git_source(S.B_COMPOSED_BRIEF, "libs/agents/commander/" + name),
                  "Commander source differs from approved pin: " + name)


def actual_dirs(path):
    if path.name == "agents" and (path / "commander").exists():
        verify_commander_tree(path / "commander")
    return {p.name for p in path.iterdir() if p.is_dir() and p.name != "__pycache__"}
