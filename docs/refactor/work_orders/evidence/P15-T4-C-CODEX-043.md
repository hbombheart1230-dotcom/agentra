# Agentra P1.5 T4-C — Codex independent Strategist audit

**Audit report supplied by user, 2026-10-15 KST.** Audit detached FINAL `ac4642dc265811bf7ff56e32adbadf8203fed771` vs BASE `8acedae23e64c11b958556e7835b4ebf5e404e73`; clean clone, no implementation changes. **T4-C_FINAL ACCEPT / T4-D GO.** Recorded from Codex report, not falsely attributed to a GPT re-execution.

| Gate | Codex result / scope |
| --- | --- |
| STRUCTURAL_PARITY | PASS: 22 ledger segments/13 Owners exactly reconstruct BASE strategist_node AST, unchanged other defs and LLM boundary; structural tests **11 PASS** |
| DECISION_PARITY / STATE_EVENT_PARITY | PASS: native order/seams, State writes, output parity |
| MOCK_LLM_PARITY | PASS: fake ok/error/timeout/raises/error+strict, one fake invocation per test mode; only raises propagates RuntimeError as expected. **REAL_LLM_PARITY_NOT_RUN** |
| GOLDEN_PROVENANCE | PASS: pinned `8acedae` archived BASE reproduced the v3 committed golden natively in Windows with 0 mismatches; no FEATURE output used as BASE |
| FULL_PORTABLE_ORACLE | PASS: 50 archived BASE vs 50 FEATURE records, **1,141 variant IDs**, zero mismatch; output, ordered effects, exception, identity all exact FEATURE==same-host BASE |
| PLATFORM_BOUND_ORACLE | PASS with limitation: all 50 v3 records bound, with Windows separators in evidence; Windows native committed-golden exact replay 0 mismatches; Linux still compares exact FEATURE vs pinned BASE for every variant plus golden effect names/exceptions. Synthetic FEATURE digest and BASE effect-name mutation both rejected |
| OFFLINE_ISOLATION | PASS: socket, HttpClient and curl_cffi blocked; no real LLM, Broker or network in audit |
| FINAL_CI | PASS: code-tested SHA `c7583bf` run **38678362869** SUCCESS; FINAL `ac4642d` run **38679851004** SUCCESS, Linux regression, Windows native replay, exact five required JUnit tests |

**NEW P0/P1:** none.

**P2 newly found — corpus coverage replacement, NOT six independent missing IDs:** v1 `c61caab` had 50 records/1,147 variants/1,115 effects/4 bound; v2 `7a35ba1` and v3 `5201081` have 50 records/1,141 variants/1,118 effects, v3 50 bound. The 29-variant record `test_strategist_reporter_feedback_falls_back_to_reporter_analysis_when_metrics_missing` was replaced by a 23-variant max-token LLM fallback record: **net -6 variants**. The replacement adds three ordered effects (global sentiment plus two news-collection effects: 21 → 24). This is a **lost Reporter-feedback fallback scenario** despite v3 itself passing strict conservation. See [remediation ledger](P15-T4-C-GOLDEN-SCENARIO-GAP-044.md). Do not pretend all v1 scenarios remain in v3 or silently regenerate v3 again.

**Pre-existing P2/open debts** remain: BASE×2/FEATURE×2 independent-session differential **NOT RUN**; REAL_LLM_PARITY_NOT_RUN, REAL_REPORT_PARITY_BLOCKED, NTFS mtime causality, Scanner cross-seed excluded-symbol telemetry, Scanner freeze CLI PYTHONPATH; post-T4 architecture visual approval NOT STARTED. Pristine BASE UEF reproduction reported **86 pass / 20 fail / 2 errors** across the two historical UEF files; not new Strategist failures.

**Decision:** T4-C ACCEPT for deterministic/pure extraction; T4-D Commander/UI may begin *after actual current-HEAD required CI success*. No T5, bulk path reorganization, P1.5.10, Wave D, P1.6, live Broker/LLM/production changes are approved by this review.
