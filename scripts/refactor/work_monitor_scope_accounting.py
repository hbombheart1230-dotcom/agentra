"""Reproducible current Monitor inventory/proof; read-only, no runtime imports.

Disposition is scope accounting, NOT a claim of dead code or completed review of
all business behavior. Unmoved authority remains locked. Direct import consumers
are bounded to this role and its graph; dynamic consumers remain compatibility
obligations, never grounds for deletion.
"""
from __future__ import annotations
import ast
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
import work_monitor_current_tree as T

ROOT = T.ROOT
PROTECTED = ("graphs", "apps", "libs/execution", "libs/kiwoom", "libs/llm", "libs/risk", "libs/supervisor",
             "libs/agents/scanner", "libs/agents/strategist", "libs/runtime/scanner", "libs/runtime/strategist",
             "libs/reporting", ".github", "sitecustomize.py", "conftest.py", "tests/fixtures/p1_5_t4b_monitor")


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def disposition(path, name):
    if path == "graphs/nodes/monitor_node.py":
        return "SAFETY_LOCK_ORCHESTRATION", "Original intent, State/event/persistence execution order and facade seam remain."
    if name.startswith(("_to_", "to_", "_safe_")) or name in {"_is_trueish", "_clamp", "_optional_float", "monitor_policy_adjustment_inputs"}:
        return "KEEP_PATCH_PRIMITIVE", "Small existing converter/reader retained at its original use-time patch boundary."
    if name in {"build_overnight_carry_decision_payload", "eod_carry_payload"}:
        return "KEEP_REVIEWABLE_COLOCATION", "Small carry DTO colocated with original carry controller; no extra tiny Owner without Work architecture review."
    if path.endswith("/reasons.py"):
        return "SAFETY_LOCK_EXIT_PRECEDENCE", "Emergency/hard/soft/priority classification must remain at its original decision boundary."
    if path.endswith("/intraday_monitor_signals.py"):
        return "SAFETY_LOCK_SIGNAL_POLICY", "Remaining feature/check/quality/interpretation outputs feed signal scoring or gates; not presumed display-only."
    if path.endswith("/exit_policy.py") or "/monitor_exit/" in path:
        return "SAFETY_LOCK_EXIT_PRICE_STATE", "Exit decision, price truth, ladder, clock, carry, tracking or guard boundary retained."
    if "/monitor/" in path:
        return "SAFETY_LOCK_ENTRY_SIGNAL_BOUNDARY", "Remaining candidate/cascade/signal/score/guard owner participates in decisions or existing typed boundary."
    return "SAFETY_LOCK_POLICY_SHARED_BOUNDARY", "Policy/config/schema, sizing, memory, price/cash/horizon or source-precedence boundary retained; no semantic/authority transfer."


def produce(code_sha=None):
    initial = json.loads((ROOT / "docs/refactor/work_projects/evidence/monitor/continuous/program.json").read_text(encoding="utf-8"))
    old = json.loads((ROOT / "docs/refactor/work_projects/evidence/monitor/path_ledger.json").read_text(encoding="utf-8"))
    whole = {r["source"]: r["destination"] for r in old["maps"]} | T.WHOLE_MOVES
    reverse = {b: a for a, b in whole.items()}
    body_owners = {s["owner"] for s in T.BODY_MOVES.values()}
    paths = sorted({r["path"] for r in initial["inventory"]} | set(whole.values()) | body_owners)
    code_sha = code_sha or subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    subprocess.run(["git", "merge-base", "--is-ancestor", code_sha, "HEAD"], cwd=ROOT, check=True)
    if subprocess.check_output(["git", "diff", "--name-only", code_sha, "--", *paths], cwd=ROOT).strip():
        raise AssertionError("current role sources do not match pinned code SHA")
    sources = {p: (ROOT / p).read_text(encoding="utf-8") for p in paths}
    consumers = {p: [] for p in paths}
    by_module = {p[:-3].replace("/", "."): p for p in paths}
    for consumer, source in sources.items():
        for n in ast.walk(T._tree(source)):
            if not isinstance(n, ast.ImportFrom):
                continue
            if n.module in by_module:
                consumers[by_module[n.module]].append({"file": consumer, "line": n.lineno, "names": [a.name for a in n.names]})
            for a in n.names:
                if (n.module or "") + "." + a.name in by_module:
                    consumers[by_module[(n.module or "") + "." + a.name]].append({"file": consumer, "line": n.lineno, "names": ["<module>"]})
    rows = []
    for path in paths:
        source = sources[path]
        if path in whole:
            tree = T._tree(source)
            if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant) and isinstance(tree.body[0].value.value, str):
                tree.body = tree.body[1:]
            if T._dump(tree) != T._dump(ast.parse(T.shim_source(path, whole[path]))):
                raise AssertionError("nonexact identity shim: " + path)
            kind, proof = "COMPAT_IDENTITY_SHIM", "Exact registered three-statement AST; canonical BASE bytes checked separately."
        elif path in reverse:
            if source != T.base_source(reverse[path]):
                raise AssertionError("whole BASE implementation changed: " + path)
            expected = subprocess.check_output(["git", "rev-parse", T.BASE + ":" + reverse[path]], cwd=ROOT).strip()
            actual = subprocess.check_output(["git", "rev-parse", "HEAD:" + path], cwd=ROOT).strip()
            if actual != expected:
                raise AssertionError("committed BASE Git blob differs: " + path)
            kind, proof = "CANONICAL_WHOLE_BLOB", "Full raw BASE source equality."
        elif path in T.BODY_MOVES:
            T.verified_current_source(path)
            kind, proof = "COMPAT_BODY_FACADE", "Full original module and exact grouped Owner AST reconstruction, all unmoved definitions protected."
        elif path in body_owners:
            origin = next(p for p, s in T.BODY_MOVES.items() if s["owner"] == path)
            if T._dump(T._tree(source)) != T._dump(T.body_templates(origin)[1]):
                raise AssertionError("changed grouped Owner: " + path)
            kind, proof = "CANONICAL_NAMED_BODIES", "Exact BASE statement bodies with only declared use-time global qualification/signature extension."
        else:
            if source != T.base_source(path):
                raise AssertionError("retained source changed: " + path)
            kind, proof = "RETAINED_BASE_BYTES", "All source bytes retained (newline-normalized UTF-8, BOM preserved)."
        symbols = []
        for node in T._tree(source).body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            group = [(node.name, node)] + ([(node.name + "." + child.name, child) for child in node.body if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))] if isinstance(node, ast.ClassDef) else [])
            for name, fn in group:
                if kind.startswith("CANONICAL_"):
                    category, reason = "IMPLEMENTATION_MOVED_VERIFIED", proof
                elif path in T.BODY_MOVES and name in T.BODY_MOVES[path]["functions"]:
                    category, reason = "KEEP_PUBLIC_COMPAT_WRAPPER", "Original public/private function identity path/signature and use-time dependency resolution."
                else:
                    category, reason = disposition(path, name)
                symbols.append({"symbol": name, "line": fn.lineno, "LOC": fn.end_lineno - fn.lineno + 1,
                                "disposition": category, "reason": reason, "ast_sha256": digest(T._dump(fn))})
        rows.append({"path": path, "LOC": len(source.splitlines()), "kind": kind, "proof": proof,
                     "source_sha256": digest(source), "direct_role_import_consumers": consumers[path], "symbols": symbols})
    changed_protected = subprocess.check_output(["git", "diff", "--name-only", initial["program_start"], "--", *PROTECTED], cwd=ROOT, text=True).splitlines()
    if changed_protected:
        raise AssertionError("protected paths changed: " + str(changed_protected))
    fixtures = []
    for p in sorted((ROOT / "tests/fixtures/work_monitor").glob("*.json")):
        relative = p.relative_to(ROOT).as_posix()
        raw = subprocess.check_output(["git", "show", code_sha + ":" + relative], cwd=ROOT)
        data = json.loads(raw.decode("utf-8"))
        if json.loads(p.read_text(encoding="utf-8")) != data:
            raise AssertionError("fixture differs from pinned code SHA")
        fixtures.append({"path": relative, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                         "hash_basis": "raw pinned Git blob, not checkout line endings", "cases": len(data["records"])})
    return {"schema": "monitor.current_scope.v1", "code_sha": code_sha,
            "producer_sha256": hashlib.sha256(Path(__file__).read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
            "BASE": T.BASE, "program_start": initial["program_start"], "state": "PARTIAL_WITH_BLOCKERS_NOT_ROLE_READY",
            "module_count": len(rows), "symbol_count": sum(len(r["symbols"]) for r in rows),
            "module_kinds": dict(Counter(r["kind"] for r in rows)),
            "dispositions": dict(Counter(s["disposition"] for r in rows for s in r["symbols"])),
            "canonical_max_LOC": max(r["LOC"] for r in rows if r["kind"].startswith("CANONICAL_")),
            "protected_changes": changed_protected, "whole_moves": whole, "named_transfers": T.BODY_MOVES,
            "fixtures": fixtures, "modules": rows,
            "limits": ["Bounded static consumers, dynamic/external consumers NOT proven exhaustive; legacy contracts retained.",
                       "Retained disposition is a safety/scope decision, NOT dead-code proof or independent Work acceptance.",
                       "Shared gate repairs/hosted integration/full native pytest/real persisted parity remain open."]}


if __name__ == "__main__":
    if len(sys.argv) not in (1, 2):
        raise SystemExit("Optional argument: pinned source CODE SHA")
    print(json.dumps(produce(sys.argv[1] if len(sys.argv) == 2 else None), ensure_ascii=True, separators=(",", ":")))
