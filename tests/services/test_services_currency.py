from io import StringIO
import csv

from unittest.mock import AsyncMock, patch
from fastapi.responses import StreamingResponse

from app.api.schemas.currency import AmountExchange, DefinitelyCurrencyOut, CurrencyHistory
from app.services.currency import definitely_currency, list_currencies, amount_exchange, export_history, history_of_user
from app.api.schemas.currency import DefinitelyCurrencyIn

from tests.mocks.redis import setup_redis_mock

@patch("app.services.currency.get_redis", new_callable=AsyncMock)
@patch("app.services.currency.get_exchange_rate", new_callable=AsyncMock)
async def test_definitely_currency(mock_get_exchange_rate, mock_redis_client):
    setup_redis_mock(mock_redis_client, {})
    mock_get_exchange_rate.return_value = {"conversion_rate": 89.5003}

    # Первый вызов, достаем данные через API
    result = await definitely_currency(DefinitelyCurrencyIn(currency_from="EUR", currency_to="RUB"))
    assert result.currency_from == "EUR"
    assert result.currency_to == "RUB"
    assert result.conversion_rate == 89.5003
    assert mock_get_exchange_rate.call_count == 1

    # Второй вызов, достаем данные из кеша Redis
    result2 = await definitely_currency(DefinitelyCurrencyIn(currency_from="EUR", currency_to="RUB"))
    assert result2.conversion_rate == 89.5003
    assert mock_get_exchange_rate.call_count == 1

@patch("app.services.currency.get_redis", new_callable=AsyncMock)
@patch("app.services.currency.get_supported_currencies", new_callable=AsyncMock)
async def test_list_currencies(mock_get_supported_currencies, mock_redis_client):
    setup_redis_mock(mock_redis_client, {})
    mock_get_supported_currencies.return_value = {"currency_from": "USD", "conversion_rates": {"RUB": 79.0105}}

    # Первый вызов, достаем данные через API
    result = await list_currencies(currency_from="USD")
    assert result.currency_from == "USD"
    assert "conversion_rates" in result.model_dump()
    assert mock_get_supported_currencies.call_count == 1

    # Второй вызов, достаем данные из кеша Redis
    result2 = await list_currencies(currency_from="USD")
    assert "conversion_rates" in result2.model_dump()
    assert mock_get_supported_currencies.call_count == 1

@patch("app.services.currency.definitely_currency", new_callable=AsyncMock)
async def test_amount_exchange(mock_definitely_currency, create_test_db, override_get_current_user, override_get_async_session):
    current_user = override_get_current_user
    mock_definitely_currency.return_value = DefinitelyCurrencyOut(
        currency_from="EUR",
        currency_to="RUB",
        conversion_rate=89.5
    )
    exchange = AmountExchange(currency_from="EUR", currency_to="RUB", amount=10)
    result = await amount_exchange(exchange, current_user, override_get_async_session)
    assert result.currency_from == "EUR"
    assert result.currency_to == "RUB"
    assert result.converted_amount == 10 * 89.5
    assert mock_definitely_currency.call_count == 1

async def test_history_exchange(create_test_db, override_get_current_user, override_get_async_session):
    async with override_get_async_session as session:
        result = await history_of_user(session, override_get_current_user)
    assert len(result) == 2
    history1, history2 = result
    assert history1.base_currency == "EUR"
    assert history1.target_currency == "RUB"
    assert history1.amount == 100
    assert history1.converted_amount == 8980
    assert history1.rate == 89.8
    assert history1.exchange_time == "24.06.2025 11:40"

    assert history2.base_currency == "USD"
    assert history2.target_currency == "RUB"
    assert history2.amount == 10
    assert history2.converted_amount == 795
    assert history2.rate == 79.5
    assert history2.exchange_time == "23.06.2025 16:40"

@patch("app.services.currency.history_of_user")
async def test_history_export(mock_history_of_user, create_test_db, override_get_current_user, override_get_async_session):
    mock_history_of_user.return_value = [
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

    result = await export_history(format="csv", db=override_get_async_session, curr_user=override_get_current_user)
    assert isinstance(result, StreamingResponse)

    data = []
    async for ch in result.body_iterator:
        data.append(ch)
    body = ''.join(data)
    csv_data = csv.reader(StringIO(body))
    rows = list(csv_data)
    assert rows[0] == ["Currency From", "Currency To", "Rate", "Amount", "Converted amount", "Exchange Time"]
    assert rows[1] == ["EUR", "RUB", "89.8", "100.0", "8980.0", "24.06.2025 11:40"]
    assert rows[2] == ["USD", "RUB", "79.5", "10.0", "795.0", "23.06.2025 16:40"]