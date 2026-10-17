# Independent audit — Monitor role (Claude reviewer; Codex implementer)

```
AUDITED_FINAL_SHA: 602db243dc34eb4995812c3ca5c7d0f5db950667   AUDITED_CODE_SHA: cf2e6622cced71cb39bfcb3b48fd5b3dc0708a48
RUNTIME_BASE: d773709ba2f70471fad9badba4f92400f7818319   START: eeb742a33b16f6271ff364a904e187b470561c7e
CHECKOUT: fresh read-only clone at 602db243 (no edits, no commits there)
VERDICT: PASS_WITH_FINDINGS — no P0 / P1. Integration still requires the Work-owned shared gate repair below.
```

## Checks and results
| Item | Result |
|---|---|
| Scope START..602db243 | only `libs/agents/monitor/**`, 11 `libs/runtime/monitor/*` shims, own test/fixture/script/evidence; no protected, shared-test, workflow, graph or other-lane path |
| 11 blobs | canonical blob == BASE legacy blob for all 11 (10 seeds + `cycle_detail_projection_exit_decision_detail`); max 285 LOC |
| Shims | all 11 pass the strict Wave B source-AST verifier with their exact pair |
| Extra read-model | `cycle_detail_projection_exit_decision_detail`: registered in `path_ledger.json`, consumed by `graphs/nodes/monitor_node.py` via legacy path (unchanged), pure projection of `entry_info`/exit detail fields; no I/O/env/clock tokens ("logging" appears only in docstrings) |
| Mutable alias / callbacks | `signal_explanation` writes trace keys into the passed `grouped_logic_trace` (`score_passed` there is a trace field; the decision `score_passed` is computed in `libs/runtime/intraday_monitor_signals.py`, untouched). `scanner_monitor_handoff_projection` mutates the mapping returned by `facade.build_scanner_monitor_handoff_surface` (use-time facade lookup preserved). Both byte-identical to BASE, so semantics are unchanged; the handoff describes them correctly as preserved in-memory mutation, not purity |
| Decision/execution boundary | entry/exit, trigger, sizing, cascade selection, guard/cooldown/persistence and `monitor_exit/**` not modified |
| BASE fixture | `work_monitor_contracts.py` reads bodies with `git show d773709:<path>` (BASE, not FEATURE); fixture 150,032 B (< 256 KiB) |
| Role tests | 148 PASS; 148 PASS under `python -O` |
| Wave B + shim negatives + T4-B native freeze | 821 PASS |
| Shared T3/T4-B | exactly the 5 reported FAILs reproduced (below) |

## The 5 shared failures: cause and mapping verified
- T4-B `test_inlining_every_owner_reproduces...` and `test_call_sites_pass_exactly_the_declared_inputs`: `_owner_fn` (line 91) parses the legacy shim and raises `KeyError: 'build_scanner_monitor_handoff_for_cycle'`.
- T4-B `test_owner_modules_are_small_pure...` (line 228): `cycle_event_payloads.py: plain import` (the shim's `import sys as _sys`).
- T3 `test_every_historical_owner_function_resolves...` (line 95): `cycle_output_value_state_monitor missing in libs/runtime/monitor/cycle_output_projection.py`.
- T3 `test_all_owner_modules_import_and_obey...` (line 139): `cycle_detail_projection.py: plain import not allowed`.

All 5 are caused only by the gates reading the legacy path, which now holds the identity shim. **Sufficiency check:** in a scratch copy of cf2e6622 with each canonical body copied back onto its legacy path, all 5 pass. The 3 other failures in that copy were history-diff tests that broke because the copy has no Git history; those same tests pass in the real checkout. So the proposed pairs (6 T3 + 5 T4-B = exactly the 11 moved modules, no extras) are complete and exact. Work should resolve only those pairs after strict shim verification and keep every original assertion against the canonical body.

## Findings
- **P2 (Work / integration):** the 5 shared T3/T4-B gate FAILs above stay FAIL until Work repairs the shared resolver. This is a structural integration blocker, not a runtime regression.
- **P2 (implementer):** `libs/agents/monitor/`, `events/` and `projections/` have no `__init__.py` (implicit namespace packages), unlike `scanner`, `strategist` and `reporter`. Imports work, but package discovery and `__file__`-based tools behave differently. The exact agent-package allowlist entry (Work) also still has to be added. Recommend adding regular `__init__.py` docstring packages before integration.
- **P3:** T4-B native replay ran at sample_mod=4 (689/2879 variants executed; all inventory IDs validated); sample_mod=1 was NOT RUN. Real persisted/LLM parity is NOT RUN (inherited BLOCKED).
- **P3:** implementer scratch/TEMP cleanup is outstanding (recorded in its proof_manifest; manual).

Not run by this reviewer: full pytest, Linux, hosted CI, PERF (by order).
