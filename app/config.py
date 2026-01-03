import os
from typing import Annotated

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    host_db: str
    port_db: int
    postgres_db: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.host_db}:{self.port_db}/{self.postgres_db}"

    db_scale: Annotated[int, Field(le=6)]
    db_integer_digits: Annotated[int, Field(le=15)]

    redis_host: str = "localhost"
    redis_times: int = 15
    redis_seconds: int = 60
    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))


settings = Settings()  # type: ignore[call-arg]
