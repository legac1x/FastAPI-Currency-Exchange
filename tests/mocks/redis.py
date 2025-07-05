from unittest.mock import AsyncMock

def setup_redis_mock(mock_redis_client, key_values: dict):
    store = key_values.copy()

    async def get_side_effect(key):
        return store.get(key, None)

    async def set_side_effect(key: str, value, *args, **kwargs):
        store[key] = value
        return True

    fake_redis = AsyncMock()
    fake_redis.get.side_effect = get_side_effect
    fake_redis.set.side_effect = set_side_effect

    mock_redis_client.return_value = fake_redis
    return fake_redis

