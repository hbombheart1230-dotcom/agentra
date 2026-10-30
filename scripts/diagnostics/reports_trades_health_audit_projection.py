from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


def audit_reports_trades_health(reports_root: Path, *, day: str = "", facade: Any) -> Dict[str, Any]:

    trade_dirs = facade._iter_trade_dirs(reports_root, day=day)
    issues: List[Dict[str, Any]] = []
    issue_counts: Counter[str] = Counter()
    llm_status_counts: Counter[str] = Counter()
    lifecycle_status_counts: Counter[str] = Counter()
    duplicate_counts: Counter[str] = Counter()
    sidecar_counts: Counter[str] = Counter()

    for trade_dir in trade_dirs:
        trade_id = trade_dir.name
        lifecycle_path = facade._artifact_path(trade_dir, "lifecycle_bundle.json", "lifecycle/trade_lifecycle.json", "trade_lifecycle.json")
        ai_trade_report_llm_path = facade._artifact_path(
            trade_dir,
            "reports/ai_trade_report_llm_response.json",
            "ai_trade_report/ai_trade_report_llm_response.json",
        )
        brief_llm_path = facade._artifact_path(
            trade_dir,
            "reports/brief_llm_response.json",
        )
        strategist_llm_path = facade._artifact_path(
            trade_dir,
            "reports/strategist_llm_response.json",
            "strategist/strategist_llm_response.json",
        )

        for sidecar_name in ("_provenance.json", "_health.json", "_artifact_links.json"):
            if (trade_dir / sidecar_name).exists():
                sidecar_counts[f"{sidecar_name}:present"] += 1
            else:
                sidecar_counts[f"{sidecar_name}:missing"] += 1
                issues.append(
                    facade._issue(
                        severity="warn",
                        trade_id=trade_id,
                        component="trade_root",
                        code="sidecar_missing",
                        message=f"Missing additive sidecar {sidecar_name}.",
                        path=trade_dir / sidecar_name,
                    )
                )
                issue_counts["sidecar_missing"] += 1

        lifecycle = facade._read_json(lifecycle_path)
        lifecycle_diag = lifecycle.get("ai_report_diagnostics") if isinstance(lifecycle.get("ai_report_diagnostics"), dict) else {}
        lifecycle_status = str(lifecycle_diag.get("report_status") or "").strip().lower()
        if lifecycle_status:
            lifecycle_status_counts[lifecycle_status] += 1

        component_paths = {
            "ai_trade_report": ai_trade_report_llm_path,
            "brief": brief_llm_path,
            "strategist": strategist_llm_path,
        }
        component_rows: Dict[str, Dict[str, Any]] = {}
        for component, path in component_paths.items():
            payload = facade._read_json(path)
            component_rows[component] = payload
            if not payload:
                continue
            status = str(payload.get("status") or "").strip().lower()
            meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
            if component == "strategist" and bool(meta.get("synthetic_placeholder")):
                llm_status_counts["strategist:synthetic_placeholder"] += 1
                continue
            if (
                component == "strategist"
                and status == "fallback"
                and not str(payload.get("model") or "").strip()
                and not str(payload.get("raw_response_text") or "").strip()
                and not str(payload.get("error") or "").strip()
                and int(payload.get("retry_count") or 0) == 0
            ):
                llm_status_counts["strategist:synthetic_placeholder"] += 1
                continue
            if status:
                llm_status_counts[f"{component}:{status}"] += 1
            if component == "ai_trade_report" and status in {"partial", "salvaged", "repaired"}:
                missing = payload.get("required_keys_missing") if isinstance(payload.get("required_keys_missing"), list) else []
                parse_error = str(meta.get("parse_error") or payload.get("error") or "").strip()
                if facade._ai_trade_report_is_complete(trade_dir):
                    issues.append(
                        facade._issue(
                            severity="info",
                            trade_id=trade_id,
                            component=component,
                            code="llm_recovered",
                            message=f"AI trade report LLM output is {status}, but the final report artifact is structurally complete.",
                            path=path,
                        )
                    )
                    issue_counts["llm_recovered"] += 1
                else:
                    issues.append(
                        facade._issue(
                            severity="warn",
                            trade_id=trade_id,
                            component=component,
                            code="llm_partial",
                            message=f"AI trade report LLM output is {status}; missing_keys={len(missing)} parse_error={parse_error[:120]}",
                            path=path,
                        )
                    )
                    issue_counts["llm_partial"] += 1
            elif component == "brief" and status == "error":
                reason = str(meta.get("reason") or payload.get("error") or "").strip()
                issues.append(
                    facade._issue(
                        severity="warn",
                        trade_id=trade_id,
                        component=component,
                        code="llm_error",
                        message=reason or "Brief generation failed without a saved reason.",
                        path=path,
                    )
                )
                issue_counts["llm_error"] += 1
            elif component == "strategist" and status == "fallback":
                parse_mode = str(payload.get("parse_mode") or "").strip().lower()
                raw_len = len(str(payload.get("raw_response_text") or ""))
                issues.append(
                    facade._issue(
                        severity="warn",
                        trade_id=trade_id,
                        component=component,
                        code="llm_fallback",
                        message=f"Strategist LLM fell back; parse_mode={parse_mode or 'none'} raw_response_len={raw_len}.",
                        path=path,
                    )
                )
                issue_counts["llm_fallback"] += 1

        ai_report_payload = component_rows.get("ai_trade_report") or {}
        ai_report_status = str(ai_report_payload.get("status") or "").strip().lower()
        if lifecycle_status == "failed" and ai_report_status in {"partial", "salvaged", "repaired"}:
            issues.append(
                facade._issue(
                    severity="warn",
                    trade_id=trade_id,
                    component="lifecycle",
                    code="diagnostic_status_mismatch",
                    message=(
                        "Lifecycle diagnostics say failed, but an AI trade report artifact exists in "
                        f"{ai_report_status} state."
                    ),
                    path=lifecycle_path,
                )
            )
            issue_counts["diagnostic_status_mismatch"] += 1

    severity_counts = Counter(str(item.get("severity") or "info").lower() for item in issues)
    return {
        "ok": len([item for item in issues if str(item.get("severity") or "").lower() == "error"]) == 0,
        "reports_root": str(reports_root),
        "day": day,
        "trade_dir_count": len(trade_dirs),
        "llm_status_counts": dict(sorted(llm_status_counts.items())),
        "lifecycle_report_status_counts": dict(sorted(lifecycle_status_counts.items())),
        "issue_counts": dict(sorted(issue_counts.items())),
        "severity_counts": dict(sorted(severity_counts.items())),
        "duplicate_counts": dict(sorted(duplicate_counts.items())),
        "sidecar_counts": dict(sorted(sidecar_counts.items())),
        "issues": issues,
    }


