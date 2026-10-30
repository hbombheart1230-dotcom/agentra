"""LLM artifacts: Prompt message/text splitting projections (moved verbatim from llm_artifacts).

Helpers are resolved on ``facade`` (the llm_artifacts module) at call time where needed; this module never imports it.
"""
from __future__ import annotations

from typing import Any, List, Tuple


def split_prompt_messages(messages: Any) -> Tuple[str, str]:
    system_parts: List[str] = []
    user_parts: List[str] = []
    if not isinstance(messages, list):
        return "", ""
    for row in messages:
        if not isinstance(row, dict):
            continue
        role = str(row.get("role") or "").strip().lower()
        content = str(row.get("content") or "")
        if not content:
            continue
        if role == "system":
            system_parts.append(content)
        elif role == "user":
            user_parts.append(content)
    return "\n\n".join(system_parts).strip(), "\n\n".join(user_parts).strip()


def split_prompt_text(prompt_text: Any) -> Tuple[str, str]:
    text = str(prompt_text or "").strip()
    if not text:
        return "", ""
    system_prompt = ""
    user_prompt = ""
    system_match = []
    user_match = []
    current_role = ""
    current_lines: List[str] = []
    for raw_line in text.splitlines():
        line = str(raw_line or "")
        stripped = line.strip().lower()
        if stripped in {"[system]", "[user]"}:
            if current_role == "system" and current_lines:
                system_match.append("\n".join(current_lines).strip())
            elif current_role == "user" and current_lines:
                user_match.append("\n".join(current_lines).strip())
            current_role = stripped.strip("[]")
            current_lines = []
            continue
        current_lines.append(line)
    if current_role == "system" and current_lines:
        system_match.append("\n".join(current_lines).strip())
    elif current_role == "user" and current_lines:
        user_match.append("\n".join(current_lines).strip())
    system_prompt = "\n\n".join(x for x in system_match if x).strip()
    user_prompt = "\n\n".join(x for x in user_match if x).strip()
    if system_prompt or user_prompt:
        return system_prompt, user_prompt
    return "", text
