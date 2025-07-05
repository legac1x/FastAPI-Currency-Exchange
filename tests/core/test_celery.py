from app.celery_app import celery_app
from app.tasks.currency import update_currency_rates

def test_celery_beat_schedule_contains_update_currency_rates():
    schedule = celery_app.conf.beat_schedule
    assert "update-every-hour" in schedule
    task_info = schedule["update-every-hour"]
    assert task_info['task'] == "update_currency_rates"
    assert task_info["schedule"].minute == {0}
    assert task_info['schedule'].hour == set(range(24))

def test_task_registered_in_celery():
    assert "update_currency_rates" in celery_app.tasks