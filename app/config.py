import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    app_name: str = os.getenv("APP_NAME", "Autonomous AGI Lab")
    port: int = int(os.getenv("PORT", "8000"))
    host: str = os.getenv("HOST", "0.0.0.0")
    repo_root: str = os.getenv("REPO_ROOT", ".")
    memory_path: str = os.getenv("MEMORY_PATH", "./data/memory.json")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = AppConfig()
