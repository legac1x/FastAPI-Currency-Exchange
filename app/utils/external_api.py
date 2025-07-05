import httpx
import requests
from fastapi import HTTPException, status

from app.core.config import settings

API_KEY = settings.API_KEY
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}"

async def get_exchange_rate(currency_from: str = "USD", currency_to: str = "RUB"):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/pair/{currency_from}/{currency_to}")
            data = response.json()
            if data['result'] == 'error':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=data["error-type"]
                )
            conversion_rates = data["conversion_rate"]
            return {
                "currency_from": currency_from,
                "currency_to": currency_to,
                "conversion_rate": conversion_rates
            }
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

async def get_supported_currencies(currency_from: str = "USD"):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/latest/{currency_from}")
            data = response.json()
            if data['result'] == 'error':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=data["error-type"]
                )
            conversion_rates = data['conversion_rates']
            return {
                "currency_from": currency_from,
                "conversion_rates": conversion_rates
            }
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

def sync_supported_currencies(currency_from: str = "USD"):
    try:
        response = requests.get(f"{BASE_URL}/latest/{currency_from}")
        data = response.json()
        if data['result'] == 'error':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=data["error-type"]
            )
        conversion_rates = data['conversion_rates']
        return {
            "currency_from": currency_from,
            "conversion_rates": conversion_rates
        }
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