from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi_limiter.depends import RateLimiter

from app.config import settings
from app.dependencies import ExchangeServiceDep
from app.schemas import (
    ApiErrorSchema,
    ConvertedExchangeRateResponse,
    CurrencyCode,
    InputDecimal,
)

exchange_router = APIRouter(tags=["Операции с обменом"])


@exchange_router.get(
    "/exchange",
    dependencies=[
        Depends(RateLimiter(times=settings.redis_times, seconds=settings.redis_seconds))
    ],
    responses={500: {"model": ApiErrorSchema, "description": "База данных недоступна"}},
)
async def convert_amount(
    exchange_service: ExchangeServiceDep,
    from_: Annotated[CurrencyCode, Query(alias="from")],
    to: CurrencyCode,
    amount: InputDecimal,
) -> ConvertedExchangeRateResponse:
    converted = await exchange_service.convert(from_, to, amount)
    return converted
