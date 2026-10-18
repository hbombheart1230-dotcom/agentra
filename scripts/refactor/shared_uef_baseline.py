"""Reproduce the unchanged UEF9 gate from frozen BASE in an external clean archive."""
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BASE = "d773709ba2f70471fad9badba4f92400f7818319"


def main():
    subprocess.run(["git", "check-ignore", "-q", ".agentra-worktmp/probe"], cwd=ROOT, check=True)
    scratch = ROOT / ".agentra-worktmp"
    scratch.mkdir(exist_ok=True)
    if scratch.is_symlink() or not scratch.resolve().is_relative_to(ROOT.resolve()):
        raise SystemExit("Untrusted scratch root")
    output = Path(tempfile.mkdtemp(prefix="uef-baseline-", dir=scratch))
    tree = output / "tree"
    tree.mkdir()
    raw = subprocess.check_output(["git", "archive", BASE], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as archive:
        archive.extractall(tree, filter="data")
    temporary = output / "temporary"
    temporary.mkdir()
    env = dict(os.environ, TEMP=str(temporary), TMP=str(temporary), TMPDIR=str(temporary),
               DRY_RUN="1", TRADING_MODE="mock", PYTHONDONTWRITEBYTECODE="1")
    for key in ("TRADING_AGENT_PYTEST_ROOT", "TRADING_AGENT_PYTEST"):
        env.pop(key, None)
    command = [sys.executable, "-m", "pytest", "-q", "--tb=short", "-p", "no:cacheprovider",
               "tests/test_uef9_formal_authority.py", "--junitxml=" + str(output / "baseline.xml")]
    print("OUTPUT=" + str(output), flush=True)
    result = subprocess.run(command, cwd=tree, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    (output / "stdout.txt").write_text(result.stdout + result.stderr, encoding="utf-8")
    summary = {"base": BASE, "python": sys.version, "command": command, "exit": result.returncode,
               "fixture_policy": "Unmodified frozen Git archive; no production reports copied or fabricated."}
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(result.stdout, flush=True)
    print(json.dumps(summary), flush=True)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
