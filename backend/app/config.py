import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Root directory of the repository (parent of backend)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # NASA Earthdata Login Credentials
    EARTHDATA_USERNAME: str = ""
    EARTHDATA_PASSWORD: str = ""

    # API Configuration
    API_PORT: int = 8000
    API_HOST: str = "127.0.0.1"
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

    # Storage paths
    DATA_DIR: Path = (BACKEND_DIR / "data") if (BACKEND_DIR / "data").exists() else (BASE_DIR / "data")
    RAW_DIR: Path = BASE_DIR / "data" / "raw"
    PROCESSED_DIR: Path = BASE_DIR / "data" / "processed"
    CASES_DIR: Path = BASE_DIR / "data" / "cases"
    CACHE_DIR: Path = BASE_DIR / "data" / "cache"

    # Database Configuration
    DATABASE_URL: str = ""

    @property
    def db_url(self) -> str:
        return self.DATABASE_URL if self.DATABASE_URL else f"sqlite:///{self.DATA_DIR / 'parallax.db'}"

    model_config = SettingsConfigDict(
        env_file=[
            str(BASE_DIR / ".env"),
            str(BACKEND_DIR / ".env"),
        ],
        extra="ignore"
    )

settings = Settings()

# Ensure directories exist if filesystem is writable
for path in [settings.DATA_DIR, settings.RAW_DIR, settings.PROCESSED_DIR, settings.CASES_DIR, settings.CACHE_DIR]:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
