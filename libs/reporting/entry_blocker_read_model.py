from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence
from zoneinfo import ZoneInfo
import sys as _r3_sys
from libs.agents.reporter.read_models.entry_blocker_bodies_01 import (  # R-4 owner bodies (facade-injected)
    _to_float_r4_impl,
    _list_text_r4_impl,
    _normalize_blocker_family_r4_impl,
    explain_raw_blocker_r4_impl,
    _build_blocker_families_r4_impl,
    _build_family_raw_breakdown_r4_impl,
    _infer_scanner_quality_suspected_r4_impl,
    _scanner_quality_reason_explanation_r4_impl,
    _parse_ts_r4_impl,
    classify_entry_time_bucket_r4_impl,
    _resolve_structure_state_r4_impl,
    _resolve_threshold_actual_r4_impl,
    build_entry_blocker_row_r4_impl,
    build_symbol_entry_blocker_sequence_r4_impl,
    _counter_to_dict_r4_impl,
    summarize_entry_blocker_rows_r4_impl,
)
from libs.agents.reporter.read_models.entry_blocker_bodies_02 import (  # R-4 owner bodies (facade-injected)
    render_entry_blocker_summary_markdown_r4_impl,
)


KST = ZoneInfo("Asia/Seoul")

_RAW_BLOCKER_EXPLANATIONS: Dict[str, str] = {
    "pullback_not_mature": "눌림이 아직 충분히 성숙하지 않음",
    "pullback_mature": "눌림 성숙 조건을 계속 확인 중",
    "pullback_ok": "눌림 기본 조건은 통과 상태",
    "pullback_structure_ok": "눌림 구조는 유지 중",
    "pullback_volume_path_ok": "눌림 경로는 허용 범위이나 추가 확인 필요",
    "breakout_not_ready": "돌파 확인 조건 미충족",
    "breakout_ok": "돌파 기본 조건은 충족 방향",
    "breakout_path_ok": "돌파 경로는 허용 범위",
    "breakout_volume_gate_ok": "돌파 경로 추가 거래량 게이트는 충족 방향",
    "wait_for_confirmation": "추가 확인 신호를 대기 중",
    "volume_confirmation_missing": "거래량 확인 부족",
    "volume_ok": "거래량 기본 조건은 충족 방향",
    "below_vwap_reclaim_not_ready": "VWAP 회복 확인 미충족",
    "vwap_reclaim_ok": "VWAP 회복 조건은 충족 방향",
    "reclaim_gate_ok": "재회복 게이트는 충족 방향",
    "vwap_hold_ok": "VWAP 지지 유지 조건은 충족 방향",
    "rebound_ok": "반등 확인 조건은 충족 방향",
    "buy_blocked_open_position": "기존 포지션 보유 중이라 신규 매수 차단",
    "post_exit_cooldown": "직전 청산 후 재진입 대기",
    "too_extended_from_vwap": "VWAP 대비 과열/이격이 과도함",
    "extension_ok": "이격 조건은 관찰 중",
    "confidence_gate_ok": "신뢰도 게이트는 충족 방향",
    "risk_blocked": "리스크 보호 조건이 진입을 차단",
    "data_insufficient": "판단에 필요한 데이터가 부족함",
}

_BLOCKER_FAMILY_EXPLANATIONS: Dict[str, str] = {
    "pullback_timing": "눌림이 성숙 단계에 도달했는지와 눌림 경로 품질을 확인하는 축",
    "breakout_confirmation": "돌파/확인 신호가 충분히 확정되었는지 보는 축",
    "volume_confirmation": "거래량 확인과 체결 강도 관련 축",
    "reclaim_readiness": "VWAP 또는 재회복 확인이 충분한지 보는 축",
    "open_position_guard": "기존 포지션 보유로 신규 진입을 막는 구조적 가드",
    "cooldown_guard": "직전 청산 후 재진입 대기 가드",
    "rebound_confirmation": "반등 확인이 충분한지 보는 축",
    "confidence_gate": "종합 confidence 문턱과 근접도를 보는 축",
    "structure_confirmation": "차트 구조 유지 여부를 보는 축",
    "overextension_guard": "과도한 이격/과열 진입을 막는 축",
    "risk_guard": "리스크 보호 성격의 진입 차단 축",
    "other": "기타 보조 blocker 축",
    "unknown": "분류되지 않은 blocker 축",
}


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _to_float(value: Any) -> float | None:
    return _to_float_r4_impl(value, facade=_r3_sys.modules[__name__])


def _to_int(value: Any) -> int | None:
    try:
        return int(float(value))
    except Exception:
        return None


def _text(value: Any) -> str:
    return str(value or "").strip()


def _list_text(values: Any, *, limit: int = 8) -> List[str]:
    return _list_text_r4_impl(values, limit=limit, facade=_r3_sys.modules[__name__])


def _normalize_blocker_family(value: Any) -> str:
    return _normalize_blocker_family_r4_impl(value, facade=_r3_sys.modules[__name__])


def explain_raw_blocker(value: Any) -> str:
    return explain_raw_blocker_r4_impl(value, facade=_r3_sys.modules[__name__])


def explain_blocker_family(value: Any) -> str:
    key = _text(value)
    if not key:
        return ""
    return _BLOCKER_FAMILY_EXPLANATIONS.get(key, f"{key} 관련 blocker 묶음")


def _build_blocker_families(
    primary_blockers: Any,
    *,
    no_trade_code: Any = None,
    limit: int = 6,
) -> List[str]:
    return _build_blocker_families_r4_impl(primary_blockers, no_trade_code=no_trade_code, limit=limit, facade=_r3_sys.modules[__name__])


def _build_family_raw_breakdown(
    primary_blockers: Any,
    *,
    no_trade_code: Any = None,
    limit_per_family: int = 10,
) -> Dict[str, List[str]]:
    return _build_family_raw_breakdown_r4_impl(primary_blockers, no_trade_code=no_trade_code, limit_per_family=limit_per_family, facade=_r3_sys.modules[__name__])


def _infer_scanner_quality_suspected(
    *,
    no_trade_code: str,
    primary_blockers: Sequence[str],
    scanner_selected_summary: Mapping[str, Any],
    scanner_score_total: float | None,
) -> tuple[bool, str, List[str]]:
    return _infer_scanner_quality_suspected_r4_impl(no_trade_code=no_trade_code, primary_blockers=primary_blockers, scanner_selected_summary=scanner_selected_summary, scanner_score_total=scanner_score_total, facade=_r3_sys.modules[__name__])


def _scanner_quality_reason_explanation(value: Any) -> str:
    return _scanner_quality_reason_explanation_r4_impl(value, facade=_r3_sys.modules[__name__])


def _nested_counter_to_dict(counter_map: Mapping[str, Counter[str]]) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Dict[str, int]] = {}
    for key, counter in dict(counter_map or {}).items():
        out[str(key)] = _counter_to_dict(Counter(dict(counter.most_common(12))))
    return out


def _parse_ts(value: Any) -> datetime | None:
    return _parse_ts_r4_impl(value, facade=_r3_sys.modules[__name__])


def classify_entry_time_bucket(value: Any) -> str:
    return classify_entry_time_bucket_r4_impl(value, facade=_r3_sys.modules[__name__])


def _resolve_structure_state(monitor: Mapping[str, Any], blocker_surface: Mapping[str, Any]) -> str:
    return _resolve_structure_state_r4_impl(monitor, blocker_surface, facade=_r3_sys.modules[__name__])


def _resolve_threshold_actual(threshold_snapshot: Mapping[str, Any], field: str) -> Any:
    return _resolve_threshold_actual_r4_impl(threshold_snapshot, field, facade=_r3_sys.modules[__name__])


def build_entry_blocker_row(
    run_id: str,
    *,
    monitor: Mapping[str, Any],
    scanner: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    return build_entry_blocker_row_r4_impl(run_id, monitor=monitor, scanner=scanner, facade=_r3_sys.modules[__name__])


def load_entry_blocker_rows(
    canonical_root: str | Path,
    *,
    day: str,
    symbol: str = "",
    family: str = "",
    limit: int | None = None,
) -> List[Dict[str, Any]]:
    root = Path(canonical_root)
    day_root = root / day
    if not day_root.exists():
        return []
    rows: List[Dict[str, Any]] = []
    symbol_filter = _text(symbol).upper()
    family_filter = _text(family)
    for run_dir in sorted(path for path in day_root.iterdir() if path.is_dir()):
        monitor = _read_json(run_dir / "monitor.json")
        if not monitor:
            continue
        scanner = _read_json(run_dir / "scanner.json")
        row = build_entry_blocker_row(run_dir.name, monitor=monitor, scanner=scanner)
        if symbol_filter and _text(row.get("symbol")).upper() != symbol_filter:
            continue
        if family_filter and family_filter not in set(_list_text(row.get("blocker_families"), limit=12)):
            continue
        rows.append(row)
    rows.sort(key=lambda row: (_text(row.get("ts")), _text(row.get("run_id"))))
    if limit and int(limit) > 0:
        rows = rows[-int(limit) :]
    return rows


def build_symbol_entry_blocker_sequence(
    rows: Sequence[Mapping[str, Any]],
    *,
    symbol: str,
) -> List[Dict[str, Any]]:
    return build_symbol_entry_blocker_sequence_r4_impl(rows, symbol=symbol, facade=_r3_sys.modules[__name__])


def _counter_to_dict(counter: Any) -> Dict[str, int]:
    return _counter_to_dict_r4_impl(counter, facade=_r3_sys.modules[__name__])


def summarize_entry_blocker_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    symbol: str = "",
    family: str = "",
) -> Dict[str, Any]:
    return summarize_entry_blocker_rows_r4_impl(rows, symbol=symbol, family=family, facade=_r3_sys.modules[__name__])


def build_entry_blocker_day_summary(
    canonical_root: str | Path,
    *,
    day: str,
    symbol: str = "",
    family: str = "",
    limit: int | None = None,
) -> Dict[str, Any]:
    rows = load_entry_blocker_rows(canonical_root, day=day, symbol=symbol, family=family, limit=limit)
    summary = summarize_entry_blocker_rows(rows, symbol=symbol, family=family)
    summary.update(
        {
            "date": _text(day),
            "canonical_root": str(Path(canonical_root)),
            "rows": list(rows),
            "limit": int(limit or 0),
        }
    )
    return summary


def render_entry_blocker_summary_markdown(summary: Mapping[str, Any]) -> str:
    return render_entry_blocker_summary_markdown_r4_impl(summary, facade=_r3_sys.modules[__name__])


__all__ = [
    "build_entry_blocker_day_summary",
    "build_entry_blocker_row",
    "build_symbol_entry_blocker_sequence",
    "classify_entry_time_bucket",
    "explain_blocker_family",
    "explain_raw_blocker",
    "load_entry_blocker_rows",
    "render_entry_blocker_summary_markdown",
    "summarize_entry_blocker_rows",
]
