from sqlalchemy import VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Currency(Base):
    __tablename__ = 'currencies'

    code: Mapped[str] = mapped_column(VARCHAR(3), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    sign: Mapped[str] = mapped_column(VARCHAR(10))
