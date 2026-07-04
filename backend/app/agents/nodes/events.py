from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import extract_json, get_llm
from app.agents.state import GraphState

SYSTEM_PROMPT = (
    "You are a local events curator. You generate plausible, illustrative examples of the kinds "
    "of local events, festivals, and celebrations a destination typically hosts, based on its known "
    "cultural character. You are not reporting verified real-time event listings or dates."
)

PROMPT_TEMPLATE = """Destination: {name}, {country} ({region})
Cultural character: {description}

Generate 4 plausible local events/festivals/celebrations that fit this destination's culture
(e.g. seasonal festivals, craft fairs, religious observances, food festivals, music/dance events).

Respond with ONLY a JSON array, no prose, no markdown fences, in this exact shape:
[{{"name": "...", "description": "...", "category": "..."}}]

`category` should be a short label like "festival", "religious observance", "food event", "arts event".
"""


def generate_events(name: str, country: str, region: str, description: str) -> list[dict]:
    llm = get_llm(temperature=0.8)
    prompt = PROMPT_TEMPLATE.format(name=name, country=country, region=region, description=description)
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    data = extract_json(response.content)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array of events")
    return data


def events_node(state: GraphState) -> GraphState:
    destination = state.get("destination")
    if not destination:
        state["result"] = {"error": "No destination provided for events"}
        return state

    events = generate_events(
        name=destination["name"],
        country=destination["country"],
        region=destination["region"],
        description=destination["description"],
    )
    state["result"] = {"events": events}
    return state
