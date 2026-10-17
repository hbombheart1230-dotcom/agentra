"""Reporter branch artefact hygiene check (P15-WORK-005 prevention).

Rejects OS/IDE/interpreter cache artefacts and unexpanded environment-variable path components (the R10-002 incident
committed four Windows cache files under a literal `%SystemDrive%/ProgramData/...` folder). Read-only: never rewrites
history; the one historical incident commit is listed explicitly and only for its exact four paths.

Usage:
  python scripts/refactor/work_reporter_hygiene_check.py --staged          # pre-commit: staged added/renamed paths
  python scripts/refactor/work_reporter_hygiene_check.py --range A..B      # every commit in range, added paths
  python scripts/refactor/work_reporter_hygiene_check.py --worktree        # untracked, non-ignored files
Exit 0 = clean, 1 = violations (printed one per line)."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Exact historical incident (removed from the tree in 359ef16; blobs remain reachable, NOT rewritten without approval).
KNOWN_HISTORICAL = {
    "c5d004b085690d1a5fa04aa6f607c55f399b76f1": frozenset({
        "%SystemDrive%/ProgramData/Microsoft/Windows/Caches/cversions.2.db",
        "%SystemDrive%/ProgramData/Microsoft/Windows/Caches/{0A9FE8E7-7F6D-43E9-9055-49CB0F1E68C2}.2.ver0x0000000000000001.db",
        "%SystemDrive%/ProgramData/Microsoft/Windows/Caches/{6AF0698E-D558-4F6E-9B3C-3716689AF493}.2.ver0x0000000000000001.db",
        "%SystemDrive%/ProgramData/Microsoft/Windows/Caches/{DDF571F2-BE98-426D-8288-1A9A39C3FDA2}.2.ver0x0000000000000001.db",
    }),
}

_ENV_COMPONENT = re.compile(r"%[A-Za-z_][A-Za-z0-9_()]*%|^\$[A-Za-z_{]|^\$env:|^~[A-Za-z0-9_]*$")
_BAD_COMPONENTS = {"programdata", "appdata", "$recycle.bin", "system volume information", "__pycache__",
                   ".pytest_cache", ".mypy_cache", ".ruff_cache", ".ipynb_checkpoints", ".idea", ".vs", "node_modules"}
_BAD_NAMES = {"thumbs.db", "ehthumbs.db", "ehthumbs_vista.db", "desktop.ini", ".ds_store", "pagefile.sys", "hiberfil.sys",
              "ntuser.dat", ".coverage", "pytest-of"}
_BAD_SUFFIXES = (".pyc", ".pyo", ".db", ".db-journal", ".sqlite", ".sqlite3", ".lnk", ".tmp", ".swp", ".etl", ".dmp")


def path_violation(path):
    """Return a reason string if `path` (repo-relative, '/' separated) is a forbidden artefact, else None."""
    parts = [p for p in path.replace("\\", "/").split("/") if p]
    if not parts:
        return None
    if Path(path).is_absolute() or re.match(r"^[A-Za-z]:", parts[0]):
        return "absolute path"
    for comp in parts:
        if _ENV_COMPONENT.search(comp):
            return f"unexpanded environment path component {comp!r}"
        if comp.lower() in _BAD_COMPONENTS:
            return f"OS/tool cache directory {comp!r}"
    name = parts[-1].lower()
    if name in _BAD_NAMES or name.startswith("~$"):
        return f"OS/editor artefact {parts[-1]!r}"
    if name.endswith(_BAD_SUFFIXES):
        return f"binary/cache suffix {parts[-1]!r}"
    return None


def violations(paths, *, commit=None):
    allowed = KNOWN_HISTORICAL.get(commit or "", frozenset())
    out = []
    for p in paths:
        reason = path_violation(p)
        if reason and p not in allowed:
            out.append(f"{commit[:12] + ' ' if commit else ''}{p}: {reason}")
    return out


def _git(*args):
    return subprocess.check_output(["git", "-c", "core.quotepath=off", *args], cwd=ROOT).decode("utf-8")


def _z(text):
    return [x for x in text.split("\0") if x]


def staged_paths():
    return _z(_git("diff", "--cached", "--name-only", "-z", "--diff-filter=ACR"))


def range_violations(rev_range):
    out = []
    for sha in _git("rev-list", "--no-merges", rev_range).split():
        added = _z(_git("diff-tree", "--no-commit-id", "-r", "--name-only", "-z", "--diff-filter=ACR", "--root", sha))
        out += violations(added, commit=sha)
    return out


def worktree_paths():
    return _z(_git("ls-files", "--others", "--exclude-standard", "-z"))


def main(argv):
    if argv[:1] == ["--staged"]:
        found = violations(staged_paths())
    elif argv[:1] == ["--range"] and len(argv) == 2:
        found = range_violations(argv[1])
    elif argv[:1] == ["--worktree"]:
        found = violations(worktree_paths())
    else:
        print(__doc__, file=sys.stderr)
        return 2
    for line in found:
        print(line)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
