# Scripts Target-Tree Compatibility Audit — 2026-10-15

## Purpose

Prevent regression of the 138 relocated research/diagnostic/maintenance CLI entrypoints and three pre-existing example compatibility wrappers while Claude's independent T4 branch continues. This is a lightweight, **read-only static preflight**, not a substitute for the recorded 828 CLI parity checks, broader pytest, or future combined T4/PR5 acceptance.

## Files

- `scripts/diagnostics/audit_target_tree_compat.py`: verifies that every moved manifest pair still has a syntactically valid legacy wrapper and canonical module; verifies literal import and `__main__` dispatch targets; checks moved/held conservation and 141-root-wrapper inventory.
- `tests/test_scripts_target_tree_compat_audit.py`: four synthetic fixture tests; valid layout, wrong CLI target, missing canonical file and proof canonical source is parsed but never executed.
- Input: `docs/refactor/2026-10-15_scripts_bulk_manifest.json` (existing immutable inventory for this batch).

## How to run

```bash
python scripts/diagnostics/audit_target_tree_compat.py --json
python -m pytest tests/test_scripts_target_tree_compat_audit.py -q
```

## Safety and scope

- Static AST parsing only: **no target module import, CLI execution, network call, order submission, or writing reports/artifacts**.
- Preserves all 141 existing public CLI wrappers and the 138 relocated implementations. No wrapper removal until a separately approved CLI-retirement policy and dynamic-consumer evidence.
- No runtime/Graph/Reporter code, T4 branch, broker, Supervisor, Executor, Step5C authority or production settings changed.
- This audit checks literal dispatch contracts and file presence/syntax. It does **not** prove CLI behavior, monkeypatch equivalence, all dynamic calls, or Windows Scheduler behavior.
- Four fixture tests passed locally; **full Agentra checkout checks not run in this GPT environment**. Codex should run the actual repository audit and related regression before any merge approval.
- Keep PR #5 Draft; T4 remains independent and has not been merged. Update the UI JSON/Markdown histories append-only.
