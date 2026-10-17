"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/trade_report_ai.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def _sanitize_report_language_fields_r4_impl(value, *, facade):
    if isinstance(value, str):
        return facade._sanitize_forbidden_scripts_text(value)
    if isinstance(value, list):
        return [facade._sanitize_report_language_fields(item) for item in value]
    if isinstance(value, dict):
        return {key: facade._sanitize_report_language_fields(item) for key, item in value.items()}
    return value


def _first_dict_from_r4_impl(*values, facade):
    for value in values:
        data = facade._as_dict(value)
        if data:
            return data
    return {}


def _trade_report_parse_meta_r4_impl(raw, parsed, *, facade):
    result = facade.parse_llm_json_response(raw)
    candidate = parsed if isinstance(parsed, dict) else {}
    key_meta = facade.required_key_metadata(candidate, facade.AI_TRADE_REPORT_REQUIRED_KEYS)
    parse_mode = 'none'
    if bool(result.get('is_full')):
        parse_mode = 'full'
    elif bool(result.get('is_partial')):
        parse_mode = 'partial'
    return {'parse_mode': parse_mode, **key_meta, 'trailing_text': str(result.get('trailing_text') or ''), 'raw_nonempty': bool(result.get('raw_nonempty')), 'parse_error': str(result.get('error') or '')}


def _trade_report_language_meta_r4_impl(candidate, *, facade):
    sample_fields: List[str] = []

    def _collect(section: Any) -> None:
        if isinstance(section, dict):
            for key, value in section.items():
                if key in {'headline', 'summary', 'description'} and str(value or '').strip():
                    sample_fields.append(str(value or '').strip())
                elif key in {'bullets', 'watch_next', 'thesis_invalidation'} and isinstance(value, list):
                    for row in value:
                        if str(row or '').strip():
                            sample_fields.append(str(row or '').strip())
                elif key == 'full_timeline' and isinstance(value, list):
                    for row in value:
                        if isinstance(row, dict) and str(row.get('description') or '').strip():
                            sample_fields.append(str(row.get('description') or '').strip())
                elif isinstance(value, dict):
                    _collect(value)
    _collect(candidate)
    hangul_total = sum((facade._count_hangul(item) for item in sample_fields))
    latin_total = sum((facade._count_latin(item) for item in sample_fields))
    forbidden_cjk_total = sum((facade._count_forbidden_cjk_or_japanese(item) for item in sample_fields))
    english_like = [item for item in sample_fields if facade._count_hangul(item) == 0 and facade._count_latin(item) >= 8]
    requires_korean_repair = bool(sample_fields and len(english_like) >= 6 and (hangul_total == 0 or hangul_total < max(20, latin_total * 0.2)))
    if forbidden_cjk_total > 0:
        requires_korean_repair = True
    return {'language_sample_count': len(sample_fields), 'language_hangul_chars': hangul_total, 'language_latin_chars': latin_total, 'language_english_like_count': len(english_like), 'language_forbidden_cjk_chars': forbidden_cjk_total, 'requires_korean_repair': requires_korean_repair}
