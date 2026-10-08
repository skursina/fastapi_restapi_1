from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Advertisement(Base):
    __tablename__ = "advertisements"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    price: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    author: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id", 
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )


class User(Base):
    __tablename__= 'users'

    id: Mapped[int] = mapped_column(
        Integer(),
        primary_key=True,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(length=100), 
        nullable=False,
        unique=True,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    group: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='user',
    )