import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST : str = os.getenv("DB_HOST")
    DB_PORT : int = os.getenv("DB_PORT")
    DB_USER : str = os.getenv("DB_USER")
    DB_PASS : str = os.getenv("DB_PASS")
    DB_NAME : str = os.getenv("DB_NAME")

    @property
    def DATABASE_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )

settings = Settings()

