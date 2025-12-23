from typing import Annotated
from app.config import settings
from fastapi import APIRouter, Query, Depends
from fastapi_limiter.depends import RateLimiter

from app.dependencies import ExchangeServiceDep
from app.schemas import ConvertedExchangeRateResponse, CurrencyCode, InputDecimal, ApiErrorSchema

exchange_router = APIRouter(tags=['Операции с обменом'])


@exchange_router.get("/exchange",
                     response_model=ConvertedExchangeRateResponse,
                     dependencies=[Depends(RateLimiter(times=settings.redis_times, seconds=settings.redis_seconds))],
                     responses={500: {"model": ApiErrorSchema, "description": "База данных недоступна"}})
async def convert_amount(exchange_service: ExchangeServiceDep,
                         from_: Annotated[CurrencyCode, Query(alias='from')],
                         to: CurrencyCode,
                         amount: InputDecimal
                         ):
    converted = await exchange_service.convert(from_, to, amount)
    return converted
