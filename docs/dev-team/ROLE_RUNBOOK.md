> **ROLE CORRECTION (2026-10-17):** Claude owns Reporter, Codex owns Monitor, Work independently reviews both and coordinates shared T3/T4 and final integration. The authoritative current work orders are docs/dev-team/assignments/00–06. Any older Codex-as-Reporter-auditor/Runner text below is superseded.

# Agentra role boots — single-copy assignments

Do not start another worker from a vague one-line prompt. Each run reads only the current control documents and its role issue, then resumes from the last remote checkpoint. **No prior completed chat transcript reread by default.**

## Claude — Reporter continuous owner (copy into Claude CLI)

~~~text
AGENTRA P1.5 — REPORTER WHOLE-ROLE CONTINUOUS OWNER

Repository: hbombheart1230-dotcom/agentra
Implementation branch: work/reporter-role-20261017
Starting branch SHA as of design snapshot: d17d33c0c0e7b789b320b872eb386184fd6ce357
Design ref: origin/design/agentra-dev-team-loop-20261017

Read docs/dev-team/README.md, DEVELOPMENT_LOOP.md, REPORTER_PROGRAM.md, REVIEW_PROTOCOL.md, and ROLE_RUNBOOK.md from design ref (git show or fetch; do not merge design into active work tree). Then read your role's GitHub issue. Fetch current role branch HEAD and last checkpoint. Do not assume starting SHA is still HEAD.

Execute the entire Reporter RP0–RP8 program, not the next few file moves. Continue automatically: inventory -> safe code extraction -> focused proof -> commit/push -> checkpoint + issue comment -> poll review findings -> repair -> next safe batch. Use the pinned R3 dynamic facade global approach. Retain historic ledgers, public ABI, monkeypatch behavior, output bytes, exception and authority boundaries. Never self-authorize order/LLM-policy changes.

One cohesive internal batch at a time; a commit is a recovery point, not a stop condition. If one symbol blocks, prove why and do other safe work. Do not ask the operator to relay every batch. Do not request Work/Codex approval between batches. Never merge main or alter Monitor's branch. Keep notes tied to real SHA and update real UI-linked patch notes if relevant.

Terminate only at full ROLE_READY (request independent audit) or genuine total exhaustion of safe authorized scope/runtime/credits, leaving exact resumable checkpoint. Do not describe unexecuted tests as PASS. If session exits, the external supervisor or a manually restarted CLI must resume; your prompt alone does not keep a process running.
~~~

## HISTORICAL — superseded Codex audit prompt (DO NOT USE; Codex now owns Monitor)

~~~text
SUPERSEDED HISTORICAL PROMPT — DO NOT EXECUTE

Repo: hbombheart1230-dotcom/agentra
Design ref: origin/design/agentra-dev-team-loop-20261017

Read docs/dev-team/REVIEW_PROTOCOL.md and target role's scoped program; obtain role issue, latest checkpoint and actual role HEAD. Compare changed files since last reviewed SHA, check existing pinned facade/R3 contracts and negative authority tests. Reproduce focused failures in an isolated environment when available; distinguish not-run from pass. Publish structured findings with exact SHA to the role GitHub issue; do not edit or merge an active role branch. At ROLE_READY, perform final independent audit. Never simply approve because output says tests passed, and never expand trade-authority/guard policy.
~~~

## ChatGPT Work — architect/reviewer (copy into Work when review is desired)

~~~text
AGENTRA P1.5 — REVIEW WINDOW, NOT BATCH APPROVER

Use connected GitHub repository hbombheart1230-dotcom/agentra and design branch design/agentra-dev-team-loop-20261017. Read README.md and REVIEW_PROTOCOL.md in docs/dev-team, then latest role issue/checkpoint and exact remote branch HEAD. Review only the SHA delta since previous review, inspect code/ABI/monkeypatch/output/guard contracts and test evidence. Post precise P0/P1/P2 findings as a role-issue comment with reviewed SHA, reproducer, and acceptance test. If architecture needs revision, commit a proposal on a separate design branch and link it; do not edit running role branches. Do not stop workers or demand per-batch approval. Prepare one daily operator digest when explicitly requested/configured. Never claim background monitoring is active unless an actual schedule/runner was installed.
~~~

## Real automation bootstrap — separate task after documents

Assign a separate infrastructure worker to implement a *non-trading* runner with (1) authenticated persistent sessions for each role, (2) bounded tokens/credits/CPU, (3) role issue comment polling and idempotent acknowledgements, (4) crash resume, (5) safety stop flags, (6) isolated test outputs, (7) daily digest. Do not put API keys in repo or allow issue comments to execute arbitrary code. Test in mock-only mode. Get explicit operator approval before enabling any unattended runner.

## Canonical role issue IDs

Reporter = https://github.com/hbombheart1230-dotcom/agentra/issues/11
Monitor = https://github.com/hbombheart1230-dotcom/agentra/issues/12

Use issue comments for asynchronous cross-branch reviewer findings; do not mistake a documentation-only design PR for executable orchestration.
