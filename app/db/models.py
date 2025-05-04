from datetime import datetime, timezone

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    password: Mapped[str]
    email: Mapped[str]
    exchistory: Mapped[list["ExchangeHistory"]] = relationship("ExchangeHistory", back_populates="user")

class ExchangeHistory(Base):
    __tablename__ = "exchangehistory"

    id: Mapped[int] = mapped_column(primary_key=True)

    from_currency: Mapped[str]
    to_currency: Mapped[str]

    time_currency: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="exchistory")
