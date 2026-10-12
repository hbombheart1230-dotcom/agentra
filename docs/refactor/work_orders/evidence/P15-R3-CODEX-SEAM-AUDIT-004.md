# R3 Codex seam audit 004 — PASS_WITH_FINDINGS

Audited code SHA: `651220191e4e61506984e6020355d1c411100204`.
Evidence provenance: result supplied by user, not rerun by GPT.

- `test_p152_r3_moved_bodies.py`: 298 passed.
- Seam challenge: 357 direct cases across 57 moved functions; exit 0; 57/57 use-time lookup checks pass.
- Pre-repair comparison was attempted without a working-directory override and ran in operational `C:\Agentra`. Write audit observed an external writer change. This run is INVALID as comparison evidence; its cause/effect is not established. Do not claim live checkout clean and do not rerun tests there.
- Actual historical report/LLM parity: BLOCKED / NOT RUN. Whole pytest NOT RUN in this audit. Prior isolated full suite had 5115 pass, 35 fail, 27 skip, 2 error, 9 deselected (failure nodes same as baseline), plus a separate controlled-mock-lane write finding.
- No code/branch/merge changes made by Codex.

Verdict: PASS_WITH_FINDINGS for R3 seam restoration only. P1.5.2 OPEN; P1.5.3 NOT AUTHORIZED; main merge/live deployment forbidden.
