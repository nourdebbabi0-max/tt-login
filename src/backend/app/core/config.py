from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SESSION_INACTIVITY_EXPIRE_MINUTES: int = 10

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM: str

    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 15

    FRONTEND_BASE_URL: str = "http://localhost:5179"
    FRONTEND_ACTIVATION_URL: str = "http://localhost:5179/activate-account"
    FRONTEND_RESET_URL: str = "http://localhost:5179/reset-password"
    FRONTEND_SECURE_VALIDATE_URL: str = "http://localhost:5179/recuperation-securisee/validate"
    FRONTEND_SECURE_RESET_URL: str = "http://localhost:5179/recuperation-securisee/reset"

    class Config:
        env_file = ".env"


settings = Settings()