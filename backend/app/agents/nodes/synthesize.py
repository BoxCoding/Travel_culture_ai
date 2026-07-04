import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import get_llm, get_text
from app.agents.state import GraphState

SYSTEM_PROMPT = (
    "You are a warm, knowledgeable travel-and-culture concierge chatting with a traveler. Turn the "
    "structured agent output below into a single natural-language reply, conversational in tone, "
    "concise but helpful. If the content is AI-generated/illustrative rather than verified fact, "
    "briefly note that lightly (e.g. 'worth double-checking before you go')."
)

PROMPT_TEMPLATE = """User's message: {message}
Detected intent: {intent}

Structured agent result:
{result}

Write the natural-language chat reply now. No markdown headers, just a friendly conversational reply.
"""


def synthesize(message: str, intent: str, result: dict) -> str:
    llm = get_llm(temperature=0.6)
    prompt = PROMPT_TEMPLATE.format(message=message, intent=intent, result=json.dumps(result, ensure_ascii=False))
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    return get_text(response.content).strip()


def synthesize_node(state: GraphState) -> GraphState:
    reply = synthesize(state.get("chat_message", ""), state.get("intent", "chat"), state.get("result", {}))
    state["reply"] = reply
    return state
