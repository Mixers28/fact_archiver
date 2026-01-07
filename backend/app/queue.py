from redis import Redis
from rq import Queue

from app.settings import get_redis_url


def get_queue(name: str = "default") -> Queue:
    redis_conn = Redis.from_url(get_redis_url())
    return Queue(name, connection=redis_conn)
