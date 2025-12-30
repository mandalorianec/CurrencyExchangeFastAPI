from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter

from app.config import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis_url = f"redis://{settings.redis_host}:6379"
    redis_connection = redis.from_url(redis_url, encoding="utf8")
    await FastAPILimiter.init(redis_connection)
    yield
    await FastAPILimiter.close()
