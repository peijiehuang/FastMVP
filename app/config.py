from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "RuoYi-FastAPI"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "mysql+aiomysql://root:password@localhost:3306/ruoyi_fast"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    TOKEN_EXPIRE_MINUTES: int = 30

    # Captcha
    CAPTCHA_ENABLED: bool = True
    CAPTCHA_EXPIRE_SECONDS: int = 120

    # File Upload
    UPLOAD_PATH: str = "./uploads"

    # Account lock after failed login attempts
    MAX_RETRY_COUNT: int = 5
    LOCK_TIME_MINUTES: int = 10

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
