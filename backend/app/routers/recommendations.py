from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agents.nodes.recommend import generate_recommendations
from app.auth import get_current_user_optional
from app.database import get_db
from app.models import Destination
from app.schemas import RecommendationOut, RecommendationRequest

router = APIRouter(tags=["recommendations"])


@router.post("/recommendations", response_model=RecommendationOut)
def recommend(
    body: RecommendationRequest,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user_optional),
):
    query = db.query(Destination)
    if body.region:
        query = query.filter(Destination.region.ilike(body.region))
    destinations = query.all()
    if not destinations:
        destinations = db.query(Destination).all()

    catalog = [
        {
            "name": d.name,
            "country": d.country,
            "region": d.region,
            "tags": d.tag_list,
            "description": d.description,
        }
        for d in destinations
    ]

    try:
        data = generate_recommendations(
            interests=body.interests,
            budget=body.budget,
            duration_days=body.duration_days,
            region=body.region,
            travel_style=body.travel_style,
            catalog=catalog,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini generation failed: {exc}",
        ) from exc

    return RecommendationOut(**data)
