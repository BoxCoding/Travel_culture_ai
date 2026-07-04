from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud.firestore_v1.client import Client

from app.agents.nodes.recommend import generate_recommendations
from app.auth import get_current_user_optional
from app.firestore_client import get_firestore_client
from app.schemas import RecommendationOut, RecommendationRequest

router = APIRouter(tags=["recommendations"])


@router.post("/recommendations", response_model=RecommendationOut)
def recommend(
    body: RecommendationRequest,
    db: Client = Depends(get_firestore_client),
    _user=Depends(get_current_user_optional),
):
    docs = list(db.collection("destinations").stream())
    destinations = [d.to_dict() for d in docs]

    if body.region:
        region_lower = body.region.lower()
        filtered = [d for d in destinations if d.get("region", "").lower() == region_lower]
        if filtered:
            destinations = filtered

    catalog = [
        {
            "name": d.get("name", ""),
            "country": d.get("country", ""),
            "region": d.get("region", ""),
            "tags": d.get("tags", []),
            "description": d.get("description", ""),
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
