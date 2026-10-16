# V2-053/054 — GPT scoped structural acceptance (2026-10-16)

**DECISION: V2_SCOPED_ACCEPTED_WITH_FINDINGS.** Scope is the five already-relocated Scanner context modules and their compatibility/test contract only. This is not P1.5 final acceptance, clean broad-suite certification, live trading authorization, or permission for broad refactor.

**PINNED FINAL SHA:** 4c6cddedcfab910181e2fa8a9f7642b628f4f164

## Accepted structural evidence
- Five Scanner V2 BASE/canonical implementation Git blobs were byte-identical, old/new paths resolved to one module object, facade/monkeypatch seams maintained and 136/136 BASE-frozen public Scanner wrapper cases matched.
- Historic Wave B 768/768 passed. The initial fail-open regex owner checker was rejected; the reworked exact five-path AST allowlist rejects 21 mutated source strings and one temp-file mutation. Explicit exceptions work under Python -O and the optimized negative suite is present. Scanner ranking, Rank-1, protected authority files and runtime implementations remained unchanged in the 054 delta.
- Final hosted CI required jobs all SUCCESS: T4 Linux/Windows 38845229579; Reporting/Web/Windows LF 38845229501; Scripts Linux/Windows 38845229604. UI patch-note formats are synchronized.

## Findings and retained debt
1. The retained JUnit/log artifacts show 38 BASE and 37 FINAL failures/errors. The **37 shared observed signatures** matched by test ID, class, terminal location, test location and normalized first cause line; there were no FINAL-only failures *within those reported artifacts*. The 37 errors remain UNFIXED. Raw artifact SHA-256s are in the 054 manifest.
2. **HISTORICAL_RUN_PROVENANCE=BLOCKED.** Neither JUnit nor logs independently authenticate Git SHA and dependency/environment fingerprint. Operator-attributed BASE/FINAL SHAs are not independently established. Do not claim complete semantic-cause equality or authenticated broad-suite parity.
3. The final reviewer disclosed earlier authorship of branch commits. The pinned SHA re-verification provides useful evidence but is not fully disjoint-author independent verification; preserve this audit independence caveat in subsequent release review.
4. The BASE-only generated_at time-boundary flake and other P1.5 broad acceptance gaps are not waived.

GPT judges historical broad-run provenance non-blocking for this limited *structural module relocation*, given direct exact-blob, module identity, frozen wrapper and safety gates. Any newly observed functional/authority regression immediately reopens this decision.

**NEXT ACTIVE WORK:** docs/refactor/work_orders/P15-TREE-MIGRATION-V3-055.md. The HYBRID-7 V3 target remains frozen. Main and trading authority remain frozen.
