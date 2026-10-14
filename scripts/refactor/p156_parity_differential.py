"""P1.5 Second Pass parity-evidence harness: isolated-session baseline/feature call differential (harness only).

Isolation contract: every run (BASE#n / FEATURE#n) gets its OWN clone ("session root") created under --work-root
(outside the audited repository), its own TEMP/TMP, its own recorder log and stdout file; nothing is shared between
runs, so concurrent runs cannot interfere through cwd-relative ``data/``/``reports``/SQLite/ledger paths. The scrubbed
environment contains no credentials. Production writes are checked by listing every session root's untracked/modified
files after the run (writes land only inside the disposable session root).

    python scripts/refactor/p156_parity_differential.py --repo <clone> --baseline-sha <sha> --feature-sha <sha> \
        --names <names.json> --tests <tests.txt> --work-root <empty dir outside repo> --out-dir <new dir> \
        --mode det|natural [--sequential] [--keep-sessions]

The comparator keeps everything byte-exact except fields on an explicit, justified allowlist (see TOLERANCE_RULES);
ranking / risk / intent / quantity / price / authority fields are never tolerance-eligible.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = os.environ.get("P156_PYTHON") or sys.executable
LIVE_ROOT = r"C:\Agentra"

# --------------------------------------------------------------------------------------------------------------------
# Comparator
# --------------------------------------------------------------------------------------------------------------------
# Field-level, justified tolerance rules. A rule applies only to a diff leaf whose path ends with one of `keys` AND whose
# values satisfy `check`. Anything else is a REAL difference. No rule covers ranking, score, risk, intent, side,
# quantity, price, authority, approval or order fields.
_HEX_ID = re.compile(r"^'?(?:[a-z_]+_)?[0-9a-f]{12,64}'?$")
_MTIME_SIG = re.compile(r":\d{15,19}:")


def _num(x):
    try:
        return float(str(x).strip("'"))
    except Exception:
        return None


def _chk_run_id(u, v):
    return bool(_HEX_ID.match(str(u))) and bool(_HEX_ID.match(str(v)))


_MEMORY_ID = re.compile(r"^'?memory_[0-9a-f]{20}'?$")


def _chk_memory_id(u, v):
    return bool(_MEMORY_ID.match(str(u))) and bool(_MEMORY_ID.match(str(v)))


def _chk_mtime_signature(u, v):
    return _MTIME_SIG.sub(":#:", str(u)) == _MTIME_SIG.sub(":#:", str(v))


def _chk_small_age(u, v):
    a, b = _num(u), _num(v)
    return a is not None and b is not None and abs(a - b) <= 2.0


TOLERANCE_RULES = {
    "R-ID": {"keys": ("run_id", "request_id", "trace_id", "event_id"),
             "check": _chk_run_id,
             "why": "randomly generated identifier (uuid/hex) that embeds no market or decision value; the generic key "
                    "'strategy' is NOT eligible (only memory-packet ids under an explicit packet-id container, see "
                    "R-MEMORY-PACKET-ID)"},
    "R-MEMORY-PACKET-ID": {"keys": ("packet_id",), "check": lambda u, v: _chk_memory_id(u, v),
                           "why": "content hash id of a memory packet whose payload embeds the session temp path "
                                  "(<pid>-<uuid>); valid only as memory_<20 hex> on BOTH sides, as leaf `packet_id` or "
                                  "under an explicit packet-id container"},
    "R-MTIME": {"keys": ("source_signature",), "check": _chk_mtime_signature,
                "why": "artifact signature embeds the file mtime_ns of a fixture written by the test itself"},
    "R-MTIME-DERIVED": {"keys": (), "check": lambda u, v: False,
                        "why": "hash of an LLM prompt/response artifact whose prompt embeds the same record's "
                               "source_signature (file mtime_ns); applies only when that signature differs in the same record"},
    "R-AGE": {"keys": ("minutes_since_open", "minute_snapshot_age_minutes", "quote_age_sec",
                       "expected_exit_quote_age_sec", "age_sec"), "check": _chk_small_age,
              "why": "wall-clock derived age (<=2 units) between two processes started at different instants"},
}


def _leaf_key(path):
    for p in reversed(path):
        if isinstance(p, str):
            return p.strip("'")
    return ""


def _walk(x, y, path, out):
    if isinstance(x, dict) and isinstance(y, dict) and len(x) == 1 == len(y) and "d" in x and "d" in y:
        dx = {k: v for k, v in x["d"]}
        dy = {k: v for k, v in y["d"]}
        for k in sorted(set(dx) | set(dy)):
            if k not in dx or k not in dy:
                out.append((path + [k], dx.get(k, "<absent>"), dy.get(k, "<absent>")))
            elif dx[k] != dy[k]:
                _walk(dx[k], dy[k], path + [k], out)
        return
    if isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
        for i, (p, q) in enumerate(zip(x, y)):
            if p != q:
                _walk(p, q, path + [i], out)
        return
    out.append((path, x, y))


_ID_CONTAINERS = ("packet_ids", "layer_packet_ids", "applied_packet_ids")
# fields whose value is a pure function of a prompt/response that embeds the artifact mtime signature
_MTIME_DERIVED_KEYS = ("prompt_hash", "response_hash")


def _justify(path, u, v, record_has_mtime_diff=False):
    key = _leaf_key(path)
    strs = [p.strip("'") for p in path if isinstance(p, str)]
    for rid, rule in TOLERANCE_RULES.items():
        if key in rule["keys"] and rule["check"](u, v):
            return rid
    # memory packet ids per layer/strategy: only directly under an explicit packet-id container, memory_<20 hex> both sides
    if len(strs) >= 2 and strs[-2] in _ID_CONTAINERS and _chk_memory_id(u, v):
        return "R-MEMORY-PACKET-ID"
    if record_has_mtime_diff and key in _MTIME_DERIVED_KEYS and _chk_run_id(u, v):
        return "R-MTIME-DERIVED"
    return None


def _diffs(rec_a, rec_b):
    """List of (path, a, b) leaf differences from KEEP payloads; None when no payload is available."""
    if len(rec_a) > 4 and len(rec_b) > 4 and isinstance(rec_a[4], str) and isinstance(rec_b[4], str):
        out = []
        _walk(json.loads(rec_a[4]), json.loads(rec_b[4]), [], out)
        return out
    return None


def compare(runs):
    """runs: {'b1','b2','f1','f2' -> loaded recorder log}. Returns (summary, details)."""
    keys = set()
    for r in runs.values():
        keys |= set(r["calls"])
    per_function = {}
    cls_total = {"BYTE_IDENTICAL": 0, "JUSTIFIED_TOLERANCE": 0, "REAL_MISMATCH": 0, "UNRESOLVED": 0}
    details = []
    outcome_equal = all(runs["b1"]["outcomes"] == runs[k]["outcomes"] for k in runs if k != "b1")
    for k in sorted(keys):
        seqs = {n: runs[n]["calls"].get(k, []) for n in runs}
        n_calls = max(len(s) for s in seqs.values())
        for i in range(n_calls):
            recs = {n: (s[i] if i < len(s) else None) for n, s in seqs.items()}
            fname = next((r[0] for r in recs.values() if r), "?")
            slot = per_function.setdefault(fname, {"calls": 0, "BYTE_IDENTICAL": 0, "JUSTIFIED_TOLERANCE": 0,
                                                   "REAL_MISMATCH": 0, "UNRESOLVED": 0})
            slot["calls"] += 1
            base = recs["b1"]
            row = {"test": k, "ordinal": i, "function": fname}
            if any(r is None for r in recs.values()):
                c, row["reason"] = "REAL_MISMATCH", "call-count differs between sessions"
            else:
                core = {n: r[:4] for n, r in recs.items()}
                all_equal = all(core[n] == core["b1"] for n in core)
                if all_equal:
                    c = "BYTE_IDENTICAL"
                else:
                    b_stable = core["b1"] == core["b2"]
                    f_stable = core["f1"] == core["f2"]
                    d = _diffs(recs["b1"], recs["f1"]) if core["b1"] != core["f1"] else []
                    if d is None:
                        c, row["reason"] = "UNRESOLVED", "no normalized payload retained (run without R3_KEEP)"
                    elif core["b1"] == core["f1"]:
                        c, row["reason"] = "UNRESOLVED", "BASE#1==FEATURE#1 but repeats differ (instability inside one side)"
                    else:
                        has_mtime = any(_leaf_key(p) == "source_signature" and _chk_mtime_signature(u, v)
                                        for p, u, v in d)
                        rules = [_justify(p, u, v, has_mtime) for p, u, v in d]
                        if d and all(rules):
                            c = "JUSTIFIED_TOLERANCE"
                            row["rules"] = sorted(set(rules))
                        elif b_stable and f_stable:
                            c, row["reason"] = "REAL_MISMATCH", "BASE and FEATURE are each repeatable but differ"
                        else:
                            c, row["reason"] = "UNRESOLVED", "repeats unstable and differences not on a justified field"
                        row["diff_sample"] = [{"path": [str(x) for x in p], "base": str(u)[:120], "feature": str(v)[:120],
                                               "rule": r} for (p, u, v), r in list(zip(d, rules))[:6]]
            row["class"] = c
            slot[c] += 1
            cls_total[c] += 1
            if c != "BYTE_IDENTICAL":
                details.append(row)
    total = sum(cls_total.values())
    summary = {"total_calls": total, **cls_total, "per_function": per_function,
               "test_outcomes_identical_across_all_sessions": outcome_equal,
               "failed_tests": sorted(k for k, v in runs["b1"]["outcomes"].items() if v != "passed")}
    return summary, details


# --------------------------------------------------------------------------------------------------------------------
# Session orchestration
# --------------------------------------------------------------------------------------------------------------------
def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _lex_under(child, parent):
    c = os.path.normcase(os.path.normpath(str(child)))
    p = os.path.normcase(os.path.normpath(parent))
    return c == p or c.startswith(p + os.sep)


def _git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, encoding="utf-8",
                          errors="replace")


def make_session(repo, work_root, name, sha):
    root = Path(work_root) / name
    if root.exists():
        raise SystemExit(f"session root already exists (refusing to reuse): {root}")
    r = _git("clone", "--quiet", "--no-hardlinks", str(repo), str(root), cwd=work_root)
    if r.returncode:
        raise SystemExit("clone failed: " + r.stderr[-400:])
    r = _git("checkout", "--quiet", "--detach", sha, cwd=root)
    if r.returncode:
        raise SystemExit("checkout failed: " + r.stderr[-400:])
    return root


_PLACEHOLDER = re.compile(r"%[A-Za-z_][A-Za-z0-9_]*%|\$\{[^}]*\}|\$[A-Za-z_][A-Za-z0-9_]*")
# variables whose value is ONE filesystem path and therefore must be absolute and fully resolved
_ABS_PATH_VARS = ("TEMP", "TMP", "PYTHONPYCACHEPREFIX", "R3_ROOT", "R3_NAMES", "R3_LOG", "CONTROLLED_MOCK_LANE_LOG_ROOT")


def assert_resolved_env(env):
    """A child interpreter given an unexpanded placeholder (e.g. PYTHONPYCACHEPREFIX=%SystemDrive%/pyc) would treat it
    as a RELATIVE path and create a literal `%SystemDrive%` directory tree under its cwd - clone-local debris. Fail closed."""
    bad = []
    for key, value in env.items():
        text = str(value)
        if _PLACEHOLDER.search(text):
            bad.append(f"{key} contains an unresolved placeholder: {text!r}")
        elif key in _ABS_PATH_VARS and not os.path.isabs(text):
            bad.append(f"{key} must be an absolute resolved path: {text!r}")
    if bad:
        raise SystemExit("unresolved/relative environment for a session: " + "; ".join(bad))
    return env


def _system_drive():
    """Resolved system drive (e.g. `C:`): the parent value, else the drive of SYSTEMROOT, else C:."""
    val = os.environ.get("SYSTEMDRIVE", "")
    if val and not _PLACEHOLDER.search(val):
        return val
    drive = os.path.splitdrive(os.environ.get("SYSTEMROOT", r"C:\Windows"))[0]
    return drive or "C:"


def session_env(root, session_dir, harness_dir, names, log, mode, keep, effect_funcs="", pin_pid=False):
    env = {
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", r"C:\Windows"),
        # Root cause of the T3-0.2 P1: a Microsoft Store (MSIX app-execution-alias) CPython started with a scrubbed
        # environment WITHOUT SYSTEMDRIVE creates a literal `%SystemDrive%\ProgramData\Microsoft\Windows\Caches\*.db`
        # tree in its cwd (the session clone) at interpreter startup, before any user code runs.
        "SYSTEMDRIVE": _system_drive(),
        "PATH": os.pathsep.join([str(Path(PY).parent), r"C:\Program Files\Git\cmd", r"C:\Windows\System32", r"C:\Windows"]),
        "TEMP": str(session_dir / "tmp"), "TMP": str(session_dir / "tmp"),
        "PYTHONUTF8": "1", "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1",
        # never inherited: an unresolved or relative prefix would put bytecode debris inside the session clone
        "PYTHONPYCACHEPREFIX": str(session_dir / "pycache"),
        "PYTHONPATH": str(harness_dir),
        "R3_ROOT": str(root), "R3_NAMES": str(names), "R3_LOG": str(log), "R3_POST": "1",
        "P156_DETERMINISM": "1" if mode == "det" else "0",
        # supported knob of libs/runtime/controlled_mock_lanes/ledger.py: without it the ledger writes cwd-relative
        # data/logs/controlled_mock_lanes inside the repository root (project write audit then fails the session)
        "CONTROLLED_MOCK_LANE_LOG_ROOT": str(session_dir / "mock_lane_logs"),
    }
    if keep:
        env["R3_KEEP"] = "1"
    if pin_pid:
        env["P156_PID_PIN"] = "full"
    assert_resolved_env(env)
    if effect_funcs:
        # ordered file-effect capture (opens/writes/renames/removes with content digests) for the listed functions
        env["R3_EFFECTS"] = "1"
        env["R3_EFFECT_FUNCS"] = effect_funcs
    return env


# --------------------------------------------------------------------------------------------------------------------
# Write containment (T3-0.3). Guarantee name: PRE_POST_END_STATE_MANIFEST_EQUIVALENCE.
# A before/after manifest proves that the END STATE of the session root equals its START STATE (strict mode: down to the
# SHA-256 of every file). It does NOT prove that no transient write-and-restore happened during the run, it does NOT
# cover paths outside the session root, and it is NOT OS-wide write interception.
# --------------------------------------------------------------------------------------------------------------------
MANIFEST_SCHEMA = "p156_tree_manifest.v1"
CONTAINMENT_GUARANTEE = "PRE_POST_END_STATE_MANIFEST_EQUIVALENCE"
CONTAINMENT_NOT_PROVEN = ("transient write-and-restore during execution", "writes outside the session root",
                          "OS-wide write interception")
MODE_STRICT = "strict_sha256"
MODE_FAST = "fast_metadata_only"
DIFF_KINDS = ("CREATED", "DELETED", "TYPE_CHANGED", "CONTENT_CHANGED", "METADATA_CHANGED", "SCAN_ERROR")
_REPARSE = 0x400  # FILE_ATTRIBUTE_REPARSE_POINT


def snapshot_tree(root):
    """LEGACY path-name-only snapshot (diagnostics only). It cannot see modification or deletion and `audit_session`
    refuses it. Use `snapshot_manifest`."""
    return set(snapshot_manifest(root, MODE_FAST)["entries"])


def _entry_for(path, st, strict):
    import stat as _st
    attrs = getattr(st, "st_file_attributes", 0)
    mode = st.st_mode
    if _st.S_ISLNK(mode) or (attrs & _REPARSE and not _st.S_ISREG(mode)):
        try:
            target = os.readlink(path)
        except OSError as exc:
            return None, f"unsupported reparse point / unreadable link: {exc}"
        return {"type": "symlink", "target": str(target), "size": 0, "mtime_ns": st.st_mtime_ns}, None
    if _st.S_ISDIR(mode):
        return {"type": "dir", "size": 0, "mtime_ns": st.st_mtime_ns}, None
    if _st.S_ISREG(mode):
        e = {"type": "file", "size": st.st_size, "mtime_ns": st.st_mtime_ns}
        if strict:
            try:
                e["sha256"] = _sha256(path)
            except OSError as exc:
                return None, f"unreadable file: {exc}"
            try:
                st2 = os.lstat(path)
            except OSError as exc:
                return None, f"vanished while hashing: {exc}"
            if (st2.st_size, st2.st_mtime_ns) != (st.st_size, st.st_mtime_ns):
                return None, "unstable: file changed while it was being hashed"
        return e, None
    return None, f"unsupported file type (st_mode={mode:#o})"


def snapshot_manifest(root, mode=MODE_STRICT):
    """Structured manifest of every entry below `root` (files, directories incl. empty and git-ignored ones, symlinks),
    excluding the top-level `.git` metadata. Entry: {type, size, mtime_ns, sha256 (strict files), target (symlinks)}.
    Anything that cannot be classified, read or hashed stably is recorded in `errors` (fail closed at diff time)."""
    if mode not in (MODE_STRICT, MODE_FAST):
        raise ValueError(f"unknown manifest mode {mode!r}")
    strict = mode == MODE_STRICT
    root = str(root)
    entries, errors = {}, []
    t0 = time.perf_counter()
    stack = [root]
    while stack:
        cur = stack.pop()
        try:
            with os.scandir(cur) as it:
                names = sorted(e.name for e in it)
        except OSError as exc:
            errors.append({"path": os.path.relpath(cur, root).replace("\\", "/"), "error": f"unlistable: {exc}"})
            continue
        for name in names:
            full = os.path.join(cur, name)
            rel = os.path.relpath(full, root).replace("\\", "/")
            if cur == root and name == ".git":
                continue
            try:
                st = os.lstat(full)
            except OSError as exc:
                errors.append({"path": rel, "error": f"lstat failed: {exc}"})
                continue
            e, err = _entry_for(full, st, strict)
            if err:
                errors.append({"path": rel, "error": err})
                continue
            entries[rel] = e
            if e["type"] == "dir":
                stack.append(full)
    canon = json.dumps(entries, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return {"schema": MANIFEST_SCHEMA, "mode": mode, "entries": entries, "errors": errors,
            "stats": {"entries": len(entries), "files": sum(1 for v in entries.values() if v["type"] == "file"),
                      "dirs": sum(1 for v in entries.values() if v["type"] == "dir"),
                      "bytes": sum(v["size"] for v in entries.values() if v["type"] == "file"),
                      "scan_seconds": round(time.perf_counter() - t0, 3)},
            "manifest_sha256": hashlib.sha256(canon.encode("utf-8")).hexdigest()}


def diff_manifests(before, after):
    """Every difference between two manifests of the same mode as [{path, kind, before, after}]. Fail closed: scan
    errors in either manifest are SCAN_ERROR differences; manifests of different modes cannot be compared."""
    for m in (before, after):
        if not isinstance(m, dict) or m.get("schema") != MANIFEST_SCHEMA:
            raise TypeError("audit requires structured manifests from snapshot_manifest(); a path-name-only snapshot "
                            "cannot prove containment")
    if before["mode"] != after["mode"]:
        raise ValueError("manifest modes differ: %s vs %s" % (before["mode"], after["mode"]))
    out = []
    for side, m in (("before", before), ("after", after)):
        for err in m["errors"]:
            out.append({"path": err["path"], "kind": "SCAN_ERROR", "before": None, "after": None,
                        "detail": f"{side}: {err['error']}"})
    b, a = before["entries"], after["entries"]
    for p in sorted(set(a) - set(b)):
        out.append({"path": p, "kind": "CREATED", "before": None, "after": a[p]})
    for p in sorted(set(b) - set(a)):
        out.append({"path": p, "kind": "DELETED", "before": b[p], "after": None})
    strict = before["mode"] == MODE_STRICT
    for p in sorted(set(a) & set(b)):
        x, y = b[p], a[p]
        if x["type"] != y["type"]:
            kind = "TYPE_CHANGED"
        elif x["type"] == "file":
            if x["size"] != y["size"] or (strict and x["sha256"] != y["sha256"]):
                kind = "CONTENT_CHANGED"
            elif x["mtime_ns"] != y["mtime_ns"]:
                kind = "METADATA_CHANGED"  # in fast mode content equivalence is NOT proven
            else:
                continue
        elif x["type"] == "symlink":
            if x["target"] != y["target"]:
                kind = "CONTENT_CHANGED"
            elif x["mtime_ns"] != y["mtime_ns"]:
                kind = "METADATA_CHANGED"
            else:
                continue
        else:  # dir
            if x["mtime_ns"] == y["mtime_ns"]:
                continue
            kind = "METADATA_CHANGED"
        out.append({"path": p, "kind": kind, "before": x, "after": y})
    return out


AUDIT_BANNER = "PRODUCTION PATH WRITE DETECTED"


def audit_session(before, after, stdout_text, exit_code, expect_failures=0):
    """Verdict for one session: any filesystem difference inside the session root (created, deleted, type/content/
    metadata changed, scan error), the project's own production-write banner, or an unexpected exit code is a FAIL."""
    diffs = diff_manifests(before, after)
    counts = {k: sum(1 for d in diffs if d["kind"] == k) for k in DIFF_KINDS}
    banner = AUDIT_BANNER in stdout_text
    problems = []
    if diffs:
        problems.append("filesystem differences inside the session root: %s" %
                        ", ".join(f"{k}={n}" for k, n in counts.items() if n))
    if banner:
        problems.append("project write audit banner present")
    if expect_failures == 0 and exit_code != 0:
        problems.append("pytest exit code %s (expected 0)" % exit_code)
    if expect_failures > 0 and not (exit_code == 1 and ("%d failed" % expect_failures) in stdout_text):
        problems.append("pytest exit code %s without exactly %d known failure(s)" % (exit_code, expect_failures))
    return {"guarantee": CONTAINMENT_GUARANTEE, "manifest_mode": before["mode"],
            "content_equivalence_proven": before["mode"] == MODE_STRICT,
            "differences_total": len(diffs), "difference_counts": counts,
            "new_paths_in_session_root": counts["CREATED"],
            "differences": diffs,
            "manifest_sha256_before": before["manifest_sha256"], "manifest_sha256_after": after["manifest_sha256"],
            "project_write_audit_banner": banner, "exit_code": exit_code, "problems": problems,
            "verdict": "FAIL" if problems else "PASS"}


# ---- failed-session evidence (T3.2): METADATA ONLY -----------------------------------------------------------------
# Three different things must not be confused:
#   1. data READ for verification  - strict mode reads and SHA-256-hashes every file body in the session root;
#   2. metadata RETAINED locally   - classification, counts, and (path, type, size, mtime_ns, sha256) manifests;
#   3. files UPLOADED/COMMITTED    - nothing in `failed_sessions/` or the run output directory is ever exported
#                                    automatically; the only export-safe file is `summary.json` (counts + path digests).
# File BODIES of a failed session are never copied: a benign file name can carry any secret, and no name- or
# pattern-based detector can prove otherwise. There is deliberately no switch that re-enables body copies.
FAILED_EVIDENCE_CAPS = {"max_differences": 2000, "max_manifest_entries": 50000}
TASK_OWNED_MARKER = ".p156_task_owned"
LOCAL_ONLY_NOTICE = (
    "LOCAL ONLY - do not upload, attach or commit this directory.\n"
    "It holds paths, sizes, mtimes and SHA-256 digests of a FAILED parity session (no file bodies). Paths may reveal\n"
    "sensitive names and a digest of a short/low-entropy file can be brute-forced; pytest output and call logs next to it\n"
    "are NOT sanitized. Export only `summary.json` (counts and path digests).\n")


def path_digest(path):
    """Stable, non-reversible-by-inspection label for a path in export-safe evidence (not a secrecy guarantee for
    guessable paths)."""
    return hashlib.sha256(str(path).encode("utf-8")).hexdigest()[:16]


def export_safe_differences(differences, limit=20):
    """Export-safe view of a difference list: kind + path digest only (no path text, no hashes, no sizes)."""
    return [{"kind": d["kind"], "path_digest": path_digest(d["path"])} for d in differences[:limit]]


def preserve_failed_evidence(root, verdict, dest, before, after, caps=None):
    """Write a compact, bounded, METADATA-ONLY bundle for a FAILED session BEFORE its disposable clone is cleaned:
    the classified difference list and both manifests (paths, types, sizes, mtimes, SHA-256). `root` is accepted for
    API compatibility and is never read: no file body is copied. Returns the bundle summary."""
    caps = {**FAILED_EVIDENCE_CAPS, **(caps or {})}
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / TASK_OWNED_MARKER).write_text("p156 failed-session evidence bundle (metadata only)\n", encoding="utf-8")
    (dest / "LOCAL_ONLY.txt").write_text(LOCAL_ONLY_NOTICE, encoding="utf-8")
    diffs = verdict["differences"]
    listed = diffs[:caps["max_differences"]]
    body = {k: v for k, v in verdict.items() if k != "differences"}
    body["differences"] = listed
    body["differences_listed"] = len(listed)
    body["differences_total_recorded"] = len(diffs)
    (dest / "diff.json").write_text(json.dumps(body, indent=1, ensure_ascii=False), encoding="utf-8")
    manifests = {}
    for tag, m in (("before", before), ("after", after)):
        entries = m["entries"]
        keep = {k: v for k, v in m.items() if k != "entries"}
        if len(entries) <= caps["max_manifest_entries"]:
            keep["entries"] = entries
            manifests[tag] = "full"
        else:
            keep["entries"] = {}
            manifests[tag] = "digest_only (entries exceed max_manifest_entries)"
        (dest / f"manifest_{tag}.json").write_text(json.dumps(keep, indent=0, ensure_ascii=False), encoding="utf-8")
    summary = {"file_bodies_retained": False, "copied": [], "retention": "metadata_only", "manifests": manifests,
               "differences_listed": len(listed), "differences_total_recorded": len(diffs), "caps": caps,
               "export_safe_file": "summary.json", "local_only_notice": "LOCAL_ONLY.txt"}
    (dest / "bundle.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    return summary


def prune_task_owned(parent, keep=5, max_age_days=14.0, max_total_bytes=64 << 20, now=None):
    """Finite retention for failed-evidence bundles: only DIRECT children of `parent` that carry TASK_OWNED_MARKER are
    ever considered; the newest `keep` survive, older than `max_age_days` or beyond `max_total_bytes` are removed.
    Anything without the marker (Codex clones, user workspaces) is never touched. Returns the removed names."""
    parent = Path(parent)
    now = time.time() if now is None else now
    owned = []
    for child in (parent.iterdir() if parent.is_dir() else []):
        if child.is_dir() and not child.is_symlink() and (child / TASK_OWNED_MARKER).is_file():
            size = sum(f.stat().st_size for f in child.rglob("*") if f.is_file())
            owned.append((child.stat().st_mtime, child, size))
    owned.sort(key=lambda t: t[0], reverse=True)
    removed, kept_bytes = [], 0
    for idx, (mtime, child, size) in enumerate(owned):
        too_old = (now - mtime) > max_age_days * 86400
        if idx >= keep or too_old or kept_bytes + size > max_total_bytes:
            shutil.rmtree(child, ignore_errors=True)
            removed.append(child.name)
        else:
            kept_bytes += size
    return removed


def _remove_task_owned(path, owner_root):
    """Delete a disposable session directory only if it is strictly inside the run's own work root."""
    p, o = Path(path).resolve(), Path(owner_root).resolve()
    if p == o or not _lex_under(p, str(o)):
        raise SystemExit(f"refusing to delete a directory outside the task-owned work root: {p}")
    shutil.rmtree(p, ignore_errors=True)


def preflight_interpreter(py, scratch, harness_dir, names, mode="det"):
    """Start the session interpreter ONCE with the exact scrubbed session environment inside a scratch directory and fail
    closed if it writes anything into its cwd (e.g. Microsoft Store Python without SYSTEMDRIVE). Returns the snapshot
    diff (empty on success). The scratch directory belongs to the caller."""
    scratch = Path(scratch)
    tree = scratch / "tree"
    tree.mkdir(parents=True, exist_ok=True)
    (scratch / "tmp").mkdir(exist_ok=True)
    env = session_env(tree, scratch, harness_dir, names, scratch / "calls.json", mode, False)
    before = snapshot_manifest(tree, MODE_STRICT)
    r = subprocess.run([py, "-c", "import sys; sys.stdout.write('ok')"], cwd=str(tree), env=env, capture_output=True,
                       text=True, timeout=120)
    created = sorted(d["path"] for d in diff_manifests(before, snapshot_manifest(tree, MODE_STRICT)))
    if r.returncode != 0:
        raise SystemExit(f"interpreter preflight failed (exit {r.returncode}): {(r.stderr or '')[-300:]}")
    if created:
        raise SystemExit("interpreter preflight: the session interpreter created paths in its cwd under the scrubbed "
                         "session environment (clone-local debris): " + ", ".join(created[:8]))
    return created


def run_sessions(args):
    repo = Path(args.repo).resolve()
    work = Path(args.work_root).resolve()
    out = Path(args.out_dir).resolve()
    for label, p in (("repo", repo), ("work-root", work), ("out-dir", out)):
        if _lex_under(p, LIVE_ROOT):
            raise SystemExit(f"{label} is inside the protected live root")
    if _lex_under(work, repo) or _lex_under(out, repo):
        raise SystemExit("work-root/out-dir must be outside the audited repository")
    work.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=False)
    (work / TASK_OWNED_MARKER).write_text("p156 run-owned disposable work root\n", encoding="utf-8")
    (out / "LOCAL_ONLY.txt").write_text(
        "LOCAL ONLY except summary.json. pytest_*.out, raw_calls_*.json, containment_*.json and failed_sessions/ may hold "
        "paths, digests or arbitrary test output and are never sanitized; do not upload or commit them.\n", encoding="utf-8")
    manifest_mode = MODE_FAST if getattr(args, "containment", "strict") == "fast" else MODE_STRICT
    harness = work / "_harness"
    harness.mkdir()
    names_path = Path(args.names).resolve()
    pre_dir = work / "_preflight"
    pre_dir.mkdir()
    preflight_interpreter(PY, pre_dir, harness, names_path, args.mode)
    shutil.rmtree(pre_dir, ignore_errors=True)
    for fname in ("p152_r3_call_recorder.py", "p156_determinism_plugin.py"):
        shutil.copy2(HERE / fname, harness / fname)
    names = Path(args.names).resolve()
    tests = [t.strip() for t in Path(args.tests).read_text(encoding="utf-8").splitlines() if t.strip()]
    specs = [("b1", args.baseline_sha), ("b2", args.baseline_sha), ("f1", args.feature_sha), ("f2", args.feature_sha)]
    sha_of = dict(specs)
    cmd_tail = ["-m", "pytest", "-q", "-p", "p152_r3_call_recorder", "-p", "p156_determinism_plugin",
                "-p", "no:cacheprovider", *tests]
    order = []
    sessions = {}

    def prepare(tag, dirname):
        sdir = work / dirname
        sdir.mkdir()
        (sdir / "tmp").mkdir()
        root = make_session(repo, sdir, "tree", sha_of[tag])
        s = {"tag": tag, "sha": sha_of[tag], "dir": sdir, "root": root, "log": sdir / "calls.json",
             "stdout": sdir / "pytest.out"}
        sessions[tag] = s
        return s

    def launch(s):
        env = session_env(s["root"], s["dir"], harness, names, s["log"], args.mode, True, getattr(args, "effect_funcs", ""), bool(getattr(args, "pin_pid", False)))
        fh = open(s["stdout"], "wb")
        order.append(s["tag"])
        s["before"] = snapshot_manifest(s["root"], manifest_mode)
        return subprocess.Popen([PY, *cmd_tail], cwd=str(s["root"]), env=env, stdout=fh, stderr=subprocess.STDOUT), fh

    def finish(s, p, fh):
        p.wait()
        fh.close()
        s["exit"] = p.returncode
        text = Path(s["stdout"]).read_text(encoding="utf-8", errors="replace")
        after = snapshot_manifest(s["root"], manifest_mode)
        s["contained"] = audit_session(s["before"], after, text, p.returncode, expect_failures=args.expect_failures)
        # classification and evidence are recorded BEFORE any cleanup (same-path mode removes the clone right after)
        (out / f"containment_{s['tag']}.json").write_text(json.dumps(
            {"tag": s["tag"], "sha": s["sha"], "scan_seconds": {"before": s["before"]["stats"]["scan_seconds"],
                                                                "after": after["stats"]["scan_seconds"]},
             "stats": after["stats"], **s["contained"]}, indent=1, ensure_ascii=False), encoding="utf-8")
        if s["contained"]["verdict"] != "PASS":
            s["failed_evidence"] = preserve_failed_evidence(s["root"], s["contained"], out / "failed_sessions" / s["tag"],
                                                            s["before"], after)
        # export-safe view for summary.json: counts + kind/path-digest only (paths and hashes stay in the local files)
        s["contained"] = {k: v for k, v in s["contained"].items() if k != "differences"} | {
            "differences_export_safe": export_safe_differences(s["contained"]["differences"])}
        s["pytest_summary"] = _tail(s["stdout"])
        s["log_sha256"] = _sha256(s["log"])
        s["log_bytes"] = s["log"].stat().st_size
        shutil.copy2(s["log"], out / f"raw_calls_{s['tag']}.json")
        shutil.copy2(s["stdout"], out / f"pytest_{s['tag']}.out")

    if args.same_path:
        # strictly sequential, one disposable clone at a time at an IDENTICAL path: removes session-path-dependent
        # content (e.g. hashes of artifacts that embed the session root) from the comparison
        for tag in ("b1", "f1", "b2", "f2"):
            s = prepare(tag, "s_run")
            p, fh = launch(s)
            try:
                finish(s, p, fh)
            finally:
                _remove_task_owned(s["dir"], work)
    elif args.sequential:
        for tag in ("b1", "f1", "b2", "f2"):
            s = prepare(tag, f"s_{tag}")
            p, fh = launch(s)
            finish(s, p, fh)
    else:
        procs = {}
        for tag in ("b1", "b2", "f1", "f2"):
            prepare(tag, f"s_{tag}")
        for tag in ("b1", "b2", "f1", "f2"):
            procs[tag] = launch(sessions[tag])
        for tag, (p, fh) in procs.items():
            finish(sessions[tag], p, fh)
    runs = {t: json.load(open(out / f"raw_calls_{t}.json", encoding="utf-8")) for t in sessions}
    summary, details = compare(runs)
    contained = {t: s["contained"] for t, s in sessions.items()}
    evidence = {
        "schema": "p156_parity_differential.v1",
        "mode": args.mode, "sequential": bool(args.sequential or args.same_path), "same_session_path": bool(args.same_path),
        "baseline_sha": args.baseline_sha, "feature_sha": args.feature_sha,
        "repo_head_for_harness": _git("rev-parse", "HEAD", cwd=repo).stdout.strip(),
        "names": json.loads(names.read_text(encoding="utf-8")),
        "test_files": tests, "execution_order": order,
        "sessions": {t: {"sha": s["sha"], "exit_code": s.get("exit"), "log_sha256": s["log_sha256"],
                         "log_bytes": s["log_bytes"], "pytest_summary": s["pytest_summary"]}
                     for t, s in sessions.items()},
        "isolation": {"separate_session_roots": True, "separate_temp_dirs": True, "write_containment": contained,
                      "containment_guarantee": CONTAINMENT_GUARANTEE, "containment_manifest_mode": manifest_mode,
                      "content_equivalence_proven": manifest_mode == MODE_STRICT,
                      "containment_not_proven": list(CONTAINMENT_NOT_PROVEN),
                      "containment_verdict": "PASS" if all(v["verdict"] == "PASS" for v in contained.values()) else "FAIL",
                      "failed_sessions": sorted(t for t, v in contained.items() if v["verdict"] != "PASS")},
        "tolerance_rules": {k: {"keys": list(v["keys"]), "why": v["why"]} for k, v in TOLERANCE_RULES.items()},
        "summary": summary,
        "reproduce": " ".join([PY, "scripts/refactor/p156_parity_differential.py", "--repo", "<clone>",
                               "--baseline-sha", args.baseline_sha, "--feature-sha", args.feature_sha,
                               "--names", "<names.json>", "--tests", "<tests.txt>", "--work-root", "<empty dir>",
                               "--out-dir", "<new dir>", "--mode", args.mode] + (["--sequential"] if args.sequential else []) + (["--same-path"] if args.same_path else [])),
    }
    (out / "summary.json").write_text(json.dumps(evidence, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "non_identical_details.json").write_text(json.dumps(details, indent=1, ensure_ascii=False), encoding="utf-8")
    if not args.keep_sessions:
        for s in sessions.values():
            _remove_task_owned(s["dir"], work)
    return evidence


def _tail(path):
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").strip().splitlines()
        return lines[-1] if lines else ""
    except OSError:
        return ""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--baseline-sha", required=True)
    ap.add_argument("--feature-sha", required=True)
    ap.add_argument("--names", required=True)
    ap.add_argument("--tests", required=True)
    ap.add_argument("--work-root", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--mode", choices=("det", "natural"), default="det")
    ap.add_argument("--sequential", action="store_true")
    ap.add_argument("--pin-pid", action="store_true",
                    help="keep os.getpid constant for the whole session (anchor suites that tolerate it)")
    ap.add_argument("--effect-funcs", default="",
                    help="comma list of <module>.<name> (or *) whose ordered file effects are captured and compared")
    ap.add_argument("--same-path", action="store_true",
                    help="sequential runs, each in a fresh disposable clone at the SAME path")
    ap.add_argument("--expect-failures", type=int, default=0,
                    help="number of known baseline test failures that make exit code 1 acceptable (0 = exit must be 0)")
    ap.add_argument("--keep-sessions", action="store_true",
                    help="UNSAFE for real data: keeps the complete disposable clones (file bodies included) on local disk")
    ap.add_argument("--containment", choices=("strict", "fast"), default="strict",
                    help="strict: SHA-256 of every file (content equivalence proven); fast: size+mtime only "
                         "(content equivalence NOT proven, labelled in the evidence)")
    a = ap.parse_args(argv)
    ev = run_sessions(a)
    s = ev["summary"]
    bad = {t: v["problems"] for t, v in ev["isolation"]["write_containment"].items() if v["verdict"] != "PASS"}
    print(json.dumps({k: s[k] for k in ("total_calls", "BYTE_IDENTICAL", "JUSTIFIED_TOLERANCE", "REAL_MISMATCH",
                                         "UNRESOLVED", "test_outcomes_identical_across_all_sessions")}))
    if bad:
        print("ISOLATION_VERDICT=FAIL", json.dumps(bad))
        raise SystemExit(2)
    print("ISOLATION_VERDICT=PASS")


if __name__ == "__main__":
    main()
