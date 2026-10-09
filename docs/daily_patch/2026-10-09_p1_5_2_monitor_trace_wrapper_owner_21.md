# P1.5.2 — Monitor Public Trace Wrapper Owner 21 (2026-10-09)

- Base SHA `42f6ad832672edca8d29b5f350360eefa78df88d` on `refactor/p1.5`.
- Moved unchanged original implementations of `resolve_strategist_adaptive_exit`, `build_monitor_stop_policy_trace`, and `build_monitor_blocker_trace` into `trade_story_human_parts/monitor_traces.py` (107 physical LOC), retaining public names/signatures and explicit call-time dependency injections.
- Original three AST function bodies unchanged and 32 input combinations x 3 public functions produced equal results in isolated before/after comparison. `normalize_stop_thresholds`, `resolve_adaptive_stop_loss_pct`, `safe_float`, `format_ratio_pct`, `clip`, and `list_text` still resolve from public wrappers at call time.
- Human payload parent 431 -> exactly 350 physical LOC; new owner 107 LOC. This achieves this module's size cap, NOT P1.5.2 final closure or other public façade acceptance.
- New compatibility/monkeypatch tests included in broad Reporting CI. No trading order, strategy, Supervisor/Executor, broker, UEF, R6.2, Step5C/D, Docker or live data writes. P1.5.2 OPEN.
