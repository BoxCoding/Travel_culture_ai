from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DestinationOut(BaseModel):
    id: str
    name: str
    country: str
    region: str
    description: str
    image_url: str
    lat: float
    lng: float
    tags: list[str]

    model_config = ConfigDict(from_attributes=True)


class AIContentOut(BaseModel):
    """Shared shape for HiddenGem / Event / Experience."""

    id: str
    destination_id: str
    name: str
    description: str
    category: str
    ai_generated: bool

    model_config = ConfigDict(from_attributes=True)


class HeritageOut(BaseModel):
    id: str
    destination_id: str
    title: str
    narrative: str
    theme: str
    ai_generated: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StorytellingRequest(BaseModel):
    destination_id: str
    theme: str | None = None


class StorytellingOut(BaseModel):
    id: str
    destination_id: str
    title: str
    content: str
    theme: str
    ai_generated: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecommendationRequest(BaseModel):
    interests: list[str] = Field(default_factory=list)
    budget: str | None = None
    duration_days: int | None = None
    region: str | None = None
    travel_style: str | None = None


class RankedAttraction(BaseModel):
    name: str
    reason: str


class RankedGem(BaseModel):
    name: str
    reason: str


class RecommendationOut(BaseModel):
    summary: str
    attractions: list[RankedAttraction]
    hidden_gems: list[RankedGem]


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


class ChatOut(BaseModel):
    reply: str
    thread_id: str


class SaveItemRequest(BaseModel):
    item_type: str  # "hidden_gem" | "experience" | "event"
    destination_id: str


class SavedItemOut(BaseModel):
    id: str
    item_type: str
    item_id: str
    destination_id: str
    created_at: datetime
    item: dict | None = None

    model_config = ConfigDict(from_attributes=True)
