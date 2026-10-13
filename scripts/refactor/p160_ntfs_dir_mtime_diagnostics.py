"""T3-0.3 NTFS directory-mtime diagnostics (P2, UNRESOLVED). Facts only - this module never tolerates a change.

  probe             sample directory mtimes of the checkout under data/ at several instants with BOTH os.lstat and
                    scandir DirEntry.stat and print/write a JSON record
  summarize-settle  turn the log + exit code of the throw-away settle session into a JSON record (did the FIRST audited
                    session of a fresh checkout report MODIFIED directory entries?)

Both emit a `::notice` workflow annotation when GITHUB_ACTIONS is set so the record is readable without log access.
Neither modifies the repository, conftest.py or sitecustomize.py."""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WATCH = ("data",)


def _dir_views(root: Path) -> dict:
    out = {}
    for top in WATCH:
        base = root / top
        if not base.is_dir():
            continue
        stack = [base]
        while stack:
            cur = stack.pop()
            out[os.path.relpath(cur, root).replace("\\", "/")] = {"lstat": os.lstat(cur).st_mtime_ns, "direntry": None}
            with os.scandir(cur) as it:
                for e in it:
                    if e.is_dir(follow_symlinks=False):
                        rel = os.path.relpath(e.path, root).replace("\\", "/")
                        out.setdefault(rel, {"lstat": None, "direntry": None})["direntry"] = e.stat(
                            follow_symlinks=False).st_mtime_ns
                        stack.append(Path(e.path))
    return out


def probe(delays=(0.0, 0.2, 1.0, 5.0)) -> dict:
    samples = []
    for d in delays:
        time.sleep(d)
        samples.append({"after_s": d, "dirs": _dir_views(ROOT)})
    first = samples[0]["dirs"]
    changed = {}
    for s in samples[1:]:
        for rel, v in s["dirs"].items():
            f = first.get(rel)
            if f is None:
                continue
            for api in ("lstat", "direntry"):
                if v[api] is not None and f[api] is not None and v[api] != f[api]:
                    changed.setdefault(rel, []).append({"api": api, "after_s": s["after_s"], "delta_ns": v[api] - f[api]})
    mismatch = sorted(rel for rel, v in samples[-1]["dirs"].items()
                      if v["lstat"] is not None and v["direntry"] is not None and v["lstat"] != v["direntry"])
    return {"kind": "ntfs_dir_mtime_probe", "platform": sys.platform, "python": sys.version.split()[0],
            "directories": len(first), "changed_between_samples": changed,
            "lstat_vs_direntry_mismatch": mismatch, "reproduced": bool(changed or mismatch),
            "status": "UNRESOLVED", "note": "diagnostic only; no tolerance is derived from this record"}


_MODIFIED = re.compile(r"^\s*MODIFIED\s+(\S+)\s+size=(-?\d+)->(-?\d+)\s+mtime_ns=(\d+)->(\d+)", re.M)


def summarize_settle(log_path: str, rc: int) -> dict:
    text = Path(log_path).read_text(encoding="utf-8", errors="replace") if Path(log_path).is_file() else ""
    rows = [{"path": p, "size_before": int(a), "size_after": int(b), "mtime_delta_ns": int(m2) - int(m1)}
            for p, a, b, m1, m2 in _MODIFIED.findall(text)]
    return {"kind": "ntfs_settle_session_summary", "first_session_exit_code": rc,
            "banner_present": "PRODUCTION PATH WRITE DETECTED" in text,
            "modified_entries": rows, "directory_only": all(r["size_before"] == -1 for r in rows),
            "status": "UNRESOLVED", "note": "causality not established; the settle session is a workaround, not a fix"}


def _emit(record: dict, out_path: str | None, title: str) -> None:
    text = json.dumps(record, indent=1, sort_keys=True)
    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        Path(out_path).write_text(text, encoding="utf-8")
    print(text)
    if os.environ.get("GITHUB_ACTIONS"):
        flat = json.dumps(record, sort_keys=True)[:6000].replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        print(f"::notice title={title}::{flat}")


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in ("probe", "summarize-settle"):
        print(__doc__)
        return 2
    out = argv[argv.index("--out") + 1] if "--out" in argv else None
    if argv[0] == "probe":
        _emit(probe(), out, "ntfs-dir-mtime-probe")
    else:
        _emit(summarize_settle(argv[1], int(argv[2])), out, "ntfs-settle-summary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
