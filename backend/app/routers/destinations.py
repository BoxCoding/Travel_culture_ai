from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agents.nodes.events import generate_events
from app.agents.nodes.experiences import generate_experiences
from app.agents.nodes.heritage import generate_heritage
from app.agents.nodes.hidden_gems import generate_hidden_gems
from app.auth import get_current_user_optional
from app.database import get_db
from app.models import Destination, Event, Experience, HiddenGem, Story
from app.schemas import AIContentOut, DestinationOut, ExperienceOut, HeritageOut

router = APIRouter(prefix="/destinations", tags=["destinations"])

HERITAGE_THEME = "__heritage__"


def _run_llm(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as exc:  # noqa: BLE001 - surface as a clean upstream error
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini generation failed: {exc}",
        ) from exc


def _get_destination_or_404(db: Session, destination_id: int) -> Destination:
    dest = db.get(Destination, destination_id)
    if not dest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found")
    return dest


@router.get("", response_model=list[DestinationOut])
def list_destinations(
    q: str | None = None,
    region: str | None = None,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user_optional),
):
    query = db.query(Destination)
    if region:
        query = query.filter(Destination.region.ilike(region))
    if q:
        like = f"%{q}%"
        query = query.filter(Destination.name.ilike(like) | Destination.country.ilike(like) | Destination.description.ilike(like))
    destinations = query.all()
    return [DestinationOut(**_serialize_destination(d)) for d in destinations]


def _serialize_destination(d: Destination) -> dict:
    return {
        "id": d.id,
        "name": d.name,
        "country": d.country,
        "region": d.region,
        "description": d.description,
        "image_url": d.image_url,
        "lat": d.lat,
        "lng": d.lng,
        "tags": d.tag_list,
    }


@router.get("/{destination_id}", response_model=DestinationOut)
def get_destination(destination_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user_optional)):
    dest = _get_destination_or_404(db, destination_id)
    return DestinationOut(**_serialize_destination(dest))


@router.get("/{destination_id}/hidden-gems", response_model=list[AIContentOut])
def get_hidden_gems(destination_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user_optional)):
    dest = _get_destination_or_404(db, destination_id)

    existing = db.query(HiddenGem).filter(HiddenGem.destination_id == destination_id).all()
    if existing:
        return [AIContentOut.model_validate(g) for g in existing]

    generated = _run_llm(generate_hidden_gems, dest.name, dest.country, dest.region, dest.description)
    rows = []
    for item in generated:
        gem = HiddenGem(
            destination_id=destination_id,
            name=item.get("name", "Unnamed spot"),
            description=item.get("description", ""),
            category=item.get("category", ""),
            ai_generated=True,
        )
        db.add(gem)
        rows.append(gem)
    db.commit()
    for gem in rows:
        db.refresh(gem)
    return [AIContentOut.model_validate(g) for g in rows]


@router.get("/{destination_id}/heritage", response_model=HeritageOut)
def get_heritage(destination_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user_optional)):
    dest = _get_destination_or_404(db, destination_id)

    existing = (
        db.query(Story)
        .filter(Story.destination_id == destination_id, Story.theme == HERITAGE_THEME)
        .first()
    )
    if existing:
        return HeritageOut(
            id=existing.id,
            destination_id=existing.destination_id,
            title=existing.title,
            content=existing.content,
            theme=existing.theme,
            created_at=existing.created_at,
        )

    content = _run_llm(generate_heritage, dest.name, dest.country, dest.region, dest.description)
    story = Story(
        destination_id=destination_id,
        title=f"Heritage of {dest.name}",
        content=content,
        theme=HERITAGE_THEME,
    )
    db.add(story)
    db.commit()
    db.refresh(story)
    return HeritageOut(
        id=story.id,
        destination_id=story.destination_id,
        title=story.title,
        content=story.content,
        theme=story.theme,
        created_at=story.created_at,
    )


@router.get("/{destination_id}/events", response_model=list[AIContentOut])
def get_events(destination_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user_optional)):
    dest = _get_destination_or_404(db, destination_id)

    existing = db.query(Event).filter(Event.destination_id == destination_id).all()
    if existing:
        return [AIContentOut.model_validate(e) for e in existing]

    generated = _run_llm(generate_events, dest.name, dest.country, dest.region, dest.description)
    rows = []
    for item in generated:
        event = Event(
            destination_id=destination_id,
            name=item.get("name", "Unnamed event"),
            description=item.get("description", ""),
            category=item.get("category", ""),
            ai_generated=True,
        )
        db.add(event)
        rows.append(event)
    db.commit()
    for event in rows:
        db.refresh(event)
    return [AIContentOut.model_validate(e) for e in rows]


@router.get("/{destination_id}/experiences", response_model=list[ExperienceOut])
def get_experiences(destination_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user_optional)):
    dest = _get_destination_or_404(db, destination_id)

    existing = db.query(Experience).filter(Experience.destination_id == destination_id).all()
    if existing:
        return [ExperienceOut.from_model(e) for e in existing]

    generated = _run_llm(generate_experiences, dest.name, dest.country, dest.region, dest.description)
    rows = []
    for item in generated:
        exp = Experience(
            destination_id=destination_id,
            name=item.get("name", "Unnamed experience"),
            description=item.get("description", ""),
            type=item.get("type", "workshop"),
            contact_info=item.get("contact_info", ""),
            ai_generated=True,
        )
        db.add(exp)
        rows.append(exp)
    db.commit()
    for exp in rows:
        db.refresh(exp)
    return [ExperienceOut.from_model(e) for e in rows]
