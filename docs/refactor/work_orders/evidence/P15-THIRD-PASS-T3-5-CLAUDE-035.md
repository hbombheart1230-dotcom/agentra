# P15 Third Pass T3.5 — Cross-agent output contract refactor (Claude)

BASE `eb53dc1fe56c2a70a21271faf2f3c25c9711e309`; hard entry gate verified before any edit: GitHub Actions run 38514409185 on exactly this SHA = **Linux regression SUCCESS + Windows harness isolation smoke SUCCESS**; Codex T3.2 ACCEPT (export-safe summary P2 CLOSED, file-body retention P2 CLOSED, strict containment PASS, no new P0/P1/P2). Scope: `libs/contracts/agent_outputs.py` (canonical public contract facade) and new contract-owned stage modules in `libs/contracts/`, tests, one CI gate step, docs. **No** change to Broker/real LLM/production trading, Supervisor approval authority, Executor order execution, Step5C CAS/UNKNOWN quarantine, `graphs/`, `apps/`, `libs/runtime/`, `main`, live `C:\Agentra`, Q12 worktrees, production reports, Docker or scheduler. REAL_REPORT_PARITY_BLOCKED remains OPEN; NTFS settle P2 UNRESOLVED; T4/T5/Wave D NOT STARTED.

## 1. Result (before / after)

| Public builder (names and signatures unchanged) | LOC BASE | LOC now |
|---|---|---|
| `build_monitor_output_artifact` | 807 | 71 |
| `build_strategist_output_artifact` | 528 | 20 |
| `build_scanner_output_artifact` | 464 | 75 |
| `build_commander_output_artifact` | 356 | 52 |
| `libs/contracts/agent_outputs.py` | 3,864 lines | 1,916 lines |

Largest remaining functions in the touched area: `build_executor_output_artifact` 122 and `build_commander_shadow_artifact` 119 (out of scope, unchanged); largest new stage `monitor_decision_rule_evidence` 201 LOC (SAFETY_LOCK below). All new modules are <= 350 lines (max 316).

## 2. New module responsibilities (all under `libs/contracts/`)

| Module | Lines | Responsibility |
|---|---|---|
| `agent_output_values.py` | 93 | pure value normalisers (`_clip`, `_dict`, `_listify`, `_safe_int`...) moved verbatim, re-exported by the facade under the same names |
| `strategist_output_context.py` | 316 | market/news inputs, decision/theme/policy facts, plan/horizon facts (3 stages, records) |
| `strategist_output_fields.py` / `strategist_output_plan_fields.py` | 254 / 130 | ordered artifact field groups: market/playbook, frame, theme/news/fallback, commander context, horizon; plan/policy, traces/handoff/feedback, LLM/policy/bias, refs/macro |
| `scanner_output_context.py` | 299 | row/feature sources, applied-policy evidence, policy bias evidence |
| `scanner_output_fields.py` | 227 | pool/ranking, policy/compatibility, bias trace, selection trace, policy guard, refs/preview field groups |
| `monitor_output_context.py` | 186 | state surface sources, no-trade policy trace, entry cascade/handoff, focus projection |
| `monitor_output_decision.py` | 250 | decision-rule evidence (exit / hold / entry rule evaluation facts) |
| `monitor_output_memory_bias.py` | 123 | memory-bias application (hold / exit / entry) and commander memory trace |
| `monitor_output_fields.py` / `monitor_output_policy_fields.py` / `monitor_output_exit_fields.py` | 95 / 116 / 223 | ordered artifact field groups: decision/no-trade/handoff, policy/memory/signal, trace/price/exit metrics/PnL |
| `commander_output_context.py` | 132 | route / runtime / portfolio facts incl. shadow summary and selected route |
| `commander_output_policy.py` | 160 | decision summary & refresh facts, applied-policy provenance |
| `commander_output_fields.py` | 191 | ordered artifact field groups: route, decision, shadow/refresh, policy, observability/checkpoints |

Final artifact assembly (`_base_output`, the `artifact.update({**stage_fields...})` order), the remaining runtime surface calls
(`build_*_surface`, `build_*_memory_application_trace`) and `validate_artifact` stay in the public builders in `agent_outputs.py`:
the facade remains the single schema/validation authority; no second schema source and no output authority moved into graphs or
runtime agents. Stage functions are verbatim statement runs (typed `NamedTuple` records for multi-output stages, field order =
legacy positional order) or verbatim dict item ranges (`**stage(...)` in the same key order). Module globals still owned by the
facade (`_utc_now_iso`, `_base_output`, `_commander_shadow_*`, the imported runtime builders) are resolved at use time as
`facade.NAME` exactly like earlier stages (monkeypatch seams intact); only the pure value normalisers are imported directly.

## 3. Evidence

BASE-frozen fixtures were committed **before** any implementation change (`44333fd`): 148 inputs captured on BASE from the full offline suite (strategist 16, scanner 20, monitor 22, commander 46, commander shadow 24, supervisor 10, executor 10) plus a deterministic single-key variant corpus (18,497 variants: drop / null / empty of every top-level key, nested key drops, commander route x status x phase x runtime-status x reason grid). Frozen under a controlled clock: exact output bytes with insertion order, input non-mutation, exceptions, and the use-time runtime-dependency call trace.

| Check | Result |
|---|---|
| Replay of the full frozen corpus on the T3.5 code | **0 mismatches** (148 inputs, 18,497 variants; `frozen_fixture_inventory.json`) |
| Public signatures / names / schema constants | identical to BASE (`public_surface.json` test) |
| AST inline-reconstruction of every stage into its public builder == BASE builder (4 builders, 43 stages: 15 runs + 28 dict item ranges) | pass; a deliberately mutated stage literal is rejected (negative check done) |
| Moved value helpers AST-identical, facade re-export identity; non-moved facade definitions AST-identical | pass |
| Stage modules: <= 350 lines, imports only `__future__`/`typing`/value helpers, no I/O/clock/env tokens, no unresolved globals, no `if True:` scaffold | pass |
| Use-time monkeypatch seam (patching a runtime surface builder on the facade changes the artifact) | pass |
| Full local suite (clean venv, FEATURE tree): 7,700 passed, 27 skipped, 35 failed + 2 errors | the 34 failures + 2 errors known at BASE (`uef2a/uef5/uef6c/uef9/step5b/apps-api isolation`, identical set pre-existing at BASE) plus **1 Windows file-lock flake** `test_r61_scope_fix.py::test_g_two_processes...` (WinError 32 in the readiness-evidence lock; passes 3/3 in isolation and 33/33 on pristine BASE; unrelated to contracts) - not counted as PASS |
| Impacted offline integration tests (44 files incl. scanner/commander/monitor/strategist/operator brief/reporter consumers) | 1,398 passed |
| BASE x2 / FEATURE x2 differential, strict SHA-256 write containment, 42 test files | 4/4 sessions exit 0, **1,341 passed each**, containment PASS (0 differences); **647 recorded calls: 641 BYTE_IDENTICAL, 6 JUSTIFIED_TOLERANCE, 0 REAL_MISMATCH, 0 UNRESOLVED** |
| Per function (recorded) | commander 27/27, commander shadow 212/212, supervisor 6/6, executor 7/7 identical; scanner 24 + 1 justified; strategist/monitor/validate_artifact incl. the justified ones |

The 6 justified records are all `R-MEMORY-PACKET-ID` (a `memory_<20hex>` content-hash id embeds the session temp path): it differs between the two BASE sessions and between the two FEATURE sessions in both involved tests (`test_decision_trace_ledger...`, `test_strategist_trace_logging_writes_evidence_entries`), i.e. session-path dependent, not BASE-vs-FEATURE dependent. No tolerance was added or changed.

A first differential attempt included `test_execute_from_packet.py` and `test_step5c_execution_owner.py`; those failed identically in **all four** sessions (11 failures incl. BASE; exit code 1 -> harness FAIL) under the scrubbed/pid-pinned harness environment (multiprocess/restart and mock-broker tests) although they pass in the normal suite (1,398 passed). They exercise Executor/Step5C, not the output builders; they were excluded from the differential, which is stated here rather than hidden. They run in the normal CI regression.

Deterministic fixture parity is **not** real Reporter/production artifact parity: REAL_REPORT_PARITY_BLOCKED stays OPEN.

## 4. Safety invariants and defer decisions

* Preserved by verbatim AST identity and byte parity: scanner canonical rank/selection and tie-break fields, monitor entry/hold/exit decision fields, commander selected route and blocked reason, supervisor/executor builders (not modified).
* **SAFETY_LOCK / DEFER (not forced):** (a) `monitor_decision_rule_evidence` (201 LOC, 24 outputs): one contiguous exit/hold/entry rule-evaluation run with interleaved branches; splitting it would change observable evaluation order or require inventing new intermediate contracts -> left as one stage; (b) `scanner_policy_bias_evidence` (155 LOC): ranking-adjacent bias evidence, same reason; (c) the remaining runtime-surface calls and `validate_artifact` deliberately stay in the public builders; (d) `build_executor_output_artifact` (122) and `build_commander_shadow_artifact` (119) are outside the four named builders and untouched.
* Public contract fields: unchanged (fixture bytes). No new schema source.

## 5. Remaining structural debt

Stage records still use `Any` field types; stage signatures list many explicit inputs (intentional, verbatim locals); `_build_strategist_trace_summary` (107), `_commander_shadow_actual_runtime` (84) and `_build_scanner_trace_summary` (83) helpers remain in the facade; semantic field-group names are mine and need review; the 201/155-LOC SAFETY_LOCK stages.

## 6. CI

Recorded after the hosted run (delivery commit).
