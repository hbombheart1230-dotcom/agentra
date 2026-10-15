from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def _remove_tree(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    else:
        try:
            path.unlink()
        except OSError:
            pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Clean repo-local legacy pytest scratch artifacts.")
    parser.parse_args(argv)
    repo_root = Path(__file__).resolve().parents[1]
    keep = {
        repo_root / ".pytest-work",
        repo_root / ".pytest_cache",
    }
    patterns = [
        ".pytest-work-*",
        ".pytest-work-local*",
        "pytest-cache-files-*",
        "data/.pytest-work-*",
        "data/.pytest-work-local*",
        "data/pytest-cache-files-*",
    ]
    for pattern in patterns:
        for path in repo_root.glob(pattern):
            if path.resolve() in keep:
                continue
            _remove_tree(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
