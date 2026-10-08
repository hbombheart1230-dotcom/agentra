# 2026-10-06 -- yfinance dependency restore and data-source status integrity

Data-integrity / environment fix. No strategy, scoring, UEF, execution, ownership (R1-R5) or runtime-mode
semantics changed. Docker was not rebuilt or restarted; no replay or backfill of today's expired captures.

## Incident

- `TradingAgent-MockExamDay-Q12-BTC-0855` returned 2 at 08:55: `capture_status=MISSING`,
  `reason=btc_usd_point_in_time_source_missing`, 4 attempts, 0 sources. The script maps exit 2 to
  "not CAPTURED".
- Cause: `yfinance` is not in `requirements.txt` and was lost when `C:\Agentra\venv` was recreated on
  2026-10-03 (the migration drift audit left it out as optional). `_yf_rows()` swallowed the ImportError and
  returned `[]`.
- Blast radius: the Q10 08:50 preopen snapshot was written `CAPTURED` with 13/13 observations `UNAVAILABLE`
  (12/13 available on 2026-10-01/02). The Docker image never contained yfinance (it only installs `requirements.txt`).

## Changes

1. `requirements.txt`: `yfinance==1.7.0`; installed into the host venv via `pip install -r requirements.txt`.
2. `libs/market/yfinance_support.py` (new): `DataSourceDependencyError`, `require_yfinance()`,
   `yfinance_dependency_status()`, `try_yfinance(component)` (one explicit ERROR log per component).
3. Collectors fail loudly: Q12 `_yf_rows`, Q12 08:55 capture (`DEPENDENCY_MISSING`, no retry, exit 3),
   Q10 provider + capture script (nothing persisted, exit 3), preopen macro snapshot (+ script exit 3;
   opening-macro slot -> `CAPTURE_FAILED` with the explicit error), Q12 vNext fetchers.
4. Loop-adjacent best-effort paths keep degrading but log explicitly: `global_sentiment`, `news_pipeline`
   yfinance fallback, scanner feature hydration (`dependency_missing:yfinance` instead of
   `yfinance_unavailable`), decision-context seed; `load_btc_signal_rows` carries
   `fallback_reason` / `data_source_error` instead of crashing baseline loops.
5. Q10 status semantics: all observations `UNAVAILABLE` -> `capture_status=DATA_UNAVAILABLE`,
   `reason=all_lead_market_observations_unavailable`, `observation_summary{total,available}`; snapshot still
   persisted and immutable. Partial data stays `CAPTURED`. Consumers requiring `CAPTURED`
   (controlled-lane signals/coordinator, `check_q9_q12_readiness`, capture script exit code) treat it as not captured.

Exit codes (Q10, Q12, macro capture scripts): 0 captured, 2 not captured, 3 required dependency missing.

## Verification

- Host venv: yfinance 1.7.0 on Python 3.14.2, `pip check` clean.
- Docker parity (static): throwaway `python:3.12-slim-bookworm` `pip install --dry-run -r requirements.txt` resolves
  the same set (yfinance 1.7.0, pandas 3.0.6, numpy 2.5.3). The running image `trading-agent-20261002:61586ae`
  does not contain yfinance and needs a post-close rebuild. (Pulling the base tag updated the local
  `python:3.12-slim-bookworm` tag; the running container is unaffected.)
- Read-only dry loads (no artifacts written): Q10 12/13 AVAILABLE (hynix_adr unavailable, as before);
  Q12 BTC/USD and BTC/KRW eligible for an 08:55 point-in-time capture; global_sentiment inputs populated;
  yfinance news returned 0 items for AAPL/NVDA/005930.KS (upstream/unclear, not a dependency error).
- Tests: `tests/test_yfinance_dependency_integrity.py` (27) plus related Q10/Q12/macro/sentiment/news/hydration
  suites pass.
- Not touched: today's Q12 snapshot (MISSING) and Q10 snapshot (CAPTURED, 0/13) remain as written.

## Follow-up

- Rebuild the trading image after the close so the container carries the declared dependency.
- Consider a dependency check (`yfinance_dependency_status()`) in the operator readiness check.
