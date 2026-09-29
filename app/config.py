import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

class Settings:
    PROJECT_NAME: str = "PocketSmart AI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Smart GenAI-Powered Budget & Recommendation Assistant"
    
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "pocketsmart_custom_jwt_secret_key_2026_default_secret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    COOKIE_NAME: str = "pocketsmart_session"
    
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_TYPES: set = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
    UPLOAD_DIR: Path = BASE_DIR / "static" / "uploads"
    
    DB_PATH: Path = BASE_DIR / "pocketsmart.db"

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
