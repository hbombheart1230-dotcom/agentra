"""Owner38: exact pinned AST, symbol-aware news output and facade monkeypatch parity."""
import ast
import subprocess
from pathlib import Path
import pytest
import libs.reporting.trade_report_markdown_clean as api
from libs.reporting.trade_report.markdown_clean_parts import news_headlines as owner

BASE = "0409687aa76e195bd001d7756419b86b9580c531"
SOURCE = "libs/reporting/trade_report_markdown_clean.py"
NAMES = (
    "_strip_html_tags", "_clean_news_title", "_sample_news_titles",
    "_normalize_news_symbol", "_news_symbol_from_item",
    "_sample_news_titles_for_symbol", "_mismatched_symbol_news_bullet",
    "_news_linkage_strength_label",
)

def originals():
    source = subprocess.check_output(
        ["git", "show", f"{BASE}:{SOURCE}"], text=True, encoding="utf-8-sig"
    )
    symbols = {n.name: n for n in ast.parse(source).body
               if isinstance(n, ast.FunctionDef) and n.name in NAMES}
    assert len(symbols) == len(NAMES)
    scope = vars(api).copy()
    for node in symbols.values():
        exec(compile(ast.Module(body=[node], type_ignores=[]), "<original-owner38>", "exec"), scope)
    return symbols, scope

@pytest.mark.parametrize("name", NAMES)
def test_original_body_ast_and_owner_size(name):
    original, _ = originals()
    updated = next(n for n in ast.parse(Path(owner.__file__).read_text(encoding="utf-8")).body
                   if isinstance(n, ast.FunctionDef) and n.name == name + "_impl")
    assert ast.dump(ast.Module(body=original[name].body, type_ignores=[]), include_attributes=False) == ast.dump(
        ast.Module(body=updated.body, type_ignores=[]), include_attributes=False)
    assert len(Path(owner.__file__).read_text(encoding="utf-8").splitlines()) <= 350

@pytest.mark.parametrize("name,args,kwargs", [
    ("_strip_html_tags", ("&amp; <b>반도체</b>",), {}),
    ("_strip_html_tags", ("NewsItem(title='삼성전자', url='https://example.test')",), {}),
    ("_clean_news_title", ("테스트 기사...",), {}),
    ("_sample_news_titles", (["A", "A", "B", "C"],), {"limit": 2}),
    ("_sample_news_titles", ([],), {}),
    ("_normalize_news_symbol", ("삼성전자(005930)",), {}),
    ("_normalize_news_symbol", ("UNKNOWN",), {}),
    ("_news_symbol_from_item", ({"symbol": "005930"},), {}),
    ("_news_symbol_from_item", ({"ticker": "000660"},), {}),
    ("_news_symbol_from_item", ("005930: 삼성전자 기사",), {}),
    ("_news_symbol_from_item", ("NewsItem(symbol='005930')",), {}),
    ("_sample_news_titles_for_symbol", ("005930", ["005930: A", "000660: B"]), {}),
    ("_sample_news_titles_for_symbol", ("005930", ["untagged A", "untagged B"]), {}),
    ("_sample_news_titles_for_symbol", ("005930", ["000660: competitor"], ["005930: selected"]), {}),
    ("_sample_news_titles_for_symbol", ("005930", ["000660: competitor"]), {}),
    ("_sample_news_titles_for_symbol", ("", ["A", "B"]), {"limit": 1}),
    ("_mismatched_symbol_news_bullet", ("종목 뉴스 000660: B", "005930"), {}),
    ("_mismatched_symbol_news_bullet", ("종목 뉴스 005930: A", "005930"), {}),
    ("_mismatched_symbol_news_bullet", ("일반 뉴스 000660: B", "005930"), {}),
    ("_news_linkage_strength_label", ("strong",), {}),
    ("_news_linkage_strength_label", ("unknown",), {}),
])
def test_original_synthetic_results(name,args,kwargs):
    _, original = originals()
    assert getattr(api,name)(*args,**kwargs) == original[name](*args,**kwargs)

def test_call_time_facade_patch_seams(monkeypatch):
    original_strip = api._strip_html_tags
    monkeypatch.setattr(api, "_strip_html_tags", lambda value: "PATCHED")
    assert api._clean_news_title("ignore") == "PATCHED"
    monkeypatch.setattr(api, "_clean_news_title", lambda value: "NEWS_PATCH")
    assert api._sample_news_titles(["anything"]) == ["NEWS_PATCH"]
    monkeypatch.setattr(api, "_sample_news_titles", lambda rows, limit=2: ["MATCHED"])
    assert api._sample_news_titles_for_symbol("005930", ["005930: selected"]) == ["MATCHED"]
    monkeypatch.setattr(api, "_normalize_news_symbol", lambda item: "005930")
    assert api._news_symbol_from_item({"ticker": "ignored"}) == "005930"
    assert api._mismatched_symbol_news_bullet("종목 뉴스 000660: mismatch", "ignored")
    monkeypatch.setattr(api, "_metadata_value", lambda value: "METADATA_PATCH")
    assert api._news_linkage_strength_label("unknown") == "METADATA_PATCH"
    monkeypatch.setattr(api, "_strip_html_tags", original_strip)
    monkeypatch.setattr(api, "_clip", lambda *args, **kwargs: "CLIP_PATCH")
    assert api._strip_html_tags("ignored") == "CLIP_PATCH"
