"""R10-A offline contract runner: execute ONE Reporter function inside a given source tree (BASE archive or HEAD) against a
temp report tree and print a JSON observation. Used by tests/test_work_reporter_r10_retained_io_contracts.py.

  python work_reporter_contract_runner.py <tree_root> <spec.json>

spec: {"module": "...", "function": "...", "calls": [{"args": [...], "kwargs": {...}}], "data_root": "<abs path>"}
String values "$ROOT" / "$ROOT/<rel>" are replaced by Path objects under data_root. The clock is frozen (every loaded
libs/graphs ``datetime`` binding), filesystem observations (open/read_text/read_bytes/exists/is_file/is_dir/iterdir/glob/
rglob/write_*/mkdir/unlink) are recorded IN ORDER, and the absolute data_root prefix is replaced by "<ROOT>" in all output.
No network, LLM, broker or production paths are touched (data_root is a temp dir)."""
import datetime as _dt
import importlib
import json
import sys
from pathlib import Path

FROZEN = "2026-10-17T09:00:00+00:00"


class FrozenDatetime(_dt.datetime):
    @classmethod
    def now(cls, tz=None):
        base = cls.fromisoformat(FROZEN)
        return base.astimezone(tz) if tz is not None else base.replace(tzinfo=None)

    @classmethod
    def utcnow(cls):
        return cls.fromisoformat(FROZEN).replace(tzinfo=None)


def main():
    tree, spec_path = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
    sys.path.insert(0, str(tree))
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    root = Path(spec["data_root"])
    module = importlib.import_module(spec["module"])
    for mod in list(sys.modules.values()):
        if getattr(mod, "__name__", "").startswith(("libs.", "graphs.")) and getattr(mod, "datetime", None) is _dt.datetime:
            mod.datetime = FrozenDatetime
    fn = getattr(module, spec["function"])
    log = []
    import builtins
    real_open = builtins.open

    def wrap(cls, name):
        orig = getattr(cls, name)

        def inner(self, *a, **k):
            log.append([name, str(self)])
            return orig(self, *a, **k)
        setattr(cls, name, inner)
    for name in ("read_text", "read_bytes", "exists", "is_file", "is_dir", "iterdir", "glob", "rglob", "write_text",
                 "write_bytes", "mkdir", "unlink", "open"):
        wrap(Path, name)

    def spy_open(file, *a, **k):
        log.append(["builtins.open", str(file), (a[0] if a else k.get("mode", "r"))])
        return real_open(file, *a, **k)
    builtins.open = spy_open

    def conv(v):
        if isinstance(v, str) and v.startswith("$STRROOT"):
            return str(root / v[9:]) if len(v) > 8 else str(root)
        if isinstance(v, str) and v.startswith("$FN:"):  # a callable from the tree under test, e.g. the facade's own helper
            mod_name, attr = v[4:].split(":")
            return getattr(importlib.import_module(mod_name), attr)
        if isinstance(v, str) and v.startswith("$ROOT"):
            return root / v[6:] if len(v) > 5 else root
        if isinstance(v, list):
            return [conv(x) for x in v]
        if isinstance(v, dict):
            return {k: conv(x) for k, x in v.items()}
        return v
    prefixes = sorted({str(root), root.as_posix(), str(root).replace("\\", "\\\\"), json.dumps(str(root))[1:-1]}, key=len, reverse=True)

    def scrub(s):
        s = str(s)
        for prefix in prefixes:
            s = s.replace(prefix, "<ROOT>")
        return s
    results = []
    for call in spec["calls"]:
        del log[:]
        try:
            value = fn(*conv(call["args"]), **conv(call["kwargs"]))
            if hasattr(value, "__next__"):
                value = list(value)
            out = ["ok", json.dumps(value, ensure_ascii=False, default=repr)]
        except Exception as exc:  # noqa: BLE001
            out = ["exc", type(exc).__name__, str(exc)]
        results.append({"outcome": [scrub(x) for x in out], "fs": [[scrub(y) for y in x] for x in log]})
    builtins.open = real_open
    import hashlib
    tree_after = sorted([p.relative_to(root).as_posix(), hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "<dir>"]
                        for p in root.rglob("*"))
    text = json.dumps({"calls": results, "data_tree_after": tree_after}, ensure_ascii=False)
    sys.stdout.buffer.write(text.encode("utf-8"))


if __name__ == "__main__":
    main()
