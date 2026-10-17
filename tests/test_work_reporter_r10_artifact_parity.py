"""Reporter R10-B: cross-boundary report artifact parity (offline, synthetic inputs, temp dirs only).

Chain per tree (pinned BASE archive vs HEAD), each in a fresh interpreter with a frozen clock:
  story_input -> build_deterministic_trade_report -> render_trade_report_markdown / render_trade_summary_markdown
              -> render_trade_report_markdown_clean / render_trade_summary_markdown_clean
The produced report JSON and Markdown must be byte-identical between BASE and HEAD (Korean text, CRLF inside inputs,
missing/partial sections). The artifacts are then written under canonical file names into a temp trade dir and read
through the path-based API adapter `apps/api/adapters/safe_reports.py` (loaded without the FastAPI app package), which
must return identical payloads for BASE- and HEAD-produced artifacts, including missing / empty / malformed / oversize
artifact cases. No LLM, network, production report path or writer code is invoked."""
import importlib.util
import io
import json
import subprocess
import sys
import tarfile
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASE = "d773709ba2f70471fad9badba4f92400f7818319"

CHAIN = r'''
import datetime as _dt, json, sys
FROZEN = "2026-10-17T09:00:00+00:00"
class F(_dt.datetime):
    @classmethod
    def now(cls, tz=None):
        b = cls.fromisoformat(FROZEN); return b.astimezone(tz) if tz is not None else b.replace(tzinfo=None)
    @classmethod
    def utcnow(cls):
        return cls.fromisoformat(FROZEN).replace(tzinfo=None)
import libs.reporting.trade_report_ai as ai
import libs.reporting.trade_report_markdown_clean as md
for m in list(sys.modules.values()):
    if getattr(m, "__name__", "").startswith(("libs.", "graphs.")) and getattr(m, "datetime", None) is _dt.datetime:
        m.datetime = F
out = []
for story in json.loads(sys.stdin.buffer.read().decode("utf-8")):
    row = {}
    try:
        rep = ai.build_deterministic_trade_report(story)
        row["report_json"] = json.dumps(rep, ensure_ascii=False, indent=2, default=repr)
        for name, fn in (("report_md", ai.render_trade_report_markdown), ("summary_md", ai.render_trade_summary_markdown),
                         ("report_md_clean", md.render_trade_report_markdown_clean),
                         ("summary_md_clean", md.render_trade_summary_markdown_clean)):
            try:
                row[name] = fn(rep)
            except Exception as exc:
                row[name] = "EXC:%s:%s" % (type(exc).__name__, exc)
    except Exception as exc:
        row["error"] = "EXC:%s:%s" % (type(exc).__name__, exc)
    out.append(row)
sys.stdout.buffer.write(json.dumps(out, ensure_ascii=False).encode("utf-8"))
'''

STORIES = [
    {},
    {"trade_id": "TRD_20261017_005930_01", "symbol": "005930", "symbol_name": "삼성전자", "action": "SELL", "day": "2026-10-17",
     "entry": {"price": 81000, "qty": 3, "ts": "2026-10-17T00:01:00Z", "reason": "VWAP 돌파\r\n거래량 증가"},
     "exit": {"price": 82400, "qty": 3, "ts": "2026-10-17T02:10:00Z", "reason": "목표가 도달"},
     "pnl": 4200, "pnl_pct": 0.0173, "holding_duration": "2h 9m",
     "market_context_at_entry": {"summary": "강세장", "vix_level": 19.4, "market_news_titles": ["반도체 강세", "환율 안정"]},
     "why_this_symbol_was_chosen": {"basis": "rank 1", "selected_rank": 1, "score": 3.2},
     "strategist": {"summary": "모멘텀 추종", "confidence": 0.7}},
    {"trade_id": "TRD_X", "symbol": None, "action": "BUY", "entry": "not-a-dict", "pnl": "n/a", "lifecycle": []},
]


@pytest.fixture(scope="module")
def base_tree(tmp_path_factory):
    if subprocess.run(["git", "cat-file", "-e", BASE + "^{commit}"], cwd=ROOT).returncode != 0:
        raise AssertionError(f"pinned BASE {BASE} not in this clone: fetch with full history (fetch-depth: 0)")
    root = tmp_path_factory.mktemp("base_tree_b")
    data = subprocess.run(["git", "archive", BASE, "libs", "graphs"], cwd=ROOT, capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as tf:
        tf.extractall(root)
    return root


def produce(tree, tmp):
    script = tmp / "chain.py"
    script.write_text(CHAIN, encoding="utf-8")
    # full inherited environment (Windows needs SYSTEMDRIVE etc.; a stripped env makes the OS create a literal
    # "%SystemDrive%" folder in the cwd) and a temp cwd so nothing can ever be created inside the repository
    env = dict(__import__("os").environ, PYTHONPATH=str(tree), PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    r = subprocess.run([sys.executable, str(script)], cwd=str(tmp), input=json.dumps(STORIES, ensure_ascii=False).encode("utf-8"),
                       capture_output=True, env=env)
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")[-2000:]
    return json.loads(r.stdout.decode("utf-8"))


def load_safe_reports():
    """Load apps/api/adapters/safe_reports.py and its infrastructure dependency WITHOUT importing apps/api/__init__.py
    (which builds the FastAPI app). Pure path-based reader; same source file the API uses."""
    pkgs = {"apps": ROOT / "apps", "apps.api": ROOT / "apps/api", "apps.api.adapters": ROOT / "apps/api/adapters",
            "apps.api.infrastructure": ROOT / "apps/api/infrastructure"}
    saved = {k: sys.modules.get(k) for k in list(pkgs) + ["apps.api.infrastructure.bounded_reader", "apps.api.adapters.safe_reports"]}
    try:
        for name, path in pkgs.items():
            mod = types.ModuleType(name)
            mod.__path__ = [str(path)]
            sys.modules[name] = mod
        for name in ("apps.api.infrastructure.bounded_reader", "apps.api.adapters.safe_reports"):
            spec = importlib.util.spec_from_file_location(name, ROOT / (name.replace(".", "/") + ".py"))
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
        return sys.modules["apps.api.adapters.safe_reports"]
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


def write_artifacts(trade_dir, row):
    rep = trade_dir / "reports"
    rep.mkdir(parents=True, exist_ok=True)
    if "report_json" in row:
        (rep / "ai_trade_report.json").write_text(row["report_json"], encoding="utf-8")
        (rep / "ai_trade_report.md").write_text(row.get("report_md", ""), encoding="utf-8")
        (rep / "ai_trade_summary.md").write_text(row.get("summary_md", ""), encoding="utf-8")


def api_view(sr, trade_dir):
    out = {}
    for spec in sr.REPORT_SPECS:
        try:
            out[spec.report_id] = json.dumps(sr.read_safe_report(trade_dir, spec, max_bytes=1_000_000), ensure_ascii=False, default=repr)
        except Exception as exc:  # noqa: BLE001
            out[spec.report_id] = f"EXC:{type(exc).__name__}:{exc}"
    # only the absolute temp location differs between the two trade dirs; everything else is compared verbatim
    return {k: v.replace(str(trade_dir), "<TRADE>").replace(repr(str(trade_dir))[1:-1], "<TRADE>") for k, v in out.items()}


def test_producer_chain_bytes_equal_base_and_api_reads_identically(base_tree, tmp_path):
    base_rows, head_rows = produce(base_tree, tmp_path), produce(ROOT, tmp_path)
    assert len(base_rows) == len(head_rows) == len(STORIES)
    for i, (b, h) in enumerate(zip(base_rows, head_rows)):
        assert h == b, i  # exact JSON/Markdown text incl. Korean and newlines
    rich = head_rows[1]
    assert "report_json" in rich and "삼성전자" in rich["report_json"] + rich.get("summary_md", "")  # populated path exercised
    sr = load_safe_reports()
    for i, (b, h) in enumerate(zip(base_rows, head_rows)):
        bd, hd = tmp_path / f"b{i}" / "TRD", tmp_path / f"h{i}" / "TRD"
        write_artifacts(bd, b)
        write_artifacts(hd, h)
        assert api_view(sr, hd) == api_view(sr, bd), i


def test_api_reader_edge_artifacts_are_stable(tmp_path):
    sr = load_safe_reports()
    trade = tmp_path / "TRD"
    (trade / "reports").mkdir(parents=True)
    views = [api_view(sr, trade)]  # all missing
    (trade / "reports" / "ai_trade_report.json").write_text("", encoding="utf-8")
    (trade / "reports" / "ai_trade_summary.md").write_bytes(b"# \xec\x9a\x94\xec\x95\xbd\r\n- a\r\n")
    views.append(api_view(sr, trade))
    (trade / "reports" / "ai_trade_report.json").write_text("{not json", encoding="utf-8")
    views.append(api_view(sr, trade))
    assert views[0] != views[1]  # empty-json + CRLF summary differ from all-missing
    assert views[2]["ai-summary"] == views[1]["ai-summary"]  # summary untouched by the json change
    assert api_view(sr, trade) == views[2]  # deterministic on repeat
    assert any("\r\n" in v or "\\r\\n" in v for v in views[1].values())  # CRLF bytes surface unchanged


def test_negative_renderer_newline_mutation_is_detected(base_tree, tmp_path):
    import shutil
    mutated = tmp_path / "mut"
    shutil.copytree(base_tree / "libs", mutated / "libs")
    shutil.copytree(base_tree / "graphs", mutated / "graphs")
    changed = 0
    for target in sorted((mutated / "libs/reporting").glob("trade_report*.py")) + sorted((mutated / "libs/reporting/trade_report").rglob("*.py")):
        src = target.read_text(encoding="utf-8-sig")
        new = src.replace('"\\n".join(', '"\\r\\n".join(').replace("'\\n'.join(", "'\\r\\n'.join(")
        if new != src:
            target.write_text(new, encoding="utf-8")
            changed += 1
    assert changed
    assert produce(mutated, tmp_path) != produce(base_tree, tmp_path)
