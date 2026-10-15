# V1-052 — Scanner `candidate_risk` relocation (Claude)

```
BASE_SHA: 860207682dc02080260e768587ac5f401f8c902a
IMPLEMENTED_SHA: (the commit that contains this file; reported in the delivery message)
BRANCH: integration/p15-t4-pr5-convergence-20261015
SCOPE: V1-SCANNER-CANDIDATE-RISK
OLD_BODY_BLOB_SHA: 8dea30aebd811d8d9f214c8bca7bef8ea41fa3f9 (libs/runtime/scanner/candidate_risk.py @ BASE)
NEW_BODY_BLOB_SHA: 8dea30aebd811d8d9f214c8bca7bef8ea41fa3f9 (libs/agents/scanner/candidate_risk.py; byte-identical, `git mv`)
OLD_NEW_MODULE_IDENTITY: libs.runtime.scanner.candidate_risk is libs.agents.scanner.candidate_risk (sys.modules replacement shim);
  verified old-first, new-first, `from package import` and package attribute, each in a fresh interpreter
DYNAMIC_AND_MONKEYPATCH_CONSUMERS: one static consumer `graphs/nodes/scanner_node.py` (`from ...candidate_risk import
  resolve_candidate_base_risk`, T4-A frozen file left unmodified; binding is the canonical function object) and
  `tests/test_scanner_candidate_risk.py`; no string/dynamic importlib reference outside docs/evidence JSON; patching a
  private (`_clamp`) through the old path is visible through the new path and in the function (shared module dict)
TARGETED_TESTS: tests/test_p166_v1052_candidate_risk_migration.py (8 tests incl. 115 frozen inputs executed on the BASE
  body, equality incl. key order), tests/test_scanner_candidate_risk.py, T4-A scanner gates/freeze, T4-B/C/D gates,
  p152/p154/p155/p156/p159 scope-ABI gates, consumer inventory
NO_RANK_SEMANTICS_CHANGE: no scanner_node/ranking/selected-rank file touched; the T4-A frozen Scanner contract passes;
  `libs/agents/scanner` holds only __init__.py and candidate_risk.py (no rank owner)
BROKER_LLM_WRITE_GUARDS: pure helper (no IO/Broker/LLM/env); test forbids edits to execution/supervisor/approval/risk/llm/kiwoom/commander/scanner_node paths
```

Notes: the shim file contains no function or copy of the implementation. A second `libs/agents` package was created
only as `libs/agents/__init__.py` + `libs/agents/scanner/__init__.py` (the singular `libs/agent/` package is unrelated and
untouched). Next: independent audit, then V2.
