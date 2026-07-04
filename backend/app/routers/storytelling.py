from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore_v1.client import Client

from app.agents.nodes.storytelling import generate_story
from app.auth import get_current_user_optional
from app.firestore_client import get_firestore_client
from app.schemas import StorytellingOut, StorytellingRequest

router = APIRouter(tags=["storytelling"])


@router.post("/storytelling", response_model=StorytellingOut)
def create_story(
    body: StorytellingRequest,
    db: Client = Depends(get_firestore_client),
    _user=Depends(get_current_user_optional),
):
    dest_doc = db.collection("destinations").document(body.destination_id).get()
    if not dest_doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found")
    dest = dest_doc.to_dict()

    theme = body.theme or "general"
    subcollection = db.collection("destinations").document(body.destination_id).collection("stories")

    existing = list(subcollection.where("theme", "==", theme).limit(1).stream())
    if existing:
        doc = existing[0]
        return StorytellingOut(id=doc.id, destination_id=body.destination_id, **doc.to_dict())

    try:
        data = generate_story(dest["name"], dest["country"], dest["region"], dest["description"], theme=body.theme)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini generation failed: {exc}",
        ) from exc

    payload = {
        "title": data.get("title", f"A story from {dest['name']}"),
        "content": data.get("content", ""),
        "theme": theme,
        "ai_generated": True,
        "created_at": datetime.now(timezone.utc),
    }
    _, doc_ref = subcollection.add(payload)

    return StorytellingOut(id=doc_ref.id, destination_id=body.destination_id, **payload)
