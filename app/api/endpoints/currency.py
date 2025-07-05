from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.api.schemas.currency import DefinitelyCurrencyIn, DefinitelyCurrencyOut, CurrencyListOut, AmountExchange, AmountExchangeOut, CurrencyHistory
from app.db.database import get_async_session
from app.api.schemas.users import UserOut
from app.services.currency import (definitely_currency, list_currencies, amount_exchange, history_of_user, export_history)

currency_router = APIRouter(prefix="/currency", tags=["currency"], dependencies=[Depends(get_current_user)])

@currency_router.post('/definitely')
async def get_definitely_currency(current_currency: DefinitelyCurrencyIn) -> DefinitelyCurrencyOut:
    return await definitely_currency(current_currency)

@currency_router.get('/list')
async def get_list_currencies(currency_from: str) -> CurrencyListOut:
    return await list_currencies(currency_from)

@currency_router.post('/amount')
async def get_amount_exchange(
    exchange: AmountExchange,
    current_user: Annotated[UserOut, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_session)]
) -> AmountExchangeOut:
    return await amount_exchange(exchange, current_user, db)

@currency_router.get("/history")
async def get_history_exchange(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[UserOut, Depends(get_current_user)]
) -> List[CurrencyHistory]:
    return await history_of_user(db, current_user)

@currency_router.get('/history/export')
async def get_history_export(
    db: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
    format: str
):
    return await export_history(format, db, current_user)