# 2026-10-06 -- Docker live-open observation and Daily UEF freshness incident

Operational record only. This note makes no code, deployment, trading, UEF, ownership,
or scheduler-behaviour change.

## Docker live-open observation

- The canonical trading runtime at the observed live open was the single Docker runtime
  (`trading-agent-live`), generation 5. The Host live-launch path recorded
  `HOST_LIVE_START_SKIPPED_CANONICAL_RUNTIME_DOCKER`; the collector path remained active.
- The retained daily operator report records two successful broker-aligned executions:
  BUY `217590` quantity 41 at the opening controlled-probe path and the corresponding
  SELL quantity 41. Its broker reconciliation reports two local and two broker records,
  all matched by order number.
- The contemporaneous Docker observation recorded `RestartCount=0` and no OOM kill. This
  is an observation of that running generation, not a new Docker acceptance or a claim
  that the image carried post-open changes.
- The earlier Docker restart-storm incident and its R1/R2 RCA remain historical records in
  the 2026-10-01/02 notes. No new restart-storm fix, Docker rebuild, or deployment is
  claimed here.

## Daily UEF result

- `TradingAgent-DailyUefEvaluation` started at 2026-10-06 16:45:02 KST from
  `C:\Agentra` at source SHA `a38bf4e9f5f6f76eaee37659c45c7c49705fcef2`.
- It ended at 16:45:03 KST with exit code 1, no canonical generation, and the explicit
  failure reason that one or more sources failed a registered freshness contract or were
  unknown. The task failed closed before it could materialize a canonical board that
  mixed a fresh `through_day` label with stale or unreviewed content.
- This is an operational freshness incident, not a UEF framework/freeze failure and not a
  successful 2026-10-06 Daily UEF publication. The retained lifecycle event does not
  identify the individual offending closeout-written source; source-level RCA remains
  open. No source artifact was repaired, backfilled, deleted, or republished.

## Status

- Restart-storm RCA: historical root cause and corrective work are documented in the
  2026-10-01/02 records; this note records no recurrence or new fix.
- Daily UEF freshness RCA: incomplete. The next investigation must identify the registered
  source(s) that were stale or unknown without altering canonical authority artifacts.
- R6/R6.1/R6.2 remain code/audit records only; their deployment and live acceptance are
  not asserted by this operational note.
