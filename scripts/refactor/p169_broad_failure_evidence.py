"""Extract observed terminal exception/location from preserved pytest JUnit.

Offline evidence processing only. Missing traceback facts remain BLOCKED.
Only known checkout roots, user temp roots and interpreter install roots are
normalized; line numbers, dataset names, exception classes and error causes stay.
This proves observed failure signatures, not every underlying semantic cause.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET


def normalize(text):
    text = re.sub(r"/+", "/", text.replace("\\", "/"))
    text = re.sub(r"C:/AgentraEvidence/b_(?:base|final)", "<TREE>", text, flags=re.I)
    text = re.sub(r"[A-Za-z]:/Users/[^/]+/AppData/Local/Temp/[^'\"\n]*", "<TEMP>", text)
    text = re.sub(r"[A-Za-z]:/[^'\"\n]*?/Lib/", "<PYTHON>/Lib/", text)
    return re.sub(r"0x[0-9a-fA-F]+", "<ADDRESS>", text)


def extract(path):
    rows = {}
    for case in ET.parse(path).iter("testcase"):
        node = case.get("classname", "").replace(".", "/") + ".py::" + case.get("name", "")
        for child in case:
            if child.tag not in ("failure", "error"):
                continue
            text = child.text or ""
            frames = re.findall(r"^(.+?\.py):(\d+): ([\w.]+)(?::.*)?$", text, re.M)
            exception = frames[-1][2] if frames else None
            location = normalize(frames[-1][0]) + ":" + frames[-1][1] if frames else None
            cause = normalize(child.get("message", "").splitlines()[0]) if child.get("message") else None
            # Last test frame is additional context, not the terminal exception frame.
            tests = re.findall(r"^(tests[\\/].+?\.py):(\d+):", text, re.M)
            test_location = normalize(tests[-1][0]) + ":" + tests[-1][1] if tests else None
            rows[node] = {"kind": child.tag, "type": exception, "loc": location,
                          "msg": cause, "test_location": test_location,
                          "evidence_status": "OBSERVED" if exception and location and cause else "BLOCKED"}
    return dict(sorted(rows.items()))


def signature(row):
    return row["kind"], row["type"], row["loc"], row["msg"], row["test_location"]


def build(base, final, base_log, final_log):
    b, f = extract(base), extract(final)
    for rows, log_path in ((b, base_log), (f, final_log)):
        log = normalize(log_path.read_text(encoding="utf-8", errors="replace"))
        for row in rows.values():
            row["terminal_frame_in_log"] = bool(row["type"] and row["loc"]
                                                and f"{row['loc']}: {row['type']}" in log)
            if not row["terminal_frame_in_log"]:
                row["evidence_status"] = "BLOCKED"
    common = set(b) & set(f)
    same = sorted(k for k in common if signature(b[k]) == signature(f[k])
                  and b[k]["evidence_status"] == f[k]["evidence_status"] == "OBSERVED")
    blocked = sorted(k for k in common if b[k]["evidence_status"] != "OBSERVED"
                     or f[k]["evidence_status"] != "OBSERVED")
    return {"schema": "p169_observed_failure_evidence.v1", "base": b, "final": f,
            "diff": {"BASE_ONLY": sorted(set(b) - set(f)), "FINAL_ONLY": sorted(set(f) - set(b)),
                     "SAME_FAILURE_SIGNATURE": same, "BLOCKED": blocked,
                     "SAME_ID_DIFFERENT_CAUSE": sorted(common - set(same) - set(blocked))},
            "raw_evidence": {p.name: {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                                      "bytes": p.stat().st_size} for p in (base, final, base_log, final_log)},
            "scope": "Observed terminal exception, location and first cause line; not proof of all semantic causes.",
            "historical_run_provenance": {"status": "BLOCKED",
                "reported_base_sha": "73f2277bfe95fda6d548572e48764966d01661e4",
                "reported_final_sha": "f476f160fa66d778b576e48a630cfa1f5878db93",
                "basis": "Original operator report only; not embedded in JUnit or authenticated by the retained logs."},
            "provenance_limit": "JUnit does not embed Git SHA or dependency fingerprint; original SHA/env association is operator-reported.",
            "normalization": "Known b_base/b_final checkout roots, user TEMP, interpreter Lib root, hex object addresses only; no line-number or general numeric tolerance."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = [args.evidence_dir / name for name in ("broad_base.xml", "broad_final.xml", "broad_base.log", "broad_final.log")]
    result = build(*paths)
    args.output.write_text(json.dumps(result, ensure_ascii=True, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: len(v) for k, v in result["diff"].items()}))


if __name__ == "__main__":
    main()
