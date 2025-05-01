import httpx
from fastapi import HTTPException, status

from app.core.config import settings

API_KEY = settings.API_KEY
BASE_URL = "https://api.exchangeratesapi.io/v1/latest"

async def get_exchange_rate(symbols: str = "RUB"):
    params = {
        "access_key": API_KEY,
        "symbols": symbols
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BASE_URL, params=params)
            data = response.json()
            if "error" in data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=data["error"]
                )
            return {"currency_from": data["base"], "currency_to": data["rates"]}
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Network error: {e}"
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"HTTP error: {e}"
            )

async def get_supported_currencies():
    async with httpx.AsyncClient() as client:
        try:
            params = {"access_key": API_KEY}
            response = await client.get(BASE_URL, params=params)
            data = response.json()
            if "error" in data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=data["error"]
                )
            return data.get("rates", {})
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Network error: {e}"
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"HTTP error: {e}"
            )
