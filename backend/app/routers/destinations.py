from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore_v1.client import Client

from app.agents.nodes.events import generate_events
from app.agents.nodes.experiences import generate_experiences
from app.agents.nodes.heritage import generate_heritage
from app.agents.nodes.hidden_gems import generate_hidden_gems
from app.auth import get_current_user_optional
from app.firestore_client import get_firestore_client
from app.schemas import AIContentOut, DestinationOut, HeritageOut

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


def _serialize_destination(doc) -> dict:
    data = doc.to_dict()
    return {
        "id": doc.id,
        "name": data.get("name", ""),
        "country": data.get("country", ""),
        "region": data.get("region", ""),
        "description": data.get("description", ""),
        "image_url": data.get("image_url", ""),
        "lat": data.get("lat", 0.0),
        "lng": data.get("lng", 0.0),
        "tags": data.get("tags", []),
    }


def _get_destination_or_404(db: Client, destination_id: str):
    doc = db.collection("destinations").document(destination_id).get()
    if not doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found")
    return doc


@router.get("", response_model=list[DestinationOut])
def list_destinations(
    q: str | None = None,
    region: str | None = None,
    db: Client = Depends(get_firestore_client),
    _user=Depends(get_current_user_optional),
):
    docs = list(db.collection("destinations").stream())
    results = [_serialize_destination(d) for d in docs]

    if region:
        region_lower = region.lower()
        results = [d for d in results if d["region"].lower() == region_lower]
    if q:
        q_lower = q.lower()
        results = [
            d
            for d in results
            if q_lower in d["name"].lower() or q_lower in d["country"].lower() or q_lower in d["description"].lower()
        ]
    return [DestinationOut(**d) for d in results]


@router.get("/{destination_id}", response_model=DestinationOut)
def get_destination(
    destination_id: str,
    db: Client = Depends(get_firestore_client),
    _user=Depends(get_current_user_optional),
):
    doc = _get_destination_or_404(db, destination_id)
    return DestinationOut(**_serialize_destination(doc))


@router.get("/{destination_id}/hidden-gems", response_model=list[AIContentOut])
def get_hidden_gems(
    destination_id: str,
    db: Client = Depends(get_firestore_client),
    _user=Depends(get_current_user_optional),
):
    dest = _get_destination_or_404(db, destination_id).to_dict()
    subcollection = db.collection("destinations").document(destination_id).collection("hidden_gems")

    existing = list(subcollection.stream())
    if existing:
        return [
            AIContentOut(id=doc.id, destination_id=destination_id, **doc.to_dict()) for doc in existing
        ]

    generated = _run_llm(generate_hidden_gems, dest["name"], dest["country"], dest["region"], dest["description"])
    out = []
    for item in generated:
        payload = {
            "name": item.get("name", "Unnamed spot"),
            "description": item.get("description", ""),
            "category": item.get("category", ""),
            "ai_generated": True,
        }
        _, doc_ref = subcollection.add(payload)
        out.append(AIContentOut(id=doc_ref.id, destination_id=destination_id, **payload))
    return out


@router.get("/{destination_id}/heritage", response_model=HeritageOut)
def get_heritage(
    destination_id: str,
    db: Client = Depends(get_firestore_client),
    _user=Depends(get_current_user_optional),
):
    dest = _get_destination_or_404(db, destination_id).to_dict()
    subcollection = db.collection("destinations").document(destination_id).collection("stories")

    existing = list(subcollection.where("theme", "==", HERITAGE_THEME).limit(1).stream())
    if existing:
        doc = existing[0]
        data = doc.to_dict()
        return HeritageOut(id=doc.id, destination_id=destination_id, **data)

    narrative = _run_llm(generate_heritage, dest["name"], dest["country"], dest["region"], dest["description"])

    payload = {
        "title": f"Heritage of {dest['name']}",
        "narrative": narrative,
        "theme": HERITAGE_THEME,
        "ai_generated": True,
        "created_at": datetime.now(timezone.utc),
    }
    _, doc_ref = subcollection.add(payload)
    return HeritageOut(id=doc_ref.id, destination_id=destination_id, **payload)


@router.get("/{destination_id}/events", response_model=list[AIContentOut])
def get_events(
    destination_id: str,
    db: Client = Depends(get_firestore_client),
    _user=Depends(get_current_user_optional),
):
    dest = _get_destination_or_404(db, destination_id).to_dict()
    subcollection = db.collection("destinations").document(destination_id).collection("events")

    existing = list(subcollection.stream())
    if existing:
        return [AIContentOut(id=doc.id, destination_id=destination_id, **doc.to_dict()) for doc in existing]

    generated = _run_llm(generate_events, dest["name"], dest["country"], dest["region"], dest["description"])
    out = []
    for item in generated:
        payload = {
            "name": item.get("name", "Unnamed event"),
            "description": item.get("description", ""),
            "category": item.get("category", ""),
            "ai_generated": True,
        }
        _, doc_ref = subcollection.add(payload)
        out.append(AIContentOut(id=doc_ref.id, destination_id=destination_id, **payload))
    return out


@router.get("/{destination_id}/experiences", response_model=list[AIContentOut])
def get_experiences(
    destination_id: str,
    db: Client = Depends(get_firestore_client),
    _user=Depends(get_current_user_optional),
):
    dest = _get_destination_or_404(db, destination_id).to_dict()
    subcollection = db.collection("destinations").document(destination_id).collection("experiences")

    existing = list(subcollection.stream())
    if existing:
        out = []
        for doc in existing:
            data = doc.to_dict()
            data["category"] = data.pop("type", data.get("category", ""))
            out.append(AIContentOut(id=doc.id, destination_id=destination_id, **data))
        return out

    generated = _run_llm(generate_experiences, dest["name"], dest["country"], dest["region"], dest["description"])
    out = []
    for item in generated:
        payload = {
            "name": item.get("name", "Unnamed experience"),
            "description": item.get("description", ""),
            "type": item.get("type", "workshop"),
            "contact_info": item.get("contact_info", ""),
            "ai_generated": True,
        }
        _, doc_ref = subcollection.add(payload)
        out_payload = dict(payload)
        out_payload["category"] = out_payload.pop("type")
        out_payload.pop("contact_info", None)
        out.append(AIContentOut(id=doc_ref.id, destination_id=destination_id, **out_payload))
    return out
