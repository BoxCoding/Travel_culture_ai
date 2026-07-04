from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import get_llm
from app.agents.state import GraphState

SYSTEM_PROMPT = (
    "You are a cultural historian who writes engaging, respectful narratives about a place's "
    "heritage and cultural significance for curious travelers. Ground your writing in the general "
    "reputation and character of the destination, but do not present invented specifics (exact dates, "
    "named individuals, statistics) as verified fact."
)

PROMPT_TEMPLATE = """Destination: {name}, {country} ({region})
Background: {description}

Write a 3-4 paragraph narrative on the cultural significance and heritage of this destination:
its historical roots, cultural traditions, and why it matters to travelers seeking authentic
cultural understanding. Write in flowing prose, no bullet points, no markdown, no headings.
"""


def generate_heritage(name: str, country: str, region: str, description: str) -> str:
    llm = get_llm(temperature=0.6)
    prompt = PROMPT_TEMPLATE.format(name=name, country=country, region=region, description=description)
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    return response.content.strip()


def heritage_node(state: GraphState) -> GraphState:
    destination = state.get("destination")
    if not destination:
        state["result"] = {"error": "No destination provided for heritage"}
        return state

    content = generate_heritage(
        name=destination["name"],
        country=destination["country"],
        region=destination["region"],
        description=destination["description"],
    )
    state["result"] = {"heritage": content}
    return state
