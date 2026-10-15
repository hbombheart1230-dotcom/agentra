# 2026-10-15 — Scripts Target-Tree Compatibility Audit

- Add read-only static AST guard for 138 relocated Scripts and three existing example wrappers (141 total).
- Verify legacy/canonical file existence, dispatch target paths and manifest conservation; never import or execute target scripts.
- Add four synthetic pytest cases: valid mapping, mismatched CLI dispatch, missing canonical file and non-execution of canonical source.
- Local fixture tests: 4 PASS. Full combined T4/PR5 tests: NOT RUN; Codex independent acceptance required.
- T4, all trading/runtime code, 141 existing wrappers, and eight Config files untouched. PR #5 Draft and unmerged.
- UI patch_notes.json and patch_notes.md appended only; no previous entries modified.
