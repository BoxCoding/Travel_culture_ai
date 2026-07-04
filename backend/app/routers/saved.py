from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import CurrentUser, get_current_user_required
from app.database import get_db
from app.models import Event, Experience, HiddenGem, SavedItem
from app.schemas import SavedItemOut, SaveItemRequest

router = APIRouter(tags=["saved"])

_ITEM_TYPE_MODELS = {
    "hidden_gem": HiddenGem,
    "experience": Experience,
    "event": Event,
}


def _serialize_item(model, item_id: int, db: Session) -> dict | None:
    row = db.get(model, item_id)
    if not row:
        return None
    data = {
        "id": row.id,
        "destination_id": row.destination_id,
        "name": row.name,
        "description": row.description,
        "ai_generated": row.ai_generated,
    }
    if model is Experience:
        data["category"] = row.type
    else:
        data["category"] = row.category
    return data


@router.post("/experiences/{item_id}/save", response_model=SavedItemOut, status_code=status.HTTP_201_CREATED)
def save_item(
    item_id: int,
    body: SaveItemRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user_required),
):
    model = _ITEM_TYPE_MODELS.get(body.item_type)
    if not model:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid item_type")

    if not db.get(model, item_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    saved = SavedItem(user_id=user.sub, item_type=body.item_type, item_id=item_id)
    db.add(saved)
    db.commit()
    db.refresh(saved)

    return SavedItemOut(
        id=saved.id,
        item_type=saved.item_type,
        item_id=saved.item_id,
        created_at=saved.created_at,
        item=_serialize_item(model, item_id, db),
    )


@router.get("/me/saved", response_model=list[SavedItemOut])
def list_saved(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user_required),
):
    rows = db.query(SavedItem).filter(SavedItem.user_id == user.sub).all()
    out = []
    for row in rows:
        model = _ITEM_TYPE_MODELS.get(row.item_type)
        item = _serialize_item(model, row.item_id, db) if model else None
        out.append(
            SavedItemOut(
                id=row.id,
                item_type=row.item_type,
                item_id=row.item_id,
                created_at=row.created_at,
                item=item,
            )
        )
    return out
