from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.config import settings
from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

engine = create_async_engine(settings.database_url)

session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with session_maker() as new_session:
        yield new_session


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # pk автоматически индексируется
