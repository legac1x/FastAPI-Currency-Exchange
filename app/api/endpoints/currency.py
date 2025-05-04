from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.currency import CurrencyConvert, CurrencyExchangeResponse, CurrencyExchangeHistory
from app.db.models import User
from app.db.database import get_async_session
from app.core.security import get_current_user
from app.utils.external_api import get_exchange_rate, get_supported_currencies
from app.services.currency import save_exchange, get_history_currency

currency_router = APIRouter(prefix="/currency", tags=["Currency"],
                            dependencies=[Depends(get_current_user)])


@currency_router.post("/exchange", response_model=CurrencyExchangeResponse)
async def get_current_currency(curr_body: CurrencyConvert, user: Annotated[User, Depends(get_current_user)],
                               session: Annotated[AsyncSession, Depends(get_async_session)]):
    currencies = ",".join(curr_body.to_currency)
    response_data_currency = await get_exchange_rate(currencies)
    response = {"user": user.username, "email": user.email, "currency_data": response_data_currency}
    await save_exchange(user=user, from_currency=response_data_currency['currency_from'],
                        to_currency=currencies, session=session)
    return CurrencyExchangeResponse(**response)

@currency_router.get('/list')
async def get_list_currency():
    return await get_supported_currencies()

@currency_router.get("/history")
async def get_exchange_history(user: Annotated[User, Depends(get_current_user)],
                               session: Annotated[AsyncSession, Depends(get_async_session)]):
    user_history = await get_history_currency(user, session)
    return CurrencyExchangeHistory(username=user.username,
                                   user_history=user_history)