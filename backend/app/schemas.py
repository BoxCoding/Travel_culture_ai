from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DestinationOut(BaseModel):
    id: int
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

    id: int
    destination_id: int
    name: str
    description: str
    category: str
    ai_generated: bool

    model_config = ConfigDict(from_attributes=True)


class ExperienceOut(BaseModel):
    """Same shape as AIContentOut; `category` is populated from the model's `type` column."""

    id: int
    destination_id: int
    name: str
    description: str
    category: str
    ai_generated: bool

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, experience) -> "ExperienceOut":
        return cls(
            id=experience.id,
            destination_id=experience.destination_id,
            name=experience.name,
            description=experience.description,
            category=experience.type,
            ai_generated=experience.ai_generated,
        )


class HeritageOut(BaseModel):
    id: int
    destination_id: int
    title: str
    content: str
    theme: str
    ai_generated: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StorytellingRequest(BaseModel):
    destination_id: int
    theme: str | None = None


class StorytellingOut(BaseModel):
    id: int
    destination_id: int
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


class SavedItemOut(BaseModel):
    id: int
    item_type: str
    item_id: int
    created_at: datetime
    item: dict | None = None

    model_config = ConfigDict(from_attributes=True)
