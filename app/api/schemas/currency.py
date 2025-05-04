from datetime import datetime
from pydantic import BaseModel

class CurrencyConvert(BaseModel):
    from_currency: str | None = None
    to_currency: list[str]

class CurrencyExchangeResponse(BaseModel):
    user: str
    email: str
    currency_data: dict

class CurrencyExchangeHistoryItem(BaseModel):
    from_currency: str
    to_currency: str
    time_currency: datetime

    class Config:
        json_encoders = {
            datetime: lambda x: x.strftime("%d.%m.%Y %H:%M")
        }

class CurrencyExchangeHistory(BaseModel):
    username: str
    user_history: list[CurrencyExchangeHistoryItem]
