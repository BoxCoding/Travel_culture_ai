from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.routers import chat, destinations, health, recommendations, saved, storytelling
from app.seed import seed_destinations


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_destinations(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Travel & Culture AI API", lifespan=lifespan)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(destinations.router, prefix="/api")
app.include_router(storytelling.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(saved.router, prefix="/api")
