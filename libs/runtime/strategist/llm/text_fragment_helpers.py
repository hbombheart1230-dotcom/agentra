"""Strategist LLM text-fragment helpers moved verbatim from the facade (S5, pure).

Bodies moved from graphs/nodes/strategist_node.py. Every former facade module global (json, ast, re) is qualified at its use
site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time capture, no getattr fallback), so
monkeypatching matches the original module-level resolution. Owner never imports the facade.
"""
from __future__ import annotations


def _strip_fenced_block_r3_impl(text, *, facade):
    s = str(text or "").strip()
    if not s.startswith("```"):
        return s
    lines = s.splitlines()
    if not lines:
        return s
    lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _parse_text_list_fragment_r3_impl(raw, *, facade):
    if raw is None:
        return []
    if isinstance(raw, (list, tuple, set)):
        return [str(x or "").strip() for x in list(raw or []) if str(x or "").strip()]
    s = str(raw or "").strip()
    if not s:
        return []
    decoded = None
    for parser in (facade.json.loads, facade.ast.literal_eval):
        try:
            decoded = parser(s)
            break
        except Exception:
            decoded = None
    if isinstance(decoded, (list, tuple, set)):
        return [str(x or "").strip() for x in list(decoded or []) if str(x or "").strip()]
    if any(sep in s for sep in ("\n", ",", ";", "|")):
        return [str(x or "").strip() for x in facade.re.split(r"[\n,;|]+", s) if str(x or "").strip()]
    return [s]
