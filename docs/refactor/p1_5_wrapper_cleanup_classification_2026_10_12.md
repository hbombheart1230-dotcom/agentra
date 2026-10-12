# P1.5.10 wrapper cleanup classification (first pass, static, no deletion)

Input data for the GPT per-function second-pass optimisation design. Machine-readable: [p1_5_wrapper_cleanup_inventory_2026_10_12.json](p1_5_wrapper_cleanup_inventory_2026_10_12.json). Evidence scope is **static only** (no runtime proof); nothing was deleted, renamed or consolidated.

| Class | Result | Disposition |
|---|---|---|
| DEFINITE_DEAD | **0** | nothing authorised for removal |
| Reporting façade ABI (436 callables) | 106 statically referenced, **330 static-unreferenced = UNKNOWN (not dead)**, 11 dynamic/wildcard/parse hazards (1,888 files scanned) | KEEP; retirement needs runtime/dynamic/CLI/monkeypatch proof (P1.5.10 later) |
| Legacy adapters `libs/agent/{commander,strategist,scanner,monitor}.py`, `apps/operator_ui/data_access*.py` | few static importers (1-3 each) but public compatibility surface | KEEP_STABLE_FACADE |
| `graphs/nodes/{scan_candidates,select_candidate,commander_node}.py`, `libs/runtime/intraday_monitor_signals.py` | 0-3 static importers; graph/registry/string wiring not provable statically | KEEP_UNTIL_CONSUMER_PROOF |
| M13 runtime modules (`m13_live_loop`, `m13_tick`, `m13_eod_report`, entrypoint, CLI) | referenced by deploy PowerShell/CLI/lock tooling | KEEP; canonical alias names added in Wave C (additive) |
| Duplicate function bodies | 114 identical-body groups / 395 functions (>=6 LOC, across libs/graphs/apps/scripts; owner `*_r3_parts` and tests excluded); largest: duplicated CLI helpers in `scripts/run_m27_*`, reporting `to_epoch`/`_iter_jsonl` families | KEEP: independent CLIs/readers, no consumer proof, low benefit; candidates for a later shared-helper design |
| State / env aliases (`m13_tick_pipeline`, `M13_LIVE_LOCK_*`, `legacy_m10`) | live contract | KEEP; dual-key migration is second pass |

No small-helper duplicate was consolidated: the benefit did not justify losing independent module seams or touching CLI tooling without consumer evidence.
