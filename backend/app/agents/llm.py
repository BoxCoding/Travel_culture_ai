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


def extract_json(text: str) -> Any:
    """Best-effort extraction of a JSON object/array from an LLM text response."""
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
