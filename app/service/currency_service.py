from app.models.currency import Currency
from app.repositories.currency_repository import CurrencyRepository
from app.schemas import CurrencySchema


class CurrencyService:
    def __init__(self, rep: CurrencyRepository):
        self.rep = rep

    async def get_all_currencies(self) -> list[Currency]:
        return await self.rep.get_all()

    async def get_currency_by(self, code: str) -> Currency:
        currency = await self.rep.get_currency_by(code)
        return currency

    async def add_currency(self, currency: CurrencySchema) -> Currency:
        await self.rep.add_currency(currency)
        created_currency = await self.rep.get_currency_by(currency.code)
        return created_currency
