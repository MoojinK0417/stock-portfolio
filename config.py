from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_host: str
    database_name: str
    database_user: str
    database_password: str
    database_port: int
    auth_secret_key: str
    auth_algorithm: str
    api_url: str
    open_api_key: str
    api_url: str

    class Config:
        env_file = ".env"

settings = Settings()

SQL_ALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.database_user}:{settings.database_password}@"
    f"{settings.database_host}:{settings.database_port}/{settings.database_name}"
)
