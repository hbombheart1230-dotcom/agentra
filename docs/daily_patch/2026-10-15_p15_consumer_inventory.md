# 2026-10-15 — T4+PR5 full tracked consumer inventory
- Integration source `b05b36a`; read-only AST inventory CI `38715884053` SUCCESS: 3,560 tracked, 2,226 Python, 0 parse errors, 4,486 static edges, 162 literal dynamic edges, 58 unresolved dynamic sites.
- 193 root scripts include **141 protected public compatibility wrappers**, not all deletable.
- `libs/agent/monitor.py` 3 and `libs/agent/reporter.py` 16 observed static consumers; do not delete these or other old interfaces using zero-static-consumer assumption.
- `libs/reporting/evaluation/` has 133 imported modules, 327 inbound cross-boundary static edges and 68 outgoing edges. Bulk move blocked.
- Root artifact names `b.jsonl` (3,514,424 B; 10 textual filename hits) and `_health.json` (167 B; 32 filename hits) analyzed in CI `38716302208`; no deletion and no content disclosure.
- Independent Codex audit work order authored; no implied Codex execution or approval.
- Original `main` / T4 / PR5 branches frozen; no operational code, State, Broker/LLM, UEF, Step5C or wrapper relocation.
