from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Query
from fastapi_limiter.depends import RateLimiter

from app.config import settings
from app.schemas import ApiErrorSchema, ConvertedExchangeRateResponse, CurrencyCode, InputDecimal
from app.service.exchange_service import ExchangeService

exchange_router = APIRouter(tags=["Операции с обменом"])


@exchange_router.get(
    "/exchange",
    dependencies=[Depends(RateLimiter(times=settings.redis_times, seconds=settings.redis_seconds))],
    responses={500: {"model": ApiErrorSchema, "description": "База данных недоступна"}},
)
@inject
async def convert_amount(
    from_: Annotated[CurrencyCode, Query(alias="from")],
    to: CurrencyCode,
    amount: InputDecimal,
    exchange_service: FromDishka[ExchangeService],
) -> ConvertedExchangeRateResponse:
    converted = await exchange_service.convert(from_, to, amount)
    return converted
