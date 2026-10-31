from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

from libs.core.symbols import normalize_symbol
from libs.runtime.strategy_horizon_feedback import (
    build_post_exit_shadow_placeholder,
    update_post_exit_shadow_with_price_observations,
)
import sys as _r3_sys
from libs.reporting import post_exit_shadow_scalar_projection as _scalar_owner
from libs.reporting import post_exit_shadow_format_projection as _format_owner
from libs.reporting import post_exit_shadow_env_projection as _env_owner
from libs.reporting import post_exit_shadow_freshness_projection as _freshness_owner
from libs.agents.reporter.narrative.post_exit_recap_bodies_01 import (  # R-4 owner bodies (facade-injected)
    _symbol_candidates_r4_impl,
    _rows_from_record_r4_impl,
    _latest_epoch_r4_impl,
    _epoch_seconds_r4_impl,
    _shadow_latest_required_epoch_r4_impl,
    _minute_row_key_r4_impl,
    merge_minute_rows_r4_impl,
    fetch_fresh_minute_rows_for_symbol_r4_impl,
    minute_rows_for_symbol_from_state_r4_impl,
    _parse_exit_kst_date_r4_impl,
    _row_kst_date_r4_impl,
    _row_kst_hhmmss_r4_impl,
    same_day_closeout_rows_for_shadow_r4_impl,
    _checkpoint_target_after_regular_close_r4_impl,
    _fill_regular_close_bound_pending_checkpoints_r4_impl,
    _post_exit_shadow_from_report_r4_impl,
    _checkpoint_summary_r4_impl,
    _render_trade_recap_markdown_r4_impl,
)
from libs.agents.reporter.narrative.post_exit_recap_bodies_02 import (  # R-4 owner bodies (facade-injected)
    _render_daily_recap_markdown_r4_impl,
)
from libs.agents.reporter.narrative.post_exit_shadow_recap_r8_bodies_01 import (  # R-4 owner bodies (facade-injected)
    _post_exit_shadow_from_lifecycle_r4_impl,
    _trade_label_r4_impl,
    build_post_exit_shadow_recap_r4_impl,
)


CHECKPOINT_LABELS = ("+5m", "+15m", "+30m", "+60m", "EOD")
KST = timezone(timedelta(hours=9), name="KST")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return raw if isinstance(raw, dict) else {}


def resolve_post_exit_state_path(reports_root: Path, state_path: Path | None = None) -> Path | None:
    candidates: List[Path] = []
    if state_path is not None and str(state_path).strip():
        candidates.append(Path(state_path))
    for key in ("STATE_STORE_PATH", "MOCK_EXAM_STATE_PATH"):
        raw = str(os.getenv(key) or "").strip()
        if raw:
            candidates.append(Path(raw))

    reports_root_path = Path(reports_root)
    candidates.append(reports_root_path.parent / "data" / "state.json")
    candidates.append(Path("data/state.json"))

    for candidate in candidates:
        path = candidate
        if not path.is_absolute():
            path = (Path.cwd() / path).resolve()
        if path.exists():
            return path
    return None


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8-sig", newline="\n")


def _as_dict(value: Any) -> Dict[str, Any]:
    return _scalar_owner._as_dict(value)


def _as_list(value: Any) -> List[Any]:
    return _scalar_owner._as_list(value)


def _symbol_candidates(symbol: str) -> List[str]:
    return _symbol_candidates_r4_impl(symbol, facade=_r3_sys.modules[__name__])


def _rows_from_record(record: Any, candidates: List[str]) -> List[Dict[str, Any]]:
    return _rows_from_record_r4_impl(record, candidates, facade=_r3_sys.modules[__name__])


def _latest_epoch(rows: Iterable[Mapping[str, Any]]) -> int:
    return _latest_epoch_r4_impl(rows, facade=_r3_sys.modules[__name__])


def _epoch_seconds(value: Any) -> float | None:
    return _epoch_seconds_r4_impl(value, facade=_r3_sys.modules[__name__])


def _fresh_minute_fetch_enabled() -> bool:
    return _env_owner._fresh_minute_fetch_enabled(facade=_r3_sys.modules[__name__])


def _shadow_latest_required_epoch(shadow: Mapping[str, Any]) -> float | None:
    return _shadow_latest_required_epoch_r4_impl(shadow, facade=_r3_sys.modules[__name__])


def _rows_reach_epoch(rows: Iterable[Mapping[str, Any]], target_epoch: float | None) -> bool:
    return _freshness_owner._rows_reach_epoch(rows, target_epoch, facade=_r3_sys.modules[__name__])


def _rows_reach_regular_close(rows: Iterable[Mapping[str, Any]]) -> bool:
    return _freshness_owner._rows_reach_regular_close(rows, facade=_r3_sys.modules[__name__])


def _post_exit_shadow_needs_fresh_minutes(shadow: Mapping[str, Any], rows: List[Dict[str, Any]]) -> bool:
    target_epoch = _shadow_latest_required_epoch(shadow)
    now_epoch = datetime.now(timezone.utc).timestamp()
    if target_epoch is not None:
        if now_epoch + 30.0 < target_epoch:
            return False
        if not _rows_reach_epoch(rows, target_epoch):
            return True

    now_kst = datetime.now(timezone.utc).astimezone(KST)
    checkpoints = _as_dict(shadow.get("checkpoints"))
    eod = _as_dict(checkpoints.get("EOD"))
    eod_pending = str(eod.get("status") or "").strip().lower() != "observed"
    if eod_pending and now_kst.strftime("%H%M%S") >= "153500":
        return not _rows_reach_regular_close(rows)
    return False


def _minute_row_key(row: Mapping[str, Any]) -> str:
    return _minute_row_key_r4_impl(row, facade=_r3_sys.modules[__name__])


def merge_minute_rows(*row_groups: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    return merge_minute_rows_r4_impl(*row_groups, facade=_r3_sys.modules[__name__])


def opening_rank1_eod_fallback_row(
    *, reports_root: Path, day: str, symbol: str
) -> tuple[Dict[str, Any] | None, Dict[str, Any]]:
    path = (
        Path(reports_root)
        / "evaluation"
        / "opening_rank1_shadow"
        / str(day)
        / "opening_rank1_shadow_daily.json"
    )
    payload = _read_json(path)
    normalized = normalize_symbol(symbol or "", allow_test_symbols=True)
    for raw in payload.get("episodes") or []:
        episode = _as_dict(raw)
        if normalize_symbol(episode.get("symbol") or "", allow_test_symbols=True) != normalized:
            continue
        eod = _as_dict(_as_dict(episode.get("checkpoints")).get("EOD"))
        if str(eod.get("status") or "").strip().lower() != "observed":
            continue
        price = eod.get("price") if eod.get("price") not in (None, "") else eod.get("observed_price")
        try:
            close = float(price)
        except Exception:
            continue
        observed_epoch = _epoch_seconds(eod.get("observed_epoch") or eod.get("observed_ts"))
        if observed_epoch is None:
            try:
                observed_epoch = datetime.fromisoformat(str(day)).replace(
                    hour=15, minute=30, tzinfo=KST
                ).timestamp()
            except Exception:
                continue
        observed_kst = datetime.fromtimestamp(observed_epoch, tz=timezone.utc).astimezone(KST)
        row = {
            "ts": int(observed_epoch),
            "raw_ts": observed_kst.strftime("%Y%m%d%H%M%S"),
            "open": close,
            "high": close,
            "low": close,
            "close": close,
            "volume": eod.get("volume"),
            "source": "opening_rank1_shadow.EOD",
            "eod_fallback": True,
        }
        return row, {
            "applied": True,
            "source": "opening_rank1_shadow.EOD",
            "source_path": str(path),
        }
    return None, {
        "applied": False,
        "reason": "matching_observed_opening_rank1_eod_not_found",
        "source_path": str(path),
    }


def fetch_fresh_minute_rows_for_symbol(symbol: str, *, run_id: str = "post_exit_shadow_recap") -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    return fetch_fresh_minute_rows_for_symbol_r4_impl(symbol, run_id=run_id, facade=_r3_sys.modules[__name__])


def minute_rows_for_symbol_from_state(state: Mapping[str, Any], symbol: str) -> List[Dict[str, Any]]:
    return minute_rows_for_symbol_from_state_r4_impl(state, symbol, facade=_r3_sys.modules[__name__])


def _parse_exit_kst_date(exit_ts: Any) -> str:
    return _parse_exit_kst_date_r4_impl(exit_ts, facade=_r3_sys.modules[__name__])


def _row_kst_date(row: Mapping[str, Any]) -> str:
    return _row_kst_date_r4_impl(row, facade=_r3_sys.modules[__name__])


def _row_kst_hhmmss(row: Mapping[str, Any]) -> str:
    return _row_kst_hhmmss_r4_impl(row, facade=_r3_sys.modules[__name__])


def same_day_closeout_rows_for_shadow(shadow: Mapping[str, Any], rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Keep the recap scoped to the sell date and full close, not T+1 drift."""
    return same_day_closeout_rows_for_shadow_r4_impl(shadow, rows, facade=_r3_sys.modules[__name__])


def _checkpoint_target_after_regular_close(row: Mapping[str, Any]) -> bool:
    return _checkpoint_target_after_regular_close_r4_impl(row, facade=_r3_sys.modules[__name__])


def _fill_regular_close_bound_pending_checkpoints(shadow: Mapping[str, Any]) -> Dict[str, Any]:
    """Close reporting-only checkpoints that mature after the regular session.

    A trade sold after 14:30 can have a +60m target past 15:30. Regular-session
    minute bars stop at the close, so a strict target lookup would stay pending
    forever even after the 16:00 recap. In that case the regular close is the
    final same-session observation for the report.
    """
    return _fill_regular_close_bound_pending_checkpoints_r4_impl(shadow, facade=_r3_sys.modules[__name__])


def _post_exit_shadow_from_report(report: Mapping[str, Any]) -> Dict[str, Any]:
    return _post_exit_shadow_from_report_r4_impl(report, facade=_r3_sys.modules[__name__])


def _post_exit_shadow_from_lifecycle(report_path: Path) -> Dict[str, Any]:
    return _post_exit_shadow_from_lifecycle_r4_impl(report_path, facade=_r3_sys.modules[__name__])


def _checkpoint_summary(shadow: Mapping[str, Any]) -> Dict[str, Any]:
    return _checkpoint_summary_r4_impl(shadow, facade=_r3_sys.modules[__name__])


def _pct(value: Any) -> str:
    return _format_owner._pct(value)


def _price(value: Any) -> str:
    return _format_owner._price(value)


def _trade_label(path: Path, report: Mapping[str, Any], shadow: Mapping[str, Any]) -> str:
    return _trade_label_r4_impl(path, report, shadow, facade=_r3_sys.modules[__name__])


def iter_trade_report_json_paths(reports_root: Path, day: str) -> List[Path]:
    trade_root = reports_root / "trades" / day
    if not trade_root.exists():
        return []
    return sorted(trade_root.rglob("reports/ai_trade_report.json"))


def build_post_exit_shadow_recap(
    *,
    reports_root: Path,
    day: str,
    state: Mapping[str, Any] | None = None,
    generated_at: str | None = None,
) -> Dict[str, Any]:
    return build_post_exit_shadow_recap_r4_impl(reports_root=reports_root, day=day, state=state, generated_at=generated_at, facade=_r3_sys.modules[__name__])


def render_post_exit_shadow_trade_recap_md(trade: Mapping[str, Any]) -> str:
    lines = [
        f"# 매도 후 가격 추적 Recap - {trade.get('label')}",
        "",
        "- 기준: 실제 매도 후 같은 종목을 가상 보유했다고 가정한 관측-only 결과입니다.",
        "- 적용: 기존 거래 리포트 본문은 수정하지 않습니다.",
        f"- 가격 관측 상태: {trade.get('price_observation_status')}",
        f"- 사유: {trade.get('price_observation_reason') or '-'}",
        f"- 마지막 관측 시각: {trade.get('latest_observed_ts') or '-'}",
        f"- 최선 관측 지점: {trade.get('best_exit_offset') or '-'} / {_price(trade.get('best_exit_price'))}",
        f"- 최대 매도 후 상승: {_pct(trade.get('max_post_exit_upside_pct'))}",
        f"- 최대 매도 후 하락: {_pct(trade.get('max_post_exit_drawdown_pct'))}",
        "",
        "| 지점 | 상태 | 가격 | 수익률 | 관측 시각 |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    checkpoints = _as_dict(trade.get("checkpoints"))
    for label in CHECKPOINT_LABELS:
        row = _as_dict(checkpoints.get(label))
        lines.append(
            f"| {label} | {row.get('status') or 'pending'} | {_price(row.get('price'))} | "
            f"{_pct(row.get('return_pct'))} | {row.get('observed_ts') or row.get('latest_observed_ts') or '-'} |"
        )
    return "\n".join(lines) + "\n"


def render_post_exit_shadow_daily_recap_md(recap: Mapping[str, Any]) -> str:
    summary = _as_dict(recap.get("summary"))
    lines = [
        f"# 매도 후 가격 추적 일괄 Recap ({recap.get('day')})",
        "",
        "- 기준: 16:00 closeout에서 당일 매도 후 가격 추적을 일괄 산출합니다.",
        "- 적용: 기존 ai_trade_report 본문은 수정하지 않고 별도 recap 파일만 생성합니다.",
        f"- 총 대상: {summary.get('total', 0)}건",
        f"- 관측 완료: {summary.get('observed', 0)}건",
        f"- EOD 관측 완료: {summary.get('eod_observed', 0)}건",
        f"- 대기: {summary.get('pending', 0)}건",
        "",
        "| 거래 | 상태 | +5m | +15m | +30m | +60m | EOD | 최선 지점 | 최대 상승 |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for trade in _as_list(recap.get("trades")):
        if not isinstance(trade, dict):
            continue
        checkpoints = _as_dict(trade.get("checkpoints"))
        returns = []
        for label in CHECKPOINT_LABELS:
            row = _as_dict(checkpoints.get(label))
            returns.append(_pct(row.get("return_pct")) if row.get("status") == "observed" else "-")
        lines.append(
            f"| {trade.get('label')} | {trade.get('price_observation_status')} | "
            f"{returns[0]} | {returns[1]} | {returns[2]} | {returns[3]} | {returns[4]} | "
            f"{trade.get('best_exit_offset') or '-'} | {_pct(trade.get('max_post_exit_upside_pct'))} |"
        )
    return "\n".join(lines) + "\n"


def render_post_exit_shadow_trade_recap_md(trade: Mapping[str, Any]) -> str:
    lines = [
        f"# 매도 후 가격 추적 Recap - {trade.get('label')}",
        "",
        "- 기준: 실제 매도 후 같은 종목을 가상 보유했다고 가정한 관측-only 결과입니다.",
        "- 적용: 기존 ai_trade_report 본문은 수정하지 않고 recap 및 summary 산출물만 갱신합니다.",
        f"- 가격 관측 상태: {trade.get('price_observation_status')}",
        f"- 사유: {trade.get('price_observation_reason') or '-'}",
        f"- 마지막 관측 시각: {trade.get('latest_observed_ts') or '-'}",
        f"- 최선 관측 지점: {trade.get('best_exit_offset') or '-'} / {_price(trade.get('best_exit_price'))}",
        f"- 최대 매도 후 상승: {_pct(trade.get('max_post_exit_upside_pct'))}",
        f"- 최대 매도 후 하락: {_pct(trade.get('max_post_exit_drawdown_pct'))}",
        "",
        "| 지점 | 상태 | 가격 | 수익률 | 관측 시각 |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    checkpoints = _as_dict(trade.get("checkpoints"))
    for label in CHECKPOINT_LABELS:
        row = _as_dict(checkpoints.get(label))
        lines.append(
            f"| {label} | {row.get('status') or 'pending'} | {_price(row.get('price'))} | "
            f"{_pct(row.get('return_pct'))} | {row.get('observed_ts') or row.get('latest_observed_ts') or '-'} |"
        )
    return "\n".join(lines) + "\n"


def render_post_exit_shadow_daily_recap_md(recap: Mapping[str, Any]) -> str:
    summary = _as_dict(recap.get("summary"))
    lines = [
        f"# 매도 후 가격 추적 일괄 Recap ({recap.get('day')})",
        "",
        "- 기준: stage4 closeout review와 16:00 closeout에서 당일 매도 후 가격 추적을 일괄 갱신합니다.",
        "- 적용: 기존 ai_trade_report 본문은 수정하지 않고 recap 및 ai_trade_summary 산출물만 갱신합니다.",
        f"- 총 대상: {summary.get('total', 0)}건",
        f"- 관측 완료: {summary.get('observed', 0)}건",
        f"- EOD 관측 완료: {summary.get('eod_observed', 0)}건",
        f"- 대기: {summary.get('pending', 0)}건",
        "",
        "| 거래 | 상태 | +5m | +15m | +30m | +60m | EOD | 최선 지점 | 최대 상승 |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for trade in _as_list(recap.get("trades")):
        if not isinstance(trade, dict):
            continue
        checkpoints = _as_dict(trade.get("checkpoints"))
        returns = []
        for label in CHECKPOINT_LABELS:
            row = _as_dict(checkpoints.get(label))
            returns.append(_pct(row.get("return_pct")) if row.get("status") == "observed" else "-")
        lines.append(
            f"| {trade.get('label')} | {trade.get('price_observation_status')} | "
            f"{returns[0]} | {returns[1]} | {returns[2]} | {returns[3]} | {returns[4]} | "
            f"{trade.get('best_exit_offset') or '-'} | {_pct(trade.get('max_post_exit_upside_pct'))} |"
        )
    return "\n".join(lines) + "\n"


def _render_trade_recap_markdown(trade: Mapping[str, Any]) -> str:
    return _render_trade_recap_markdown_r4_impl(trade, facade=_r3_sys.modules[__name__])


def _render_daily_recap_markdown(recap: Mapping[str, Any]) -> str:
    return _render_daily_recap_markdown_r4_impl(recap, facade=_r3_sys.modules[__name__])


def write_post_exit_shadow_recap_outputs(
    recap: Mapping[str, Any],
    *,
    report_dir: Path,
) -> Dict[str, str]:
    report_dir.mkdir(parents=True, exist_ok=True)
    day = str(recap.get("day") or "unknown")
    daily_json = report_dir / day / "post_exit_shadow_recap.json"
    daily_md = report_dir / day / "post_exit_shadow_recap.md"

    for trade in _as_list(recap.get("trades")):
        if not isinstance(trade, dict):
            continue
        _refresh_trade_summary_from_recap(trade)
        json_path = Path(str(trade.get("recap_json_path") or ""))
        md_path = Path(str(trade.get("recap_md_path") or ""))
        if str(json_path):
            _write_json(json_path, trade)
        if str(md_path):
            _write_text(md_path, _render_trade_recap_markdown(trade))

    _write_json(daily_json, recap)
    _write_text(daily_md, _render_daily_recap_markdown(recap))

    return {"report_json_path": str(daily_json), "report_md_path": str(daily_md)}


def _refresh_trade_summary_from_recap(trade: Dict[str, Any]) -> None:
    report_path = Path(str(trade.get("report_path") or ""))
    if not str(report_path) or not report_path.exists():
        trade["summary_refresh"] = {"attempted": False, "reason": "report_path_missing"}
        return

    reports_dir = report_path.parent
    summary_md_path = reports_dir / "ai_trade_summary.md"
    summary_input_path = reports_dir / "ai_trade_summary_input.json"
    summary_json_path = reports_dir / "ai_trade_summary.json"
    if not summary_md_path.exists() and not summary_input_path.exists():
        trade["summary_refresh"] = {"attempted": False, "reason": "summary_artifacts_missing"}
        return

    try:
        report = _read_json(report_path)
        shadow = _as_dict(trade.get("post_exit_shadow"))
        if shadow:
            report["post_exit_shadow"] = dict(shadow)
            fact_payload = _as_dict(report.get("fact_payload"))
            fact_trade = _as_dict(fact_payload.get("trade"))
            fact_trade["post_exit_shadow"] = dict(shadow)
            fact_payload["trade"] = fact_trade
            fact_payload["post_exit_shadow"] = dict(shadow)
            report["fact_payload"] = fact_payload

        from libs.reporting.trade_report_ai import (
            build_trade_summary_input,
            render_trade_summary_markdown,
            render_trade_summary_markdown_with_evaluation,
        )

        if summary_input_path.exists():
            _write_json(summary_input_path, build_trade_summary_input(report))
        if summary_md_path.exists():
            summary_report = _read_json(summary_json_path) if summary_json_path.exists() else {}
            if summary_report:
                summary_md = render_trade_summary_markdown_with_evaluation(report, summary_report)
            else:
                summary_md = render_trade_summary_markdown(report)
            _write_text(summary_md_path, summary_md)
        trade["summary_refresh"] = {
            "attempted": True,
            "ok": True,
            "summary_md_path": str(summary_md_path) if summary_md_path.exists() else "",
            "summary_input_path": str(summary_input_path) if summary_input_path.exists() else "",
        }
    except Exception as exc:
        trade["summary_refresh"] = {
            "attempted": True,
            "ok": False,
            "reason": "summary_refresh_failed",
            "error": str(exc),
        }


def generate_post_exit_shadow_recap(
    *,
    reports_root: Path,
    report_dir: Path,
    day: str,
    state_path: Path | None = None,
) -> Dict[str, Any]:
    resolved_state_path = resolve_post_exit_state_path(reports_root, state_path)
    state = _read_json(resolved_state_path) if resolved_state_path and resolved_state_path.exists() else {}
    recap = build_post_exit_shadow_recap(
        reports_root=reports_root,
        day=day,
        state=state,
    )
    recap["source"] = {
        "state_path": str(resolved_state_path) if resolved_state_path else "",
        "state_loaded": bool(state),
        "state_top_level_keys": len(state) if isinstance(state, dict) else 0,
    }
    paths = write_post_exit_shadow_recap_outputs(recap, report_dir=report_dir)
    out = dict(recap)
    out.update(paths)
    return out
