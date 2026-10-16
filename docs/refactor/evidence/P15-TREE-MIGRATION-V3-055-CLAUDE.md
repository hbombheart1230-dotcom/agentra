# V3-055 — Scanner read-only projections relocation (Claude)

```
BASE_SHA: 9735c81c29f5aaf2b98a44a03b9c73e30b473f19
BRANCH: integration/p15-t4-pr5-convergence-20261015
ATTEMPTED_5: candidate_context_projection, control_eligibility, output_payloads, output_snapshots, selection_evidence_projection
MOVED: all 5      SAFETY_BLOCKED: none
OLD_NEW_GIT_BLOB_PARITY (byte-identical via git mv; old BASE blob == canonical blob):
  candidate_context_projection: 15fd6fc26a511cf648d886e9c7668e8b019f13e0
  control_eligibility: d47013045a37b97a6a1b5d50e067934b628d3251
  output_payloads: fe5e34d58aecb7972adc02e0faa8c89eeb8555f0
  output_snapshots: 02ef48a408338fcb010e82241ef2c694b039979e
  selection_evidence_projection: bf20e9af5ec4988e7fef831b0cbb3e44644f6914
MODULE_IDENTITY_AND_PATCH_SEAMS: each old path is a 3-statement sys.modules identity shim; fresh-interpreter old-first,
  new-first and `from package import` forms give one module object; all functions shared; monkeypatch via the old path is
  visible through the new path. Each shim also passes the same strict source-AST verifier as the V2 shims (exact shape,
  mapping hard-coded in the test) and mutation checks (extra raise, extra import, wrong canonical target).
CONSUMERS: graphs/nodes/scanner_node.py (unmodified; every imported name is the canonical object), tests
  test_ai_effectiveness_provenance, test_q9_start_gate, test_quant_factors; the second-pass ledger references two owners
  but reads an immutable stage snapshot, its gates pass unchanged
BASE_FROZEN_PROJECTION_CASES: 218 cases (202 real caller inputs and BASE results recorded on the pinned BASE tree while the
  existing Scanner/quant/Q9 tests ran + 16 edge inputs for the pure public functions) reproduced exactly through the old and
  the new path, incl. JSON key order. The two facade-body modules (candidate_context, selection_evidence) are verified through the T4-A
  BASE-frozen scanner_node contract (full State and event order) which passes unchanged.
RANK_TOP1_PARITY: T4-A scanner_node contract/freeze and gates pass; no ranking/selection file touched
WAVE_B: 768/768 unchanged; strict-verifier negatives and V3 tests also pass under python -O
```

The Wave B allowlist was NOT extended: none of the five owners appears in the Wave B ledger, so the fail-closed allowlist and
its 768 cases are untouched. `libs/agents/scanner/` now holds `candidate_risk.py`, `context/` and `projections/`; no other
agent packages were created.
