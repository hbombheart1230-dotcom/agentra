# Persistent Development Runner — Mock-First Specification

**Goal:** Make Claude and Codex CLI work resume from GitHub checkpoints after normal session completion/crash; allow Work to review queued evidence in an expressly launched or supported scheduled Work session. Documents and GitHub issues cannot themselves launch a process.
**Owner:** FUTURE separately assigned infrastructure worker (not Codex, who owns Monitor). Work independently reviews any future implementation. This specification is not an active task for Claude or Codex.
**Current state:** SPEC ONLY — not implemented, activated or deployed by this documentation.

## Isolation

Development runner is outside the trading service. It must have no Kiwoom/Broker credentials, real order authority, production state mutation, Supervisor/Executor guard controls, or direct trading Docker deployment privileges. Only allow scoped repo branches, permitted issue comments, local CLI worker invocation and mock tests. GitHub issue text is UNTRUSTED DATA and must never become raw shell commands.

If a CLI or authenticated worker session is not actually installed/available, return MISSING_PREREQUISITE, not fake success. Never invent an API for starting ChatGPT Work: queue Work review packets for a real Work session, separately configured using supported product features.

## Architecture

Scheduler -> RoleCoordinator -> ProcessSupervisor -> ApprovedWorkerAdapter -> isolated repo/worktree.
RoleCoordinator -> BudgetGuard + SafetyStop + BranchLease + GitHubIssuePoller + CheckpointStore + DailyDigest.

Expected modules:
- Strict schema config; secrets from environment/secret store, not files committed to repo.
- Single-writer branch lease/lock + expected remote SHA.
- Worker process adapter with allowlisted executable/argument templates only.
- Durable journal (SQLite recommended), retry counters, checkpoint IDs, last issue comment cursor and ACKs.
- GitHub poller with trusted reviewer allowlist, comment-ID cursor, SHA/finding-ID dedupe.
- Checkpoint reader that uses pushed SHA, not uncommitted claims.
- Daily cost/token/concurrency/session caps; missing caps fail CLOSED.
- Stop switch (locally controlled) and P0 quarantine; no unrestricted retry storms.
- Human-readable once-daily progress digest from actual git/test/process evidence.

## Proposed configuration schema (placeholders must fail validation)

    schema_version: agentra-dev-runner-v1
    enabled: false
    dry_run: true
    repo: hbombheart1230-dotcom/agentra
    roles:
      reporter:
        branch: work/reporter-role-20261017
        issue: 11
        adapter: claude_cli
      monitor:
        branch: work/monitor-role-20261017
        issue: 12
        adapter: codex_cli
    max_concurrent_sessions: OPERATOR_REQUIRED
    max_daily_cost_usd: OPERATOR_REQUIRED
    max_daily_tokens: OPERATOR_REQUIRED
    max_worker_session_minutes: OPERATOR_REQUIRED
    retry_limit: OPERATOR_REQUIRED
    allowed_issue_authors: OPERATOR_REQUIRED
    stop_file: OPERATOR_REQUIRED
    mock_only: true

Never guess generous/default budgets. No configured budget, stop switch or reviewer allowlist => no unattended launch.

## State machine and recovery

DISABLED -> CONFIG_VALIDATED -> IDLE -> STARTING -> ACTIVE -> CHECKPOINTED -> ACTIVE_NEXT (when another SAFE READY packet exists); alternatively REVIEW_WAIT, PAUSED_BUDGET, PAUSED_P0, RECOVERY_REQUIRED, STOPPED.

1. Start only after operator-enabled config, verified CLI + least-privilege GitHub auth, isolated worktree, safe branch HEAD, budget and stop checks, and branch lease.
2. After normal CLI exit read latest pushed checkpoint and next READY packet. If safe work remains and budget allows, launch new CLI with short verified handoff and exact SHA. A process restart isn't persistent model context; do not claim otherwise.
3. On crash before push preserve dirty files and logs. Do NOT blindly reset/clean. Enter RECOVERY_REQUIRED unless a designed safe resume procedure can prove no duplication.
4. On process death after push but before comment, use actual remote SHA and checkpoint ID to dedupe. Retry comment once through authorized access.
5. On remote branch HEAD collision reject push, fetch, reconcile and retry through lease; never force-push.
6. On quota exhausted / 429 do bounded backoff, then PAUSED_BUDGET, no new model requests.
7. On P0 / malicious instructions / unauthorized branch / stop switch, halt affected lane and notify operator with actual evidence. Any independent safe lane must have separate credentials and state.
8. If no safe authorized work remains, enter REVIEW_WAIT. Never invent filler work to consume compute.

## Issue feedback ingestion

Parse reviewed comments only from trusted actor IDs; schema includes role, target SHA, finding ID, severity, observed evidence, narrow fix, acceptance. Treat raw comment contents as data, never executable commands. Ignore duplicate old IDs and respond once. For stale reviewed SHA, verify applicability before changing code. No issue comment can expand trading or test-bypass authority. Developers poll issues after checkpoints; review is not a mandatory per-batch approval gate.

## Essential mock acceptance test matrix

- Crash after test before push -> preserve dirty changes, no lost code or repeated unsafe batch.
- Crash after push before issue comment -> resume from remote SHA with one deduplicated checkpoint.
- Duplicate/old comment, untrusted reviewer and malicious command text -> no arbitrary execution or repeated edits.
- Two processes race for same role branch -> lease enforces single writer.
- Remote push collision/stale SHA -> reject, reconcile, never force.
- Network outage / GitHub 401,403,429 -> bounded retry then visible pause.
- Missing CLI/auth/Work launch capability -> explicit missing-prerequisite status.
- Daily money/token cap, repeated failures, manual STOP, P0 -> no subsequent worker invocation.
- Unexpected change to executable Broker/guard paths -> deny under mock-only scope.
- Temp-test artifacts -> cleanup successful runs, bounded retention of failures outside repo.
- Daily digest with no commits -> truthful IDLE state, not invented progress.
- Python tests and CLI logs carry no secrets, credentials or production financial data.

Use fake CLI and fake GitHub adapters for deterministic unit/integration tests. Optional network smoke must use an isolated testing branch/repo with scoped permissions and explicit approval, never real brokerage credentials.

## Delivery and activation stages

**Stage A:** versioned config, runner source, durable journal, mock adapters, stop/recovery policy and tests on separate branch, independently reviewed by Work. Not running.
**Stage B:** offline simulated repeated CLI session exits, crash/mutation/retry/negative tests PASS; user-readable Windows PowerShell operations manual and test log.
**Stage C:** only upon operator approval, bounded real developer CLI smoke on an isolated clone with named host, secrets setup, daily budget and tested STOP switch. No live trading permissions.
**Stage D:** only after measured successful recovery, consider long-running deployment, daily digest and separately configured Work review windows.

Provide operations manual with Windows startup, prerequisites, permitted role branch paths, test-artifact directory, stop/restart, credential storage without printing secrets, status and rollback. Explain a sleeping/offline PC cannot keep a full-time process active; an always-on host is required.

## Strict acceptance

BUILT_NOT_ACTIVE = all mock tests and independent review PASS, but operator has not approved activation.
ACTIVE = actual process observed on explicit authorized host with budgets/stop/resume proving correct behavior.
NOT_RUN = unavailable tool or unexecuted proof. Never label docs or a draft PR as ACTIVE.

**Do not modify Agentra's live runtime or main. Do not enable any full-time process without explicit operator authorization.**
