from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Destination(Base):
    __tablename__ = "destinations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    country: Mapped[str] = mapped_column(String(120), nullable=False)
    region: Mapped[str] = mapped_column(String(60), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    lat: Mapped[float] = mapped_column(nullable=False)
    lng: Mapped[float] = mapped_column(nullable=False)
    tags: Mapped[str] = mapped_column(String(500), nullable=False, default="")  # comma-separated

    hidden_gems: Mapped[list["HiddenGem"]] = relationship(back_populates="destination", cascade="all, delete-orphan")
    stories: Mapped[list["Story"]] = relationship(back_populates="destination", cascade="all, delete-orphan")
    events: Mapped[list["Event"]] = relationship(back_populates="destination", cascade="all, delete-orphan")
    experiences: Mapped[list["Experience"]] = relationship(back_populates="destination", cascade="all, delete-orphan")

    @property
    def tag_list(self) -> list[str]:
        return [t.strip() for t in self.tags.split(",") if t.strip()]


class HiddenGem(Base):
    __tablename__ = "hidden_gems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    ai_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    destination: Mapped["Destination"] = relationship(back_populates="hidden_gems")


class Story(Base):
    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    theme: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    destination: Mapped["Destination"] = relationship(back_populates="stories")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    ai_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    destination: Mapped["Destination"] = relationship(back_populates="events")


class Experience(Base):
    __tablename__ = "experiences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination_id: Mapped[int] = mapped_column(ForeignKey("destinations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(40), nullable=False)  # workshop/homestay/artisan/festival/culinary
    contact_info: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    ai_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    destination: Mapped["Destination"] = relationship(back_populates="experiences")


class SavedItem(Base):
    __tablename__ = "saved_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(120), nullable=False)
    item_type: Mapped[str] = mapped_column(String(40), nullable=False)  # hidden_gem/experience/event
    item_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
