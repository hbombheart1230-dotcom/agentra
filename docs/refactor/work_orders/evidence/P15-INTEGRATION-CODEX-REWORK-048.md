# P1.5 integration Codex REWORK — resolution and acceptance gates

**Audited HEAD:** `e207b612ec9ad6aae3b89d4eb2b507f30c7d0dcd`. **Independent Codex result:** REWORK (106 offline PASS, 2 FAIL; 5 patch-note/API PASS). This document does NOT claim independent acceptance after the fixes.

## P1 — No-ZIP CI rule

Independent audit noted `docs/refactor/work_orders/CURRENT.md` declares "No ZIP / CI packaging forbidden", yet `.github/workflows/p15-integration-changed-files-bundle.yml` generated and uploaded an archive (run [38716792551](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38716792551)).
**Resolution:** delete only this dedicated CI workflow; retain policy. User-facing ZIPs must be generated externally to repository GitHub Actions and include only updated files. Existing artifact is historical; no declaration that it was never produced.

**Gate:** verify `.github/workflows/p15-integration-changed-files-bundle.yml` is absent in the new HEAD; `git diff --name-status e207b612ec9ad6aae3b89d4eb2b507f30c7d0dcd..HEAD` shows D; no equivalent packaging workflow exists in this integration slice.

## P2 — Windows baseline report byte contract

Codex found two parametrized failures in `tests/test_baseline_shared_owners.py:121-132` under native Windows. Contract requires `json.dumps(..., ensure_ascii=False, indent=2) + "\\n"` encoded as UTF-8. Original `baseline_artifact_io.write_json_dict` used `Path.write_text` default newline translation, emitting CRLF on Windows.
**Resolution:** explicitly pass `newline="\\n"` (Python 3.12) to preserve LF bytes across platforms; retain payload serialization, exception behavior and read semantics.

**Gate:** both native Windows parametrizations PASS in new required `baseline-lf-windows-native` job, Linux contract remains PASS, Q10/Q12 frozen baseline parity and T4 Linux/Windows complete successfully. No live API/LLM/orders.

## Still open / not asserted

Integration acceptance: **BLOCKED until SHA-specific required CI + Codex independent audit**. Reporter/real LLM parity, T4-C displaced Reporter-feedback fallback and safety authority remain separate gates. Main, T5, Wave D, P1.5.10 and bulk folder moves forbidden.

## Correction after failed CI on `c1f7323bb6187cc78bfb053c04d1205712a8dd29`

- Updated Linux [38718952518](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38718952518) showed two FileNotFoundError exceptions in Q10/Q12 baseline fixture. Native Windows test failed identically. Root cause: accidental literal `\\n` embedded in Python comment at `baseline_artifact_io.py:19` caused the actual `path.write_text` expression to be commented out. It was introduced by the first P2 fix.
- Second commit restores separate executable call line while retaining explicit newline. Do not treat fix as PASS until rerun on both OS.
