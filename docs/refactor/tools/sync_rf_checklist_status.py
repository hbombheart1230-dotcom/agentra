#!/usr/bin/env python3
"""Sync 14 LEAD RF original DONE checkboxes and NEXT gates into STATUS.md.

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
QUEUE = BASE / "plan" / "queue" / "04_LEAD_ACCEPTANCE"
START, END = "<!-- RF_LEAD_CHECKLIST_START -->", "<!-- RF_LEAD_CHECKLIST_END -->"
ORDER = "063 067 015 050 031 014 016 028 029 033 034 032 065 069".split()
BOX = re.compile(r"^- \[([ xX])\] .*? — \*\*(MET|N/A|PARTIAL|PENDING|SAFETY_BLOCKED|MISSING)\*\*", re.M)
META = re.compile(r"<!-- RF_CHECKLIST_META (\{[^\n]+\}) -->")


def render():
    lines = [
        "## LEAD RF 원본 체크리스트 — 한눈에 보는 잔여 조건",
        "",
        "각 RF 원본 \`DONE 체크\`의 **7개 항목**을 읽은 스냅샷입니다. **MET**는 증거 확인, **N/A**는 조건부 비적용으로 DONE이나 PASS로 세지 않습니다. **PARTIAL/PENDING/SAFETY_BLOCKED**는 미완료입니다. 링크를 열면 체크 이유와 증거 범위가 있습니다. 이 표는 파일 저장 시 실시간 조회되는 것이 아니라 동기화 명령으로 갱신됩니다.",
        "",
        "| RF 원본 | Owner→Peer | 체크 / 미완료 | 남은 체크 | 다음 해제 조건 · 담당 | 상태 |",
        "|---|---|---:|---|---|---|",
    ]
    total = 0
    for rf in ORDER:
        parent = "FROM_CLAUDE_A" if int(rf) < 60 else "FROM_CODEX_B"
        path = QUEUE / parent / f"RF-{rf}.md"
        content = path.read_text(encoding="utf-8")
        found = re.search(r"^## DONE 체크\s*\n(.*?)(?=^## |\Z)", content, re.M | re.S)
        if found is None:
            raise ValueError(f"{path}: no original checklist")
        marks = BOX.findall(found.group(1))
        meta = META.findall(found.group(1))
        if len(marks) != 7 or len(meta) != 1:
            raise ValueError(f"{path}: requires seven marked criteria and one metadata record")
        state = json.loads(meta[0])
        checked, missing = [], []
        for idx, (mark, verdict) in enumerate(marks, 1):
            if (mark.lower() == "x") != (verdict in ("MET", "N/A")):
                raise ValueError(f"{path}: checkbox/verdict disagree at C{idx}")
            (checked if mark.lower() == "x" else missing).append(idx)
        if state["next"] not in missing:
            raise ValueError(f"{path}: NEXT gate must be unchecked")
        total += len(checked)
        link = f"queue/04_LEAD_ACCEPTANCE/{parent}/RF-{rf}.md"
        owner_peer = "A → B" if int(rf) < 60 else "B → A"
        remains = ",".join(f"C{i}" for i in missing) or "—"
        gate = state["gate"].replace("|", "/").replace("\n", " ")
        owner = state["owner"].replace("|", "/").replace("\n", " ")
        lines.append(
            f"| [RF-{rf}]({link}) | {owner_peer} | {len(checked)}/7 · {len(missing)}남음 | {remains} | "
            f"**C{state['next']}** {gate} (**{owner}**) | {state['decision']} |"
        )
    lines.extend([
        "",
        f"**LEAD 14건:** 체크 {total}/98 · 미완료 {98-total}/98. 물리 DONE은 아직 14건(기존)이고, 위 체크 숫자는 RF 종결 건수가 아닙니다.",
        "",
        "RF 체크/증거 변경 시 같은 커밋에 \`python docs/refactor/tools/sync_rf_checklist_status.py --write\` 실행. \`--check\`로 STATUS 동기화 상태 검사. D00·기존 CI·보호 코드는 수정하지 않습니다."
    ])
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    op = p.add_mutually_exclusive_group(required=True)
    op.add_argument("--write", action="store_true")
    op.add_argument("--check", action="store_true")
    args = p.parse_args()
    source = STATUS.read_text(encoding="utf-8")
    if source.count(START) != 1 or source.count(END) != 1:
        raise ValueError("STATUS markers missing or repeated")
    before, rest = source.split(START, 1)
    _, after = rest.split(END, 1)
    updated = before + START + "\n" + render() + "\n" + END + after
    if args.check:
        if source != updated:
            raise SystemExit("STALE: run --write after RF checklist changes")
        print("PASS: 14 original LEAD checklists match STATUS")
    elif updated != source:
        STATUS.write_text(updated, encoding="utf-8")
        print("UPDATED: STATUS 14 RF checklists")
    else:
        print("UNCHANGED: STATUS current")


if __name__ == "__main__":
    main()
