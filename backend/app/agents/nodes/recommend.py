from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import extract_json, get_llm
from app.agents.state import GraphState

SYSTEM_PROMPT = (
    "You are an expert travel-and-culture concierge. Given a traveler's interests and constraints, "
    "you recommend attractions and lesser-known hidden gems across our destination catalog, with "
    "clear reasoning tied to their stated preferences. Recommendations are illustrative suggestions, "
    "not verified bookings or guarantees."
)

PROMPT_TEMPLATE = """Traveler profile:
- Interests: {interests}
- Budget: {budget}
- Trip duration (days): {duration_days}
- Preferred region: {region}
- Travel style: {travel_style}

Candidate destinations (name — country — region — tags — description):
{catalog}

Recommend a ranked shortlist of attractions (across the most fitting destinations) plus a couple of
hidden-gem style suggestions, tailored to the traveler profile above. Give a short overall summary.

Respond with ONLY a JSON object, no prose, no markdown fences, in this exact shape:
{{
  "summary": "...",
  "attractions": [{{"name": "...", "reason": "..."}}],
  "hidden_gems": [{{"name": "...", "reason": "..."}}]
}}
"""


def generate_recommendations(
    interests: list[str],
    budget: str | None,
    duration_days: int | None,
    region: str | None,
    travel_style: str | None,
    catalog: list[dict],
) -> dict:
    llm = get_llm(temperature=0.7)
    catalog_lines = "\n".join(
        f"- {d['name']} — {d['country']} — {d['region']} — tags: {', '.join(d['tags'])} — {d['description']}"
        for d in catalog
    )
    prompt = PROMPT_TEMPLATE.format(
        interests=", ".join(interests) if interests else "open to anything",
        budget=budget or "unspecified",
        duration_days=duration_days if duration_days is not None else "unspecified",
        region=region or "no preference",
        travel_style=travel_style or "unspecified",
        catalog=catalog_lines,
    )
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    data = extract_json(response.content)
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object for recommendations")
    data.setdefault("attractions", [])
    data.setdefault("hidden_gems", [])
    data.setdefault("summary", "")
    return data


def recommend_attractions_node(state: GraphState) -> GraphState:
    catalog = state.get("result", {}).get("catalog", [])
    data = generate_recommendations(
        interests=state.get("interests", []),
        budget=state.get("budget"),
        duration_days=state.get("duration_days"),
        region=state.get("region"),
        travel_style=state.get("travel_style"),
        catalog=catalog,
    )
    state["result"] = data
    return state
