from unittest.mock import patch
import csv
from io import StringIO

from fastapi.responses import StreamingResponse

from app.api.schemas.currency import DefinitelyCurrencyIn, DefinitelyCurrencyOut, CurrencyHistory

url_services_for_patch = "app.api.endpoints.currency."

async def test_get_definitely_currency(client):
    data = DefinitelyCurrencyIn(
        currency_from="USD",
        currency_to="RUB"
    )
    mock_definitely_currency = DefinitelyCurrencyOut(
        currency_from="USD",
        currency_to="RUB",
        conversion_rate=79.512
    )
    with patch(f"{url_services_for_patch}definitely_currency", return_value=mock_definitely_currency):
        result = await client.post(url="/currency/definitely", json=data.model_dump())
        assert result.status_code == 200
        result_json = result.json()
        assert result_json == {"currency_from":"USD",
            "currency_to": "RUB",
            "conversion_rate": 79.512
        }

async def test_get_list_currencies(client):
    mock_data = {
        "currency_from": "USD",
        "conversion_rates": {
		"USD": 1,
		"RUB": 79.512,
		"EUR": 0.9013,
		"GBP": 0.7679, }
    }
    with patch(f"{url_services_for_patch}list_currencies", return_value=mock_data):
        result = await client.get("/currency/list", params={"currency_from": "USD"})
        assert result.status_code == 200
        result_json = result.json()
        assert result_json == {
            "currency_from": "USD",
            "conversion_rates": {
                "USD": 1,
                "RUB": 79.512,
                "EUR": 0.9013,
                "GBP": 0.7679, }
        }

async def test_get_amount_exchange(client):
    mock_data = {
        "currency_from": "USD",
        "currency_to": "RUB",
        "converted_amount": 795.12
    }
    with patch(f"{url_services_for_patch}amount_exchange", return_value=mock_data):
        result_data = {
            "currency_from": "USD",
            "currency_to": "RUB",
            "amount": 10.0
        }
        result = await client.post("/currency/amount", json=result_data)
        assert result.status_code == 200
        result_json = result.json()
        assert result_json == {
            "currency_from": "USD",
            "currency_to": "RUB",
            "converted_amount": 795.12
        }

async def test_get_history_exchange(client):
    mock_data = [
        {
            "base_currency": "EUR",
            "target_currency": "RUB",
            "rate": 89.812,
            "amount": 100.0,
            "converted_amount": 8981.2,
            "exchange_time": "24.06.2025 11:40"
        },
        {
            "base_currency": "USD",
            "target_currency": "RUB",
            "rate": 79.512,
            "amount": 10.0,
            "converted_amount": 795.12,
            "exchange_time": "23.06.2025 16:40"
        }
    ]
    with patch(f"{url_services_for_patch}history_of_user", return_value=mock_data):
        result = await client.get("/currency/history")
        assert result.status_code == 200
        result_json = result.json()
        assert result_json == [
        {
            "base_currency": "EUR",
            "target_currency": "RUB",
            "rate": 89.812,
            "amount": 100.0,
            "converted_amount": 8981.2,
            "exchange_time": "24.06.2025 11:40"
        },
        {
            "base_currency": "USD",
            "target_currency": "RUB",
            "rate": 79.512,
            "amount": 10.0,
            "converted_amount": 795.12,
            "exchange_time": "23.06.2025 16:40"
        }
    ]

async def test_get_history_export(client):
    mock_history_of_user = [
        CurrencyHistory(
            base_currency="EUR",
            target_currency="RUB",
            rate=89.8,
            amount=100,
            converted_amount=8980,
            exchange_time="24.06.2025 11:40"
        ),
        CurrencyHistory(base_currency="USD",
            target_currency="RUB",
            amount=10,
            converted_amount=795,
            rate=79.5,
            exchange_time="23.06.2025 16:40",
        )
    ]
    file = StringIO()
    writer = csv.writer(file)
    for r in mock_history_of_user:
        writer.writerow([
            r.base_currency,
            r.target_currency,
            r.rate,
            r.amount,
            r.converted_amount,
            r.exchange_time
        ])
    file.seek(0)
    mock_response = StreamingResponse(file, media_type="test/csv", headers={"Content-Disposition": "attachment; filename=conversion_history.csv"})
    with patch(f"{url_services_for_patch}export_history", return_value=mock_response) as mock:
        result = await client.get("/currency/history/export", params={"format": "csv"})
        assert result.status_code == 200
        assert result.headers["Content-Disposition"] == "attachment; filename=conversion_history.csv"