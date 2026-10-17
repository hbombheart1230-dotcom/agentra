"""R8 C1: evidence-based per-function triage of the R-4..R-7 remaining (non-trivial) facade functions.

For every function recorded as skipped (except thin delegations / short helpers) this inspects the real AST: actual calls
to file/OS/time/env/network/LLM/broker/truth APIs, references to module identity, and where the scanner token occurs
(code vs string/annotation). Output rows are machine-readable; dispositions are rule-based and conservative."""
import ast
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVD = ROOT / "docs/refactor/work_projects/evidence/reporter"
IO_ATTR = {"read_text", "write_text", "read_bytes", "write_bytes", "open", "mkdir", "exists", "is_file", "is_dir", "glob", "rglob",
           "iterdir", "unlink", "rename", "replace", "stat", "touch", "resolve", "load", "loads", "dump", "dumps", "getenv",
           "sleep", "time", "now", "utcnow", "monotonic", "info", "warning", "error", "debug", "exception", "write", "flush"}
IO_NAME = {"open", "print", "Path", "input"}
AUTH = re.compile(r"(llm|LLM|openai|openrouter|anthropic|client|retry|model|broker|kiwoom|truth|order|execute|submit|feedback|memory_write|lock|queue)")


def classify(src, fn):
    calls, auth = [], set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name) and f.id in IO_NAME:
                calls.append(f.id)
            elif isinstance(f, ast.Attribute) and f.attr in IO_ATTR:
                base = f.value.id if isinstance(f.value, ast.Name) else type(f.value).__name__
                if not (f.attr in {"load", "loads", "dump", "dumps"} and base != "json") and not (f.attr == "replace" and base not in ("os", "Path")):
                    if f.attr in {"dumps", "loads"}:
                        continue  # in-memory JSON is not I/O
                    calls.append(f"{base}.{f.attr}")
        if isinstance(n, ast.Name) and AUTH.search(n.id):
            auth.add(n.id)
        if isinstance(n, ast.Attribute) and AUTH.search(n.attr):
            auth.add(n.attr)
    ident = "__name__" in ast.get_source_segment(src, fn) or "_r3_sys" in ast.get_source_segment(src, fn)
    return sorted(set(calls)), sorted(auth), ident


def main():
    led = json.loads((EVD / "r4_facade_ledger.json").read_text(encoding="utf-8"))
    rows = []
    for path, skipped in led["skipped"].items():
        src = (ROOT / path).read_text(encoding="utf-8-sig")
        tree = ast.parse(src)
        fns = {}
        for n in tree.body:
            if isinstance(n, ast.FunctionDef):
                fns.setdefault(n.name, []).append(n)
        for name, reason in skipped.items():
            if reason.startswith(("already thin", "short")):
                continue
            fn = fns[name][-1]
            calls, auth, ident = classify(src, fn)
            callers = [x for x in subprocess.run(["git", "grep", "-lw", name, "--", "*.py"], cwd=ROOT, capture_output=True, text=True).stdout.split() if x != path]
            if len(fns[name]) > 1:
                disp, nxt = "RETAIN_FACADE", "redefinition: effective last definition is the facade behavior; dead first def kept for ABI/history"
            elif ident:
                disp, nxt = "RETAIN_FACADE", "module identity is a contract (passes its own module as facade to parts)"
            elif reason.startswith("excluded by caller"):
                disp, nxt = "NEEDS_AUTHORITY", "LLM routing / reporter agent / cross-facade import: keep until separately approved"
            elif any(a for a in auth if re.search(r"llm|LLM|openai|openrouter|anthropic|retry|model|client", a)):
                disp, nxt = "NEEDS_AUTHORITY", "LLM routing/retry/cost related names"
            elif any(a for a in auth if re.search(r"broker|kiwoom|truth|order|execute|submit", a)):
                disp, nxt = "NEEDS_AUTHORITY", "broker/truth/execution related names"
            elif calls:
                disp, nxt = "RETAIN_FACADE", "real read/write/time/log call: needs temp-dir parity fixture before any move"
            else:
                disp, nxt = "SAFE_MOVE_CANDIDATE", "token false positive (no I/O/authority call in AST); move with R4 proof"
            rows.append({"legacy_path": path, "name": name, "scanner_reason": reason, "real_effect_calls": calls,
                         "authority_names": auth, "module_identity": ident, "callers": callers[:8], "disposition": disp,
                         "next_action": nxt})
    out = {"schema": "agentra.work.reporter.r8_triage.v1", "rows": rows}
    (EVD / "r8_function_triage.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    import collections
    print(collections.Counter(r["disposition"] for r in rows), len(rows))


if __name__ == "__main__":
    main()
