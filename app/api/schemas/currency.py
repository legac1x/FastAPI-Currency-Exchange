from pydantic import BaseModel

class Currency(BaseModel):
    currency_from: str
    currency_to: str

class DefinitelyCurrencyIn(Currency):
    pass

class DefinitelyCurrencyOut(Currency):
    conversion_rate: float

class CurrencyListOut(BaseModel):
    currency_from: str
    conversion_rates: dict[str, float | str]

class AmountExchange(Currency):
    amount: float

class AmountExchangeOut(Currency):
    converted_amount: float

class CurrencyHistory(BaseModel):
    base_currency: str
    target_currency: str
    rate: float
    amount: float
    converted_amount: float
    exchange_time: str

