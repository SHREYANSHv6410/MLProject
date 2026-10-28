import os
from pathlib import Path


class Settings:
    PROJECT_NAME: str = "ReplySense"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Root paths - 4 parents: config.py -> core -> app -> backend -> root
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    ARTIFACTS_DIR: Path = Path(os.getenv("MODEL_DIR", str(BASE_DIR / "artifacts")))
    if not ARTIFACTS_DIR.is_absolute():
        ARTIFACTS_DIR = BASE_DIR / ARTIFACTS_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    
    # ML settings
    MODEL_PATH: Path = ARTIFACTS_DIR / "model.joblib"
    METADATA_PATH: Path = ARTIFACTS_DIR / "metadata.json"
    METRICS_PATH: Path = ARTIFACTS_DIR / "evaluation_report.json"
    DEFAULT_HORIZON_HOURS: float = float(os.getenv("DEFAULT_REPLY_HORIZON_HOURS", "24.0"))
    
    # History & Privacy
    ENABLE_HISTORY: bool = os.getenv("ENABLE_HISTORY", "true").lower() in ("true", "1", "yes")
    DATABASE_PATH: Path = BASE_DIR / "replysense.db"
    MAX_FILE_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB
    MAX_PREVIEW_MESSAGES: int = 500
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]


settings = Settings()
