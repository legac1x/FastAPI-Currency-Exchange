from datetime import datetime, timezone
from typing import List

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    hash_password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    history: Mapped[List["ConversionHistory"]] = relationship("ConversionHistory", back_populates="user")

class ConversionHistory(Base):
    __tablename__ = "conversion_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    base_currency: Mapped[str]
    target_currency: Mapped[str]
    amount: Mapped[float]
    converted_amount: Mapped[float]
    rate: Mapped[float]
    exchange_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="history")

class CurrencyRate(Base):
    __tablename__ = "currency_rates"

    id: Mapped[int] = mapped_column(primary_key=True)
    base_currency: Mapped[str]
    target_currency: Mapped[str]
    rate: Mapped[float]
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )