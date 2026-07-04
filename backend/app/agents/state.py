from typing import Any, TypedDict


class GraphState(TypedDict, total=False):
    intent: str
    destination: dict[str, Any] | None
    interests: list[str]
    messages: list[dict[str, str]]
    result: dict[str, Any]
    # extra free-form fields nodes read/write for their own purposes
    theme: str | None
    budget: str | None
    duration_days: int | None
    region: str | None
    travel_style: str | None
    chat_message: str
    reply: str
