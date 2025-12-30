from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DECIMAL

if TYPE_CHECKING:
    from app.models.currency import Currency

from app.database import Base


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    base_currency_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("currencies.id"), index=True
    )
    target_currency_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("currencies.id"), index=True
    )
    rate: Mapped[Decimal] = mapped_column(DECIMAL(21, 6))

    base_currency: Mapped["Currency"] = relationship(foreign_keys=[base_currency_id])
    target_currency: Mapped["Currency"] = relationship(
        foreign_keys=[target_currency_id]
    )

    __table_args__ = (
        Index(
            "ix_base_id_target_id_unique",
            "base_currency_id",
            "target_currency_id",
            unique=True,
        ),
    )
