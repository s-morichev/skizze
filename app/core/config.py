from pathlib import Path

from pydantic import BaseSettings, EmailStr, Field, validator


class Settings(BaseSettings):
    access_token_expire_minutes: int = 30
    debug: bool = Field(default=True, env="BACKEND_DEBUG")
    secret_key: str = Field(..., env="BACKEND_SECRET_KEY")
    admin_email: EmailStr = Field(..., env="BACKEND_ADMIN_EMAIL")
    admin_password: str = Field(..., env="BACKEND_ADMIN_PASSWORD")
    sqlalchemy_database_uri: str = Field(
        ...,
        env="BACKEND_PG_DSN",
    )

    @validator("sqlalchemy_database_uri", pre=True)
    def replace_scheme_to_async(cls, database_uri: str) -> str:  # noqa: N805
        return database_uri.replace("postgresql://", "postgresql+asyncpg://")

    class Config(object):
        # для запуска на хосте и дебага
        env_file = Path(__file__).parent.parent.parent / ".env.local"


settings = Settings()
