from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore_v1.client import Client

from app.auth import CurrentUser, get_current_user_required
from app.firestore_client import get_firestore_client
from app.schemas import SavedItemOut, SaveItemRequest

router = APIRouter(tags=["saved"])

_ITEM_TYPE_SUBCOLLECTIONS = {
    "hidden_gem": "hidden_gems",
    "experience": "experiences",
    "event": "events",
}


def _serialize_source_item(db: Client, destination_id: str, item_type: str, item_id: str) -> dict | None:
    subcollection_name = _ITEM_TYPE_SUBCOLLECTIONS.get(item_type)
    if not subcollection_name:
        return None
    doc = (
        db.collection("destinations")
        .document(destination_id)
        .collection(subcollection_name)
        .document(item_id)
        .get()
    )
    if not doc.exists:
        return None
    data = doc.to_dict()
    if item_type == "experience":
        data["category"] = data.pop("type", data.get("category", ""))
    return {
        "id": doc.id,
        "destination_id": destination_id,
        "name": data.get("name", ""),
        "description": data.get("description", ""),
        "ai_generated": data.get("ai_generated", False),
        "category": data.get("category", ""),
    }


@router.post("/experiences/{item_id}/save", response_model=SavedItemOut, status_code=status.HTTP_201_CREATED)
def save_item(
    item_id: str,
    body: SaveItemRequest,
    db: Client = Depends(get_firestore_client),
    user: CurrentUser = Depends(get_current_user_required),
):
    if body.item_type not in _ITEM_TYPE_SUBCOLLECTIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid item_type")

    source_item = _serialize_source_item(db, body.destination_id, body.item_type, item_id)
    if not source_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    payload = {
        "user_id": user.sub,
        "item_type": body.item_type,
        "item_id": item_id,
        "destination_id": body.destination_id,
        "created_at": datetime.now(timezone.utc),
    }
    _, doc_ref = db.collection("saved_items").add(payload)

    return SavedItemOut(id=doc_ref.id, item=source_item, **payload)


@router.get("/me/saved", response_model=list[SavedItemOut])
def list_saved(
    db: Client = Depends(get_firestore_client),
    user: CurrentUser = Depends(get_current_user_required),
):
    docs = db.collection("saved_items").where("user_id", "==", user.sub).stream()
    out = []
    for doc in docs:
        data = doc.to_dict()
        item = _serialize_source_item(db, data["destination_id"], data["item_type"], data["item_id"])
        out.append(SavedItemOut(id=doc.id, item=item, **data))
    return out
