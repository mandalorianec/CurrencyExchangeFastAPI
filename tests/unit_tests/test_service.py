from decimal import Decimal

import pytest

from app.exceptions import CurrencyNotFoundError
from app.service.currency_service import CurrencyService
from app.service.exchange_service import ExchangeService


@pytest.mark.anyio
@pytest.mark.parametrize("amount", [(Decimal(24))])
async def test_convert_usd_rub(
        exchange_service: ExchangeService, amount: Decimal, rub_currency, usd_currency,
        exchange_rate_usd_rub
) -> None:
    response = (await exchange_service.convert("USD", "RUB", amount)).converted_amount
    assert response == Decimal(str(exchange_rate_usd_rub.rate)) * amount


@pytest.mark.anyio
@pytest.mark.parametrize("amount", [(Decimal(24))])
async def test_convert_rub_usd(exchange_service: ExchangeService, amount: Decimal, rub_currency,
                               usd_currency, exchange_rate_usd_rub) -> None:
    response = (await exchange_service.convert("RUB", "USD", amount)).converted_amount
    assert response == (1 / Decimal(str(exchange_rate_usd_rub.rate)) * amount).quantize(Decimal("0.000001"))


@pytest.mark.anyio
async def test_convert_eur_rub(exchange_service: ExchangeService, eur_currency, usd_currency, exchange_rate_usd_rub,
                               exchange_rate_usd_eur) -> None:
    response = await exchange_service.convert("EUR", "RUB", Decimal('24'))
    assert response.converted_amount == Decimal('2195.294118')


@pytest.mark.anyio
async def test_get_non_existent_currency(currency_service: CurrencyService) -> None:
    with pytest.raises(CurrencyNotFoundError):
        await currency_service.get_currency_by("USD")
