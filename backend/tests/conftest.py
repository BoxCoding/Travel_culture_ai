import os
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from jose import jwt

os.environ.setdefault("AUTH_BRIDGE_SECRET", "test-secret")
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")

from app.config import get_settings  # noqa: E402
from app.firestore_client import get_firestore_client  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import seed_destinations  # noqa: E402
from tests.fake_firestore import FakeFirestoreClient  # noqa: E402

JAIPUR = {
    "name": "Jaipur",
    "country": "India",
    "region": "Asia",
    "description": "The Pink City, capital of Rajasthan.",
    "image_url": "https://images.unsplash.com/photo-1477587458883-47145ed94245",
    "lat": 26.9124,
    "lng": 75.7873,
    "tags": ["heritage", "architecture"],
}


@pytest.fixture()
def fake_db():
    """A fresh in-memory Firestore double, seeded the same way the real app seeds on startup."""
    db = FakeFirestoreClient()
    seed_destinations(db)
    return db


@pytest.fixture()
def client(fake_db, monkeypatch):
    """TestClient wired to the fake Firestore instead of a real GCP project."""
    app.dependency_overrides[get_firestore_client] = lambda: fake_db
    # app/agents/graph.py calls get_firestore_client() directly (not via FastAPI Depends),
    # so the chat-graph path needs its own patch to see the same fake instance.
    monkeypatch.setattr("app.agents.graph.get_firestore_client", lambda: fake_db)
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def bridge_token():
    """Mints a valid bridge JWT the same way the Next.js frontend would."""

    def _make(sub="user-123", email="traveler@example.com"):
        settings = get_settings()
        return jwt.encode({"sub": sub, "email": email}, settings.auth_bridge_secret, algorithm="HS256")

    return _make


@pytest.fixture()
def auth_headers(bridge_token):
    return {"Authorization": f"Bearer {bridge_token()}"}


@pytest.fixture(autouse=True)
def mock_gemini(monkeypatch):
    """Patches every Gemini-calling function at the LLM boundary, in every namespace that
    imported it (router modules import `generate_X` directly; node modules call their own
    module-local function; both need patching since `from x import y` creates a separate binding).

    Tests can still override an individual mock's `.return_value` for scenario-specific behavior.
    """
    mocks = {
        "hidden_gems": MagicMock(
            return_value=[
                {"name": "Panna Meena ka Kund", "description": "A quiet stepwell few tourists find.", "category": "viewpoint"},
                {"name": "Sanganer block-print lane", "description": "Family workshops still hand-printing cotton.", "category": "craft workshop"},
            ]
        ),
        "heritage": MagicMock(
            return_value="Jaipur's pink-washed facades reflect a 1876 royal welcome tradition, and its planned "
            "grid still houses artisan lineages practicing block-printing and gem-cutting passed down for generations."
        ),
        "events": MagicMock(
            return_value=[
                {"name": "Teej Festival", "description": "Monsoon festival with processions and swings.", "category": "festival"},
            ]
        ),
        "experiences": MagicMock(
            return_value=[
                {"name": "Blue pottery workshop", "description": "Half-day hands-on class with a local artisan.", "type": "workshop", "contact_info": "via local guild"},
            ]
        ),
        "story": MagicMock(
            return_value={"title": "Dawn Over the Pink City", "content": "I woke before sunrise as the bazaar shutters rattled open..."}
        ),
        "recommendations": MagicMock(
            return_value={
                "summary": "Jaipur suits your interest in heritage and architecture within a short trip.",
                "attractions": [{"name": "Hawa Mahal", "reason": "Iconic honeycomb facade matching your architecture interest."}],
                "hidden_gems": [{"name": "Panna Meena ka Kund", "reason": "A quiet stepwell most visitors miss."}],
            }
        ),
        "classify_intent": MagicMock(return_value={"intent": "hidden_gems", "destination_name": "Jaipur"}),
        "synthesize": MagicMock(return_value="Jaipur has some wonderful hidden gems worth seeking out!"),
    }

    monkeypatch.setattr("app.routers.destinations.generate_hidden_gems", mocks["hidden_gems"])
    monkeypatch.setattr("app.agents.nodes.hidden_gems.generate_hidden_gems", mocks["hidden_gems"])

    monkeypatch.setattr("app.routers.destinations.generate_heritage", mocks["heritage"])
    monkeypatch.setattr("app.agents.nodes.heritage.generate_heritage", mocks["heritage"])

    monkeypatch.setattr("app.routers.destinations.generate_events", mocks["events"])
    monkeypatch.setattr("app.agents.nodes.events.generate_events", mocks["events"])

    monkeypatch.setattr("app.routers.destinations.generate_experiences", mocks["experiences"])
    monkeypatch.setattr("app.agents.nodes.experiences.generate_experiences", mocks["experiences"])

    monkeypatch.setattr("app.routers.storytelling.generate_story", mocks["story"])
    monkeypatch.setattr("app.agents.nodes.storytelling.generate_story", mocks["story"])

    monkeypatch.setattr("app.routers.recommendations.generate_recommendations", mocks["recommendations"])
    monkeypatch.setattr("app.agents.nodes.recommend.generate_recommendations", mocks["recommendations"])

    monkeypatch.setattr("app.agents.nodes.classify_intent.classify_intent", mocks["classify_intent"])
    monkeypatch.setattr("app.agents.nodes.synthesize.synthesize", mocks["synthesize"])

    return mocks
