#!/usr/bin/env python3
"""Migrate 93 RF Markdown DONE checklists from historical seven criteria to FAST-3.

Only markdown under docs/refactor/plan/queue is touched; no runtime, orders,
configuration or CI workflow changes.  Use --write for migration, --check
to validate.  Existing legacy evidence is moved into a non-blocking section.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

QUEUE = Path(__file__).resolve().parents[1] / "plan" / "queue"
STAGES = {"01_PENDING", "02_DEVELOPING", "03_PEER_REVIEW", "04_LEAD_ACCEPTANCE", "05_DONE", "06_REWORK"}
CHECK = re.compile(r"^- \[([ xX])\] (.*)$", re.M)
META = re.compile(r"<!-- RF_CHECKLIST_META (\{[^\n]+\}) -->")
START = re.compile(r"(?m)^## DONE 체크\s*$")
NEXT_SECTION = re.compile(r"(?m)^## ")
DESCRIPTION = (
    "G1 CODE_READY — 원격 Owner·변경/KEEP 범위 및 핵심 호환 확인",
    "G2 TEST_READY — 변경 경계 관련 pytest/stdlib smoke 성공, 전체 peer·-O 비차단",
    "G3 INTEGRATED_DONE — 최소 통합/KEEP + 관련 smoke/CI + STATUS DONE",
)


def convert(path: Path, source: str) -> tuple[str, bool]:
    found = START.search(source)
    if not found:
        raise ValueError(f"{path}: missing ## DONE 체크")
    next_header = NEXT_SECTION.search(source, found.end())
    stop = next_header.start() if next_header else len(source)
    body = source[found.end():stop]
    rows = list(CHECK.finditer(body))
    if len(rows) == 3:
        # Already in the new format.
        if len(META.findall(body)) != 1:
            raise ValueError(f"{path}: FAST-3 metadata missing")
        return source, False
    if len(rows) != 7:
        raise ValueError(f"{path}: requires 7 legacy or 3 new criteria; found {len(rows)}")
    metas = META.findall(body)
    if len(metas) > 1:
        raise ValueError(f"{path}: duplicate legacy metadata")
    legacy = json.loads(metas[0]) if metas else {"next":1,"gate":"legacy","owner":"UNKNOWN","decision":"PENDING"}
    if not isinstance(legacy, dict):
        raise ValueError(f"{path}: malformed legacy metadata")
    verdicts = []
    for row in rows:
        match = re.search(r"— \*\*(MET|N/A|PARTIAL|PENDING|SAFETY_BLOCKED|MISSING|BLOCKED)\*\*", row.group(2))
        verdicts.append(match.group(1) if match else ("MET" if row.group(1).lower() == "x" else "PENDING"))
    is_done = path.parent.parent.name == "05_DONE"
    if is_done and any(v not in ("MET", "N/A") for v in verdicts):
        raise ValueError(f"{path}: historical DONE contains unfinished gate")
    if is_done:
        new_verdicts = ["MET", "MET", "MET"]
    else:
        g1 = "MET" if all(v in ("MET", "N/A") for v in verdicts[:2]) else "PARTIAL"
        g2 = "MET" if verdicts[2] == "MET" else ("PARTIAL" if verdicts[2] in ("PARTIAL", "MISSING") else "PENDING")
        new_verdicts = [g1, g2, "PENDING"]
    next_gate = next((i for i, v in enumerate(new_verdicts, 1) if v not in ("MET", "N/A")), 3)
    new_meta = {"next": next_gate,
                "gate": "FAST-3 next unmet gate; focus on changed files, not historical full-owner peer",
                "owner": "C05",
                "decision": "DONE" if is_done else "FAST_3_PENDING"}
    fresh = [
        "- [" + ("x" if v in ("MET", "N/A") else " ") + "] " + label + " — **" + v + "**"
        for label, v in zip(DESCRIPTION, new_verdicts)
    ]
    fresh.append("")
    fresh.append("<!-- RF_CHECKLIST_META " + json.dumps(new_meta, ensure_ascii=False, separators=(",", ":")) + " -->")
    fresh.append("")
    fresh.append("> FAST-3가 공식 수용 기준입니다. 아래 레거시 검증 이력은 비차단 참고 기록이며 신규 완료 조건이 아닙니다.")
    archive = [
        "## 레거시 C1~C7 체크 이력 (FAST-3 비차단)",
        "",
        *["> " + m.group(0) for m in rows],
        "",
        "<!-- RF_CHECKLIST_META_LEGACY " + json.dumps(legacy, ensure_ascii=False, separators=(",", ":")) + " -->",
        "",
    ]
    # Retain non-checklist observations / evidence links exactly as historical content.
    remainder = CHECK.sub("", body)
    remainder = META.sub("", remainder).strip()
    if remainder:
        archive.extend(["### 과거 검증·판정 상세 (이력)", "", remainder, ""])
    result = source[:found.end()] + "\n" + "\n".join(fresh) + "\n" + "\n".join(archive) + source[stop:]
    return result, True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = sorted(QUEUE.rglob("RF-[0-9][0-9][0-9].md"))
    ids = [f.stem for f in files]
    if len(files) != 93 or sorted(ids) != [f"RF-{i:03d}" for i in range(1, 94)]:
        raise ValueError("Expected exactly one RF-001..RF-093 file each")
    changes = []
    for path in files:
        if path.parent.parent.name not in STAGES:
            raise ValueError(f"Invalid stage: {path}")
        before = path.read_text(encoding="utf-8")
        after, changed = convert(path, before)
        if changed:
            changes.append((path, after))
    if args.check:
        if changes:
            raise SystemExit(f"MIGRATION_PENDING: {len(changes)} / 93 RFs still use legacy seven-gate checklist")
        print("PASS: all 93 RFs have FAST-3 checklist")
    else:
        for path, data in changes:
            path.write_text(data, encoding="utf-8")
        print(f"FAST_3_MIGRATED={len(changes)} of 93; previously migrated={93-len(changes)}")


if __name__ == "__main__":
    main()
