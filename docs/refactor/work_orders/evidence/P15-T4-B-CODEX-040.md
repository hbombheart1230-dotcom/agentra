# P1.5 T4-B — Codex independent Monitor audit (user-delivered report)

**Review date:** 2026-10-15 KST. **Verdict: T4-B ACCEPT / T4-C GO.** This is a record of the user's Codex audit results; GPT has not independently rerun the local full corpus. Source final SHA `4e242e5b1fc609b0ec012e0c6faed37b202e4aa0`.

## Independent findings

| Check | Verdict | Evidence |
| --- | --- | --- |
| Structural parity | PASS | 42 ledger segments / 15 Owners reconstruct all four BASE ASTs, Owners 22–231 LOC; structural gates 13 PASS |
| Decision parity | PASS | Focused Monitor intent-only, fallback, source-price/exit guard regressions 139 PASS |
| Exit precedence | PASS | `_t4_ret` immediate identity-return ladder preserves sequence and exception/control-flow; `libs/runtime/exit_policy.py` around original 549–641 |
| State/event parity | PASS | State/effect sequence and output ordering frozen; no production writes or trading authority changes reported |
| Golden oracle | PASS | Independently re-ran portable full sample_mod=1 149 pinned BASE + 149 FEATURE records with 0 mismatches; all 2,879 variant IDs; integrity 133 portable checked / 16 platform-bound / 0 errors. Cross-platform bound values use same-host pinned BASE. |
| Final hosted CI | PASS | Required GitHub Actions run `38664980307` SUCCESS on exact FINAL; Linux regression and Windows native Monitor replay + strict 5-test JUnit accounting both passed. |
| Linux timeout | JUSTIFIED | 20 → 35 min; run `38660492205` took ~21m18s, exceeding old cap; FINAL succeeded. |
| T4-A scope pin | PASS | `c338ba3` accepted Scanner stage-end pin, ancestry checked; Monitor edits should not relax Scanner gate. |

**New P0/P1:** none. **P2 OPEN:** BASE×2/FEATURE×2 independent session differential not run; other AST, portable 2,879-variant replay and 139 focused tests suffice for T4-C entry, but do not call the differential PASS. Retain in broad acceptance.

**Other OPEN:** REAL_REPORT_PARITY_BLOCKED; NTFS mtime causality P2; PYTHONHASHSEED telemetry order P2; direct Scanner freeze CLI PYTHONPATH P2; mandatory post-T4 architecture visualization gate NOT STARTED.

**Authority:** T4-B final ACCEPT. T4-C pure-Strategist extraction may start under its own scope; no runtime/LLM, Broker/Executor/Supervisor/Step5C authority change is authorized by this audit.
