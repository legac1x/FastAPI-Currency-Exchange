import json
from datetime import datetime
from unittest.mock import patch, Mock

from app.db.models import CurrencyRate
from app.tasks.currency import update_currency_rates

@patch("app.tasks.currency.sync_supported_currencies", new_callable=Mock)
@patch("app.tasks.currency.sync_session_maker")
def test_update_currency_rates(mock_sync_session_maker, mock_sync_supported_currencies):
    mock_sync_supported_currencies.return_value = {
        "currency_from": "USD",
        "conversion_rates": {
            "USD": 1.0,
            "EUR": 0.93,
            "RUB": 79.51
        }
    }

    existing_currency = CurrencyRate(
        base_currency="USD",
        target_currency="EUR",
        rate=0.9,
        updated_at=datetime(2025, 6, 15, 9, 0, 0)
    )

    mock_session = Mock()

    mock_result = Mock()
    mock_scalars = Mock()
    mock_scalars.all.return_value = [existing_currency]
    mock_result.scalars.return_value = mock_scalars

    mock_session.execute.return_value = mock_result

    mock_sync_session_maker.return_value.__enter__.return_value = mock_session
    mock_sync_session_maker.return_value.__exit__.return_value = None

    update_currency_rates()

    assert existing_currency.rate == 0.93

    added_obj = None
    for call in mock_session.add.call_args_list:
        arg = call.args[0]
        if arg.target_currency == "RUB":
            added_obj = arg
            break

    assert added_obj is not None
    assert added_obj.rate == 79.51