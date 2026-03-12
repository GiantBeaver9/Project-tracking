from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Project Tracker"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DB_DRIVER: str = "ODBC+Driver+17+for+SQL+Server"
    DB_HOST: str = "localhost"
    DB_PORT: int = 1433
    DB_NAME: str = "project_tracker"
    DB_USER: str = ""
    DB_PASSWORD: str = ""

    @property
    def database_url(self) -> str:
        return (
            f"mssql+pyodbc://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?driver={self.DB_DRIVER}"
        )

    # Auth / JWT
    SECRET_KEY: str = "CHANGE-ME-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Bcrypt
    BCRYPT_COST_FACTOR: int = 12

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    model_config = {"env_prefix": "PT_", "env_file": ".env", "extra": "ignore"}


settings = Settings()
