from datetime import datetime, timezone

from sqlalchemy import select
from requests.exceptions import RequestException

from app.utils.external_api import sync_supported_currencies
from app.celery_app import celery_app
from app.db.database import sync_session_maker
from app.db.models import CurrencyRate


@celery_app.task(
    name="update_currency_rates",
    bind=True,
    autoretry_for=(RequestException, Exception),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5}
)
def update_currency_rates(self):
    base_currency = "USD"
    data = sync_supported_currencies(base_currency)
    conversion_rates = data["conversion_rates"]
    with sync_session_maker() as session:
        stmt = select(CurrencyRate).where(CurrencyRate.base_currency == base_currency)
        res = session.execute(stmt)
        existing_rates = {rate.target_currency: rate for rate in res.scalars().all()}
        update_time = datetime.now(timezone.utc)

        for target_currency, rate in conversion_rates.items():
            if target_currency == base_currency:
                continue
            if target_currency in existing_rates:
                existing_rates[target_currency].rate = rate
                existing_rates[target_currency].updated_at = update_time
            else:
                session.add(CurrencyRate(
                    base_currency=base_currency,
                    target_currency=target_currency,
                    rate=rate,
                    updated_at=update_time
                ))
        session.commit()


