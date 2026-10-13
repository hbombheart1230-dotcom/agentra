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


def session_env(root, session_dir, harness_dir, names, log, mode, keep):
    env = {
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", r"C:\Windows"),
        "PATH": os.pathsep.join([str(Path(PY).parent), r"C:\Program Files\Git\cmd", r"C:\Windows\System32", r"C:\Windows"]),
        "TEMP": str(session_dir / "tmp"), "TMP": str(session_dir / "tmp"),
        "PYTHONUTF8": "1", "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": str(harness_dir),
        "R3_ROOT": str(root), "R3_NAMES": str(names), "R3_LOG": str(log), "R3_POST": "1",
        "P156_DETERMINISM": "1" if mode == "det" else "0",
        # supported knob of libs/runtime/controlled_mock_lanes/ledger.py: without it the ledger writes cwd-relative
        # data/logs/controlled_mock_lanes inside the repository root (project write audit then fails the session)
        "CONTROLLED_MOCK_LANE_LOG_ROOT": str(session_dir / "mock_lane_logs"),
    }
    if keep:
        env["R3_KEEP"] = "1"
    return env


def snapshot_tree(root):
    """Every file AND directory (including empty and git-ignored ones) below root, excluding the .git directory."""
    seen = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not (Path(dirpath) == Path(root) and d == ".git")]
        base = Path(dirpath)
        for name in dirnames + filenames:
            seen.add(str((base / name).relative_to(root)).replace("\\", "/"))
    return seen


AUDIT_BANNER = "PRODUCTION PATH WRITE DETECTED"


def audit_session(before, after, stdout_text, exit_code, expect_failures=0):
    """Verdict for one session: any new path (file, directory, empty or git-ignored) inside the session root, the
    project's own production-write banner, or an exit code other than the expected one is a FAIL."""
    new_paths = sorted(after - before)
    banner = AUDIT_BANNER in stdout_text
    problems = []
    if new_paths:
        problems.append("new paths created inside the session root: %d" % len(new_paths))
    if banner:
        problems.append("project write audit banner present")
    if expect_failures == 0 and exit_code != 0:
        problems.append("pytest exit code %s (expected 0)" % exit_code)
    if expect_failures > 0 and not (exit_code == 1 and ("%d failed" % expect_failures) in stdout_text):
        problems.append("pytest exit code %s without exactly %d known failure(s)" % (exit_code, expect_failures))
    return {"new_paths_in_session_root": len(new_paths), "new_paths_sample": new_paths[:20],
            "project_write_audit_banner": banner, "exit_code": exit_code, "problems": problems,
            "verdict": "FAIL" if problems else "PASS"}


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
    harness = work / "_harness"
    harness.mkdir()
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
        env = session_env(s["root"], s["dir"], harness, names, s["log"], args.mode, True)
        fh = open(s["stdout"], "wb")
        order.append(s["tag"])
        s["before"] = snapshot_tree(s["root"])
        return subprocess.Popen([PY, *cmd_tail], cwd=str(s["root"]), env=env, stdout=fh, stderr=subprocess.STDOUT), fh

    def finish(s, p, fh):
        p.wait()
        fh.close()
        s["exit"] = p.returncode
        text = Path(s["stdout"]).read_text(encoding="utf-8", errors="replace")
        s["contained"] = audit_session(s["before"], snapshot_tree(s["root"]), text, p.returncode,
                                       expect_failures=args.expect_failures)
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
            finish(s, p, fh)
            shutil.rmtree(s["dir"], ignore_errors=True)
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
        "isolation": {"separate_session_roots": True, "separate_temp_dirs": True, "write_containment": contained},
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
            shutil.rmtree(s["dir"], ignore_errors=True)
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
    ap.add_argument("--same-path", action="store_true",
                    help="sequential runs, each in a fresh disposable clone at the SAME path")
    ap.add_argument("--expect-failures", type=int, default=0,
                    help="number of known baseline test failures that make exit code 1 acceptable (0 = exit must be 0)")
    ap.add_argument("--keep-sessions", action="store_true")
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
