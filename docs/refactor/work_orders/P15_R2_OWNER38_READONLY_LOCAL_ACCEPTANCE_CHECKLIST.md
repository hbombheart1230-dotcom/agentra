# P1.5.2 Owner38 — Local Read-Only Acceptance Checklist (Claude + Codex)

**Source-of-truth branch:** `refactor/p1.5`; CODE SHA `80f56edfbbda8d336b09e7c5f0b18069d77785b9` (documentation-only commits may advance HEAD). Remote CI 38025461656 SUCCESS (337+286). This is NOT a full P1.5.2 acceptance or P1.5.3 instruction.

## Worktree and safety preflight (each verifier independently)
1. Observe actual `C:\Agentra` `git branch --show-current`, `git rev-parse HEAD`, `git status --porcelain=v1 -uall`, `git worktree list --porcelain`; reconcile with remote without reset/clean/checkout/pull or destroying existing dirty Q12 worktrees. Verify main frozen ancestry, no remote access assumptions.
2. READ ONLY to local runtime/source and production roots. No Python runtime code edits, no trading mode/approval modification, real orders, Broker/LLM network, Docker/scheduler restart, deletion, live replay, production SQLite/report output writes or secret exposure.
3. Isolate historical artifact copies outside production and the repo; use session-scoped temp directories with cleanup on success and bounded failure logs.

## Parity and compatibility proof
4. Re-check 37 bounded Owner modules, DAG/reverse-import guard, 436 public façade callable ABI, and `getattr`/dynamic import/monkeypatch/plugin consumers, including 8 Owner38 news-symbol/title functions and patch dependencies `_clip`, `_listify`, `_metadata_value`, `_clean_news_title`, `_normalize_news_symbol`. Static absence is never evidence for DEAD deletion.
5. Compare actual pre/post read-only copied historical Markdown/JSON bytes including selected symbol and rank, news source precedence, competitor-headline exclusions, Unicode, line endings, data types/order and fallback/exception behavior. Record fixture paths and hashes; do not call the real LLM.
6. Compare captured LLM prompt/message bytes, model IDs, retry/timeout/fallback semantics from original evidence, not live calls. Run complete safe repository pytest against pinned pre/post snapshots outside production write paths, record test numbers and missing gates.
7. Independently check no scope creep to Supervisor/Executor/Broker, 7-agent topology, UEF, Step5C/D, R6.2 readiness ownership, Q12 dirty worktrees, frozen P1.3 Docker and Scanner scoring.

## Reporting and stage gate
- Claude submits immutable measured PASS/PASS_WITH_FINDINGS/FAIL/BLOCKED to `docs/refactor/work_orders/evidence/P15-R2-GPT-VERIFY-002-CLAUDE.md`, with local SHA, exact test command counts, report hashes, untested gates and explicit zero live execution.
- Codex independently submits the same evidence structure to `docs/refactor/work_orders/evidence/P15-R2-GPT-VERIFY-002-CODEX.md`; no code rewrites by either verifier.
- Reports may be committed only through non-destructive authorized evidence-only handling. GPT/operator reviews separately; **P1.5.2 OPEN and P1.5.3 forbidden until explicit acceptance**.
