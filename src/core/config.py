from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="password")
    POSTGRES_DB: str = Field(default="posts_db")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)

    ELASTICSEARCH_HOST: str = Field(default="localhost")
    ELASTICSEARCH_PORT: int = Field(default=9200)

    DEBUG: bool = Field(default=False)

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def ELASTICSEARCH_URL(self) -> str:
        return f"http://{self.ELASTICSEARCH_HOST}:{self.ELASTICSEARCH_PORT}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
