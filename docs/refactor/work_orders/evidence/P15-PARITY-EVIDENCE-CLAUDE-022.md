# P15 Second Pass — Parity evidence closure (Claude, harness/evidence only)

Audited code: `fb21f2b12db84c294b1c634adb21cd8545bf9568`; baseline code `1f7add2b0f9b5a33399da27edcdd2f390bdf911b`. No Agentra production code changed in this closure; only `scripts/refactor/p156_*` (harness), `tests/test_p156_parity_harness.py`, evidence, docs and one CI line. Live `C:\Agentra`, Q12, broker, LLM, production data untouched; no ZIP. Per the stop order the repeated full 140-file x 4-session loop was halted; the remaining proof is targeted.

## 1. Evidence secured
| Evidence | Location | Result |
|---|---|---|
| Original raw logs of the 1,131-call run (4 x ~366 MB, SHA-256 in [manifest](../../evidence/p156_parity/raw_evidence_manifest.json)) | `C:\AgentraEvidence\spc8_*.json` (external, not committed) | **PRESENT**. Strict field-rule reclassification: 915 identical / 108 justified / 9 mismatch / 99 unresolved. This run is NOT a PASS: both baseline runs shared one clone directory and live market data was read |
| Isolated deterministic differential v1/v2 (4 sessions each, BASE x2 + FEATURE x2, own clone/TEMP/log per session) | `par_out_det`, `par_out_det2` | 1,131 calls; v2 = 1,020 identical / 86 justified (R-ID 55, R-MTIME 28, R-MTIME+R-MTIME-DERIVED 3) / **0 real mismatch** / 25 unresolved; 2,949 of 2,950 tests passed in every session (only `test_api_routes_are_get_only`, a known baseline failure); outcomes identical in all 4 sessions |
| Targeted A: the 6 tests behind the 9 legacy mismatches; sequential, fresh clone per session at one identical path | `par_out_A` | 17 calls, **17 byte-identical** |
| Targeted B: the 24 tests behind the 25 v2 unresolved records | `par_out_B` | 28 calls, **28 byte-identical**; 24/24 passed in all 4 sessions |

## 2. Real functional mismatch
**None found.** No decision-bearing field (ranking, score, risk, intent, side, quantity, price, authority) differed between BASE and FEATURE in any isolated session. Every non-identical record in v2 differs only on identifier / mtime / length fields that trace to one cause (below), and the targeted reruns that remove that cause are byte-identical.

## 3. Unresolved items and risk
- 25 v2 records (all `strategist_node` and its scanner/monitor echoes) were unresolved only because each carried the same artifact: the test temp root is `<pid>-<uuid>`, `reporter_analysis_digest.artifact_path` embeds it, so a memory-packet content hash (`stable_evidence_id`) and the LLM payload char count / prompt_hash vary per process (PID digits change lengths by 1-2 chars). The root cause was dumped and diffed (only that path differed). **Risk: LOW** — resolved by Targeted B (28/28 identical). Not tolerance-excused.
- Legacy 99 unresolved / 9 mismatches: root causes (shared clone directory, yfinance live data through curl_cffi, PID paths, mtime) are removed in the isolated deterministic mode, and the 6 mismatch tests are 17/17 identical (Targeted A). The earlier "139 tolerance-equal" claim is withdrawn; tolerance is now field-specific and justified in code (`TOLERANCE_RULES`).
- Disclosure: an intermediate same-path full run with a global `os.getpid` pin was discarded because the pin itself broke 27 pid/lock tests identically in all sessions; its raw logs were removed when I re-ran, so it is not claimed as evidence. The pin is now scoped to the conftest temp-root derivation and restored at `pytest_sessionstart`.

## 4. Do the determinism controls distort verdicts?
Clock (`time.*`, `datetime.datetime.now/utcnow/today`, tick 2^-10 s per call, reset per test, `sleep` advances the fake clock), `uuid.uuid4` (per-test sequence), `random` seed, network/yfinance/curl_cffi blocked, `os.getpid` pinned only while the session temp root is derived. All are applied identically to BASE and FEATURE, only inside the harness process, never in production code. They cannot turn a decision difference into equality: derived values depend on the *number* of clock/uuid calls, so a feature tree with different control flow would differ. Network blocking removes live-market inputs (offline fallbacks run on both sides); that is a coverage limit, listed below. `date.today()` stays real (replacing `datetime.date` breaks pandas C extensions).

## 5. Isolation state
Each run uses its own clone (session root), TEMP/TMP, recorder log and stdout file; the recorder guard refuses the live root and non-clone roots; the orchestrator refuses work/out dirs inside the repo or live root (unit-tested). Write containment: 0 changed/untracked paths in every session root of v2. `controlled_mock_lanes` operational write-isolation remains OPEN (not modified; its test writes landed only in per-session roots). Production writes: **0**.

## 6. Codex re-audit readiness
READY for the targeted evidence above. Still BLOCKED / NOT RUN: real frozen report/LLM request-response and Operator Brief byte parity vs frozen artifacts; full native pytest, Docker, UEF (Wave D); live-market-data-dependent paths (blocked in deterministic mode); `controlled_mock_lanes` operational-path isolation; Executor/Supervisor stay SAFETY_LOCK.

Reproduce: `python scripts/refactor/p156_parity_differential.py --repo <clone> --baseline-sha 1f7add2b0f9b5a33399da27edcdd2f390bdf911b --feature-sha fb21f2b12db84c294b1c634adb21cd8545bf9568 --names <names.json> --tests <tests.txt> --work-root <empty dir outside repo> --out-dir <new dir> --mode det --same-path` (target lists: the 6 legacy-mismatch tests and the 24 v2-unresolved tests are named in `targetedA_summary.json` / `targetedB_summary.json`).
