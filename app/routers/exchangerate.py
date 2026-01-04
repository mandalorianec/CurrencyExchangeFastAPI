from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi_limiter.depends import RateLimiter

from app.config import settings
from app.dependencies import CurrencyServiceDep, ExchangeRateServiceDep, _divide_codepair
from app.exceptions import CurrencyNotFoundError
from app.models.exchangerate import ExchangeRate
from app.schemas import ApiErrorSchema, ExchangeRateResponse, ExchangeRateSchema, InputDecimal

exchange_rate_router = APIRouter(tags=["Операции с обменным курсами"])


@exchange_rate_router.get(
    "/exchangeRates",
    response_model=list[ExchangeRateResponse],
    responses={500: {"model": ApiErrorSchema, "description": "База данных недоступна"}},
)
async def get_all_exchangerates(exchangerate_service: ExchangeRateServiceDep) -> list[ExchangeRate]:
    exchangerates = await exchangerate_service.get_all_exchangerates()
    return exchangerates


@exchange_rate_router.post(
    "/exchangeRates",
    response_model=ExchangeRateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=settings.redis_times, seconds=settings.redis_seconds))],
    responses={
        400: {"model": ApiErrorSchema, "description": "Отсутствует нужное поле формы"},
        409: {"model": ApiErrorSchema, "description": "Валютная пара с таким кодом уже существует"},
        404: {"model": ApiErrorSchema, "description": "Одна (или обе) валюта из валютной пары не существует в БД"},
        500: {"model": ApiErrorSchema, "description": "База данных недоступна"},
    },
)
async def add_new_exchangerate(
    exchangerate: Annotated[ExchangeRateSchema, Form()],
    currency_service: CurrencyServiceDep,
    exchangerate_service: ExchangeRateServiceDep,
) -> ExchangeRate:
    try:
        base_currency = await currency_service.get_currency_by(exchangerate.base_currency_code)
        target_currency = await currency_service.get_currency_by(exchangerate.target_currency_code)
    except CurrencyNotFoundError as e:
        raise HTTPException(
            status_code=e.code, detail="Одна (или обе) валюта из валютной пары не существует в БД"
        ) from e

    created_exchange_rate = await exchangerate_service.add_exchangerate(
        exchangerate, base_currency.id, target_currency.id
    )
    return created_exchange_rate


@exchange_rate_router.get(
    "/exchangeRate/{codepair}",
    response_model=ExchangeRateResponse,
    responses={
        400: {"model": ApiErrorSchema, "description": "Коды валют пары отсутствуют в адресе"},
        404: {"model": ApiErrorSchema, "description": "Обменный курс для пары не найден"},
        500: {"model": ApiErrorSchema, "description": "База данных недоступна"},
    },
)
async def get_exchangerate_by_codepair(
    codes: Annotated[tuple[str, str], Depends(_divide_codepair)], exchangerate_service: ExchangeRateServiceDep
) -> ExchangeRate:
    base_code, target_code = codes
    exchangerate = await exchangerate_service.get_exchangerate_by_codepair(base_code, target_code)
    return exchangerate


@exchange_rate_router.patch(
    "/exchangeRate/{codepair}",
    response_model=ExchangeRateResponse,
    responses={
        400: {"model": ApiErrorSchema, "description": "Отсутствует нужное поле формы"},
        404: {"model": ApiErrorSchema, "description": "Валютная пара отсутствует в базе данных"},
        500: {"model": ApiErrorSchema, "description": "База данных недоступна"},
    },
)
async def change_exchangerate_by_codepair(
    codes: Annotated[tuple[str, str], Depends(_divide_codepair)],
    rate: Annotated[InputDecimal, Form()],
    exchangerate_service: ExchangeRateServiceDep,
) -> ExchangeRate:
    base_code, target_code = codes
    new_exchangerate = await exchangerate_service.update_exchangerate(base_code, target_code, rate)
    return new_exchangerate
