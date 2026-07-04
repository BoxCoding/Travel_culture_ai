import json
import re
from functools import lru_cache
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import get_settings


@lru_cache
def get_llm(temperature: float = 0.7) -> ChatGoogleGenerativeAI:
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=temperature,
    )


_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


def get_text(content: Any) -> str:
    """Normalizes a LangChain message's `.content` to a plain string.

    Some models (including some Gemini variants) return `.content` as a list of content
    blocks (e.g. [{"type": "text", "text": "..."}]) instead of a raw string, which breaks
    any code that assumes a string (regex search, .strip(), etc).
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(str(item.get("text", "")))
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(content)


def extract_json(content: Any) -> Any:
    """Best-effort extraction of a JSON object/array from an LLM response."""
    text = get_text(content)
    match = _FENCE_RE.search(text)
    candidate = match.group(1) if match else text.strip()
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    # fall back to grabbing the outermost {...} or [...] span
    for open_ch, close_ch in (("{", "}"), ("[", "]")):
        start = candidate.find(open_ch)
        end = candidate.rfind(close_ch)
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(candidate[start : end + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError(f"Could not parse JSON from LLM response: {text[:200]!r}")
