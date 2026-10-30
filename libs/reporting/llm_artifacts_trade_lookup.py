"""LLM artifacts trade directory lookup (moved verbatim from llm_artifacts).

Helpers are resolved on ``facade`` (the llm_artifacts module) at call time; this module never imports it.
Read-only filesystem scans only.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def iter_trade_dirs(trade_day_root: Path) -> List[Path]:
    root = Path(trade_day_root)
    if not root.exists() or not root.is_dir():
        return []
    found: Dict[str, Path] = {}
    for path in root.rglob("*"):
        if not path.is_dir():
            continue
        name = str(path.name or "").strip()
        if name in {"reports", "brief", "ai_trade_report", "lifecycle", "strategist", "evidence"}:
            trade_root = path.parent
        else:
            trade_root = path
        trade_name = str(trade_root.name or "").strip()
        if not trade_name.startswith("TRD_") and not (
            (path / "lifecycle_bundle.json").exists()
            or (path / "aggregated_execution_bundle.json").exists()
            or (path / "trade_lifecycle.json").exists()
        ):
            continue
        found[str(trade_root.resolve())] = trade_root
    return sorted(found.values(), key=lambda item: (item.parent.name, item.name))


def find_trade_dir(trade_day_root: Path, trade_id: str, *, facade: Any) -> Path | None:
    normalized_trade_id = str(trade_id or "").strip()
    if not normalized_trade_id:
        return None
    root = Path(trade_day_root)
    direct = root / normalized_trade_id
    if direct.exists() and direct.is_dir():
        return direct
    for trade_dir in facade.iter_trade_dirs(root):
        if trade_dir.name == normalized_trade_id:
            return trade_dir
    return None


def _looks_like_trade_day_dir(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False
    try:
        for child in path.iterdir():
            if not child.is_dir():
                continue
            if str(child.name or "").startswith("TRD_"):
                return True
            for grandchild in child.iterdir():
                if grandchild.is_dir() and str(grandchild.name or "").startswith("TRD_"):
                    return True
        return False
    except Exception:
        return False


def misplaced_trade_day_root(reports_root: Path, day: str, *, facade: Any) -> Path | None:
    normalized_day = str(day or "").strip()
    if not normalized_day:
        return None
    primary = facade.canonical_trade_day_root(reports_root, normalized_day)
    repo_root = facade._repo_root_from_reports_root(reports_root)
    candidate = repo_root / normalized_day
    if candidate == primary:
        return None
    if not facade._looks_like_trade_day_dir(candidate):
        return None
    return candidate


def resolve_trade_day_root(reports_root: Path, day: str, *, facade: Any) -> Path:
    primary = facade.canonical_trade_day_root(reports_root, day)
    if primary.exists():
        return primary
    fallback = facade.misplaced_trade_day_root(reports_root, day)
    if fallback is not None:
        return fallback
    return primary


def iter_trade_day_roots(reports_root: Path, *, facade: Any) -> List[Path]:
    roots: List[Path] = []
    seen_days: set[str] = set()
    canonical_root = Path(reports_root) / "trades"
    if canonical_root.exists():
        for child in sorted(path for path in canonical_root.iterdir() if path.is_dir()):
            roots.append(child)
            seen_days.add(child.name)
    repo_root = facade._repo_root_from_reports_root(reports_root)
    for child in sorted(path for path in repo_root.iterdir() if path.is_dir()):
        if child.name in seen_days:
            continue
        if not facade._looks_like_trade_day_dir(child):
            continue
        roots.append(child)
    return roots


def list_misplaced_trade_day_roots(reports_root: Path, *, facade: Any) -> List[Path]:
    repo_root = facade._repo_root_from_reports_root(reports_root)
    canonical_root = Path(reports_root) / "trades"
    canonical_days = {
        child.name
        for child in canonical_root.iterdir()
        if canonical_root.exists() and child.is_dir()
    } if canonical_root.exists() else set()
    out: List[Path] = []
    for child in sorted(path for path in repo_root.iterdir() if path.is_dir()):
        if child.name in canonical_days:
            continue
        if not facade._looks_like_trade_day_dir(child):
            continue
        out.append(child)
    return out
