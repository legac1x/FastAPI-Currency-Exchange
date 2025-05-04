from typing import Annotated

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, ExchangeHistory
from app.api.schemas.currency import CurrencyExchangeHistoryItem

async def save_exchange(user: User, from_currency: str, to_currency: str,
                        session: AsyncSession):
    exchange = ExchangeHistory(
        from_currency=from_currency,
        to_currency=to_currency,
        user_id=user.id
    )
    session.add(exchange)
    await session.commit()

async def get_history_currency(user: User, session: AsyncSession):
    res = await session.execute(
        select(ExchangeHistory.from_currency, ExchangeHistory.to_currency, ExchangeHistory.time_currency).
        where(ExchangeHistory.user_id == user.id))
    user_history = res.mappings().all()
    return [CurrencyExchangeHistoryItem(**item) for item in user_history]
