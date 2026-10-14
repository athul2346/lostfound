from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@lostfound.local"
    BASE_URL: str = "http://localhost:8000"
    UPLOAD_DIR: str = "uploads"
    MAX_PHOTOS_PER_ITEM: int = 5
    MAX_PHOTO_BYTES: int = 5 * 1024 * 1024  # 5 MB

    class Config:
        env_file = ".env"


settings = Settings()