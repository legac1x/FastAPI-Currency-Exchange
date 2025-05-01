from pydantic import BaseModel

class Currency(BaseModel):
    from_currency: str | None = None
    to_currency: list[str]