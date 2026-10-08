"""Chunked reader for the top-level array of the large indent=2 JSON dumps this repo writes.

`q9_decision_windows.json` reaches ~130 MB; `json.loads` of one transiently needs ~860 MiB of
Python objects (plus the file text), which alone overflows the 1 GiB closeout container.
Consumers that need only a few fields per window stream it with `iter_json_array`, and the one
consumer that rewrites the document uses `read_json_array_and_rest`.

Both rely on the layout `json.dump(..., indent=2)` produces -- the array opens on its own
top-level line as `  "<key>": [` -- and fall back to a plain `json.loads` for anything else.
A truncated/corrupt file raises `ValueError` part-way; callers discard what they collected,
which matches the `{}` / "no windows" result the whole-file `json.loads` readers gave.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator, Mapping

_STREAM_CHUNK_CHARS = 4 * 1024 * 1024
_WHITESPACE = " \n\r\t,"


def _stream(path: Path, key: str, strict: bool = False) -> Iterator[Any]:
    """Yield each array item, then finally a `(head, tail)` tuple for the rest of the document.

    `head` is the text before the array line, `tail` the text after the closing `]`, so that
    `json.loads(head + '\\n  "<key>": []' + tail)` is the document with an empty array.
    Items are never tuples (JSON has none), so the final tuple is unambiguous.
    """
    marker = f'\n  "{key}": ['
    try:
        handle = path.open("r", encoding="utf-8")
    except OSError:
        if strict:
            raise
        return
    with handle:
        buffer = handle.read(_STREAM_CHUNK_CHARS)
        start = buffer.find(marker)
        if start < 0:
            try:
                payload = json.loads(buffer + handle.read())
            except ValueError:
                if strict:
                    raise
                return
            if isinstance(payload, Mapping):
                for item in payload.get(key) or []:
                    yield item
                rest = dict(payload)
                rest[key] = []
                yield ("__rest__", rest)
            return
        head = buffer[:start]
        decoder = json.JSONDecoder()
        position = start + len(marker)
        exhausted = False
        while True:
            while True:
                while position < len(buffer) and buffer[position] in _WHITESPACE:
                    position += 1
                if position < len(buffer) or exhausted:
                    break
                chunk = handle.read(_STREAM_CHUNK_CHARS)
                if not chunk:
                    exhausted = True
                else:
                    buffer = buffer[position:] + chunk
                    position = 0
            if position >= len(buffer) or buffer[position] == "]":
                break
            while True:
                try:
                    item, end = decoder.raw_decode(buffer, position)
                    break
                except ValueError:
                    chunk = "" if exhausted else handle.read(_STREAM_CHUNK_CHARS)
                    if not chunk:
                        raise
                    buffer = buffer[position:] + chunk
                    position = 0
            yield item
            position = end
            if position > _STREAM_CHUNK_CHARS:
                buffer = buffer[position:]
                position = 0
        if position >= len(buffer):
            raise ValueError(f"{path}: array {key!r} is not closed")
        tail = buffer[position + 1:] + handle.read()
        yield ("__rest__", (head, f'\n  "{key}": []', tail))


def iter_json_array(path: Path, key: str, *, strict: bool = False) -> Iterator[Any]:
    """Yield the items of the top-level array `key` of a JSON object file, one at a time.

    By default a missing/unparseable file yields nothing. With `strict=True` it raises
    `OSError`/`ValueError` instead, for callers that must tell "unreadable" from "no items".
    """
    for item in _stream(path, key, strict):
        if isinstance(item, tuple):
            return
        yield item


def read_json_array_and_rest(path: Path, key: str) -> tuple[list[Any], dict[str, Any]]:
    """`(items, rest)` where `rest` is the whole document with `key` set to `[]` (key order kept).

    Equivalent to `payload = json.loads(text); items = payload[key]; payload[key] = []`, without
    holding the file text or a second copy. Unreadable/corrupt files give `([], {})`.
    """
    items: list[Any] = []
    rest: dict[str, Any] = {}
    try:
        for item in _stream(path, key):
            if isinstance(item, tuple):
                _, value = item
                if isinstance(value, tuple):
                    head, marker, tail = value
                    parsed = json.loads(head + marker + tail)
                    rest = parsed if isinstance(parsed, dict) else {}
                else:
                    rest = value
                break
            items.append(item)
    except ValueError:
        return [], {}
    return items, rest
