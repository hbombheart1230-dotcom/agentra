# 2026-10-08 — P1.5 Reporting branch consolidation (implementation)

## Single active implementation branch
CANONICAL: `codex/p1.5-reporting`
CANONICAL DESIGN: `design/p1.5-p1.6-modernization`

## Git history proof
The canonical refactor branch was created from `fbfab9b3f56152f08a2ce50e69cc8173496fde7d`.
GitHub compare verified that each previous implementation branch is strictly contained in this lineage:
- P1.5.1: `5193ecd7` (54 commits behind `fbfab9b`, 0 ahead)
- R2-A: `cf25e055` (38 behind, 0 ahead)
- R2-B: `24df850f` (24 behind, 0 ahead)
- R2-C: `602d935` (12 behind, 0 ahead)
- Residual R2-C: `fbfab9b` (exact canonical code source)

The cumulative code changed previously, and the current ref consolidation introduces NO further runtime Python changes.

## Design authority
- Original design `docs/refactor/p1_5_reporting_implementation_packet_v1_0.md` remains on the consolidated design branch.
- Revised `docs/refactor/p1_5_reporting_implementation_packet_v1_1.md` on that design branch requires one owner per responsibility and explicit consumer-backed wrapper retention/retirement.
- v1.1 design is not silently copied into this runtime tree. Implementation changes must reference the canonical design branch at a pinned commit.

## CI + artifacts
- Redirect existing broader Reporting Python 3.12 + seam/UI regression to `codex/p1.5-reporting`.
- Changed-files ZIP uses `git diff HEAD^ HEAD` in an ephemeral GitHub Actions runner rather than a permanent artifacts/* branch.
- Existing patch notes UI canonical JSON and Markdown are appended, preserving history.

## External references / cleanup
Other tranche branches should receive no additional commits and can be deleted after preserved ancestry and dependent PR checks. Existing open CI-only PR #2 still targets the P1.5.1 branch; do NOT delete that base until the PR is closed or retargeted. The GitHub connection in this session offers branch creation/ref updates but no direct delete-ref action; removal has not been performed. CI-only PR #3 and the earlier observability PR #1 are separate and unchanged.

## Safety / status
Production `main`, runtime, Docker, UEF, Supervisor/Executor/broker authority and real orders were untouched.
R2-A/B/C extraction checkpoint PASS remains historical; the full v1.1 P1.5.2 acceptance remains gated.
