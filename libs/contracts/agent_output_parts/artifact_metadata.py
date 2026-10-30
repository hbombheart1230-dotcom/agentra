from typing import Any, Dict


def phase(state: Dict[str, Any], *, facade) -> str:
    return str(state.get("runtime_phase") or state.get("phase") or "").strip()


def parse_day_from_timestamp(value: str, *, facade) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if len(text) == 10 and text[4:5] == "-" and text[7:8] == "-":
        return text
    normalized = text.replace("Z", "+00:00") if text.endswith("Z") else text
    try:
        return facade.kst_day_str(facade.datetime.fromisoformat(normalized))
    except Exception:
        if len(text) >= 10 and text[4:5] == "-" and text[7:8] == "-":
            return text[:10]
    return ""
