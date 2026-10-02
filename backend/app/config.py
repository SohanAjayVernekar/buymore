from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    postgres_url: str
    mongodb_url: str
    mongodb_database: str = "buymore"
    elasticsearch_url: str
    elasticsearch_index: str = "orders"
    rabbitmq_url: str
    cors_origins: str = "http://localhost:5174"


settings = Settings()
