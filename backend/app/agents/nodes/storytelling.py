from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import get_llm
from app.agents.state import GraphState

SYSTEM_PROMPT = (
    "You are a gifted travel storyteller who writes immersive, first-person or narrative-style "
    "heritage storytelling pieces that bring a destination's culture to life for a reader. Use vivid "
    "sensory detail. This is creative, illustrative storytelling, not a factual record."
)

PROMPT_TEMPLATE = """Destination: {name}, {country} ({region})
Background: {description}
{theme_line}

Write an immersive first-person narrative piece (4-6 paragraphs) that tells a heritage/cultural
story about this destination, evoking its atmosphere, traditions, and sense of place. Write in
flowing prose, no bullet points, no markdown, no headings. Also produce a short evocative title.

Respond with ONLY a JSON object, no prose, no markdown fences, in this exact shape:
{{"title": "...", "content": "..."}}
"""


def generate_story(name: str, country: str, region: str, description: str, theme: str | None = None) -> dict:
    from app.agents.llm import extract_json

    llm = get_llm(temperature=0.9)
    theme_line = f"Theme to weave in: {theme}" if theme else ""
    prompt = PROMPT_TEMPLATE.format(
        name=name, country=country, region=region, description=description, theme_line=theme_line
    )
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    data = extract_json(response.content)
    if not isinstance(data, dict) or "title" not in data or "content" not in data:
        raise ValueError("Expected a JSON object with title and content")
    return data


def storytelling_node(state: GraphState) -> GraphState:
    destination = state.get("destination")
    if not destination:
        state["result"] = {"error": "No destination provided for storytelling"}
        return state

    story = generate_story(
        name=destination["name"],
        country=destination["country"],
        region=destination["region"],
        description=destination["description"],
        theme=state.get("theme"),
    )
    state["result"] = {"story": story}
    return state
