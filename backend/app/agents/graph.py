from langgraph.graph import END, StateGraph

from app.agents.nodes.classify_intent import classify_intent_node, route_intent
from app.agents.nodes.events import events_node
from app.agents.nodes.experiences import experiences_node
from app.agents.nodes.heritage import heritage_node
from app.agents.nodes.hidden_gems import hidden_gems_node
from app.agents.nodes.recommend import recommend_attractions_node
from app.agents.nodes.storytelling import storytelling_node
from app.agents.nodes.synthesize import synthesize_node
from app.agents.state import GraphState
from app.firestore_client import get_firestore_client


def _destination_to_dict(doc) -> dict:
    data = doc.to_dict()
    return {
        "id": doc.id,
        "name": data.get("name", ""),
        "country": data.get("country", ""),
        "region": data.get("region", ""),
        "description": data.get("description", ""),
        "tags": data.get("tags", []),
    }


def _resolve_destination_node(state: GraphState) -> GraphState:
    """Chat messages only carry a destination name hint (from classify_intent), so look it up here."""
    if state.get("destination"):
        return state

    hint = (state.get("result") or {}).get("destination_name_hint")
    if not hint:
        return state

    db = get_firestore_client()
    hint_lower = hint.lower()
    for doc in db.collection("destinations").stream():
        if hint_lower in doc.to_dict().get("name", "").lower():
            state["destination"] = _destination_to_dict(doc)
            break
    return state


def _recommend_from_chat_node(state: GraphState) -> GraphState:
    db = get_firestore_client()
    catalog = [
        {
            "name": data.get("name", ""),
            "country": data.get("country", ""),
            "region": data.get("region", ""),
            "tags": data.get("tags", []),
            "description": data.get("description", ""),
        }
        for data in (doc.to_dict() for doc in db.collection("destinations").stream())
    ]

    state.setdefault("result", {})["catalog"] = catalog
    if not state.get("interests") and state.get("chat_message"):
        state["interests"] = [state["chat_message"]]
    return recommend_attractions_node(state)


def _chat_passthrough_node(state: GraphState) -> GraphState:
    state["result"] = {"note": "general conversation, no specific travel-content lookup performed"}
    return state


def build_chat_graph():
    graph = StateGraph(GraphState)

    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("resolve_destination", _resolve_destination_node)
    graph.add_node("recommend_attractions", _recommend_from_chat_node)
    graph.add_node("hidden_gems", hidden_gems_node)
    graph.add_node("storytelling", storytelling_node)
    graph.add_node("heritage", heritage_node)
    graph.add_node("events", events_node)
    graph.add_node("experiences", experiences_node)
    graph.add_node("chat", _chat_passthrough_node)
    graph.add_node("synthesize", synthesize_node)

    graph.set_entry_point("classify_intent")
    graph.add_edge("classify_intent", "resolve_destination")

    content_nodes = [
        "recommend_attractions",
        "hidden_gems",
        "storytelling",
        "heritage",
        "events",
        "experiences",
        "chat",
    ]
    graph.add_conditional_edges(
        "resolve_destination",
        route_intent,
        {name: name for name in content_nodes},
    )

    for name in content_nodes:
        graph.add_edge(name, "synthesize")

    graph.add_edge("synthesize", END)

    return graph.compile()


_compiled_graph = None


def get_chat_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_chat_graph()
    return _compiled_graph
