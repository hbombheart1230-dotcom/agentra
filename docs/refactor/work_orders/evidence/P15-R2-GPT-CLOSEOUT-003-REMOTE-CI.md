# P1.5.2 Integration Closeout 003 — Remote CI Evidence
Date 2026-10-10
Branch refactor/p1.5
Original implementation runtime SHA: 80f56edfbbda8d336b09e7c5f0b18069d77785b9
Integration tested SHA: a68d901430a06f267ef3b0be66d048ecc2a0d64e
CI run: https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38031366650 — **SUCCESS**

## Selected remote CI (not full repository)
- Reporting tests: **337 PASSED**, 1 warning.
- Owner/compatibility/public-ABI/UI tests: **286 PASSED**, 1 warning.
- Expanded offline Reporter/Node/Service/Operator/trace/mock LLM tests: **83 PASSED**.
- New closeout machine-inventory tests: **3 PASSED**.
- **709 selected tests passed**. Source/Owner parity, static consumer scan and ZIP upload passed.
- Machine inventory artifact: https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38031366650/artifacts/11661939277. It asserts 436 public callables, 37 bounded Owners, no off-scope modified files, and `closeout_allowed=false`.
- Integration-only modified-files ZIP: https://github.com/hbombheart1230-dotcom/agentra/actions/runs/38031366650/artifacts/11661589426 (historical earlier document snapshot; final HEAD CI reruns include final docs).
- No Reporting runtime implementation code changed during this tranche.
- Existing façade sizes: AI **2761**, Markdown **2658**, Story **636** LOC. Size goals NOT MET; wrapper and consumer compatibility debt remains OPEN.

## Mandatory local acceptance — all NOT RUN
1. Actual C:\Agentra SHA, worktrees and two Q12 dirty states verification.
2. Immutable pre/post real Markdown/JSON bytes, provenance/selected symbol/rank and source-precedence golden equality.
3. Captured LLM prompt/message/model/call count/retry/fallback/timeout parity without real LLM.
4. Complete safely isolated repository pytest and original baseline equivalence.
5. Two separate local READ-ONLY Claude and Codex evidence reports.
6. Operator acceptance of verified wrapper/size debt. No P1.5.3 or main merge.

These are STOP gates. No broker submit, production data write, scheduler or Docker restart or live trading.
