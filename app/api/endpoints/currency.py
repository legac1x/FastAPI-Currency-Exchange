from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.schemas.currency import Currency
from app.api.schemas.user import UserOut
from app.core.security import get_current_user
from app.utils.external_api import get_exchange_rate, get_supported_currencies

currency_router = APIRouter(prefix="/currency", tags=["Currency"],
                            dependencies=[Depends(get_current_user)])


@currency_router.post("/exchange")
async def get_current_currency(curr_body: Currency, user: Annotated[UserOut, Depends(get_current_user)]):
    currencies = ",".join(curr_body.to_currency)
    response_data_currency = await get_exchange_rate(currencies)
    return {"User": user.username, "Email": user.email, "currency_data": response_data_currency}

@currency_router.get('/list')
async def get_list_currency():
    return await get_supported_currencies()