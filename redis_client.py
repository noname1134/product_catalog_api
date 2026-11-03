import os

import redis
from dotenv import load_dotenv

load_dotenv()


def get_redis_client():
    return redis.Redis(
        host=os.environ["REDIS_HOST"],
        port=int(os.environ["REDIS_PORT"]),
        db=int(os.environ["REDIS_DB"]),
        decode_responses=True,
    )