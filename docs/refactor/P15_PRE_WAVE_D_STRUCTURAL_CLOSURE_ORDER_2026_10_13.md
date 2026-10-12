# P1.5 sequence — pre-Wave-D structural closure

Status: ARCHITECTURE PLAN. Source branch: refactor/p1.5.

1. Claude completes second-pass S1–S6 bulk modularization (Reporter excluded in this pass only).
2. Codex independently audits the second-pass checkpoint.
3. GPT re-inspects actual code across all seven agents INCLUDING Reporter, not only the initial selected Python source paths. Classify giant functions, facade ABI consumers, duplicated Owners, dangerous capabilities and remaining SPLIT/MOVE/MERGE/KEEP/REVIEW/SAFETY_LOCK decisions.
4. Claude executes third-and-later coherent BULK modularization rounds to close remaining structural debt, INCLUDING Reporter. Specifically inspect Reporter bundle runtime (intraday_trade_reports.py), trade-report AI/Markdown/Story facades, numbered body Owners and 436 reporting ABI names (330 were UNKNOWN in Wave C). Only split when consumer, mutation order and behavior parity can be established; no unsafe deletion or cosmetic 100-line batches.
5. Codex independently audits structural convergence; any unproven high-risk broker/LLM/DB/approval changes remain SAFETY_LOCK with explicit fixture requirements, not falsely passed.
6. Only THEN run Wave D/P1.5.11 mandatory full native pytest, Docker mocked integration, UEF replay/cross-day, real frozen Reporter Markdown/JSON/LLM parity, Executor real-case parity and controlled-mock-lane write isolation. An essential missing verification blocks final acceptance.
7. GPT and user decide P1.5 freeze and separate later main merge/deployment.

IMPORTANT: Earlier master/target notes saying “second pass -> Codex -> Wave D” are superseded by this plan. Reporter exclusion is scoped to the initial second-pass S1–S6 ONLY, NOT to all work before Wave D. This is a planning decision, not a completed refactor or test result. Reporter source and actual trading authority remain untouched by this document.
