from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import extract_json, get_llm
from app.agents.state import GraphState

SYSTEM_PROMPT = (
    "You are a cultural immersion travel designer. You generate plausible, authentic-feeling local "
    "experience ideas (workshops, homestays, artisan visits, culinary experiences, festivals) for a "
    "destination. These are illustrative concepts, not verified bookable listings, and contact_info "
    "should stay generic (e.g. 'ask at the local tourism office') rather than invented phone numbers."
)

PROMPT_TEMPLATE = """Destination: {name}, {country} ({region})
Cultural character: {description}

Generate 4 authentic local cultural experience ideas spanning different types: workshop, homestay,
artisan, festival, culinary. Each should feel grounded in the destination's actual culture.

Respond with ONLY a JSON array, no prose, no markdown fences, in this exact shape:
[{{"name": "...", "description": "...", "type": "workshop|homestay|artisan|festival|culinary", "contact_info": "..."}}]
"""


def generate_experiences(name: str, country: str, region: str, description: str) -> list[dict]:
    llm = get_llm(temperature=0.8)
    prompt = PROMPT_TEMPLATE.format(name=name, country=country, region=region, description=description)
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    data = extract_json(response.content)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array of experiences")
    return data


def experiences_node(state: GraphState) -> GraphState:
    destination = state.get("destination")
    if not destination:
        state["result"] = {"error": "No destination provided for experiences"}
        return state

    experiences = generate_experiences(
        name=destination["name"],
        country=destination["country"],
        region=destination["region"],
        description=destination["description"],
    )
    state["result"] = {"experiences": experiences}
    return state
