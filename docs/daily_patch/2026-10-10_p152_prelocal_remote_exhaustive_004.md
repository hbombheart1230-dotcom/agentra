# P1.5.2 Remote Prelocal Coverage 004 — 2026-10-10

## Direction and scope
User approved GPT remote-first source and integration audit before any user-local Claude/Codex verification. Branch `refactor/p1.5`. Prior Owner38 runtime source remains frozen; no P1.5.3.

## New tests and audits
- Existing 709 selected offline CI PASS on SHA `4db23efbc69c176d0901bf8f4a7dbc9f6d234bf8`.
- Build `scripts/refactor/p152_prelocal_consumer_debt.py`: automatically list all 436 public Reporting facade symbols, names, current disposition, static consumer files/reference types, conservative KEEP/WRAPPER recommendation and dynamic hazard. Missing static reference is NOT an inference of DEAD.
- Add `tests/test_p152_prelocal_consumer_debt.py` guaranteeing no deletion authority, no automatic waiver and still OPEN.
- GitHub separate remote `broad_remote_offline` job runs `pytest -q tests -m "not heavy and not docker and not benchmark" --maxfail=12` in clean ephemeral CI under mock/DRY_RUN without Kiwoom/OpenRouter credentials; always retain JUnit evidence.
- Results may reveal out-of-scope baseline/environment failures; report them honestly and do not modify unrelated trading/authority code just to force CI green.
- Actual C:\Agentra real Markdown/JSON and prompt parity, local complete full pytest, independent verification and human final decision remain NOT RUN. Q12 dirty worktrees, UEF, Step5C/D, R6.2, Docker and real orders untouched.

CI results for this tranche must be added to separate follow-up evidence after the remote runs conclude.
