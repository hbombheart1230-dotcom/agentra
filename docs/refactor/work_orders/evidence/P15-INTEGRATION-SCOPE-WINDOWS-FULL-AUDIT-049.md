# Integrated T4-D scope and native-Windows production audit correction

Source prior SHA: `8405ed8343ef2bca87493267322d9095fa659ca7`. Branch: `integration/p15-t4-pr5-convergence-20261015` (the sole active development branch; main is retained as protected default).

## Why the integration T4 Linux gate failed
Historical integration Actions [38716792220](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38716792220) failed 1/15 in `test_p165_t4d_extraction_gates.py::test_t4d_changed_paths_stay_in_commander_ui_scope_and_touch_no_authority_surface`. It compared T4-D BASE `97934d2` directly to integration HEAD, erroneously attributing PR #5 `libs/diagnostics/__init__.py` to T4-D.

Fix preserves T4-D scope, AST replay, golden and authority protections:
1. Compare original immutable `97934d2 .. ad365913` only for T4-D's own changed-path whitelist.
2. Detect pinned T4-D final SHA ancestry before applying the pinned comparison; original pre-final T4 branches still use BASE..HEAD.
3. On integrated HEAD, independently reject any changes after `ad365913` under `graphs/commander_runtime.py`, `libs/runtime/commander/`, `apps/operator_ui/`, forbidden authority prefixes, and T4-D frozen fixture path.
4. Do not deselect/skip the existing structural test or weaken its original allowlist. PR #5 non-T4 changes remain verified by their own Scripts and Reporting contract workflows.

## Why native Windows Reporter job failed after its two baseline tests PASSED
Run [38719306809](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38719306809): `2 passed` in native Windows, but `conftest.py` fast production-write manifest reported MODIFIED *directory metadata only*: `data/originals`, `data/specs` with sentinel size -1 and mtime delta. No specific file content writes were shown in this log. This is a fail-closed safety signal; do NOT mark the prior CI PASS.

Native Windows standalone Q10/Q12 byte-contract CI now sets `PRODUCTION_WRITE_AUDIT_MODE=full`, the repository's existing explicit stronger file scanner that traverses all file paths, checking size+mtime at any depth instead of treating directory mtime alone as file modification. Production-write checks are **not disabled**. If full scan discovers a file write or fails, keep BLOCKED and investigate. Full tier does not attest directory-only changes, so preserve the prior metadata finding as open P2 until root cause proven.

## Gate
- No ZIP CI; UI patch notes/daily patch append-only.
- Re-run mandatory Linux T4 / Windows T4, Scripts Linux/Windows, Reporting/API/Web including Q10/Q12 Windows file audit on the same integrated source SHA.
- After successful CI, local Codex independent recheck of T4 scope and Windows full-audit semantics, then GPT + user final acceptance. No main merge or delete yet.
