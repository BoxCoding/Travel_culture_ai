from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agents.nodes.storytelling import generate_story
from app.auth import get_current_user_optional
from app.database import get_db
from app.models import Destination, Story
from app.schemas import StorytellingOut, StorytellingRequest

router = APIRouter(tags=["storytelling"])


@router.post("/storytelling", response_model=StorytellingOut)
def create_story(
    body: StorytellingRequest,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user_optional),
):
    dest = db.get(Destination, body.destination_id)
    if not dest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found")

    theme = body.theme or "general"

    existing = (
        db.query(Story)
        .filter(Story.destination_id == body.destination_id, Story.theme == theme)
        .first()
    )
    if existing:
        return StorytellingOut(
            id=existing.id,
            destination_id=existing.destination_id,
            title=existing.title,
            content=existing.content,
            theme=existing.theme,
            created_at=existing.created_at,
        )

    try:
        data = generate_story(dest.name, dest.country, dest.region, dest.description, theme=body.theme)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini generation failed: {exc}",
        ) from exc

    story = Story(
        destination_id=body.destination_id,
        title=data.get("title", f"A story from {dest.name}"),
        content=data.get("content", ""),
        theme=theme,
    )
    db.add(story)
    db.commit()
    db.refresh(story)

    return StorytellingOut(
        id=story.id,
        destination_id=story.destination_id,
        title=story.title,
        content=story.content,
        theme=story.theme,
        created_at=story.created_at,
    )
