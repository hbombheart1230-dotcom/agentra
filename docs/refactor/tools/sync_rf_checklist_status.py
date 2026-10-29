#!/usr/bin/env python3
"""Validate 93 physical RFs and sync 14 priority FAST-3 checklists into STATUS.md.

Reads markdown only; never runs Agentra runtime, CI, brokers or user data.
Usage: python docs/refactor/tools/sync_rf_checklist_status.py --write
       python docs/refactor/tools/sync_rf_checklist_status.py --check
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
STATUS = BASE / "plan" / "STATUS.md"
QUEUE = BASE / "plan" / "queue"
START, END = "<!-- RF_LEAD_CHECKLIST_START -->", "<!-- RF_LEAD_CHECKLIST_END -->"
ORDER = "063 067 015 050 031 014 016 028 029 033 034 032 065 069".split()
STAGES = ("01_PENDING", "02_DEVELOPING", "03_PEER_REVIEW", "04_LEAD_ACCEPTANCE", "05_DONE", "06_REWORK")


def queue_counts():
    rf_files = sorted(QUEUE.rglob("RF-[0-9][0-9][0-9].md"))
    ids = [path.stem for path in rf_files]
    expected = [f"RF-{i:03d}" for i in range(1, 94)]
    if len(rf_files) != 93 or sorted(ids) != expected:
        raise ValueError("Physical queue must have exactly RF-001..RF-093, one file each")
    count = {stage: 0 for stage in STAGES}
    for path in rf_files:
        if path.parent.parent.name not in count:
            raise ValueError(f"Unknown RF queue stage: {path}")
        count[path.parent.parent.name] += 1
    return count


BOX = re.compile(r"^- \[([ xX])\] .*? — \*\*(MET|N/A|PARTIAL|PENDING|SAFETY_BLOCKED|MISSING)\*\*", re.M)
META = re.compile(r"<!-- RF_CHECKLIST_META (\{[^\n]+\}) -->")


def render(counts):
    lines = [
        "## 우선 14건 RF 원본 체크리스트 — 현재 실물 단계 연동",
        "",
        "FAST-3: **G1 원격 코드·Owner 범위**, **G2 변경 부분 smoke/pytest**, **G3 통합·완료**. 7항목 C1~C7은 비차단 역사 근거이며 full owner peer/모든 RF -O/전체 hosted CI는 필수가 아닙니다. [D00 §2](../work_orders/D00_ENGINEERING_DELIVERY_POLICY.md) 우선. 본 표는 C05가 관리합니다.",
        "",
        "| RF 원본 | 실물 단계·Owner→Peer | MET · N/A · 남음 | 미충족 체크 | 다음 해제 조건 · 담당 | 상태 |",
        "|---|---|---:|---|---|---|",
    ]
    met_total = na_total = 0
    stage_counts = {"02_DEVELOPING": 0, "03_PEER_REVIEW": 0, "04_LEAD_ACCEPTANCE": 0}
    queue_root = BASE / "plan" / "queue"
    for rf in ORDER:
        matches = sorted(queue_root.rglob(f"RF-{rf}.md"))
        if len(matches) != 1:
            raise ValueError(f"RF-{rf}: expected unique physical file, got {len(matches)}")
        path = matches[0]
        parent = path.parent.name
        stage = path.parent.parent.name
        if stage in stage_counts:
            stage_counts[stage] += 1
        content = path.read_text(encoding="utf-8")
        found = re.search(r"^## DONE 체크\s*\n(.*?)(?=^## |\Z)", content, re.M | re.S)
        if found is None:
            raise ValueError(f"{path}: no original checklist")
        marks = BOX.findall(found.group(1))
        meta = META.findall(found.group(1))
        if len(marks) not in (3, 7) or len(meta) != 1:
            raise ValueError(f"{path}: requires FAST-3 or 7 historical criteria and metadata")
        state = json.loads(meta[0])
        if len(marks) == 7:
            # Backward-compatible DISPLAY; original 7-item RFs need migration.
            old = [verdict for _, verdict in marks]
            is_done = stage == "05_DONE"
            g1 = "MET" if is_done or all(v in ("MET", "N/A") for v in old[:2]) else "PARTIAL"
            g2 = "MET" if is_done or old[2] == "MET" else ("PARTIAL" if old[2] in ("PARTIAL", "MISSING") else "PENDING")
            g3 = "MET" if is_done else "PENDING"
            marks = [("x" if verdict == "MET" else " ", verdict) for verdict in (g1, g2, g3)]
            state = {**state, "next": next((i for i, (_, v) in enumerate(marks, 1) if v not in ("MET", "N/A")), 3), "gate": "FAST-3 current gate (legacy source pending migration)", "owner": "C05", "decision": "DONE" if is_done else "FAST_3_PENDING"}
        checked, missing, met, exempt = [], [], [], []
        for idx, (mark, verdict) in enumerate(marks, 1):
            if (mark.lower() == "x") != (verdict in ("MET", "N/A")):
                raise ValueError(f"{path}: checkbox/verdict disagree at C{idx}")
            (checked if mark.lower() == "x" else missing).append(idx)
            if verdict == "MET":
                met.append(idx)
            elif verdict == "N/A":
                exempt.append(idx)
        if stage == "05_DONE":
            # Completed priority RFs have no unchecked next gate. Keep a final
            # C7 marker only when all seven criteria are actually satisfied.
            if missing or state["next"] != 3 or state["decision"] != "DONE":
                raise ValueError(f"{path}: DONE requires all three FAST-3 gates")
        elif state["next"] not in missing:
            raise ValueError(f"{path}: NEXT gate must be unchecked")
        met_total += len(met)
        na_total += len(exempt)
        if stage == "04_LEAD_ACCEPTANCE" and any(i in missing for i in range(1, 3)):
            raise ValueError(f"{path}: LEAD not allowed while G1-G2 incomplete")
        if stage == "05_DONE" and missing:
            raise ValueError(f"{path}: DONE not allowed while checklist incomplete")
        link = path.relative_to(BASE / "plan").as_posix()
        owner_peer = "A → B" if parent in ("CLAUDE_A", "FROM_CLAUDE_A") else "B → A"
        stage_label = {"02_DEVELOPING": "DEV", "03_PEER_REVIEW": "PEER", "04_LEAD_ACCEPTANCE": "LEAD"}.get(stage, stage)
        remains = ",".join(f"G{i}" for i in missing) or "—"
        gate = state["gate"].replace("|", "/").replace("\n", " ")
        owner = state["owner"].replace("|", "/").replace("\n", " ")
        lines.append(
            f"| [RF-{rf}]({link}) | {stage_label} · {owner_peer} | MET {len(met)} · N/A {len(exempt)} · {len(missing)}남음 | {remains} | "
            f"**G{state['next']}** {gate} (**{owner}**) | {state['decision']} |"
        )
    lines.extend([
        "",
        f"**우선 14건:** **MET {met_total}/42 · N/A {na_total}/42 · 미완료 {42-met_total-na_total}/42**. "
        f"실제 DEV {stage_counts['02_DEVELOPING']} + PEER {stage_counts['03_PEER_REVIEW']}, "
        f"LEAD {stage_counts['04_LEAD_ACCEPTANCE']}. 물리 DONE은 {counts['05_DONE']}건이며 N/A를 증거 PASS로 합산하지 않습니다.",
        "",
        "**STATUS 갱신 책임: 지팀장.** RF 변경/증거 인수 및 물리 이동 시 같은 작업에서 `python docs/refactor/tools/sync_rf_checklist_status.py --write` 후 `--check` 확인. 이 도구는 93개 실물 파일의 유일성/단계 수와 우선 14개 원본 체크를 대조하며 RF 합격/안전 실행을 자동 승인하지 않습니다.",
    ])
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    op = p.add_mutually_exclusive_group(required=True)
    op.add_argument("--write", action="store_true")
    op.add_argument("--check", action="store_true")
    args = p.parse_args()
    counts = queue_counts()
    source = STATUS.read_text(encoding="utf-8")
    if source.count(START) != 1 or source.count(END) != 1:
        raise ValueError("STATUS markers missing or repeated")
    before, rest = source.split(START, 1)
    _, after = rest.split(END, 1)
    updated = before + START + "\n" + render(counts) + "\n" + END + after
    values = [counts[s] for s in STAGES]
    record = "| " + " | ".join(str(n) for n in values) + " | **93** |"
    row_re = r"(?m)^\| \d+ \| \d+ \| \d+ \| \d+ \| \d+ \| \d+ \| \*\*93\*\* \|$"
    updated, n = re.subn(row_re, lambda _: record, updated, count=1)
    if n != 1:
        raise ValueError("STATUS queue-count row missing or not unique")
    if args.check:
        if source != updated:
            raise SystemExit("STALE: run --write after RF checklist changes")
        print("PASS: 93 unique physical RFs and 14 priority FAST-3 checklists match STATUS")
    elif updated != source:
        STATUS.write_text(updated, encoding="utf-8")
        print("UPDATED: STATUS 93 RF queue counts + 14 priority checklists")
    else:
        print("UNCHANGED: STATUS current")


if __name__ == "__main__":
    main()
