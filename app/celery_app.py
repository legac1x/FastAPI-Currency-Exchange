from celery import Celery
from celery.schedules import crontab


celery_app = Celery("currency_app", broker="redis://redis:6379/0", backend="redis://redis:6379/1")

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json']
)

celery_app.conf.beat_schedule = {
    "update-every-hour": {
        "task": "update_currency_rates",
        "schedule": crontab(minute=0, hour='*')
    }
}

celery_app.conf.timezone = "UTC"
from app.tasks import currency