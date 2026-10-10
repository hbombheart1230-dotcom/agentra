"""Read-only pre/post P1.5.2 saved-report snapshot parity.

Compare independent FROZEN copies, never use live reports or execute trading/LLM
code. Refuse empty inputs, symlinks, same root, or evidence output inside either
input root. JSON semantic equality is diagnostic, NOT a byte-equality waiver.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

REPORT_EXTENSIONS = {".json", ".jsonl", ".md"}
JSON_PARSE_CAP = 4 * 1024 * 1024


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _relative_files(root: Path, *, max_files: int) -> dict[str, Path]:
    files = {}
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Symlink forbidden in snapshot: {path}")
        if path.is_file() and path.suffix.lower() in REPORT_EXTENSIONS:
            rel = path.relative_to(root).as_posix()
            files[rel] = path
            if len(files) > max_files:
                raise ValueError(f"Too many snapshot files; cap={max_files}")
    if not files:
        raise ValueError(f"No JSON/JSONL/Markdown files in snapshot root: {root}")
    return files


def _json_semantic(raw: bytes, suffix: str) -> str | None:
    if len(raw) > JSON_PARSE_CAP:
        return None
    try:
        text = raw.decode("utf-8-sig")
        if suffix.lower() == ".jsonl":
            data = [json.loads(line) for line in text.splitlines() if line.strip()]
        else:
            data = json.loads(text)
        return sha256(json.dumps(data, ensure_ascii=False, sort_keys=True,
                                 separators=(",", ":")).encode("utf-8"))
    except (UnicodeError, ValueError, TypeError):
        return None


def _manifest(files: dict[str, Path]) -> dict[str, dict]:
    result = {}
    for rel, path in sorted(files.items()):
        raw = path.read_bytes()
        result[rel] = {
            "sha256": sha256(raw),
            "byte_count": len(raw),
            "canonical_json_sha256": (
                _json_semantic(raw, path.suffix) if path.suffix.lower() in {".json", ".jsonl"} else None
            ),
        }
    return result


def compare_snapshots(
    before: Path, after: Path, *,
    out: Path | None = None,
    llm_relative_path: str | None = None,
    max_files: int = 10000,
    before_sha: str = "",
    after_sha: str = "",
) -> dict:
    before, after = before.resolve(strict=True), after.resolve(strict=True)
    if not before.is_dir() or not after.is_dir() or before == after:
        raise ValueError("Require two distinct existing FROZEN snapshot directories")
    if max_files < 1:
        raise ValueError("max_files must be positive")
    if before_sha and not re.fullmatch(r"[0-9a-f]{40}", before_sha):
        raise ValueError("before_sha must be a 40-character lowercase git SHA")
    if after_sha and not re.fullmatch(r"[0-9a-f]{40}", after_sha):
        raise ValueError("after_sha must be a 40-character lowercase git SHA")
    if out is not None:
        target = out.resolve()
        if target == before or target == after or before in target.parents or after in target.parents:
            raise ValueError("Evidence output must be OUTSIDE both immutable snapshot roots")
    a = _manifest(_relative_files(before, max_files=max_files))
    b = _manifest(_relative_files(after, max_files=max_files))
    keys = sorted(a.keys() | b.keys())
    differences = []
    for rel in keys:
        left, right = a.get(rel), b.get(rel)
        if left == right:
            continue
        if left is None:
            kind = "ADDED"
        elif right is None:
            kind = "MISSING"
        elif left["sha256"] == right["sha256"]:
            continue
        elif (
            left["canonical_json_sha256"] is not None
            and left["canonical_json_sha256"] == right["canonical_json_sha256"]
        ):
            kind = "BYTE_FORMAT_ONLY"
        else:
            kind = "CONTENT_OR_SEMANTIC_DRIFT"
        # No secrets, private prompt bodies or trade payloads included.
        differences.append({
            "relative_path": rel,
            "kind": kind,
            "before_sha256": left["sha256"] if left else None,
            "after_sha256": right["sha256"] if right else None,
        })
    if llm_relative_path:
        candidate = Path(llm_relative_path)
        if (
            candidate.is_absolute() or ".." in candidate.parts
            or candidate.as_posix() not in a or candidate.as_posix() not in b
            or candidate.suffix.lower() not in {".json", ".jsonl"}
        ):
            raise ValueError("--llm-relative-path must identify one JSON/JSONL file in BOTH frozen roots")
        llm = {
            "relative_path": candidate.as_posix(),
            "capture_present": True,
            "byte_equal": a[candidate.as_posix()]["sha256"] == b[candidate.as_posix()]["sha256"],
            "json_semantic_equal": (
                a[candidate.as_posix()]["canonical_json_sha256"] is not None
                and a[candidate.as_posix()]["canonical_json_sha256"]
                == b[candidate.as_posix()]["canonical_json_sha256"]
            ),
            "external_llm_invoked": False,
        }
    else:
        llm = {"capture_present": False, "status": "NOT_RUN_NO_CAPTURE"}
    result = {
        "schema": "p152_saved_snapshot_parity.v1",
        "evidence_scope": "FROZEN_SAVED_FILES_ONLY_NOT_LIVE_ENVIRONMENT",
        "baseline_commit_sha": before_sha or "UNVERIFIED",
        "candidate_commit_sha": after_sha or "UNVERIFIED",
        "before_file_count": len(a),
        "after_file_count": len(b),
        "compared_path_count": len(keys),
        "difference_count": len(differences),
        "differences": differences,
        "llm_capture": llm,
        "byte_parity": "PASS" if not differences else "FAIL",
        "local_actual_snapshot_provenance": "REQUIRES_INDEPENDENT_LOCAL_VALIDATION",
        "authorizes_p152_completion": False,
        "authorizes_p153": False,
    }
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True, type=Path, help="frozen original report COPY root")
    parser.add_argument("--after", required=True, type=Path, help="frozen refactored report COPY root")
    parser.add_argument("--out", required=True, type=Path, help="evidence JSON OUTSIDE both roots")
    parser.add_argument("--llm-relative-path", help="optional saved prompt/call trace JSON relative to both roots")
    parser.add_argument("--before-sha", default="")
    parser.add_argument("--after-sha", default="")
    parser.add_argument("--max-files", type=int, default=10000)
    args = parser.parse_args()
    try:
        result = compare_snapshots(
            args.before, args.after, out=args.out,
            llm_relative_path=args.llm_relative_path,
            max_files=args.max_files, before_sha=args.before_sha, after_sha=args.after_sha,
        )
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(
        f"P1.5.2 SAVED SNAPSHOT byte parity {result['byte_parity']}: "
        f"{result['compared_path_count']} paths, {result['difference_count']} differences; "
        f"LLM capture={'present' if result['llm_capture'].get('capture_present') else 'NOT RUN'}"
    )
    return 0 if result["byte_parity"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
