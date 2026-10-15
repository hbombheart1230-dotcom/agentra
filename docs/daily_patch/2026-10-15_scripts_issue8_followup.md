# 2026-10-15 — Issue #8 follow-up


## Follow-up iteration 2 — baseline fcc0944d

Status: **SCRIPTS_CONTINUATION_IN_PROGRESS**. Scope is only the GPT follow-up at
https://github.com/hbombheart1230-dotcom/agentra/issues/8#issuecomment-6184128399.
The accepted inventory and prior 141/20 audits were reused, not repeated.
Observed T4 HEAD: ac4642dc265811bf7ff56e32adbadf8203fed771; no T4 source edits.

### Three TEST_BLOCKED deltas (original disposition JSON remains baseline evidence)

- `run_opening_rank1_deep_dive.py`: empty `episodes` reproduced IndexError in
  `outlier_sensitivity` at `descending[0]`. One-line offline research fix returns
  `top1_return_pct: null` when no return is available, preserving nonempty results.
  Full pipeline with an explicitly empty research fixture writes JSON/CSV/Markdown
  only under pytest OS temp. This empty-data test block is resolved; entrypoint stays KEEP.
- `run_pytest.py`: retained Windows `venv/Scripts/python.exe` contract (caller:
  `scripts/run_pytest.cmd`, original inventory evidence). Mocked existence/dispatch
  verifies argv boundaries, repo CWD, child exit code, both prohibited --basetemp
  forms and missing-venv fail-closed behavior. Contract test block resolved; KEEP.
  This does not claim execution of a real Windows venv from this Linux host.
- `run_uef5_historical_recompute.py`: real CLI runs against an empty OS-temp root
  from an unrelated CWD with --no-write. Existing engine returns COMPLETE for an
  empty workload: discovered/considered/recomputed=0; every family admissible_units=0;
  no output files. This is not historical evidence acceptance. An existing focused
  authority test confirms missing receipt/archive/normalized roots remain NOT_PROVEN
  and emit no admitted candles. CLI test block resolved, but real historical
  recomputation remains TEST_BLOCKED until genuine admissible evidence is supplied.
  No production evidence was synthesized, no Reporting implementation changed.

### Redundant helper review (no consolidation authorized)

AST exact-body comparison of existing root top-level private functions (at least
20 AST nodes, excluding trivial delegates) found five duplicate groups only:
`_env_path` in demo_m14_mock_order.py / demo_m14_order_status.py;
`_write_jsonl`, `_clear_file`, `_env_bool`, `_env_int` in
 demo_m14_quote_then_order.py / demo_m15_smoke.py.
Direct callers use these for catalog paths, EXECUTION_ENABLED, quantities/prices,
intent/event deletion and order/approval logging. A private name is not proof of a
non-runtime helper: these are order-capable paths. Consolidation is BLOCKED by
protected trading-path scope and absent offline broker-parity/ownership approval.
No qualifying safe non-runtime duplicate was proven in this bounded exact-body
check; this is not a claim of no semantic duplication elsewhere.
Physical moves/renames/wrapper retirement remain BLOCKED pending explicit
ARCH_CONVERGENCE_APPROVED and external/manual usage proof. All141 wrappers stay.

### Separate Q12 operational review — no scheduler edit

Source confirmation: `register_mock_exam_tasks_example.bat` lines37/43 create
`%TASK_PREFIX%-Q12-Preopen` and `%TASK_PREFIX%-Q12-BTC-0855` with prefix
`TradingAgent-MockExamDay`; `unregister_mock_exam_tasks_example.bat` deletes only
Preopen, Session, SessionWatchdog, Closeout. Thus the two fully expanded names are
`TradingAgent-MockExamDay-Q12-Preopen` and `TradingAgent-MockExamDay-Q12-BTC-0855`.
Proposed future tests for owner review only: capture schtasks arguments with a stub,
compare exact expanded create/delete sets and task scope, verify unrelated names
are untouched and capture failure/exit semantics without invoking Task Scheduler.
Do not fix the asymmetric policy automatically. Live launchers were not executed.

### Focused evidence

- New follow-up tests7 PASS plus existing research tests5 PASS (12 total).
- Existing missing-authority test1 PASS, isolated fixture only.
- Pytest temporary outputs are outside repo; successful run directories cleaned.
- One nonfatal pytest warning: cache_dir option with cacheprovider disabled.
- No full CI/828 CLI replay or inventory reclassification.
- UI notes append-only; Issue #9 not started; PR #5 remains Draft.
