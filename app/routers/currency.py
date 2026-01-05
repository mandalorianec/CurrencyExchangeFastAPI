from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Form, status
from fastapi_limiter.depends import RateLimiter

from app.config import settings
from app.models.currency import Currency
from app.schemas import ApiErrorSchema, CurrencyCode, CurrencyResponse, CurrencySchema
from app.service.currency_service import CurrencyService

currency_router = APIRouter(tags=["Операции с валютой"])


@currency_router.get(
    "/currencies",
    response_model=list[CurrencyResponse],
    responses={500: {"model": ApiErrorSchema, "description": "База данных недоступна"}},
)
@inject
async def get_all_currencies(currency_service: FromDishka[CurrencyService]) -> list[Currency]:
    currencies = await currency_service.get_all_currencies()
    return currencies


@currency_router.post(
    "/currencies",
    response_model=CurrencyResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=settings.redis_times, seconds=settings.redis_seconds))],
    responses={
        400: {"model": ApiErrorSchema, "description": "Отсутствует нужное поле формы"},
        409: {"model": ApiErrorSchema, "description": "Валюта с таким кодом уже существует"},
        500: {"model": ApiErrorSchema, "description": "База данных недоступна"},
    },
)
@inject
async def add_new_currency(
    currency: Annotated[CurrencySchema, Form()], currency_service: FromDishka[CurrencyService]
) -> Currency:
    created_currency = await currency_service.add_currency(currency)
    return created_currency


@currency_router.get(
    "/currency/{code}",
    response_model=CurrencyResponse,
    responses={
        400: {"model": ApiErrorSchema, "description": "Код валюты отсутствует в адресе"},
        404: {"model": ApiErrorSchema, "description": "Валюта не найдена"},
        500: {"model": ApiErrorSchema, "description": "База данных недоступна"},
    },
)
@inject
async def get_currency(code: CurrencyCode, currency_service: FromDishka[CurrencyService]) -> Currency:
    currency = await currency_service.get_currency_by(code)
    return currency
