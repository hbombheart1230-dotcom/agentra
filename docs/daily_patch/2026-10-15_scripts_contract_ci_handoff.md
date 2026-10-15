# 2026-10-15 — GPT scripts CI and Codex handoff

- Add standalone Python 3.12 Linux/Windows GitHub Actions for 141 static legacy wrapper path checks and four fixture tests; no trading execution or API credentials.
- Locally independently ran four fixture tests in an isolated /tmp archive extraction: 4 PASS.
- Record a minimal Codex Cloud work order for full-checkout static audit and representative offline CLI parity.
- This change is scoped to CI/docs, no T4 branch changes, wrapper removals, broker or runtime changes. PR #5 remains Draft/unmerged.
- GitHub Actions success and full-checkout actual static audit remain PENDING (not claimed).

## Windows CI isolation follow-up

- Initial GitHub Actions: Linux SUCCESS; Windows four assertions PASSED, but the repository-wide production path isolation watchdog failed on directory-only NTFS mtime changes for data/originals and data/specs.
- Static full-checkout wrapper audits passed on both Linux and Windows: moved=138, held=19, wrappers=141, checked=141, issues=[].
- Only synthetic static unit tests moved to RUNNER_TEMP, retaining separate full-checkout audit. This does not weaken repository-wide isolation tests or change the watchdog.
- Updated CI rerun remains a separate acceptance gate.
