import respx
from httpx import Response, RequestError
from fastapi import HTTPException
import pytest

from app.utils.external_api import get_exchange_rate, get_supported_currencies
from app.core.config import settings

API_KEY = settings.API_KEY
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}"


@respx.mock
async def test_get_exchange_rate_success():
    fake_response = {
        "result": "success",
        "base_code": "USD",
        "target_code": "RUB",
        "conversion_rate": 79.5
    }

    route = respx.get(f"{BASE_URL}/pair/USD/RUB").mock(return_value=Response(200, json=fake_response))

    result = await get_exchange_rate("USD", "RUB")

    assert route.called
    assert result == {
        "currency_from": "USD",
        "currency_to": "RUB",
        "conversion_rate": 79.5
    }

@pytest.mark.parametrize("side_effect, mock_response, expected_details", [
    (None, {"result": "error", "error-type": "unknown-code"}, "unknown-code"),
    (RequestError("Connection time out"), None, "Network error: Connection time out")
])
@respx.mock
async def test_get_exchange_rate_errors(side_effect, mock_response, expected_details):
    if side_effect:
        respx.get(f"{BASE_URL}/pair/USD/RUB").mock(side_effect=side_effect)
        with pytest.raises(HTTPException) as exc_info:
            await get_exchange_rate("USD", "RUB")
    else:
        respx.get(f"{BASE_URL}/pair/ZXC/QWE").mock(return_value=Response(200, json=mock_response))
        with pytest.raises(HTTPException) as exc_info:
            await get_exchange_rate("ZXC", "QWE")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == expected_details

@respx.mock
async def test_get_supported_currencies_success():
    fake_response = {
        "result": "success",
        "base_code": "USD",
        "conversion_rates": {
		"USD": 1,
		"AUD": 1.4817,
		"BGN": 1.7741,
		"CAD": 1.3168,
		"CHF": 0.9774,
		"CNY": 6.9454,
		"EGP": 15.7361,
		"EUR": 0.9013,
		"GBP": 0.7679,
        "RUB": 79.5123}
    }
    route = respx.get(f"{BASE_URL}/latest/USD").mock(return_value=Response(200, json=fake_response))
    result = await get_supported_currencies("USD")

    assert route.called
    assert result == {
        "currency_from": "USD",
        "conversion_rates": {
		"USD": 1,
		"AUD": 1.4817,
		"BGN": 1.7741,
		"CAD": 1.3168,
		"CHF": 0.9774,
		"CNY": 6.9454,
		"EGP": 15.7361,
		"EUR": 0.9013,
		"GBP": 0.7679,
        "RUB": 79.5123}
    }

@pytest.mark.parametrize("side_effect, mock_response, expected_details", [
    (RequestError("Connection time out"), None, "Network error: Connection time out"),
    (None, {"result": "error", "error-type": "unknown-code"}, "unknown-code")
])
@respx.mock
async def test_get_supported_errors(side_effect, mock_response, expected_details):
    if side_effect:
        respx.get(f"{BASE_URL}/latest/USD").mock(side_effect=side_effect)
        with pytest.raises(HTTPException) as exc_info:
            await get_supported_currencies("USD")
    else:
        respx.get(f"{BASE_URL}/latest/QWE").mock(return_value=Response(200, json=mock_response))
        with pytest.raises(HTTPException) as exc_info:
            await get_supported_currencies("QWE")

    assert exc_info.value.status_code ==  400
    assert exc_info.value.detail == expected_details