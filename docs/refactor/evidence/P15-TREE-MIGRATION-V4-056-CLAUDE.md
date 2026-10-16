# V4-056 — Scanner policy helpers relocation (Claude)

```
WORK_ORDER: V4-056
BASE_SHA: 0a3a224c2da8f8305cdf7f9c296cb0e7fea46766
BRANCH: integration/p15-t4-pr5-convergence-20261015
MOVED: 5/5 -> libs/agents/scanner/policy/        SAFETY_BLOCKED: none
MOVED_5_AND_BLOBS (byte-identical via git mv; old BASE blob == canonical blob):
  symbol_prior: 9bbc39ae6c00d56fad056be3eec6962a726fae29
  blocker_family_overlay: 81d59515d0bae9402d1f3987a39856d329a21166
  repeat_guard: 5f794e544dd0597d36c1f2dee8f474b386df120c
  guidance: 3318a80a01b8b00b29fb2753fa48ed16c9f25387
  compatibility: 323d5a54f5e26cb18c5ea590a8f0b3d2726d8953
ORIGINAL_OWNER_CONSUMERS: only graphs/nodes/scanner_node.py (unmodified, binds the canonical _r3_impl bodies and injects
  its own module as `facade`); referenced in the Wave B ledger (extended allowlist, below); not referenced by the T3 current-owner ledger
IMPORT_MONKEYPATCH_FACADE_SEAMS: each old path is a 3-statement sys.modules identity shim; fresh-interpreter old-first, new-first
  and `from package import` forms give one module object; all functions shared (function __module__ is the canonical module);
  monkeypatch through the old path is visible through the new one; patching a node global (`_clamp`) changes the moved body's
  result (facade late binding preserved)
BASE_FROZEN_CASES: 318 cases through the PUBLIC scanner_node wrappers generated on the pinned BASE tree (git archive) -
  repeat penalty/cooldown across env defaults and clock-injected states, history/normalization, blocker overlay, symbol prior,
  guidance weights and structured bias, monitor policy/frame/compatibility signal, mock override - 41 recorded exceptions,
  input-mutation flag recorded (0 mutations), clock frozen, SCANNER_* env controlled; reproduced exactly on FINAL incl. key order;
  two consecutive FINAL computes identical. Fixture 191 KB (single small JSON)
T3_WAVE_B_-O_NEGATIVE_GATES: Wave B allowlist extended by exactly the five V4 pairs (version "V2-053/054+V4-056", hard-coded,
  strict source-AST shape, no regex fallback); the allowlist test now asserts the exact 5 + 5 mapping; the negative suite and the
  V4 test pass under python -O; T3 current-owner and static-purity gates unchanged and passing
SCANNER_RANK_TOP1_STATE_PARITY: T4-A BASE-frozen scanner_node contract (full State, selected/rank-1) and gates pass unchanged
```
