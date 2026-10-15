# 2026-10-15 — Codex REWORK targeted P1 / P2 resolution

Integration base under audit: `e207b612ec9ad6aae3b89d4eb2b507f30c7d0dcd` (merge T4 + PR #5). Independent Codex verdict: **REWORK**, no P1/P2 waivers.

- **P1 ZIP policy conflict:** removed `.github/workflows/p15-integration-changed-files-bundle.yml` from Git tree. Historical workflow run `38716792551` did produce a ZIP, but no future integration-CI packaging/upload is authorized. The binding `CURRENT.md` rule remains: `No ZIP / CI packaging forbidden; user patch archive external only`. The user's changed-files-only ZIP requirement is fulfilled outside repository CI.
- **P2 Windows LF byte contract:** exact-string JSON contract at `tests/test_baseline_shared_owners.py::test_pipeline_io_facades_preserve_bytes_and_error_contract` expects terminal LF. `Path.write_text` on Windows previously translated newlines to CRLF; set `newline="\\n"` explicitly in `libs/reporting/baseline_artifact_io.py`. This is an intentional Windows-only byte normalization to the already asserted contract, not a change to JSON shape, strategy or trading authorization.
- Add `baseline-lf-windows-native` required job in `.github/workflows/p15-integration-crossbranch-compat.yml` executing the same parametrized test under native Windows. Prior audit 106 PASS / 2 FAIL and patch-note 5 PASS were observed on old HEAD; do not claim rerun results until updated CI is SUCCESS.
- Trading/UEF/Step5C/UNKNOWN/real Broker/LLM paths, T4 fixtures and `main` unchanged; no large folder moves. 
- T4 full integrated Linux/Windows CI must be SUCCESS at the code SHA before integration acceptance; after that local Codex independent recheck required.

## Immediate correction after first updated SHA CI

- Previous SHA `c1f7323bb6187cc78bfb053c04d1205712a8dd29` introduced a literal backslash-n in a comment, accidentally commenting out the writer invocation. Linux and Windows Q10/Q12 baseline tests failed with FileNotFoundError; this was NOT a newline comparison failure. This error was introduced by GPT and is not an inherited project defect.
- Corrective change restores a real source newline before the active `path.write_text(..., newline="\\n")` call. No change to other source modules. First updated CI failure remains in evidence as failed, not PASS.
- Required next test: both Q10/Q12 native-Windows parameterizations and Linux Reporting compatibility PASS at corrective SHA. P1 policy removal remains intact. No extra ZIP CI.
