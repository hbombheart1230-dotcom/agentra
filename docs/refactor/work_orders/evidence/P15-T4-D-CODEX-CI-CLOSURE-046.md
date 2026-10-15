# T4-D independent Codex audit — post-CI closure evidence
Date: 2026-10-15 KST
T4 HEAD: `ad3659131e804f9fa84b67f3bf6a0a0b2017a064`
Implementation CODE: `0c9936e7cb96f51ab1fc16ce75bc2c35f63db62a`
Status: STRUCTURAL_GATE_CLOSED_BY_GPT_AFTER_CI; NOT P1.5 FINAL ACCEPT

## Evidence provenance
This record transcribes the independent local Codex findings supplied by the project owner in the conversation; it is NOT a claim that GPT freshly reran all tests. Codex initially returned BLOCKED only because final GitHub Actions were still running.

- Independent structural+contract: 15 PASS; focused regression: 93 PASS.
- Native frozen replay: 189 records / 6,456 variants / 0 mismatches.
- 25 moved segments, 11 Owners (40–243 LOC); 6 BASE functions' ASTs reconstructed.
- Exact Unicode/newline/fallback Markdown contract: synthetic offline parity only.
- User-supplied audit identified no new P0/P1 and no change to trading authority routes.
- CODE run [38699806358](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38699806358): SUCCESS.
- FINAL run [38702590672](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38702590672): SUCCESS, both required Linux regression and Windows isolation smoke; T4-D Windows native 5/5 accounting SUCCESS. CI results independently checked with GitHub Actions job metadata.
- With the sole final-CI blocker cleared, GPT accepts the T4-D structural slice as the integration input, without misrepresenting a subsequent Codex ACCEPT submission.

## P2 / not-run retained
- The alleged 16 baseline-vs-feature preexisting failures lack exact IDs and reproduction commands. EVIDENCE_QUALITY_GAP; no independent same-set confirmation.
- T4-C Reporter-feedback fallback coverage displaced a 29-variant scenario with a 23-variant different scenario. Restore old scenario before P1.5 final acceptance.
- REAL_BRIEF_PARITY_NOT_RUN, REAL_REPORT_PARITY_BLOCKED, REAL_LLM_PARITY_NOT_RUN, cross-seed telemetry order, NTFS mtime, and BASE×2/FEATURE×2 differential NOT RUN.
- Scope: no T5, Wave D, P1.5.10, main merge or broad folder move.
