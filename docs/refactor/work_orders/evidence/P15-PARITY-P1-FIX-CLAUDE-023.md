# P15 Parity Comparator P1 Fix (Claude, harness/evidence only)

Starting HEAD `96cc490de072bf506548b7426cc412650a51c2c0`; audited code `fb21f2b12db84c294b1c634adb21cd8545bf9568`; baseline code `1f7add2b0f9b5a33399da27edcdd2f390bdf911b`. Only `scripts/refactor/p156_parity_differential.py`, `tests/test_p156_parity_harness.py`, evidence and docs changed; no trading/strategy/Reporter/Supervisor/Executor/Broker code. No full 140-file x 4-session rerun; previous raw evidence kept (new evidence has new names, SHA-256 in [manifest](../../evidence/p156_parity/raw_evidence_manifest.json)).

## 1. R-ID comparator defect (Codex finding)
- Defect: `strategy` was on the `R-ID` key list and the id check accepted any `<prefix>_<12-64 hex>`, so a real strategy-field change such as `strategy_aaaaaaaaaaaa -> strategy_bbbbbbbbbbbb` could be excused as an "ID".
- Fix: `strategy` removed from `R-ID` (keys: run_id, request_id, trace_id, event_id). Memory-packet ids are accepted only as `memory_<20 hex>` on BOTH sides, either as leaf `packet_id` or directly under an explicit packet-id container (`packet_ids`, `layer_packet_ids`, `applied_packet_ids`), reported as rule `R-MEMORY-PACKET-ID`. `strategy`/`selected_strategy` and any strategy-selection, ranking, price, quantity or approval field are never tolerated.
- Negative/positive tests (`tests/test_p156_parity_harness.py`, 14 passed): `strategy_aaaaaaaaaaaa -> strategy_bbbbbbbbbbbb` REAL_MISMATCH; ID-shaped difference in `selected_strategy` REAL_MISMATCH; `packet_ids.strategy` memory_ id difference conditional `R-MEMORY-PACKET-ID`; `strategy` memory_-shaped difference outside the container REAL_MISMATCH; mixed memory/strategy values under the container not tolerated.
- Reclassification of the previous 86 justified records with the corrected comparator (`det2_reclassified_p1fix.json`): **still 86** (R-MEMORY-PACKET-ID 55, R-MTIME 31 incl. 3 with R-MTIME-DERIVED); 1,020 identical, 0 real mismatch, 25 unresolved — unchanged, because all 55 id records were genuine memory ids under packet-id containers.

## 2. Targeted A write-audit failure (Codex finding)
- Observed: in the earlier Targeted A evidence all four sessions had exit_code=1 although 6 tests passed; the project's own pytest write audit printed `PRODUCTION PATH WRITE DETECTED ... CREATED data/logs`. My previous summary reported only the (git-status) containment count and passed over the exit codes — that was wrong and is corrected here.
- Cause (reproduced on the baseline `1f7add2`, so pre-existing): `test_execution_disabled_buy_blocked_then_next_tick_executes` -> `_run_integrated_chain_impl` -> `run_controlled_mock_lane_path` -> `inject_controlled_mock_lane_intent` -> `ledger.record_evaluations` -> `_write_rows` -> `Path.mkdir(parents=True)` on `DEFAULT_ROOT = Path("data/logs/controlled_mock_lanes")`, i.e. a cwd-relative path inside the repository root. This is the already-known `controlled_mock_lanes` write-isolation item; production code was not modified.
- Harness fix (no audit weakened, no pre-created directories): the session environment now sets the supported knob `CONTROLLED_MOCK_LANE_LOG_ROOT` to `<session dir>/mock_lane_logs` (outside the clone root). The project's conftest audit is untouched and still runs.
- Containment check hardened: before/after `os.walk` snapshots of every file AND directory (empty and git-ignored included, `.git` excluded). Any new path in the session root, the project's `PRODUCTION PATH WRITE DETECTED` banner, or an exit code other than expected makes the session verdict FAIL and the orchestrator exits 2. Unit-tested (empty `data/logs`, `__pycache__`, banner with exit 0, exit 1 without known failures).

## 3. Re-verification (Targeted A only, sequential, fresh clone per session at one identical path)
| Item | Result |
|---|---|
| Sessions | baseline x2 (`1f7add2`), feature x2 (`fb21f2b`) |
| pytest exit codes | **0 / 0 / 0 / 0** (6 passed in each) |
| Calls | 17 / 17 **byte-identical**, 0 justified, 0 mismatch, 0 unresolved |
| Forbidden writes | **0** new paths in any session root; no audit banner; isolation verdict PASS x4 |
| Targeted B (28/28, 24 tests) | previous evidence kept unchanged |

Reproduce: `python scripts/refactor/p156_parity_differential.py --repo <clone> --baseline-sha 1f7add2b0f9b5a33399da27edcdd2f390bdf911b --feature-sha fb21f2b12db84c294b1c634adb21cd8545bf9568 --names <names.json> --tests <6 test node ids> --work-root <empty dir outside repo> --out-dir <new dir> --mode det --same-path`.

## 4. Remaining BLOCKED / OPEN
`controlled_mock_lanes` default ledger root is still cwd-relative in production code (OPEN, needs an approved code change); real frozen report/LLM and Operator Brief byte parity, full pytest/Docker/UEF (Wave D), live-market-data paths (blocked in deterministic mode), Executor/Supervisor SAFETY_LOCK.
