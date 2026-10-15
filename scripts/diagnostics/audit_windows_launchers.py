"""Read-only Windows launcher contracts; never execute launchers or expand host env."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

_SUFFIXES = {".bat", ".cmd", ".ps1"}
_FILE = re.compile(r"\b([\w.-]+\.(?:py|ps1|bat|cmd))\b", re.IGNORECASE)
_BINDING = re.compile(r'^\s*(?:set\s+"?([\w]+)=|\$([\w]+)\s*=)', re.IGNORECASE)
_VARIABLE = re.compile(r"%([\w]+)%|\$([\w]+)")
_TASK = re.compile(r'/TN\s+"([^"]+)"', re.IGNORECASE)


_PREFIX = re.compile(r'^\s*set\s+"?TASK_PREFIX=([A-Za-z0-9_.-]+)"?\s*$', re.I)
_MOCK_REGISTER = "scripts/register_mock_exam_tasks_example.bat"
_MOCK_UNREGISTER = "scripts/unregister_mock_exam_tasks_example.bat"
_FROZEN_REGISTERED = {"TradingAgent-MockExamDay-" + suffix for suffix in (
    "Q12-Preopen", "Preopen", "Q12-BTC-0855", "Session", "SessionWatchdog", "Closeout")}
_FROZEN_UNREGISTERED = _FROZEN_REGISTERED - {
    "TradingAgent-MockExamDay-Q12-Preopen", "TradingAgent-MockExamDay-Q12-BTC-0855"}


def _resolve_task(raw: str, prefix: str | None) -> tuple[str | None, str]:
    if re.fullmatch(r"[A-Za-z0-9_.-]+", raw):
        return raw, "LITERAL"
    match = re.fullmatch(r"%TASK_PREFIX%(-[A-Za-z0-9_.-]+)", raw, re.I)
    if match and prefix is not None:
        return prefix + match.group(1), "PREFIX_RESOLVED"
    return None, "UNRESOLVED"


def assert_mockexam_known_contract(result: dict) -> None:
    """Assert frozen source names only; never assert live cleanup success."""
    contract = result["mockexam_task_contract"]
    if (contract["status"] != "PROVEN"
            or set(contract["registered"]) != _FROZEN_REGISTERED
            or set(contract["unregistered"]) != _FROZEN_UNREGISTERED):
        result["issues"].append("MockExam frozen task-name contract not proven or changed")
    result["ok"] = not result["issues"]


def audit(root: Path, *, expected_count: int | None = None) -> dict:
    root = root.resolve()
    launchers = sorted(p for p in (root / "scripts").iterdir() if p.suffix.lower() in _SUFFIXES)
    issues: list[str] = []
    records = []
    tasks = []
    for path in launchers:
        source = path.read_text(encoding="utf-8-sig")
        edges = []
        bindings: dict[str, list[str]] = {}
        cwd = []
        policy = []
        commands = []
        prefix = None
        for number, line in enumerate(source.splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "::")) or re.match(r"rem(?:\s|$)", stripped, re.I):
                continue
            # Only preceding exact literal batch assignments are trusted, per file.
            if path.suffix.lower() in {".bat", ".cmd"} and re.match(
                    r'^\s*set\s+"?TASK_PREFIX=', line, re.I):
                literal = _PREFIX.fullmatch(line)
                prefix = literal.group(1) if literal else None
            # Batch expands %~dp0 without a separator before sibling filenames.
            names = _FILE.findall(re.sub(r"%~dp0", "", line, flags=re.IGNORECASE))
            binding = _BINDING.match(line)
            if binding and names:
                bindings[(binding.group(1) or binding.group(2)).lower()] = names
            dispatch = bool(re.search(
                r'^\s*(?:call\b|&|python(?:\.exe)?\b|"[^"\r\n]*(?:python\.exe|%PY%)")'
                r'|Start-Process|schtasks\s+/(?:Create|Delete)', line, re.I
            ))
            kind = ("binding" if binding else "process_match" if "CommandLine" in line
                    else "direct_dispatch" if dispatch else "literal_reference")
            for name in names:
                candidate = root / "scripts" / name
                if candidate.is_file():
                    edges.append({"target": candidate.relative_to(root).as_posix(), "line": number, "kind": kind})
                elif re.search(r"scripts[\\/]" + re.escape(name), line, re.I) or re.search(
                    r"(?:%~dp0|%SCRIPT_DIR%|\$PSScriptRoot[\s\"']+)" + re.escape(name), line, re.I
                ):
                    issues.append(f"{path.name}:{number}: missing launcher target scripts/{name}")
            if dispatch:
                commands.append({"line": number, "text": stripped})
                for match in _VARIABLE.finditer(line):
                    variable = (match.group(1) or match.group(2)).lower()
                    for name in bindings.get(variable, []):
                        candidate = root / "scripts" / name
                        if candidate.is_file():
                            edges.append({"target": candidate.relative_to(root).as_posix(), "line": number,
                                          "kind": "bound_variable_dispatch", "variable": variable})
            if re.search(r"\b(?:pushd|popd|cd\s+/d|Push-Location|Pop-Location)\b|WorkingDirectory", line, re.I):
                cwd.append({"line": number, "text": stripped})
            if re.search(r"^\s*set\s+\"?(?:MOCK_|EXECUTION_|ALLOW_|APPROVAL_|KIWOOM_)", line, re.I):
                policy.append({"line": number, "text": stripped})
            if re.search(r"schtasks\s+/(?:Create|Delete)\b", line, re.I):
                match = _TASK.search(line)
                if match:
                    resolved, resolution = _resolve_task(match.group(1), prefix)
                    tasks.append({"source": path.relative_to(root).as_posix(), "line": number,
                                  "action": "create" if re.search(r"/Create\b", line, re.I) else "delete",
                                  "task": match.group(1), "resolved_task": resolved, "resolution": resolution})
        records.append({"path": path.relative_to(root).as_posix(),
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "references": edges, "cwd_contract": cwd, "policy_assignments": policy,
                        "dispatch_commands": commands, "external_usage": "UNKNOWN; preserve entrypoint"})
    if expected_count is not None and len(records) != expected_count:
        issues.append(f"launcher count mismatch: {len(records)} != {expected_count}")
    created = {t["task"] for t in tasks if t["action"] == "create"}
    deleted = {t["task"] for t in tasks if t["action"] == "delete"}
    resolved_created = {t["resolved_task"] for t in tasks if t["action"] == "create" and t["resolution"] != "UNRESOLVED"}
    resolved_deleted = {t["resolved_task"] for t in tasks if t["action"] == "delete" and t["resolution"] != "UNRESOLVED"}
    present = {r["path"] for r in records}
    contract = {"status": "UNPROVEN", "cause": "both MockExam source files required",
                "registered": [], "unregistered": [], "unmatched": []}
    if {_MOCK_REGISTER, _MOCK_UNREGISTER} <= present:
        scoped = [t for t in tasks if t["source"] in {_MOCK_REGISTER, _MOCK_UNREGISTER}]
        if any(t["resolution"] == "UNRESOLVED" for t in scoped):
            contract["cause"] = "unresolved MockExam task names"
        else:
            registered = {t["resolved_task"] for t in scoped if t["action"] == "create"}
            unregistered = {t["resolved_task"] for t in scoped if t["action"] == "delete"}
            contract = {"status": "PROVEN", "cause": "literal source names only; not live scheduler state",
                        "registered": sorted(registered), "unregistered": sorted(unregistered),
                        "unmatched": sorted(registered ^ unregistered)}
    return {"unmatched_task_creates_resolved": sorted(resolved_created - resolved_deleted),
            "unmatched_task_deletes_resolved": sorted(resolved_deleted - resolved_created),
            "unresolved_tasks": [t for t in tasks if t["resolution"] == "UNRESOLVED"],
            "mockexam_task_contract": contract, "checked": len(records), "powershell": sum(p.suffix.lower() == ".ps1" for p in launchers),
            "launchers": records, "tasks": tasks, "unmatched_task_creates": sorted(created - deleted),
            "unmatched_task_deletes": sorted(deleted - created), "issues": issues, "ok": not issues,
            "limits": "Static references/bindings, not a shell interpreter. No launcher execution, host env expansion, "
                      "scheduler state, or retirement proof. Task asymmetry requires operational review, not automatic edits."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--expected-count", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-mockexam-known-contract", action="store_true")
    args = parser.parse_args()
    result = audit(args.root, expected_count=args.expected_count)
    if args.assert_mockexam_known_contract:
        assert_mockexam_known_contract(result)
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else
          f"Windows launchers: {result['checked']} checked, {len(result['issues'])} issue(s)")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
