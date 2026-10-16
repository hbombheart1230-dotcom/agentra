# V2-053 — Scanner context/scoring inputs relocation (Claude)

```
BASE_SHA: 73f2277bfe95fda6d548572e48764966d01661e4
BRANCH: integration/p15-t4-pr5-convergence-20261015
MODULES_ATTEMPTED: 5   MODULES_MOVED: 5   MODULES_BLOCKED: none
ORIGINAL_TO_CANONICAL_BLOB_SHA (byte-identical via git mv):
  libs/runtime/scanner/feature_coverage.py -> libs/agents/scanner/context/feature_coverage.py : 32ad1370df7ed813fe7746f6e7a01531050b4bee
  libs/runtime/scanner/sentiment_inputs.py -> libs/agents/scanner/context/sentiment_inputs.py : f514156e8eac7650140155df9f677065e6bfb38e
  libs/runtime/scanner/scoring_inputs.py -> libs/agents/scanner/context/scoring_inputs.py : b436430ea437ccf0cc52a9a8242f9a13b6aea473
  libs/runtime/scanner/macro_focus.py -> libs/agents/scanner/context/macro_focus.py : 24170e434adbf11ff35c6c0c86a72f2bb6f88c29
  libs/runtime/scanner/macro_chart_fit.py -> libs/agents/scanner/context/macro_chart_fit.py : 7a5828c8b93b7615b1df8024cb2b8dbb514c3479
OLD_NEW_MODULE_IDENTITIES: each old path is a sys.modules shim; old-first, new-first and `from package import` forms
  give the same module object (fresh interpreters); every `_r3_impl` function object is shared; monkeypatch via the
  old path is visible through the new path
CONSUMERS: only graphs/nodes/scanner_node.py (unmodified; T4-A frozen) imports these modules; its wrappers bind the
  canonical functions and inject their own module as `facade`; no dynamic/string imports, CLI/scheduler or pickle use
FROZEN_REPLAY: 136 cases through the PUBLIC Scanner wrappers generated on the pinned BASE tree (git archive) and
  reproduced exactly (incl. 3 frozen exceptions, key order); fixture tests/fixtures/p1_5_v2053_scanner_context/cases.json,
  generator scripts/refactor/p167_v2053_scanner_context_cases.py
SCANNER_RANK_ORACLE: T4-A BASE-frozen scanner_node contract (73 records / sampled variants) passes on the moved tree
GATE_ADAPTATION: tests/test_p154_wave_b_moved_bodies.py now follows an exact-form identity shim to the single canonical
  body before checking the moved-body AST (assertions unchanged; a shim with code is rejected)
```

Five siblings live in `libs/agents/scanner/context/` (plus `__init__.py`); `candidate_risk.py` stays at its V1 location;
no package stubs for other agents. No ranking, selection, Broker, LLM, Supervisor/Executor, State or production-write
path changed.
