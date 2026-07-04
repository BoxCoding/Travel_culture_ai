from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import extract_json, get_llm
from app.agents.state import GraphState

SYSTEM_PROMPT = (
    "You are a well-traveled local culture expert. You invent plausible, evocative "
    "lesser-known local spots for a destination that a curious traveler would not find "
    "in mainstream guidebooks. Be specific and sensory, but do not claim these are "
    "verified real-world facts, since you are generating illustrative content."
)

PROMPT_TEMPLATE = """Destination: {name}, {country} ({region})
Known for: {description}

Generate 4 plausible hidden gems (lesser-known spots) for this destination: things like a quiet
courtyard, a family-run workshop, a viewpoint locals favor, a small market corner, etc.

Respond with ONLY a JSON array, no prose, no markdown fences, in this exact shape:
[{{"name": "...", "description": "...", "category": "..."}}]

`category` should be a short label like "viewpoint", "market", "craft workshop", "eatery", "nature spot".
"""


def generate_hidden_gems(name: str, country: str, region: str, description: str) -> list[dict]:
    llm = get_llm(temperature=0.8)
    prompt = PROMPT_TEMPLATE.format(name=name, country=country, region=region, description=description)
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    data = extract_json(response.content)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array of hidden gems")
    return data


def hidden_gems_node(state: GraphState) -> GraphState:
    destination = state.get("destination")
    if not destination:
        state["result"] = {"error": "No destination provided for hidden_gems"}
        return state

    gems = generate_hidden_gems(
        name=destination["name"],
        country=destination["country"],
        region=destination["region"],
        description=destination["description"],
    )
    state["result"] = {"hidden_gems": gems}
    return state
