import tempfile
import unittest
from pathlib import Path

from scripts.diagnostics import check_trade_report_runtime_regression as runtime
from scripts.diagnostics import query_strategist_llm_events as query
from scripts.research import phase5_validation_markdown as markdown
from scripts.research import run_phase5_validation_bundle as bundle


class OwnerSmokeTests(unittest.TestCase):
    def test_phase5_markdown_wrapper_and_owner(self):
        payload = {'day': '2026-10-30', 'summary': {}, 'artifacts': {}}
        self.assertEqual(bundle._render_bundle_markdown(payload, repo_root=Path('.')), markdown._render_bundle_markdown(payload, repo_root=Path('.'), facade=bundle))
        with self.assertRaises(ValueError):
            bundle._render_bundle_markdown({'day': '2026-10-30', 'summary': {'symbol_report_count': 'bad'}, 'artifacts': {}}, repo_root=Path('.'))

    def test_runtime_validation_and_parser(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = {k: root / k for k in ('entry_json','hold_json','exit_json','lifecycle_bundle_json','ai_trade_report_input_json','ai_trade_report_json','ai_trade_report_md')}
            original = runtime._resolve_trade_context
            runtime._resolve_trade_context = lambda *_: {'trade_paths': paths, 'entry_payload': {}, 'exit_payload': {}, 'hold_payload': {}, 'lifecycle_bundle': {}, 'story_input': {}, 'report': {}, 'provenance': {}, 'health': {}}
            try:
                self.assertEqual(runtime.validate_trade_artifact_chain(root, 'd', 't')['failures'][:2], ['missing_artifact:entry_json', 'missing_artifact:hold_json'])
            finally:
                runtime._resolve_trade_context = original
        self.assertFalse(runtime._build_parser().parse_args([]).skip_repair)

    def test_strategist_owner_wrappers(self):
        self.assertEqual(query._to_float('2.5'), 2.5)
        self.assertEqual(query._to_float(None, 3), 3.0)
        self.assertEqual(query._infer_call_kind({'call_kind': 'custom'}), 'custom')
        self.assertEqual(query._infer_call_kind({'intent_action': 'BUY'}), 'legacy_trade_intent')
        rec = {'stage': 'strategist_llm', 'event': 'result', 'run_id': 'r', 'ts': '2026-01-01', 'payload': {'ok': False, 'context_symbol_sentiment_score': 1}}
        self.assertEqual(query._filtered_events([rec], run_id='r', only_nonzero_news=True), [rec])
