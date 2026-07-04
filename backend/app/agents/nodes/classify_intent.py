from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import extract_json, get_llm
from app.agents.state import GraphState

INTENTS = ["recommend_attractions", "hidden_gems", "storytelling", "heritage", "events", "experiences", "chat"]

SYSTEM_PROMPT = (
    "You are an intent router for a travel-and-culture concierge chatbot. Classify the user's "
    "message into exactly one of these intents: "
    + ", ".join(INTENTS)
    + ". Use 'chat' for greetings, small talk, or anything that doesn't clearly match a specific "
    "travel-content intent. If the user names a destination, extract it too."
)

PROMPT_TEMPLATE = """Conversation so far (most recent last):
{history}

Latest user message: {message}

Respond with ONLY a JSON object, no prose, no markdown fences, in this exact shape:
{{"intent": "one of {intents}", "destination_name": "destination name or null"}}
"""


def classify_intent(message: str, history: list[dict[str, str]]) -> dict:
    llm = get_llm(temperature=0.0)
    history_text = "\n".join(f"{m['role']}: {m['content']}" for m in history) or "(no prior messages)"
    prompt = PROMPT_TEMPLATE.format(history=history_text, message=message, intents=", ".join(INTENTS))
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    try:
        data = extract_json(response.content)
    except ValueError:
        data = {}
    intent = data.get("intent") if isinstance(data, dict) else None
    if intent not in INTENTS:
        intent = "chat"
    destination_name = data.get("destination_name") if isinstance(data, dict) else None
    return {"intent": intent, "destination_name": destination_name}


def classify_intent_node(state: GraphState) -> GraphState:
    result = classify_intent(state.get("chat_message", ""), state.get("messages", []))
    state["intent"] = result["intent"]
    if result.get("destination_name") and not state.get("destination"):
        state["result"] = {**state.get("result", {}), "destination_name_hint": result["destination_name"]}
    return state


def route_intent(state: GraphState) -> str:
    return state.get("intent", "chat")
