"""Terminal traceback facts must be observed, not inferred from a short message."""
from scripts.refactor.p169_broad_failure_evidence import build, extract, normalize, signature


def test_terminal_exception_and_test_location_are_separate(tmp_path):
    source = tmp_path / "junit.xml"
    source.write_text('''<testsuites><testsuite><testcase classname="tests.test_x" name="test_x">
<failure message="TypeError: wrong input">tests/test_x.py:12:
C:\\Python\\Lib\\json\\__init__.py:345: TypeError
</failure></testcase></testsuite></testsuites>''', encoding="utf-8")
    row = extract(source)["tests/test_x.py::test_x"]
    assert row["type"] == "TypeError"
    assert row["loc"] == "<PYTHON>/Lib/json/__init__.py:345"
    assert row["test_location"] == "tests/test_x.py:12"
    assert row["evidence_status"] == "OBSERVED"


def test_missing_traceback_is_blocked_even_with_exception_looking_message(tmp_path):
    source = tmp_path / "junit.xml"
    source.write_text('<testsuites><testcase classname="tests.test_x" name="test_x">'
                      '<failure message="TypeError: unverified"/></testcase></testsuites>', encoding="utf-8")
    row = extract(source)["tests/test_x.py::test_x"]
    assert row["type"] is None and row["loc"] is None
    assert row["evidence_status"] == "BLOCKED"


def test_normalization_preserves_dataset_names_line_numbers_and_error_values():
    assert normalize(r"C:\AgentraEvidence\b_base\reports\2026-05-15\x.json") == "<TREE>/reports/2026-05-15/x.json"
    assert normalize("tests/test_x.py:345: assert 12345 == 67890") == "tests/test_x.py:345: assert 12345 == 67890"
    left = dict(kind="failure", type="AssertionError", loc="tests/x.py:10", msg="assert 1 == 2", test_location=None)
    right = dict(left, msg="assert 1 == 3")
    assert signature(left) != signature(right)


def test_missing_log_corroboration_cannot_be_classified_as_equal(tmp_path):
    xml = tmp_path / "run.xml"
    xml.write_text('<testsuites><testcase classname="tests.test_x" name="test_x">'
                   '<failure message="assert False">tests/test_x.py:12: AssertionError'
                   '</failure></testcase></testsuites>', encoding="utf-8")
    log = tmp_path / "run.log"
    log.write_text("", encoding="utf-8")
    result = build(xml, xml, log, log)
    assert result["diff"]["SAME_FAILURE_SIGNATURE"] == []
    assert result["diff"]["BLOCKED"] == ["tests/test_x.py::test_x"]
    log.write_text("tests/test_x.py:12: AssertionError\n", encoding="utf-8")
    assert build(xml, xml, log, log)["diff"]["SAME_FAILURE_SIGNATURE"] == ["tests/test_x.py::test_x"]
