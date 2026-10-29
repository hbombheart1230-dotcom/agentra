"""Read-only trade report index owner."""

from typing import Any, Dict


def trade_report_index(config, *, facade):
    day_roots = facade.iter_trade_day_roots(config.reports_root)
    if not day_roots:
        return {"by_run_id": {}, "by_story_id": {}}

    by_run_id: Dict[str, Dict[str, Any]] = {}
    by_story_id: Dict[str, Dict[str, Any]] = {}
    seen_bundle_paths: set[str] = set()
    bundle_candidates = sorted(
        [
            path
            for day_root in day_roots
            for trade_dir in facade.iter_trade_dirs(day_root)
            for path in (
                trade_dir / "lifecycle_bundle.json",
                trade_dir / "aggregated_execution_bundle.json",
            )
            if path.exists()
        ],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for bundle_path in bundle_candidates:
        key_path = str(bundle_path.resolve())
        if key_path in seen_bundle_paths:
            continue
        seen_bundle_paths.add(key_path)
        bundle = facade._read_json(bundle_path)
        if not bundle:
            continue

        bundle_day = str(bundle.get("day") or "").strip()
        lifecycle_status_hint = str(bundle.get("trade_lifecycle_status") or "").strip()
        trade_id_hint = str(bundle.get("trade_id") or bundle.get("story_id") or "").strip()
        paths = facade._trade_paths_from_bundle(bundle_path, day_hint=bundle_day, trade_id_hint=trade_id_hint)
        lifecycle_path = facade._existing_trade_path(
            paths,
            "lifecycle_bundle_json",
            "trade_lifecycle_json",
            "legacy_normalized_trade_lifecycle_json",
            "legacy_trade_lifecycle_json",
        )
        lifecycle = facade._read_json(lifecycle_path) if lifecycle_path.exists() else {}
        (
            trade_id,
            story_id,
            run_id,
            linked_run_ids,
            execution,
            story_contract,
            reporter_status_human,
            operator_conclusion_human,
            execution_outcome_human,
        ) = facade._project_trade_identity(
            lifecycle=lifecycle,
            bundle=bundle,
            paths=paths,
            bundle_path=bundle_path,
        )
        report_json_path = facade._existing_trade_path(paths, "ai_trade_report_json", "legacy_trade_report_json")
        report_md_path = facade._existing_trade_path(paths, "ai_trade_report_md", "legacy_trade_report_md")
        story_input_path = facade._existing_trade_path(paths, "ai_trade_report_input_json", "legacy_trade_story_input_json")
        operator_brief_json_path = facade._existing_trade_path(paths, "brief_json")
        operator_brief_md_path = facade._existing_trade_path(paths, "brief_md")
        strategist_llm_response_path = facade._existing_trade_path(paths, "strategist_llm_response_json")
        ai_trade_report_llm_response_path = facade._existing_trade_path(paths, "ai_trade_report_llm_response_json")
        brief_llm_response_path = facade._existing_trade_path(paths, "brief_llm_response_json")
        trade_provenance_path = facade._existing_trade_path(paths, "trade_provenance_json")
        trade_health_path = facade._existing_trade_path(paths, "trade_health_json")
        trade_artifact_links_path = facade._existing_trade_path(paths, "trade_artifact_links_json")
        trade_provenance = facade._read_json(trade_provenance_path) if trade_provenance_path.exists() else {}
        trade_health = facade._read_json(trade_health_path) if trade_health_path.exists() else {}
        report = facade._read_json(report_json_path)
        generation, lifecycle_status, lifecycle_summary, story_type, execution_mode_label, report_summary, reporter_summary = facade._project_trade_summary(
            report=report,
            lifecycle=lifecycle,
            bundle=bundle,
            operator_conclusion_human=operator_conclusion_human,
            execution_outcome_human=execution_outcome_human,
            reporter_status_human=reporter_status_human,
            story_contract=story_contract,
            facade=facade,
        )
        ts_epoch = facade._to_epoch(bundle.get("ts"))
        if ts_epoch is None:
            ts_epoch = int(bundle_path.stat().st_mtime)
        path_priority = 2 if bundle_path.name == "lifecycle_bundle.json" else (2 if bundle_path.parent.name == "lifecycle" else 1)
        symbol = facade.normalize_symbol(
            execution.get("symbol") or report.get("symbol") or "",
            allow_test_symbols=True,
        )
        action = str(execution.get("action") or report.get("action") or "").upper()
        report_exists = bool(report_json_path.exists() or report_md_path.exists())
        record = facade._project_trade_record(
            report_exists=report_exists,
            trade_id=trade_id,
            story_id=story_id,
            run_id=run_id,
            linked_run_ids=linked_run_ids,
            symbol=symbol,
            action=action,
            story_type=story_type,
            reporter_summary=reporter_summary,
            lifecycle_status=lifecycle_status,
            generation=generation,
            lifecycle_summary=lifecycle_summary,
            execution_mode_label=execution_mode_label,
            report_summary=report_summary,
            report=report,
            bundle=bundle,
            lifecycle=lifecycle,
            trade_health=trade_health,
            facade=facade,
        )
        # Keep existence probes after formatting, including repeated probes.
        record.update({
            "trade_report_json_path": str(report_json_path) if report_json_path.exists() else "",
            "trade_report_md_path": str(report_md_path) if report_md_path.exists() else "",
            "trade_story_input_path": str(story_input_path) if story_input_path.exists() else "",
            "ai_trade_report_json_path": str(report_json_path) if report_json_path.exists() else "",
            "ai_trade_report_md_path": str(report_md_path) if report_md_path.exists() else "",
            "ai_trade_report_input_path": str(story_input_path) if story_input_path.exists() else "",
            "trade_lifecycle_json_path": str(lifecycle_path) if lifecycle_path.exists() else "",
            "operator_brief_json_path": str(operator_brief_json_path) if operator_brief_json_path.exists() else "",
            "operator_brief_md_path": str(operator_brief_md_path) if operator_brief_md_path.exists() else "",
            "strategist_llm_response_path": str(strategist_llm_response_path) if strategist_llm_response_path.exists() else "",
            "ai_trade_report_llm_response_path": str(ai_trade_report_llm_response_path) if ai_trade_report_llm_response_path.exists() else "",
            "brief_llm_response_path": str(brief_llm_response_path) if brief_llm_response_path.exists() else "",
            "trade_provenance_json_path": str(trade_provenance_path) if trade_provenance_path.exists() else "",
            "trade_health_json_path": str(trade_health_path) if trade_health_path.exists() else "",
            "trade_artifact_links_json_path": str(trade_artifact_links_path) if trade_artifact_links_path.exists() else "",
            "section_provenance": (
                dict(trade_provenance.get("section_provenance") or {})
                if isinstance(trade_provenance, dict)
                else {}
            ),
            "aggregated_bundle_path": str(bundle_path),
            "trade_root_path": str(paths.get("trade_root") or ""),
            "ts_epoch": ts_epoch,
            "_path_priority": path_priority,
        })

        run_updates, story_updates = facade._project_trade_indexes(
            story_id=story_id,
            linked_run_ids=linked_run_ids,
            record=record,
            by_story_id=by_story_id,
            by_run_id=by_run_id,
        )
        by_run_id.update(run_updates)
        by_story_id.update(story_updates)
    return {"by_run_id": by_run_id, "by_story_id": by_story_id}

