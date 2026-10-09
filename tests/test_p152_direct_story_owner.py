from pathlib import Path
import ast
import inspect

from libs.reporting.trade_story_assembly_parts.direct_story import build_direct_story_input
from libs.reporting.trade_story_assembly_parts.reasoning_provenance import build_story_reasoning_provenance


def test_direct_story_is_a_single_bounded_owner_without_public_facade_dependency():
    source_path = Path(inspect.getsourcefile(build_direct_story_input))
    source = source_path.read_text(encoding="utf-8")
    assert len(source.splitlines()) <= 350
    tree = ast.parse(source)
    assert any(isinstance(node, ast.FunctionDef) and node.name == "build_direct_story_input"
               for node in tree.body)
    assert not any(
        isinstance(node, ast.ImportFrom) and (
            "trade_story_pipeline" in (node.module or "") or
            "trade_report_ai" in (node.module or "")
        )
        for node in ast.walk(tree)
    )


def test_direct_story_uses_canonical_reasoning_owner():
    assert build_story_reasoning_provenance.__module__.endswith(
        "trade_story_assembly_parts.reasoning_provenance"
    )
