# V3-055 GPT scoped structural acceptance — 2026-10-16

**DECISION:** V3_SCOPED_ACCEPTED_WITH_P2_FINDINGS. **AUDITED_SHA:** 6bf7112abc8facaf868916c1d4e7ba0504030b22. **BASE:** 9735c81c29f5aaf2b98a44a03b9c73e30b473f19.

Independent Codex verdict: PASS_WITH_FINDINGS. Remote HEAD and isolated clean checkout matched. All five Scanner read-only Projection canonical bodies had BASE-identical Git Blobs; old/new import and monkeypatch shared module-object identity. T3 Owner contract retained 53/53 prior assertions, the two extra ledger-path aliases fail closed under strict AST with normal/-O mutation counterexamples (12/12). Wave B 768 and old negative suite 32 remain green. BASE-origin 218 cases match FINAL result/key order; those directly cover three pure public modules, not candidate_context_projection and selection_evidence_projection. Those other two are covered by BASE-unchanged 5/5 blobs plus T4-A structural/frozen State/effect and Rank-1 checks (16/16). Codex audit pytest: 864 PASS / 0 FAIL / 0 SKIP. Git comparison has **22 changed paths**, not the earlier GPT-miscounted 23; user changed-only ZIP 22/22 was verified by Codex. BASE fixture JSON is 6,512,156 bytes. Required CI final SHA: T4 Linux/Windows 38863056374, Reporting/Web 38863056382, Scripts Linux/Windows 38863056768; all required jobs SUCCESS, manually skipped diagnostics excluded.

## P2 findings retained, NOT falsely closed
- Claude local 3,611 PASS / 1 SKIP evidence lacks skip node ID/reason. **UNVERIFIED** skip reason; retrieve raw report in a later small evidence task when available, otherwise preserve UNVERIFIED.
- Capture lineage: raw v3_capture.jsonl corresponded to 202 caller cases, but 82 module labels were normalized/reassigned. Codex independently checked 218 BASE-vs-FINAL oracle outputs. Preserve the normalization map and hash of raw source ONLY if available; do not invent missing SHA or call label lineage independently audited.
- Fixture is approximately 6.2 MiB and contains one duplicate input (217 distinct inputs / 218 cases). Optional compact/dedupe optimization is quality debt, not a functional defect; any future canonical fixture rewrite requires exact replay parity and fresh review.
- Inherited V2 debt: 37 recorded broad test failures/errors UNFIXED; retained historical JUnit/log SHA/environment attribution remains BLOCKED, and prior re-review had partial author overlap. No general release certification.

**Scope of approval:** The physical relocation of five Scanner Projection owners and direct compatibility tests only. No production trading, Broker, LLM, Step5C, UEF, Q10/Q12, full P1.5 final acceptance or main merge. If new semantic/safety regression appears, reopen V3.

**NEXT:** Execute docs/refactor/work_orders/P15-TREE-MIGRATION-V4-056.md only, one bounded Scanner R3 helper candidate batch. HYBRID-7 V3 target remains architecturally frozen; the word V4 refers to the fourth IMPLEMENTATION BATCH, not a redesigned tree.
