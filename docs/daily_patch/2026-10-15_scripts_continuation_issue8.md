# 2026-10-15 - Issue #8 Scripts continuation

Status: SCRIPTS_CONTINUATION_IN_PROGRESS. Issue #6 did not close the remaining Scripts scope.

- Classified all 42 remaining implementations, 8 existing delegates, 20 Windows/shell sources, 19 holds and 141 wrappers using prior evidence plus bounded current references.
- Holds: KEEP 15, TEST_BLOCKED 3, RELOCATION_CANDIDATE_AFTER_GATE 1. No deletion or physical move authorized.
- Fixed proven wrapper-auditor false accepts for disconnected ABI aliases and non-main CLI run_name; validate actual executable AST, not comments/target strings alone. All 141 current wrappers retained and pass.
- Added source-only Windows invocation/CWD/policy/task auditor and five fixtures. Existing schedule register/unregister Q12 asymmetry is an operational review item; no live launcher or task policy changed.
- Added Windows CI Parser.ParseFile syntax-only checks for six PowerShell files; never execute live launchers. Local isolated source fixtures: 12 PASS. Native Windows evidence comes from the new CI job.
- Prior 138-script/828-case and broad regression validation not repeated. No T4, Reporting Batch3, broker/guard/runtime/strategy/Config/deployment edits.
- Wrapper retirement and further physical layout changes remain blocked on ARCH_CONVERGENCE_APPROVED and consumer/retirement policy. Issue #9 UI work not started.
- Report: docs/refactor/2026-10-15_scripts_continuation_issue8.md.
- Evidence: docs/refactor/2026-10-15_scripts_remaining_dispositions.json.
