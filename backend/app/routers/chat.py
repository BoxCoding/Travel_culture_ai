import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.graph import get_chat_graph
from app.auth import CurrentUser, get_current_user_required
from app.schemas import ChatOut, ChatRequest

router = APIRouter(tags=["chat"])

# In-memory multi-turn history per thread. Fine for a single-process dev/demo backend;
# would need a shared store (Redis, DB) behind a load balancer or across restarts.
_THREAD_HISTORY: dict[str, list[dict[str, str]]] = {}


@router.post("/chat", response_model=ChatOut)
def chat(
    body: ChatRequest,
    user: CurrentUser = Depends(get_current_user_required),
):
    thread_id = body.thread_id or str(uuid.uuid4())
    history = _THREAD_HISTORY.setdefault(thread_id, [])

    graph = get_chat_graph()
    try:
        final_state = graph.invoke(
            {
                "chat_message": body.message,
                "messages": history,
                "destination": None,
                "interests": [],
                "result": {},
            }
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini generation failed: {exc}",
        ) from exc

    reply = final_state.get("reply", "Sorry, I couldn't come up with a reply just now.")

    history.append({"role": "user", "content": body.message})
    history.append({"role": "assistant", "content": reply})

    return ChatOut(reply=reply, thread_id=thread_id)
