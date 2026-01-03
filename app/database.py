from collections.abc import AsyncGenerator

from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import settings

engine = create_async_engine(settings.database_url)

session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator:
    async with session_maker() as new_session:
        yield new_session


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # pk автоматически индексируется
