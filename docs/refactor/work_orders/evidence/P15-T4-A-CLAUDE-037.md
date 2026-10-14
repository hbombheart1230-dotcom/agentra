# P15 Third Pass T4-A — Scanner structural closure (Claude)

BASE `11a11df58f8d846cd9824fcb37eced521a57e887`; freeze commit `c8a1131d9e3dc676b972548882c0e98bf91c284a`; CODE `171cc8adc303ee3914feec2918b6217c80e98f3c`. Entry gate: T3.5 Codex independent audit ACCEPT, T3.5.1 P1-A/P1-B CLOSED, no new P0/P1/P2, hosted CI 38543528229 SUCCESS, **T4 GO**. Scope: `graphs/nodes/scanner_node.py::scanner_node` and the Scanner Owners in `libs/runtime/scanner/`. No change to Supervisor/Executor authority, Step5C, orders/brokers, production data/reports, Q12 worktrees, `main`; T3.5 golden fixtures unchanged; REAL_REPORT_PARITY_BLOCKED OPEN; NTFS settle P2 UNRESOLVED; T5/Wave D NOT STARTED.

## 1. Result

| Item | Before | After |
|---|---|---|
| `scanner_node` function LOC | 1,261 | **474** |
| `graphs/nodes/scanner_node.py` lines | 1,993 | 1,223 |
| New Scanner Owners | - | 4 modules, 9 functions, 912 lines (all <= 350) |

## 2. Owner matrix (all under `libs/runtime/scanner/`)

| Owner module | Lines | Function(s) | Responsibility actually extracted |
|---|---|---|---|
| `candidate_row_projection.py` | 320 | `score_scanner_candidate_row` (309) | the whole per-candidate scoring row: base row / mock row, feature & rank inputs, score components, compatibility signal, macro chart fit, bias/memory/symbol-prior adjustments, component evidence; mutates only the candidate's own fresh `row` |
| `ranking_policy_overlay.py` | 172 | `resolve_commander_scanner_policy` (14), `apply_scanner_ranking_policy_overlay` (128) | commander/applied scanner-policy resolution; re-entry dampener, diversification, entry-bias cap, market-representative guard, blocker-family overlay (in-place row score edits and re-sorts exactly as before, selection veto) |
| `selection_output_projection.py` | 217 | `project_scanner_selection_evidence` (132), `build_ranked_candidate_rows` (48) | selected rank/margin/runner-up/factor/bias/memory-trace/veto evidence; ranked candidate rows value |
| `scanner_event_payloads.py` | 202 | 4 payload builders | source-universe snapshot value, ranking-event payload, summary payload, decision-trace payload (the emit/log/append calls stay in the node) |

Mechanics: statement windows and value expressions are moved **verbatim**; locals enter as explicit parameters; module globals of the node are resolved at use time as `facade.NAME` (monkeypatch seams intact; nested stage calls that used `_r3_sys.modules[__name__]` receive the injected `facade`); multi-output windows return `NamedTuple` records (sorted-name order). No new ranking or tie-break code exists: the only `sorted(...)` ranking sort and the overlay re-sorts are the original statements.

## 3. Responsibilities retained in `scanner_node` (SAFETY_LOCK / effect boundary)

State writes (`state[...] = ...` incl. scanner_output/skill/feature/selected/top_stock), event emission (`_emit_scanner_event` x5, `_log_scanner_summary`), evidence ledger and decision-trace/bridge calls, artifact write, selected-symbol memory write (`_remember_selected_symbol`), clock (`_resolve_now_epoch`), environment read (`SCANNER_ENFORCE_BLOCKER_FAMILY_SELECTION_VETO`), skill/feature hydration, symbol-prior loading, asset-universe/mock-broker/practical filter calls with their emitted events, and the candidate loop skeleton (`continue` on empty symbol, `scan_results.append`) plus the canonical `sorted(scan_results, ...)` rank sort. These keep their original order and authority boundary; moving them would change effect ordering, so they are deliberately not extracted.

## 4. Consumer mapping

Consumers of `scanner_node` (unchanged ABI: same name, signature, State-in/State-out): `graphs/trading_graph.py`, `graphs/nodes/scan_candidates.py`, `graphs/nodes/execute_from_packet.py`, `graphs/pipelines/offhours_validation.py`, `libs/agent/scanner.py`, `libs/runtime/commander/nodes.py`, `libs/runtime/opening_rank1_controlled_probe.py` (reads `state["selected"]["scanner_rank"]`), `libs/runtime/scanner/candidate_context_projection.py`; 41 test files reference it. Scanner -> Monitor offline integration: `tests/test_m22_skill_native_scanner_monitor.py` and the other integration tests are part of the 1,385-test targeted run.

## 5. Evidence

Frozen BASE contract (committed in `c8a1131` before any implementation edit): 73 captured Scanner States from the offline suite (24 test files) with ordered effect evidence (1,131 effect/event records), plus 1,575 deterministic variants/scenarios: single-key drop/none/empty perturbations and candidate-pool scenarios (all-scores tied, rank-1 flip by swapping the top two scores, reversed/rotated/duplicated/single/empty candidate pools, no mock rows). Frozen observables: final State (canonical JSON, key order), ordered effect/event list (name + digest of the arguments at call time, replay root scrubbed), exception, and returned-object identity.

Determinism finding (BASE property, not changed): the Scanner ranking result depends on string-hash iteration order (`PYTHONHASHSEED`); the freeze therefore pins `PYTHONHASHSEED=0` in every replay process (subprocess, like the earlier parity harness). Replays also use a constant clock, deterministic uuid/random, scrubbed scanner env knobs, a disposable root and a network guard.

| Check | Result |
|---|---|
| Full frozen corpus replay on the T4-A code (73 records + 1,575 variants/scenarios), native | **0 mismatches** (state, effect order/args, exception, identity) |
| AST inline reconstruction of all 9 stages == BASE `scanner_node` AST; non-moved definitions identical | pass (a mutated comparator in an Owner is rejected) |
| Scanner-focused + consumer + Scanner->Monitor integration tests (39 files) with historical p156/p157/p158, current T3 owner/purity/provenance, harness guards, facade ABI/symbol ledger, T3.5 structural gate | **1,385 passed** |
| BASE x2 / FEATURE x2 differential, strict SHA-256 containment, 34 test files | see section 6 |
| T3.5 golden fixtures | unchanged |
| Protected paths | `git diff 11a11df -- libs/execution libs/broker libs/supervisor libs/llm graphs/nodes/execute_from_packet.py graphs/nodes/decide_trade.py` empty |

Rank-1 / runner-up parity: the frozen scenarios include all-scores-tied and top-two swap; final State (`top_stock`, `selected`, `ranked_candidates`, `scanner_runner_up_reasons`, `scanner_margin_vs_second`, `scanner_selection_reason`) is byte-identical for every record and variant. State/event order parity: the ordered effect list is identical, including the event names and the argument digests taken at call time.

## 6. Differential (BASE x2 / FEATURE x2)

Harness at `9e312c9`-era `p156_parity_differential.py` (strict SHA-256 containment, `--pin-pid`, det mode), BASE `11a11df` x2 / FEATURE `171cc8a` x2, recorded function `scanner_node` (State in, State out), 36 test files (the 39 Scanner-related files minus the parity harness's own tests and the two files that fail identically in all four scrubbed-env sessions: `test_opening_alpha_executable_quote_refresh.py`, `test_paper_trading_execution_finalization.py` - they pass in the normal suite and are in the 1,385-test run).

| Item | Result |
|---|---|
| Sessions | 4/4 exit 0, **1,109 passed each**, outcomes identical, strict containment PASS |
| Recorded `scanner_node` calls | **79: 74 BYTE_IDENTICAL, 5 JUSTIFIED_TOLERANCE, 0 REAL_MISMATCH, 0 UNRESOLVED** |
| Justified | all `R-MEMORY-PACKET-ID` (3 test files): the memory-packet id embeds the session temp path and differs between the two BASE sessions and between the two FEATURE sessions - session dependent, not BASE-vs-FEATURE dependent; no tolerance added |

A first attempt included the parity harness's own tests and two env-sensitive files; all four sessions (BASE included) failed identically and the run was FAIL by exit code; it was repeated with the list above and is not hidden here. Deterministic fixture parity is not real Reporter/production parity.

## 7. Remaining

Independent Codex T4-A audit pending. T4-B (Monitor/Strategist/Commander/Operator UI functions) not started; T5 and Wave D not started. The platform-bound portion of the golden (13 records with Windows drive paths) is compared on foreign hosts only against same-host pinned BASE.
