# 2026-10-15 — GPT Source Work Order01

BRANCH: refactor/agentra-target-tree
BASE_SHA: 76e7232c8eda6bf28590256e89c9d511fb673e74
STATUS: SCRIPTS_CONTINUATION_IN_PROGRESS
Specification: user's inline Source Work Order01, no independent scope expansion.

## Implementation

Only canonical diagnostic scripts query_commander_resilience_events.py,
query_strategist_llm_events.py, query_trade_reason_chain.py and
query_m25_notification_events.py changed, plus focused tests and these notes.
Four independent JSONL parsing loops replaced by list(iter_jsonl_events(path));
public _load_jsonl / _iter_rows names retained. Shared reader and M25 _utc_day
unchanged. No date filter passed, no cache produced.

Trade rows prefer explicitly present execution.allowed (including false/null).
Only absent allowed falls back to an earlier verdict with matching explicit
intent_id. verdict_reason is never copied from execution.reason or a mismatched/
ID-less verdict. execution_reason and JSON keys retained.
Prior decision/LLM/verdict context is indexed by run and explicit intent ID;
conflicting top-level/decision_packet/decision_packet.intent intent IDs are
unproven. Legacy ID-less decision/LLM fallback retained only for a single
execution in the whole run with exclusively ID-less candidate context. Multiple
ID-less executions cannot inherit ambiguous run-level rationale. No new events,
order authority or runtime producer changes.

Broker diagnostic code uses finite Decimal numeric equality to zero; no float
truncation (0.5/-0.5 false) or underflow-to-zero for tiny nonzero strings. Existing
text success/failure codes and blank/None behavior preserved. No broker outcome,
approval, retry, Step5C or executor modifications.

## Focused verification

77 pytest PASS across new test_diagnostic_queries_work_order01.py and existing
trade reason, commander resilience, M25 notification, shared event reader and
Strategist ops tests (test_m20_4_llm_ops_scripts.py). One nonfatal pytest warning:
cache_dir option with cacheprovider disabled. Successful pytest temp cleans itself.

New regressions cover all specified broker boundaries, tiny nonzero decimals,
missing/empty/malformed/non-dictionary JSONL, unicode, duplicates, source order,
no cache, root/canonical import identity, explicit true/false/null allowed,
UNKNOWN/NOT_SENT outcomes, interleaved BUY/SELL intents, matching and mismatched
verdict/decision, ambiguous legacy contexts, conflicting IDs, output keys,
filters, limit and invalid action exit3.

CLI matrix: 20 scenarios × four entrypoint forms =80 fake-file subprocesses:
root direct/module and canonical direct/module, JSON/text/help/unknown-option/
missing-file behavior. stdout/stderr and exit codes equal across forms.
Eight additional base-vs-current comparisons (four scripts × JSON/text) preserve
stdout/stderr/exit codes on unchanged legacy fixtures. Trade correction itself
is verified separately, not masked by requiring erroneous prior values.

No full repository regression. No native Windows test execution performed in
this local batch; existing CI is a separate source-only contract gate, not proof
that this new diagnostic regression suite ran on Windows.

## Scope, evidence and residual limits

Latest T4 changed-path comparison excludes all code/test changes; only approved
append-only UI patch-note paths may overlap. All141 wrappers preserved. Shared
reader, graphs, execution/supervisor/risk, UEF, broker/approval, scheduler/launchers,
Config, Web/API/UI code untouched. No live event files, orders, external APIs or
operational tasks executed. Only synthetic files and isolated OS-temp paths used.

Missing/conflicting IDs cannot prove verdict attribution; fields stay empty/None
instead of assigning another intent's reason. Legacy single-execution decision/
LLM run-level context remains a compatibility fallback, not independent provenance.
Event associations use prior events in file order; no claim for out-of-order logs
or real production-data acceptance. Out-of-scope structural candidates in the
work order remain untouched. Physical layout/wrapper retirement gates remain.
PR #5 stays Draft; no main merge. Changed-files-only ZIP generated from final commit.
