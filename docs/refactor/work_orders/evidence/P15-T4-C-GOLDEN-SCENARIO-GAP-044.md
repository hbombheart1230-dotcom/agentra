# P1.5 T4-C golden-coverage gap — P2 ledger and closeout requirement

**Status:** P2 OPEN — scenario coverage debt; not an observed production/implementation behavior regression. Origin: independent Codex T4-C audit, 2026-10-15.

## Exact lost and gained coverage

- **Lost when v1 → v2:** the 29-variant record `test_strategist_reporter_feedback_falls_back_to_reporter_analysis_when_metrics_missing` was removed from the selected 50-input fixture.
- **Gained:** one different 23-variant record covering an LLM max-token fallback scenario. This is an exchange, **net -6** rather than simply a six-ID omission from one unchanged golden record.
- Effects: the old record had 21 ordered effects, the new record 24 (global sentiment + two news collection effects).
- Manifest: v1 50/1,147/1,115/4 bound; v2 50/1,141/1,118/0 bound; v3 50/1,141/1,118/50 bound.
- **Crucial distinction:** v3 full 1,141 variant conservation and same-host BASE/FEATURE parity PASS, but does not prove that the **specific** Reporter-feedback fallback remains covered.

## Mandatory closeout — before Wave D/P1.5.11 final acceptance

1. Independently recover the dropped case's exact pre-implementation BASE input from the v1 frozen artifact/capture and distinguish it from the new max-token record; do not fabricate or source from live production.
2. Add a **separate** immutable, pinned-BASE fixture or focused offline test for the Reporter-analysis-fallback path when metrics are missing. Preserve BOTH old fallback and new max-token scenario coverage. Do not silently replace/regenerate v3 to hide the swap.
3. Validate expected Reporter-memory fallback reason, output/state key order, effect order, and no real LLM/network/file writes. For platform-bound evidence use native golden on Windows and exact same-host archived BASE portable oracle on Linux. Require mutation-negative evidence and explicit test accounting as appropriate.
4. Codex independently checks that the lost case is restored to verified test coverage (distinct from current 50-record v3), then records `COVERAGE_GAP_CLOSED` or `BLOCKED`. No claim that REAL_REPORT_PARITY is resolved by synthetic/mocked fixture.
5. Until evidence is complete, retain `T4C_REPORTER_FEEDBACK_FALLBACK_COVERAGE_P2_OPEN`. T4-D pure extraction may proceed; **P1.5 final freeze cannot silently waive** this scenario gap.

Owner: Claude under separately scoped authorized fixture/test closure work; Codex independently audits; GPT/user approve P1.5 final closeout. Do not conflate with full-real Reporter/LLM parity blockers.
