# Agentra FAST-3 C01 — Codex B single-file execution order (B1–B8)

**C03 issuance:** 2026-10-30, replacement of fully REMOTE_DONE B1–B10 order blob `7b633cf2eabd65be4b489906c0d6732a953527a0`. This order is **NEW**; all previous B1–B10 are REMOTE_DONE, never repeat. Actor: Codex B exclusively. Canonical `integration/p1.5`, authorized branch `work/p15-b-operator-structure-20261022`. Read **this C01 file only** as assignment. No RF/INDEX/T00/D00/C03/queue/HANDOFF exploration or self-selection.

**Preflight:** fetch origin; record exact canonical HEAD, C01 blob, owner remote HEAD and current local B SHA before each task. Verified B source blob `fdd9948f2264a63344bb6a8807ea5851fcf686bb` at remote B HEAD `30a28fffc2c07274206e63717ff1f1561d5f941e`. The SOURCE below is 1018 lines (Python splitlines count; Git blob authoritative). Every listed target module was 404 on B remote; no A source/target overlap. Check current B source blob/target at run start: if another runner already delivered an item, mark REMOTE_DONE without rework or old-PASS rerun; continue remaining safe items.

**Implementation contract for EVERY item:** Move the **entire existing calculation BODY**, not copy it, into the named TARGET function. SOURCE retains the **same public/private name, signature, defaults and thin delegation wrapper**. Target signature may append keyword-only `facade`; call `facade=sys.modules[__name__]` (SOURCE already imports `sys as _r3_sys`). Every SOURCE global/helper used in the moved body must be resolved **at invocation** via `facade.<name>` (including `_base_output`, `validate_artifact`, `_dict`, `_clip`, other build_* and imported projection helpers), never import the facade back at module import time; retain nested closures, lazy evaluation, dict insertion order, exceptions, alias/copy identity and monkeypatch seams. No IO/network/Broker/Guard/Supervisor/Executor/Step5C/UEF/RunLab effect changes. For golden fixtures capture original SOURCE output before editing with fixed clock (`_utc_now_iso`) and compare exact ordered dict/JSON against moved version; do not call live services. Use 3–4 targeted fixture cases per item, including at least one negative/patch case. Existing tests `tests/test_rf044_contract_facade.py`, `tests/test_rf044_executor_error_serialization.py`, `tests/test_rf044_executor_input_immutability.py`, `tests/test_rf044_supervisor_blocked_consumer.py` are regression references, not frozen oracles to edit.

**Delivery:** use prepared `.venv/bin/python -m pytest -q -p no:cacheprovider <one new targeted test path>` normal exit0 (or equivalent isolated stdlib smoke if pytest unavailable). `python -O`, full peer, all-RF hosted CI are NOT required by D00 FAST-3. Commit **code/tests only**, push normal non-force to **B branch only**, verify remote ref SHA and SOURCE/TARGET/TEST blobs after every push. A terminal HTTPS credential failure is PUSH_BLOCKED only: preserve local commit; use approved GitHub exact-tree write path only if the exact reviewed tree can be transmitted and verified; otherwise report LOCAL_ONLY, keep moving to next safe item without overwriting commits. No probe commits. Never touch D00/C01/C02/RF/STATUS/C04/C05/HANDOFF or A branch. A task that is safety blocked must not stop the other seven. Final Issue #12: actual START_KST/END_KST, canonical/order/owner SHAs, each B1–B8 result, source before/after LOC/blob, targeted normal exit, push SHA or error, FIRST_BLOCKER and NEXT. C03 supply is not G1/G2/G3 or RF DONE.

### B1 — RF-044 | SOURCE `libs/contracts/agent_outputs.py::build_strategist_output_artifact` (remote blob `fdd9948f2264a63344bb6a8807ea5851fcf686bb`, L294–315) → TARGET `libs/contracts/agent_output_parts/artifact_build_strategist.py::build_strategist_output_artifact`

**BODY:** Move the entire 22-line pure strategist artifact assembly: strategist_market_news_inputs → _base_output → strategist_decision_theme_policy_facts → strategist_plan_horizon_facts → ordered strategist_artifact_* merges → validate_artifact. Keep original evaluation order and all return keys; do not change strategist decision/policy.

**3–4 targeted fixtures (input → expected):** state={} → agent='strategist', status='ok'; state={'strategist_blocked':True} → status='blocked'; fake strategist_output/selected and market context → exactly equal ordered artifact before/after; patch facade.validate_artifact spy → called once.

**Test:** `tests/test_p15_rf044_strategist_artifact_builder_owner.py`; baseline vs moved output equality, insertion order, original signature and caller monkeypatch seam. On failure, record exact failing fixture and leave item BLOCKED, then B2; never workaround by changing safety/effect contracts. **Push:** code/test only; verify remote ref plus this SOURCE, TARGET and TEST blobs.

### B2 — RF-044 | SOURCE `libs/contracts/agent_outputs.py::build_scanner_output_artifact` (remote blob `fdd9948f2264a63344bb6a8807ea5851fcf686bb`, L316–392) → TARGET `libs/contracts/agent_output_parts/artifact_build_scanner.py::build_scanner_output_artifact`

**BODY:** Move the full scanner read-only candidate-preview/rank/score/bias/provenance composition, including scanner_row_feature_sources loop, candidate_visibility_limit, runner-up lookup, dict comprehensions and ordered scanner_artifact_* merges. No scanner ranking or policy modification.

**3–4 targeted fixtures (input → expected):** empty state → agent='scanner' and same ordered keys as baseline; ranked candidates with 2 symbols → original preview/rank/score order unchanged; scanner_output with visibility limit 1 → preview truncation parity; patch facade._scanner_candidate_visibility_limit spy and verify call-time lookup.

**Test:** `tests/test_p15_rf044_scanner_artifact_builder_owner.py`; baseline vs moved output equality, insertion order, original signature and caller monkeypatch seam. On failure, record exact failing fixture and leave item BLOCKED, then B3; never workaround by changing safety/effect contracts. **Push:** code/test only; verify remote ref plus this SOURCE, TARGET and TEST blobs.

### B3 — RF-044 | SOURCE `libs/contracts/agent_outputs.py::build_monitor_output_artifact` (remote blob `fdd9948f2264a63344bb6a8807ea5851fcf686bb`, L393–465) → TARGET `libs/contracts/agent_output_parts/artifact_build_monitor.py::build_monitor_output_artifact`

**BODY:** Move entire read-only monitor artifact builder with its five nested _first_trace_{dict,list,text,bool,value} closures, no_trade fallback, focus projection, decision_rule_evidence, memory_bias_application and ordered monitor_artifact_* merges. Keep nested closures local to moved body and preserve trace precedence/None-vs-empty.

**3–4 targeted fixtures (input → expected):** empty state → agent='monitor' and original schema/order; two trace sources with conflicting keys → first nonempty dict/list/text/bool/value precedence unchanged; NOOP/no-trade fallback → same reason surface; patch facade.monitor_decision_rule_evidence spy, compare exact baseline artifact.

**Test:** `tests/test_p15_rf044_monitor_artifact_builder_owner.py`; baseline vs moved output equality, insertion order, original signature and caller monkeypatch seam. On failure, record exact failing fixture and leave item BLOCKED, then B4; never workaround by changing safety/effect contracts. **Push:** code/test only; verify remote ref plus this SOURCE, TARGET and TEST blobs.

### B4 — RF-044 | SOURCE `libs/contracts/agent_outputs.py::build_supervisor_output_artifact` (remote blob `fdd9948f2264a63344bb6a8807ea5851fcf686bb`, L466–504) → TARGET `libs/contracts/agent_output_parts/artifact_build_supervisor_executor.py::build_supervisor_output_artifact`

**BODY:** Move only pure serialization of supplied order/allowed/reason/details to output dict. Preserve blocked/approve decision, qty conversion, guard_reason strings, validation call and schema; never call Supervisor/Guard or submit an order.

**3–4 targeted fixtures (input → expected):** order={'action':'BUY','symbol':'005930','qty':2}, allowed=False, reason='risk' → agent supervisor, status blocked, approval_result False, decision block, qty 2; same order allowed=True → approve; details={'k':1} → copied blocked_allowed_details; patch facade.validate_artifact spy, compare baseline.

**Test:** `tests/test_p15_rf044_supervisor_artifact_builder_owner.py`; baseline vs moved output equality, insertion order, original signature and caller monkeypatch seam. On failure, record exact failing fixture and leave item BLOCKED, then B5; never workaround by changing safety/effect contracts. **Push:** code/test only; verify remote ref plus this SOURCE, TARGET and TEST blobs.

### B5 — RF-044 | SOURCE `libs/contracts/agent_outputs.py::build_executor_output_artifact` (remote blob `fdd9948f2264a63344bb6a8807ea5851fcf686bb`, L505–628) → TARGET `libs/contracts/agent_output_parts/artifact_build_supervisor_executor.py::build_executor_output_artifact`

**BODY:** Move only supplied execution/order result serialization; preserve all nested broker_outcome UNKNOWN, intent_claim, reconciliation, quote, ord_no fallback, order_request_summary, final_execution_status and validation fields in original order. This is output projection only: NO broker calls, order/Guard/Step5C changes or live tests.

**3–4 targeted fixtures (input → expected):** execution={'allowed':False,'status':'rejected','reason':'x'}, order={'action':'BUY','qty':1} → execution_ok False, final_execution_status rejected; execution={'allowed':True,'execution_ok':True,'broker_outcome':'UNKNOWN'} → broker_outcome UNKNOWN; nested response_payload ord_no fallback → same ord_no; original execution/order dicts unchanged, exact golden parity.

**Test:** `tests/test_p15_rf044_executor_artifact_builder_owner.py`; baseline vs moved output equality, insertion order, original signature and caller monkeypatch seam. On failure, record exact failing fixture and leave item BLOCKED, then B6; never workaround by changing safety/effect contracts. **Push:** code/test only; verify remote ref plus this SOURCE, TARGET and TEST blobs.

### B6 — RF-044 | SOURCE `libs/contracts/agent_outputs.py::_build_commander_shadow_artifact_summary` (remote blob `fdd9948f2264a63344bb6a8807ea5851fcf686bb`, L629–650) → TARGET `libs/contracts/agent_output_parts/artifact_build_shadow.py::build_commander_shadow_artifact_summary`

**BODY:** Move try/except read-only summary delegation to facade.build_commander_shadow_artifact with mode/phase/path/status/reason string defaults. Preserve broad except Exception → {} and patch-at-call-time seam; do not change commander decisions.

**3–4 targeted fixtures (input → expected):** patch facade.build_commander_shadow_artifact return {'x':1} → identical dict; patch it to raise RuntimeError → {}; status='' → forwarded 'ok'; mode/phase/path None → forwarded empty strings.

**Test:** `tests/test_p15_rf044_shadow_summary_builder_owner.py`; baseline vs moved output equality, insertion order, original signature and caller monkeypatch seam. On failure, record exact failing fixture and leave item BLOCKED, then B7; never workaround by changing safety/effect contracts. **Push:** code/test only; verify remote ref plus this SOURCE, TARGET and TEST blobs.

### B7 — RF-044 | SOURCE `libs/contracts/agent_outputs.py::build_commander_output_artifact` (remote blob `fdd9948f2264a63344bb6a8807ea5851fcf686bb`, L651–704) → TARGET `libs/contracts/agent_output_parts/artifact_build_commander.py::build_commander_output_artifact`

**BODY:** Move full read-only Commander artifact composition: route_runtime_facts, decision_refresh_facts, applied_policy_provenance, observability fallback, shadow observations, invocation/source classification, ordered commander_artifact_* merges, validation. Preserve actual_strategist_invocation None fallback, cached vs fresh and route keys; no decision routing effect.

**3–4 targeted fixtures (input → expected):** empty state, mode='shadow', phase='test', path='none', status='ok' → agent commander and exact baseline ordered artifact; strategist_cache_used true → actual_strategy_source cached_strategist; selected_route monitor_only with no invocation → actual_strategy_source none; monkeypatch facade.commander_route_runtime_facts and compare call-time parity.

**Test:** `tests/test_p15_rf044_commander_artifact_builder_owner.py`; baseline vs moved output equality, insertion order, original signature and caller monkeypatch seam. On failure, record exact failing fixture and leave item BLOCKED, then B8; never workaround by changing safety/effect contracts. **Push:** code/test only; verify remote ref plus this SOURCE, TARGET and TEST blobs.

### B8 — RF-044 | SOURCE `libs/contracts/agent_outputs.py::build_commander_shadow_artifact` (remote blob `fdd9948f2264a63344bb6a8807ea5851fcf686bb`, L900–1018) → TARGET `libs/contracts/agent_output_parts/artifact_build_shadow.py::build_commander_shadow_artifact`

**BODY:** Move entire 120-line read-only shadow assembly: observations/runtime/gate/context, no_trade_reason, recommendation/advice/gap, before/after snapshots, end-of-cycle summary, comparison text, validation. Preserve original call order, reference identity and exact strings; NO execution or integration into real decisions.

**3–4 targeted fixtures (input → expected):** empty state, mode='shadow', phase='test', path='none', status='ok' → mode shadow, decision OBSERVE_ONLY, same baseline schema; mock monitor/selected with symbol → identical comparison_summary and symbol; injected actual_runtime monitor_decision='WAIT' → comparison text exact; patch facade._commander_shadow_observations spy and verify use-time seam.

**Test:** `tests/test_p15_rf044_shadow_artifact_builder_owner.py`; baseline vs moved output equality, insertion order, original signature and caller monkeypatch seam. On failure, record exact failing fixture and leave item BLOCKED, then B1–B7 blocked recheck; never workaround by changing safety/effect contracts. **Push:** code/test only; verify remote ref plus this SOURCE, TARGET and TEST blobs.

## KEEP / verified scope / reserve

KEEP as justified: `_utc_now_iso`, `_run_ts`, `_run_day`, `_base_output` remain clock/runtime identity composition; existing `_monitor_decision_summary`, `_phase`, `_parse_day_from_timestamp`, `_required_keys_for_agent`, `_required_keys_for_artifact`, `validate_artifact`, shadow helper wrappers and already split owner modules are REMOTE_DONE; never reassign them. B1–B8 are **read-only artifact assembly**: no Broker/Guard/Supervisor/Executor execution, order decisions or runtime deployment. Any observed effect/ownership conflict is SAFETY_BLOCKED item-only, not permission to touch protected code. 

**RESERVE_VERIFIED=0 / RESERVE_NOT_VERIFIED=6**: candidate RF-044 owner helpers in other modules have not passed source/target/KEEP necessity checks; not actionable and B must not self-select. C03 must analyze new real bodies for next supply. **FIRST_BLOCKER if no safe parity:** report exact function/source/fixture and continue next item. **NEXT:** C04 selective integration at exact pushed B SHA, C05 G1/G2/G3 acceptance; C03 alone replenishes C01.
