import redis
import json
import os

# Connect to the Redis container
# We use host="redis" because that's the service name in docker-compose
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

try:
    cache = redis.from_url(REDIS_URL, decode_responses=True)
    cache.ping()
    print("Connected to Redis!")
except redis.ConnectionError:
    print("Warning: Redis not connected. Caching disabled.")
    cache = None

def get_cache(key: str):
    if not cache: return None
    data = cache.get(key)
    return json.loads(data) if data else None

def set_cache(key: str, data: dict, expire: int = 300):
    if not cache: return
    cache.set(key, json.dumps(data), ex=expire)