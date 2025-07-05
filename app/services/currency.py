from http.client import HTTPException
from typing import List
from io import StringIO
import csv
import json

from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.responses import StreamingResponse

from app.core.redis import get_redis
from app.db.models import ConversionHistory
from app.api.schemas.currency import DefinitelyCurrencyIn, DefinitelyCurrencyOut, CurrencyListOut, AmountExchange, AmountExchangeOut
from app.core.security import get_user_from_db
from app.api.schemas.users import UserOut
from app.api.schemas.currency import CurrencyHistory
from app.utils.external_api import get_exchange_rate, get_supported_currencies


async def definitely_currency(current_currency: DefinitelyCurrencyIn) -> DefinitelyCurrencyOut:
    curr_from = current_currency.currency_from.upper()
    curr_to = current_currency.currency_to.upper()
    redis = await get_redis()
    key = f"{curr_from}->{curr_to}"
    cached = await redis.get(key)
    if cached:
        con_rate = float(cached)
    else:
        response = await get_exchange_rate(currency_from=curr_from, currency_to=curr_to)
        con_rate = float(response['conversion_rate'])
        await redis.set(key, con_rate, ex=3600)
    return DefinitelyCurrencyOut(
        currency_from=curr_from,
        currency_to=curr_to,
        conversion_rate=con_rate
    )

async def list_currencies(currency_from: str) -> CurrencyListOut:
    curr_from = currency_from.upper()
    redis = await get_redis()
    key = f"{curr_from}->conversion_rates"
    cached = await redis.get(key)
    if cached:
        conv_rates = json.loads(cached)
    else:
        rates = await get_supported_currencies(curr_from)
        conv_rates = rates["conversion_rates"]
        await redis.set(key, json.dumps(conv_rates), ex=3600)
    return CurrencyListOut(
        currency_from=curr_from,
        conversion_rates=conv_rates
    )

async def amount_exchange(
    exchange: AmountExchange,
    current_user: UserOut,
    db: AsyncSession
) -> AmountExchangeOut:
    defi_curr = DefinitelyCurrencyIn(currency_from=exchange.currency_from, currency_to=exchange.currency_to)
    data = await definitely_currency(defi_curr)
    user =  await get_user_from_db(current_user.username, db)
    conv_amount = float(data.conversion_rate) * int(exchange.amount)
    history = ConversionHistory(
        base_currency=data.currency_from,
        target_currency=data.currency_to,
        amount=exchange.amount,
        converted_amount=conv_amount,
        rate=data.conversion_rate,
        user=user
    )
    db.add(history)
    await db.commit()
    response_data = AmountExchangeOut(
        currency_from=data.currency_from,
        currency_to=data.currency_to,
        converted_amount=conv_amount
    )
    return response_data

async def history_of_user(db: AsyncSession, curr_user: UserOut) -> List[CurrencyHistory]:
    user = await get_user_from_db(curr_user.username, db)
    res = await db.execute(
        select(ConversionHistory).where(ConversionHistory.user_id == user.id).order_by(
        ConversionHistory.exchange_time.desc())
    )
    list_of_history = []
    for x in res.scalars().all():
        ex_time = x.exchange_time.strftime("%d.%m.%Y %H:%M")
        curr_history = CurrencyHistory(
            base_currency=x.base_currency,
            target_currency=x.target_currency,
            rate=x.rate,
            amount=x.amount,
            converted_amount=x.converted_amount,
            exchange_time=ex_time
        )
        list_of_history.append(curr_history)
    return list_of_history

async def export_history(format: str, db: AsyncSession, curr_user: UserOut):
    if format == "csv":
        history = await history_of_user(db, curr_user)
        file = StringIO()
        writer = csv.writer(file)

        writer.writerow(["Currency From", "Currency To", "Rate", "Amount", "Converted amount", "Exchange Time"])

        for r in history:
            writer.writerow([
                r.base_currency,
                r.target_currency,
                r.rate,
                r.amount,
                r.converted_amount,
                r.exchange_time
            ])

        file.seek(0)
        return StreamingResponse(file, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=conversion_history.csv"})
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid format for download"
        )

