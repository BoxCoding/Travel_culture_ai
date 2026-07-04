"""Regression tests for app.agents.llm.get_text/extract_json.

Some Gemini responses (observed in production with gemini-3-flash-preview) return
`.content` as a list of content blocks instead of a plain string, which crashed every
generate_* function with `TypeError: expected string or bytes-like object, got 'list'`.
"""

import pytest

from app.agents.llm import extract_json, get_text


def test_get_text_passes_through_plain_string():
    assert get_text("hello world") == "hello world"


def test_get_text_joins_list_of_strings():
    assert get_text(["hello ", "world"]) == "hello world"


def test_get_text_extracts_text_field_from_content_blocks():
    content = [{"type": "text", "text": "hello "}, {"type": "text", "text": "world"}]
    assert get_text(content) == "hello world"


def test_get_text_handles_mixed_list():
    content = ["hello ", {"type": "text", "text": "world"}]
    assert get_text(content) == "hello world"


def test_extract_json_works_with_plain_string_response():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_works_with_list_shaped_response():
    """This is the exact shape that previously raised
    TypeError: expected string or bytes-like object, got 'list'."""
    content = [{"type": "text", "text": '{"summary": "ok", "attractions": [], "hidden_gems": []}'}]
    assert extract_json(content) == {"summary": "ok", "attractions": [], "hidden_gems": []}


def test_extract_json_handles_list_response_with_markdown_fence():
    content = [{"type": "text", "text": '```json\n[{"name": "Gem"}]\n```'}]
    assert extract_json(content) == [{"name": "Gem"}]


def test_extract_json_raises_clean_error_on_unparseable_content():
    with pytest.raises(ValueError):
        extract_json("this is not json at all")
